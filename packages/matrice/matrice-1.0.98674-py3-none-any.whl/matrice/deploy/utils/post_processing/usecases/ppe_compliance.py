"""
PPE compliance detection use case implementation.

This module provides a clean implementation of PPE compliance detection functionality
with counting, insights generation, and alerting capabilities.
"""

from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field
import time
from collections import deque

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
    """Configuration for PPE compliance detection use case."""
    # Detection settings
    no_hardhat_threshold: float = 0.91
    no_mask_threshold: float = 0.2
    no_safety_vest_threshold: float = 0.2
    violation_categories: List[str] = field(default_factory=lambda: [
        "NO-Hardhat", "NO-Mask", "NO-Safety Vest"
    ])
    alert_config: Optional[AlertConfig] = None
    # Full category mapping for all model classes
    index_to_category: Optional[Dict[int, str]] = field(default_factory=lambda: {
        -1: 'Hardhat',
        0: 'Mask',
        1: 'NO-Hardhat',
        2: 'NO-Mask',
        3: 'NO-Safety Vest',
        4: 'Person',
        5: 'Safety Cone',
        6: 'Safety Vest',
        7: 'machinery',
        8: 'vehicle'
    })

    def __post_init__(self):
        if not (0.0 <= self.no_hardhat_threshold <= 1.0):
            raise ValueError("no_hardhat_threshold must be between 0.0 and 1.0")
        if not (0.0 <= self.no_mask_threshold <= 1.0):
            raise ValueError("no_mask_threshold must be between 0.0 and 1.0")
        if not (0.0 <= self.no_safety_vest_threshold <= 1.0):
            raise ValueError("no_safety_vest_threshold must be between 0.0 and 1.0")


class TemporalViolationBuffer:
    """Buffer to maintain last N frames' PPE violations for temporal smoothing with robust matching."""
    def __init__(self, buffer_size=10, iou_threshold=0.5):
        self.buffer_size = buffer_size
        self.iou_threshold = iou_threshold
        self.buffer = []  # List of lists, each sublist is a frame's detections

    def update(self, current_detections):
        # Add current detections to buffer
        self.buffer.append(current_detections)
        if len(self.buffer) > self.buffer_size:
            self.buffer.pop(0)
        # Merge violations using IoU or center distance for persistence
        return self._get_persistent_violations()

    def _get_persistent_violations(self):
        # Flatten all detections in buffer
        all_detections = [det for frame in self.buffer for det in frame]
        persistent = []
        for det in all_detections:
            if not self._is_duplicate(det, persistent):
                persistent.append(det)
        return persistent

    def _is_duplicate(self, det, persistent):
        for p in persistent:
            if det['category'] == p['category'] and self._bbox_similar(det['bounding_box'], p['bounding_box']):
                return True
        return False

    def _bbox_similar(self, box1, box2):
        # Use IoU or center distance for similarity
        if self._iou(box1, box2) > self.iou_threshold:
            return True
        return False

    def _iou(self, boxA, boxB):
        # box: [x1, y1, x2, y2]
        xA = max(boxA[0], boxB[0])
        yA = max(boxA[1], boxB[1])
        xB = min(boxA[2], boxB[2])
        yB = min(boxA[3], boxB[3])
        interArea = max(0, xB - xA) * max(0, yB - yA)
        boxAArea = (boxA[2] - boxA[0]) * (boxA[3] - boxA[1])
        boxBArea = (boxB[2] - boxB[0]) * (boxB[3] - boxB[1])
        iou = interArea / float(boxAArea + boxBArea - interArea + 1e-6)
        return iou


class PPEComplianceUseCase(BaseProcessor):
    """PPE compliance detection use case with counting and analytics."""
    def __init__(self):
        super().__init__("ppe_compliance_detection")
        self.category = "ppe"
        self.temporal_buffer = TemporalViolationBuffer(buffer_size=10)  # Add buffer for smoothing

    def get_config_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "no_hardhat_threshold": {
                    "type": "number",
                    "minimum": 0.0,
                    "maximum": 1.0,
                    "default": 0.8,
                    "description": "Confidence threshold for NO-Hardhat violations"
                },
                "violation_categories": {
                    "type": "array",
                    "items": {"type": "string"},
                    "default": ["NO-Hardhat", "NO-Mask", "NO-Safety Vest"],
                    "description": "Category names for PPE violations"
                },
                "index_to_category": {
                    "type": "object",
                    "additionalProperties": {"type": "string"},
                    "description": "Mapping from category indices to names"
                },
                "alert_config": {
                    "type": "object",
                    "properties": {
                        "count_thresholds": {
                            "type": "object",
                            "additionalProperties": {"type": "integer", "minimum": 1},
                            "description": "Count thresholds for alerts"
                        }
                    }
                }
            },
            "required": ["no_hardhat_threshold"],
            "additionalProperties": False
        }

    def create_default_config(self, **overrides) -> PPEComplianceConfig:
        defaults = {
            "category": self.category,
            "usecase": self.name,
            "no_hardhat_threshold": 0.91,
            "no_mask_threshold": 0.2,
            "no_safety_vest_threshold": 0.2,
            "violation_categories": ["NO-Hardhat", "NO-Mask", "NO-Safety Vest"],
            "index_to_category": {
                -1: 'Hardhat',
                0: 'Mask',
                1: 'NO-Hardhat',
                2: 'NO-Mask',
                3: 'NO-Safety Vest',
                4: 'Person',
                5: 'Safety Cone',
                6: 'Safety Vest',
                7: 'machinery',
                8: 'vehicle'
            },
        }
        defaults.update(overrides)
        return PPEComplianceConfig(**defaults)

    def process(self, data: Any, config: ConfigProtocol,
                context: Optional[ProcessingContext] = None) -> ProcessingResult:
        start_time = time.time()
        try:
            if not isinstance(config, PPEComplianceConfig):
                return self.create_error_result(
                    "Invalid configuration type for PPE compliance detection",
                    usecase=self.name,
                    category=self.category,
                    context=context
                )
            if context is None:
                context = ProcessingContext()
            input_format = match_results_structure(data)
            context.input_format = input_format
            context.no_hardhat_threshold = config.no_hardhat_threshold
            self.logger.info(f"Processing PPE compliance detection with format: {input_format.value}")
            processed_data = data
            if config.index_to_category:
                processed_data = apply_category_mapping(processed_data, config.index_to_category)
                self.logger.debug("Applied full category mapping")
            filtered_violations = self._filter_ppe_violations(processed_data, config)
            # --- Temporal smoothing: merge with buffer ---
            smoothed_violations = self.temporal_buffer.update(filtered_violations)
            general_counting_summary = calculate_counting_summary(data)
            counting_summary = self._count_categories(smoothed_violations, config)
            alerts = self._check_alerts(counting_summary, config)
            predictions = self._extract_predictions(smoothed_violations)
            summary = self._generate_summary(counting_summary, alerts)
            context.mark_completed()
            human_text = self._build_human_text(counting_summary, alerts)
            events = self._build_events(counting_summary, human_text)
            result_data = self._build_result_data(counting_summary, general_counting_summary)
            agg_summary = self._build_agg_summary(counting_summary, human_text, events)
            result = self.create_result(
                data=result_data,
                usecase=self.name,
                category=self.category,
                context=context
            )
            result.summary = summary
            result.insights = [human_text] if human_text else []
            result.predictions = predictions
            # Ensure metrics is not present at all
            if hasattr(result, 'metrics'):
                delattr(result, 'metrics')
            result.agg_summary = agg_summary
            return result
        except Exception as e:
            self.logger.error(f"Error in PPE compliance processing: {str(e)}")
            return self.create_error_result(
                f"PPE compliance processing failed: {str(e)}",
                error_type="PPEComplianceProcessingError",
                usecase=self.name,
                category=self.category,
                context=context
            )

    def _filter_ppe_violations(self, detections: list, config: PPEComplianceConfig) -> list:
        filtered = []
        for det in detections:
            cat = det.get('category')
            conf = det.get('confidence', 1.0)
            # Only keep the three violation categories with their thresholds
            if cat == 'NO-Hardhat' and conf >= config.no_hardhat_threshold:
                filtered.append(det)
            elif cat == 'NO-Mask' and conf >= config.no_mask_threshold:
                filtered.append(det)
            elif cat == 'NO-Safety Vest' and conf >= config.no_safety_vest_threshold:
                filtered.append(det)
        return filtered

    def _count_categories(self, detections: list, config: PPEComplianceConfig) -> dict:
        counts = {}
        for det in detections:
            cat = det.get('category', 'unknown')
            counts[cat] = counts.get(cat, 0) + 1
        return {
            "total_count": sum(counts.values()),
            "per_category_count": counts,
            "detections": [
                {
                    'bounding_box': det.get('bounding_box'),
                    'category': det.get('category')
                } for det in detections
            ]
        }

    CATEGORY_DISPLAY = {
        "NO-Hardhat": "no hardhat",
        "NO-Mask": "no mask",
        "NO-Safety Vest": "no safety vest"
    }

    def _generate_insights(self, summary: dict, config: PPEComplianceConfig) -> List[str]:
        insights = []
        total = summary.get("total_count", 0)
        per_cat = summary.get("per_category_count", {})
        if total == 0:
            # No violations, return empty list (no human_text will be generated)
            return []
        insights.append(f"EVENT: {total} PPE violations detected")
        for cat, count in per_cat.items():
            display = self.CATEGORY_DISPLAY.get(cat, f"{cat} violations")
            insights.append(f"{display} detected: {count}")
        return insights

    def _check_alerts(self, summary: dict, config: PPEComplianceConfig) -> List[Dict]:
        alerts = []
        if not config.alert_config:
            return alerts
        total = summary.get("total_count", 0)
        if config.alert_config.count_thresholds:
            for category, threshold in config.alert_config.count_thresholds.items():
                if category == "all" and total >= threshold:
                    alerts.append({
                        "type": "count_threshold",
                        "severity": "warning",
                        "message": f"PPE violation count ({total}) exceeds threshold ({threshold})",
                        "category": category,
                        "current_count": total,
                        "threshold": threshold
                    })
        return alerts

    def _extract_predictions(self, detections: list) -> List[Dict[str, Any]]:
        predictions = []
        for det in detections:
            predictions.append({
                "category": det.get("category", "unknown"),
                "confidence": det.get("confidence", 0.0),
                "bounding_box": det.get("bounding_box", {})
            })
        return predictions

    def _generate_summary(self, summary: dict, alerts: List) -> str:
        total = summary.get("total_count", 0)
        if total == 0:
            return ""
        parts = [f"{total} PPE violations detected"]
        if alerts:
            parts.append(f"{len(alerts)} alert(s)")
        return ", ".join(parts)

    def _build_human_text(self, counting_summary, alerts):
        total = counting_summary.get("total_count", 0)
        per_cat = counting_summary.get("per_category_count", {})
        human_text_lines = []
        if total > 0:
            human_text_lines.append(f"{total} PPE violations detected")
            for cat, count in per_cat.items():
                display = self.CATEGORY_DISPLAY.get(cat, f"{cat} violations")
                human_text_lines.append(f"{display} detected: {count}")
            for alert in alerts:
                human_text_lines.append(f"EVENT: {alert.get('message')}")
        seen = set()
        deduped_lines = []
        for line in human_text_lines:
            if line not in seen:
                deduped_lines.append(line)
                seen.add(line)
        return "\n".join(deduped_lines)

    def _build_events(self, counting_summary, human_text):
        total = counting_summary.get("total_count", 0)
        events = []
        if total > 0:
            events.append({
                "type": "ppe_compliance_detection",
                "stream_time": time.strftime("%Y-%m-%d-%H:%M:%S UTC", time.gmtime()),
                "level": "info",
                "intensity": 0.5,
                "config": {
                    "min_value": 0,
                    "max_value": 10,
                    "level_settings": {"info": 2, "warning": 5, "critical": 7}
                },
                "application_name": "PPE Compliance Detection System",
                "application_version": "1.0",
                "location_info": None,
                "human_text": human_text or ""
            })
        return events

    def _build_result_data(self, counting_summary, general_counting_summary):
        total = counting_summary.get("total_count", 0)
        result_data = {
            "ppe_violation_summary": counting_summary,
            "general_counting_summary": general_counting_summary,
            "total_violations": total,
        }
        if total > 0:
            result_data["timestamp"] = time.time()
        return result_data

    def _build_agg_summary(self, counting_summary, human_text, events):
        total = counting_summary.get("total_count", 0)
        return {
            "events": events,
            "tracking_stats": [
                {
                    "all_results_for_tracking": counting_summary,
                    "human_text": human_text
                }
            ] if total > 0 else []
        }
