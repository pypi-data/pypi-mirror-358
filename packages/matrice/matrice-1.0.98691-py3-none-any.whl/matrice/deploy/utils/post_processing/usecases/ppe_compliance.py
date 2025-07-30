from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field
import time
from collections import deque
from datetime import datetime, timezone

from ..core.base import BaseProcessor, ProcessingContext, ProcessingResult, ConfigProtocol
from ..core.config import BaseConfig, AlertConfig
from ..utils import (
    filter_by_confidence,
    calculate_counting_summary,
    match_results_structure,
    apply_category_mapping
)

@dataclass
class PPEComplianceConfig(BaseConfig):
    no_hardhat_threshold: float = 0.91
    no_mask_threshold: float = 0.2
    no_safety_vest_threshold: float = 0.2
    violation_categories: List[str] = field(default_factory=lambda: [
        "NO-Hardhat", "NO-Mask", "NO-Safety Vest"
    ])
    alert_config: Optional[AlertConfig] = None
    index_to_category: Optional[Dict[int, str]] = field(default_factory=lambda: {
        -1: 'Hardhat', 0: 'Mask', 1: 'NO-Hardhat', 2: 'NO-Mask', 3: 'NO-Safety Vest',
        4: 'Person', 5: 'Safety Cone', 6: 'Safety Vest', 7: 'machinery', 8: 'vehicle'
    })

class PPEComplianceUseCase(BaseProcessor):
    """PPE compliance detection use case with violation smoothing and alerting."""

    def __init__(self):
        super().__init__("ppe_compliance_detection")
        self.category = "ppe"
        # For each violation category, maintain a window of last N detections (deque of dicts)
        self.window_size = 20
        self.cooldown_frames = 6  # Number of frames to persist a box after it disappears
        # For each violation category, track {instance_id: deque of detections}
        self.violation_windows = {
            cat: {} for cat in ["NO-Hardhat", "NO-Mask", "NO-Safety Vest"]
        }
        # For persistence: {cat: {instance_id: cooldown_counter}}
        self.violation_cooldowns = {
            cat: {} for cat in ["NO-Hardhat", "NO-Mask", "NO-Safety Vest"]
        }

    def process(self, data: Any, config: ConfigProtocol, context: Optional[ProcessingContext] = None) -> ProcessingResult:
        """Process PPE compliance detection and generate results."""
        start_time = time.time()
        try:
            if not isinstance(config, PPEComplianceConfig):
                return self.create_error_result("Invalid config type", usecase=self.name, category=self.category, context=context)
            if context is None:
                context = ProcessingContext()

            input_format = match_results_structure(data)
            context.input_format = input_format
            context.no_hardhat_threshold = config.no_hardhat_threshold

            processed_data = apply_category_mapping(data, config.index_to_category)
            processed_data = self._filter_ppe_violations(processed_data, config)

            general_counting_summary = calculate_counting_summary(data)
            counting_summary = self._count_categories(processed_data, config)
            insights = self._generate_insights(counting_summary, config)
            alerts = self._check_alerts(counting_summary, config)
            predictions = self._extract_predictions(processed_data)
            summary = self._generate_summary(counting_summary, alerts)

            context.mark_completed()

            result = self.create_result(
                data={
                    "counting_summary": counting_summary,
                    "general_counting_summary": general_counting_summary,
                    "alerts": alerts,
                    "total_violations": counting_summary.get("total_count", 0),
                },
                usecase=self.name,
                category=self.category,
                context=context
            )
            result.summary = summary
            result.insights = insights
            result.predictions = predictions
            return result

        except Exception as e:
            self.logger.error(f"Error in PPE compliance: {str(e)}")
            return self.create_error_result(
                f"PPE compliance processing failed: {str(e)}",
                error_type="PPEComplianceProcessingError",
                usecase=self.name,
                category=self.category,
                context=context
            )

    def _filter_ppe_violations(self, detections: list, config: PPEComplianceConfig) -> list:
        """
        Improved: Track and smooth each unique violation instance (person/box) separately using track_id if available, else bbox hash.
        Each instance gets its own window and cooldown. All valid instances are output per frame.
        """
        output = []
        for cat in self.violation_windows:
            # Step 1: Update windows for all current detections
            current_ids = set()
            for det in [d for d in detections if d.get('category') == cat]:
                # Use track_id if available, else quantized centroid as key
                if 'track_id' in det and det['track_id'] is not None:
                    instance_id = (cat, det['track_id'])
                else:
                    bbox = det.get('bounding_box', None)
                    if bbox:
                        # Quantize centroid to reduce sensitivity to small shifts
                        x = bbox.get('x', 0)
                        y = bbox.get('y', 0)
                        w = bbox.get('width', 0)
                        h = bbox.get('height', 0)
                        cx = int((x + w / 2) // 10)
                        cy = int((y + h / 2) // 10)
                        instance_id = (cat, cx, cy)
                    else:
                        instance_id = (cat, None)
                current_ids.add(instance_id)
                # Add detection to window
                if instance_id not in self.violation_windows[cat]:
                    self.violation_windows[cat][instance_id] = deque(maxlen=self.window_size)
                self.violation_windows[cat][instance_id].append(det)
                # Reset cooldown for this instance
                self.violation_cooldowns[cat][instance_id] = self.cooldown_frames

            # Step 2: For all tracked instances, decide if they should be output
            expired = []
            for instance_id, window in list(self.violation_windows[cat].items()):
                # If not seen in this frame, decrement cooldown
                if instance_id not in current_ids:
                    self.violation_cooldowns[cat][instance_id] -= 1
                # Remove if cooldown expired
                if self.violation_cooldowns[cat][instance_id] <= 0:
                    expired.append(instance_id)
                    continue
                # Smoothing: use average confidence in window
                confs = [d.get('confidence', 0.0) for d in window]
                avg_conf = sum(confs) / len(confs) if confs else 0.0
                threshold_name = f"{cat.lower().replace('-', '_')}_threshold"
                threshold = getattr(config, threshold_name, 0.2)
                if avg_conf >= threshold:
                    # Output the most recent detection in the window
                    output.append(window[-1])
            # Remove expired instances
            for instance_id in expired:
                self.violation_windows[cat].pop(instance_id, None)
                self.violation_cooldowns[cat].pop(instance_id, None)
        return output

    def _count_categories(self, detections: list, config: PPEComplianceConfig) -> dict:
        counts = {}
        for det in detections:
            cat = det.get('category', 'unknown')
            counts[cat] = counts.get(cat, 0) + 1
        return {
            "total_count": sum(counts.values()),
            "per_category_count": counts,
            "detections": [
                {"bounding_box": det.get("bounding_box"), "category": det.get("category")}
                for det in detections
            ]
        }

    CATEGORY_DISPLAY = {
        "NO-Hardhat": "No Hardhat Violations",
        "NO-Mask": "No Mask Violations",
        "NO-Safety Vest": "No Safety Vest Violations"
    }

    def _generate_insights(self, summary: dict, config: PPEComplianceConfig) -> List[str]:
        insights = []
        per_cat = summary.get("per_category_count", {})
        for cat, count in per_cat.items():
            display = self.CATEGORY_DISPLAY.get(cat, cat)
            insights.append(f"{display}:{count}")
        return insights

    def _check_alerts(self, summary: dict, config: PPEComplianceConfig) -> List[Dict]:
        alerts = []
        if not config.alert_config:
            return alerts
        total = summary.get("total_count", 0)
        if config.alert_config.count_thresholds:
            for category, threshold in config.alert_config.count_thresholds.items():
                if category == "all" and total >= threshold:
                    timestamp = datetime.now(timezone.utc).strftime('%Y-%m-%d-%H:%M:%S UTC')
                    alert_description = f"PPE violation count ({total}) exceeds threshold ({threshold})"
                    alerts.append({
                        "type": "count_threshold",
                        "severity": "warning",
                        "message": alert_description,
                        "category": category,
                        "current_count": total,
                        "threshold": threshold,
                        "human_text": f"Time: {timestamp}\n{alert_description}"
                    })
        return alerts

    def _extract_predictions(self, detections: list) -> List[Dict[str, Any]]:
        return [
            {
                "category": det.get("category", "unknown"),
                "confidence": det.get("confidence", 0.0),
                "bounding_box": det.get("bounding_box", {})
            }
            for det in detections
        ]

    def _generate_summary(self, summary: dict, alerts: List) -> str:
        total = summary.get("total_count", 0)
        parts = [f"{total} PPE violation(s) detected"] if total else []
        if alerts:
            parts.append(f"{len(alerts)} alert(s)")
        return ", ".join(parts)


