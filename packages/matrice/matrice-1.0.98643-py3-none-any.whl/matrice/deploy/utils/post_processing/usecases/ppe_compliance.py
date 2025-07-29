"""
PPE compliance detection use case implementation.

This module provides a clean implementation of PPE compliance detection functionality
with counting, insights generation, and alerting capabilities.
"""

from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field
import time

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


class PPEComplianceUseCase(BaseProcessor):
    """PPE compliance detection use case with counting and analytics."""
    def __init__(self):
        super().__init__("ppe_compliance_detection")
        self.category = "ppe"

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
            # Always apply full category mapping first
            if config.index_to_category:
                processed_data = apply_category_mapping(processed_data, config.index_to_category)
                self.logger.debug("Applied full category mapping")
            # Now filter for PPE violations with correct thresholding
            processed_data = self._filter_ppe_violations(processed_data, config)
            # General counting summary (all detections, not just violations)
            general_counting_summary = calculate_counting_summary(data)
            # PPE violation summary (custom)
            counting_summary = self._count_categories(processed_data, config)
            insights = self._generate_insights(counting_summary, config)
            alerts = self._check_alerts(counting_summary, config)
            metrics = self._calculate_metrics(counting_summary, context, config)
            predictions = self._extract_predictions(processed_data)
            summary = self._generate_summary(counting_summary, alerts)
            context.mark_completed()
            result = self.create_result(
                data={
                    "ppe_violation_summary": counting_summary,
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
            result.metrics = metrics
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

    def _generate_insights(self, summary: dict, config: PPEComplianceConfig) -> List[str]:
        insights = []
        total = summary.get("total_count", 0)
        per_cat = summary.get("per_category_count", {})
        if total == 0:
            insights.append("EVENT: No PPE violations detected.")
        else:
            insights.append(f"EVENT: {total} PPE violation(s) detected.")
            for cat, count in per_cat.items():
                insights.append(f"CATEGORY: {cat}: {count} violation(s)")
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

    def _calculate_metrics(self, summary: dict, context: ProcessingContext, config: PPEComplianceConfig) -> Dict[str, Any]:
        metrics = {
            "total_violations": summary.get("total_count", 0),
            "processing_time": context.processing_time or 0.0,
            "input_format": getattr(context.input_format, 'value', None),
            "no_hardhat_threshold": config.no_hardhat_threshold
        }
        return metrics

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
            return "No PPE violations detected."
        parts = [f"{total} PPE violation(s) detected"]
        if alerts:
            parts.append(f"{len(alerts)} alert(s)")
        return ", ".join(parts)
