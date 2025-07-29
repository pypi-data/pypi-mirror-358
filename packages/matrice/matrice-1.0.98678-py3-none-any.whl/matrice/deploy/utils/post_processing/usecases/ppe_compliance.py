from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field
import time
from collections import defaultdict

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
        self.violation_persistence = defaultdict(int)  # Tracks remaining persistence per category

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

            context.mark_completed()

            result = self.create_result(
                data={
                    "ppe_violation_summary": counting_summary,
                    "general_counting_summary": general_counting_summary,
                    "events": alerts,  # Moved alerts under events
                    "total_violations": counting_summary.get("total_count", 0)
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
        filtered = []
        current_frame_violations = set()

        for det in detections:
            cat = det.get('category')
            conf = det.get('confidence', 1.0)
            if cat == 'NO-Hardhat' and conf >= config.no_hardhat_threshold:
                filtered.append(det)
                current_frame_violations.add(cat)
            elif cat == 'NO-Mask' and conf >= config.no_mask_threshold:
                filtered.append(det)
                current_frame_violations.add(cat)
            elif cat == 'NO-Safety Vest' and conf >= config.no_safety_vest_threshold:
                filtered.append(det)
                current_frame_violations.add(cat)

        for cat in config.violation_categories:
            if cat in current_frame_violations:
                self.violation_persistence[cat] = 20
            elif self.violation_persistence[cat] > 0:
                self.violation_persistence[cat] -= 1
                filtered.append({
                    "category": cat,
                    "confidence": 1.0,
                    "bounding_box": {"xmin": 0, "ymin": 0, "xmax": 1, "ymax": 1}  # dummy
                })

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
            insights.append(f"{count} people without {display.lower()} detected")
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
