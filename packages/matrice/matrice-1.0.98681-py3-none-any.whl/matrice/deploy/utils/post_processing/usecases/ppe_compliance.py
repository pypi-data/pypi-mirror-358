from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field
import time
from collections import defaultdict, deque
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
    def __init__(self):
        super().__init__("ppe_compliance_detection")
        self.category = "ppe"
        # Persistence for each violation category
        self.persistence_window = 40
        self.violation_persistence = {
            'NO-Hardhat': {'count': 0, 'detection': None},
            'NO-Mask': {'count': 0, 'detection': None},
            'NO-Safety Vest': {'count': 0, 'detection': None}
        }

    def process(self, data: Any, config: ConfigProtocol, context: Optional[ProcessingContext] = None) -> ProcessingResult:
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
            metrics = self._calculate_metrics(counting_summary, context, config)
            predictions = self._extract_predictions(processed_data)
            summary = self._generate_summary(counting_summary, alerts)

            tracking_human_text = self._generate_tracking_human_text(counting_summary)
            events_human_text = self._generate_events_human_text(alerts)

            context.mark_completed()

            result = self.create_result(
                data={
                    "ppe_violation_summary": counting_summary,
                    "general_counting_summary": general_counting_summary,
                    "events": alerts,
                    "total_violations": counting_summary.get("total_count", 0),
                    "tracking_human_text": tracking_human_text,
                    "events_human_text": events_human_text
                },
                usecase=self.name,
                category=self.category,
                context=context
            )
            result.summary = summary
            result.insights = insights
            result.predictions = predictions
            result.metrics = metrics
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
        For the 3 violation categories, if not detected in this frame but detected in last N frames,
        persist the last seen detection for up to N frames. Do NOT use dummy bboxes, use the last valid bbox/confidence.
        """
        output = []
        fresh = {cat: False for cat in config.violation_categories}

        # First, process incoming detections and update persistence
        for det in detections:
            cat = det.get('category')
            conf = det.get('confidence', 1.0)
            if cat == 'NO-Hardhat' and conf >= config.no_hardhat_threshold:
                self.violation_persistence[cat]['count'] = self.persistence_window
                self.violation_persistence[cat]['detection'] = det
                fresh[cat] = True
            elif cat == 'NO-Mask' and conf >= config.no_mask_threshold:
                self.violation_persistence[cat]['count'] = self.persistence_window
                self.violation_persistence[cat]['detection'] = det
                fresh[cat] = True
            elif cat == 'NO-Safety Vest' and conf >= config.no_safety_vest_threshold:
                self.violation_persistence[cat]['count'] = self.persistence_window
                self.violation_persistence[cat]['detection'] = det
                fresh[cat] = True
            else:
                # For other categories (not 3 violations), just keep them as is
                output.append(det)

        # Now, for each violation category, output if it is freshly detected or within window
        for cat in config.violation_categories:
            # If freshly detected, already added above
            if fresh[cat]:
                output.append(self.violation_persistence[cat]['detection'])
            elif self.violation_persistence[cat]['count'] > 0 and self.violation_persistence[cat]['detection']:
                # Persisted violation - use last seen detection info
                output.append(self.violation_persistence[cat]['detection'])
                self.violation_persistence[cat]['count'] -= 1
            else:
                # Not present and not in window - do not output
                pass

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

    def _calculate_metrics(self, summary: dict, context: ProcessingContext, config: PPEComplianceConfig) -> Dict[str, Any]:
        return {
            "total_violations": summary.get("total_count", 0),
            "processing_time": context.processing_time or 0.0,
            "input_format": getattr(context.input_format, 'value', None),
            "no_hardhat_threshold": config.no_hardhat_threshold
        }

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

    def _generate_tracking_human_text(self, summary: dict) -> str:
        total = summary.get("total_count", 0)
        if total > 0:
            timestamp = datetime.now(timezone.utc).strftime('%Y-%m-%d-%H:%M:%S UTC')
            return f"Time: {timestamp}\nPPE Violations Detected: {total}"
        return ""

    def _generate_events_human_text(self, alerts: List) -> str:
        return "" if not alerts else ""
