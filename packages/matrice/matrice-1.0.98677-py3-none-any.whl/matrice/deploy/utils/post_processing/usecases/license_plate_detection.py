"""
License plate detection use case implementation.

This module provides a clean implementation of license plate detection functionality
with counting, insights generation, and alerting capabilities.
"""

from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field
import time

from ..core.base import (
    BaseProcessor,
    ProcessingContext,
    ProcessingResult,
    ConfigProtocol,
)
from ..core.config import BaseConfig, AlertConfig
from ..utils import (
    filter_by_confidence,
    apply_category_mapping,
    calculate_counting_summary,
    match_results_structure,
)


@dataclass
class LicensePlateConfig(BaseConfig):
    """Configuration for license plate detection use case."""

    # Detection settings
    confidence_threshold: float = 0.5

    # Category settings
    license_plate_categories: List[str] = field(
        default_factory=lambda: ["License_Plate", "license_plate"]
    )
    target_vehicle_categories: List[str] = field(
        default_factory=lambda: ["cars", "car", "vehicle", "motorcycle", "truck"]
    )

    # Alert configuration
    alert_config: Optional[AlertConfig] = None

    # Time window configuration
    time_window_minutes: int = 60
    enable_unique_counting: bool = True

    # Category mapping
    index_to_category: Optional[Dict[int, str]] = field(
        default_factory=lambda: {
            0: "License_Plate",
            1: "cars",
            2: "motorcycle",
            3: "truck",
        }
    )

    def __post_init__(self):
        """Post-initialization validation."""
        if self.confidence_threshold < 0.0 or self.confidence_threshold > 1.0:
            raise ValueError("confidence_threshold must be between 0.0 and 1.0")


class LicensePlateUseCase(BaseProcessor):
    """License plate detection use case with counting and analytics."""

    def __init__(self):
        """Initialize license plate detection use case."""
        super().__init__("license_plate_detection")
        self.category = "vehicle"

    def get_config_schema(self) -> Dict[str, Any]:
        """Get configuration schema for license plate detection."""
        return {
            "type": "object",
            "properties": {
                "confidence_threshold": {
                    "type": "number",
                    "minimum": 0.0,
                    "maximum": 1.0,
                    "default": 0.5,
                    "description": "Minimum confidence threshold for detections",
                },
                "license_plate_categories": {
                    "type": "array",
                    "items": {"type": "string"},
                    "default": ["License_Plate", "license_plate"],
                    "description": "Category names that represent license plates",
                },
                "target_vehicle_categories": {
                    "type": "array",
                    "items": {"type": "string"},
                    "default": ["cars", "car", "vehicle", "motorcycle", "truck"],
                    "description": "Category names for vehicles of interest",
                },
                "index_to_category": {
                    "type": "object",
                    "additionalProperties": {"type": "string"},
                    "description": "Mapping from category indices to names",
                },
                "alert_config": {
                    "type": "object",
                    "properties": {
                        "count_thresholds": {
                            "type": "object",
                            "additionalProperties": {"type": "integer", "minimum": 1},
                            "description": "Count thresholds for alerts",
                        }
                    },
                },
            },
            "required": ["confidence_threshold"],
            "additionalProperties": False,
        }

    def create_default_config(self, **overrides) -> LicensePlateConfig:
        """Create default configuration with optional overrides."""
        defaults = {
            "category": self.category,
            "usecase": self.name,
            "confidence_threshold": 0.5,
            "license_plate_categories": ["License_Plate", "license_plate"],
            "target_vehicle_categories": [
                "cars",
                "car",
                "vehicle",
                "motorcycle",
                "truck",
            ],
        }
        defaults.update(overrides)
        return LicensePlateConfig(**defaults)

    def process(
        self,
        data: Any,
        config: ConfigProtocol,
        context: Optional[ProcessingContext] = None,
    ) -> ProcessingResult:
        """
        Process license plate detection use case.
        """
        start_time = time.time()

        try:
            if not isinstance(config, LicensePlateConfig):
                return self.create_error_result(
                    "Invalid configuration type for license plate detection",
                    usecase=self.name,
                    category=self.category,
                    context=context,
                )

            if context is None:
                context = ProcessingContext()

            input_format = match_results_structure(data)
            context.input_format = input_format
            context.confidence_threshold = config.confidence_threshold

            self.logger.info(
                f"Processing license plate detection with format: {input_format.value}"
            )

            processed_data = data
            if config.confidence_threshold is not None:
                processed_data = filter_by_confidence(
                    processed_data, config.confidence_threshold
                )
                self.logger.debug(
                    f"Applied confidence filtering with threshold {config.confidence_threshold}"
                )

            if config.index_to_category:
                processed_data = apply_category_mapping(
                    processed_data, config.index_to_category
                )
                self.logger.debug("Applied category mapping")

            license_counting_summary = self._calculate_license_plate_summary(
                processed_data, config
            )
            vehicle_counting_summary = self._calculate_vehicle_summary(processed_data, config)
            general_counting_summary = calculate_counting_summary(processed_data)

            insights = self._generate_insights(
                license_counting_summary, vehicle_counting_summary, config
            )
            alerts = self._check_alerts(license_counting_summary, config)
            metrics = self._calculate_metrics(
                license_counting_summary, vehicle_counting_summary, config, context
            )
            predictions = self._extract_predictions(processed_data, config)
            summary = self._generate_summary(
                license_counting_summary, general_counting_summary, alerts
            )

            # Step 9: Generate structured events and tracking stats
            events = self._generate_events(license_counting_summary, vehicle_counting_summary, alerts, config)
            tracking_stats = self._generate_tracking_stats(license_counting_summary, vehicle_counting_summary, insights, summary, config)

            context.mark_completed()

            result = self.create_result(
                data={
                    "license_plate_summary": license_counting_summary,
                    "vehicle_summary": vehicle_counting_summary,
                    "general_counting_summary": general_counting_summary,
                    "alerts": alerts,
                    "total_license_plates": license_counting_summary.get(
                        "total_objects", 0
                    ),
                    "total_vehicles": vehicle_counting_summary.get("total_objects", 0),
                    "events": events,
                    "tracking_stats": tracking_stats
                },
                usecase=self.name,
                category=self.category,
                context=context,
            )

            result.summary = summary
            result.insights = insights
            result.predictions = predictions
            result.metrics = metrics

            return result

        except Exception as e:
            self.logger.error(f"Error in license plate processing: {str(e)}")
            return self.create_error_result(
                f"License plate processing failed: {str(e)}",
                error_type="LicensePlateProcessingError",
                usecase=self.name,
                category=self.category,
                context=context,
            )

    def _calculate_license_plate_summary(
        self, data: Any, config: LicensePlateConfig
    ) -> Dict[str, Any]:
        """Calculate summary for license plates only."""
        if isinstance(data, list):
            license_detections = [
                det
                for det in data
                if det.get("category", "").lower()
                in [cat.lower() for cat in config.license_plate_categories]
            ]

            return {
                "total_objects": len(license_detections),
                "by_category": {"License_Plate": len(license_detections)},
                "detections": license_detections,
            }
        return {"total_objects": 0, "by_category": {}, "detections": []}

    def _calculate_vehicle_summary(
        self, data: Any, config: LicensePlateConfig
    ) -> Dict[str, Any]:
        """Calculate summary for vehicles only."""
        if isinstance(data, list):
            vehicle_detections = [
                det
                for det in data
                if det.get("category", "").lower()
                in [cat.lower() for cat in config.target_vehicle_categories]
            ]

            summary = {
                "total_objects": len(vehicle_detections),
                "by_category": {},
                "detections": vehicle_detections,
            }
            for category in config.target_vehicle_categories:
                summary["by_category"][category] = len(
                    [
                        det
                        for det in vehicle_detections
                        if det.get("category", "").lower() == category.lower()
                    ]
                )
            return summary
        return {"total_objects": 0, "by_category": {}, "detections": []}

    def _generate_insights(
        self, license_summary: Dict, vehicle_summary: Dict, config: LicensePlateConfig
    ) -> List[str]:
        """Generate human-readable insights from detection results."""
        insights = []

        total_plates = license_summary.get("total_objects", 0)
        total_vehicles = vehicle_summary.get("total_objects", 0)

        if total_plates == 0:
            insights.append("EVENT: No license plates detected in the scene")
            if total_vehicles > 0:
                insights.append(
                    f"ANALYSIS: {total_vehicles} vehicles detected but no readable license plates"
                )
        else:
            insights.append(
                f"EVENT: Detected {total_plates} license plate{'s' if total_plates != 1 else ''}"
            )

            if total_vehicles > 0:
                detection_rate = (total_plates / total_vehicles) * 100
                insights.append(
                    f"DETECTION_RATE: {detection_rate:.1f}% license plate visibility ({total_plates}/{total_vehicles} vehicles)"
                )

                if detection_rate < 50:
                    insights.append(
                        "QUALITY: Low license plate visibility - consider improving camera angle or resolution"
                    )
                elif detection_rate > 80:
                    insights.append("QUALITY: Excellent license plate visibility")

        intensity_threshold = None
        if (
            config.alert_config
            and config.alert_config.count_thresholds
            and "license_plate" in config.alert_config.count_thresholds
        ):
            intensity_threshold = config.alert_config.count_thresholds["license_plate"]
        elif (
            config.alert_config
            and config.alert_config.count_thresholds
            and "all" in config.alert_config.count_thresholds
        ):
            intensity_threshold = config.alert_config.count_thresholds["all"]

        if intensity_threshold is not None:
            percentage = (total_plates / intensity_threshold) * 100

            if percentage < 20:
                insights.append(
                    f"INTENSITY: Low traffic volume ({percentage:.1f}% of expected capacity)"
                )
            elif percentage <= 50:
                insights.append(
                    f"INTENSITY: Moderate traffic volume ({percentage:.1f}% of expected capacity)"
                )
            elif percentage <= 70:
                insights.append(
                    f"INTENSITY:  High traffic volume ({percentage:.1f}% of expected capacity)"
                )
            else:
                insights.append(
                    f"INTENSITY:  Very high traffic density ({percentage:.1f}% of expected capacity)"
                )
        else:
            if total_plates > 10:
                insights.append(
                    f"INTENSITY:  High traffic density with {total_plates} license plates detected"
                )
            elif total_plates == 1:
                insights.append("INTENSITY: Light traffic conditions")

        if "by_category" in vehicle_summary:
            category_counts = vehicle_summary["by_category"]
            for category, count in category_counts.items():
                if count > 0 and category.lower() in [
                    cat.lower() for cat in config.target_vehicle_categories
                ]:
                    percentage = (
                        (count / total_vehicles) * 100 if total_vehicles > 0 else 0
                    )
                    insights.append(
                        f"VEHICLES: {category}: {count} detected ({percentage:.1f}% of total vehicles)"
                    )

        return insights

    def _check_alerts(
            self, license_summary: Dict, config: LicensePlateConfig
    ) -> List[Dict]:
        """Alerts are disabled in this use case."""
        return []

    def _calculate_metrics(
        self,
        license_summary: Dict,
        vehicle_summary: Dict,
        config: LicensePlateConfig,
        context: ProcessingContext,
    ) -> Dict[str, Any]:
        """Calculate detailed metrics for analytics."""
        total_plates = license_summary.get("total_objects", 0)
        total_vehicles = vehicle_summary.get("total_objects", 0)

        metrics = {
            "total_license_plates": total_plates,
            "total_vehicles": total_vehicles,
            "processing_time": context.processing_time or 0.0,
            "input_format": context.input_format.value,
            "confidence_threshold": config.confidence_threshold,
            "detection_rate_percentage": 0.0,
            "license_plate_visibility": "unknown",
        }

        if total_vehicles > 0:
            detection_rate = (total_plates / total_vehicles) * 100
            metrics["detection_rate_percentage"] = detection_rate

            if detection_rate < 30:
                metrics["license_plate_visibility"] = "poor"
            elif detection_rate < 60:
                metrics["license_plate_visibility"] = "fair"
            elif detection_rate < 85:
                metrics["license_plate_visibility"] = "good"
            else:
                metrics["license_plate_visibility"] = "excellent"

        return metrics

    def _extract_predictions(
        self, data: Any, config: LicensePlateConfig
    ) -> List[Dict[str, Any]]:
        """Extract predictions from processed data for API compatibility."""
        predictions = []

        try:
            if isinstance(data, list):
                for item in data:
                    if isinstance(item, dict):
                        prediction = {
                            "category": item.get(
                                "category", item.get("class", "unknown")
                            ),
                            "confidence": item.get(
                                "confidence", item.get("score", 0.0)
                            ),
                            "bounding_box": item.get(
                                "bounding_box", item.get("bbox", {})
                            ),
                        }
                        predictions.append(prediction)

        except Exception as e:
            self.logger.warning(f"Failed to extract predictions: {str(e)}")

        return predictions

    def _generate_summary(
        self, license_summary: Dict, general_summary: Dict, alerts: List
    ) -> str:
        """Generate human-readable summary."""
        total_plates = license_summary.get("total_objects", 0)
        total_vehicles = general_summary.get("total_objects", 0)

        if total_plates == 0 and total_vehicles == 0:
            return "No vehicles or license plates detected"

        summary_parts = []

        if total_plates > 0:
            summary_parts.append(
                f"{total_plates} license plate{'s' if total_plates != 1 else ''} detected"
            )

        if total_vehicles > 0:
            summary_parts.append(
                f"{total_vehicles} vehicle{'s' if total_vehicles != 1 else ''} detected"
            )

        if alerts:
            alert_count = len(alerts)
            summary_parts.append(
                f"{alert_count} alert{'s' if alert_count != 1 else ''}"
            )

        return ", ".join(summary_parts)

    def _generate_events(self, license_summary: Dict, vehicle_summary: Dict, alerts: List,
                         config: LicensePlateConfig) -> List[Dict]:
        """Generate structured events for the output format."""
        from datetime import datetime, timezone

        events = []
        total_plates = license_summary.get("total_objects", 0)
        total_vehicles = vehicle_summary.get("total_objects", 0)

        if total_plates > 0 or total_vehicles > 0:
            # Determine event level based on thresholds
            level = "info"
            intensity = 5.0

            if config.alert_config and config.alert_config.count_thresholds:
                threshold = config.alert_config.count_thresholds.get("license_plate",
                                                                     config.alert_config.count_thresholds.get("all",
                                                                                                              10))
                intensity = min(10.0, (total_plates / threshold) * 10) if total_plates > 0 else 3.0

                if intensity >= 7:
                    level = "critical"
                elif intensity >= 5:
                    level = "warning"
                else:
                    level = "info"
            else:
                if total_plates > 15:
                    level = "critical"
                    intensity = 9.0
                elif total_plates > 8:
                    level = "warning"
                    intensity = 7.0
                else:
                    level = "info"
                    intensity = min(10.0, total_plates / 2.0) if total_plates > 0 else 3.0

            # Main license plate detection event
            event = {
                "type": "license_plate_detection",
                "stream_time": datetime.now(timezone.utc).strftime("%Y-%m-%d-%H:%M:%S UTC"),
                "level": level,
                "intensity": round(intensity, 1),
                "config": {
                    "min_value": 0,
                    "max_value": 10,
                    "level_settings": {"info": 2, "warning": 5, "critical": 7}
                },
                "application_name": "License Plate Detection System",
                "application_version": "1.2",
                "location_info": None,
                "human_text": f"Event: License Plate Detection\nLicense Plates: {total_plates} detected."
            }
            events.append(event)

        # Add vehicle monitoring event if vehicles detected
        if total_vehicles > 0:
            vehicle_intensity = min(10.0, total_vehicles / 5.0)
            vehicle_level = "info"
            if vehicle_intensity >= 7:
                vehicle_level = "warning"
            elif vehicle_intensity >= 5:
                vehicle_level = "info"

            vehicle_event = {
                "type": "vehicle_detection",
                "stream_time": datetime.now(timezone.utc).strftime("%Y-%m-%d-%H:%M:%S UTC"),
                "level": vehicle_level,
                "intensity": round(vehicle_intensity, 1),
                "config": {
                    "min_value": 0,
                    "max_value": 10,
                    "level_settings": {"info": 2, "warning": 5, "critical": 7}
                },
                "application_name": "Vehicle Detection System",
                "application_version": "1.2",
                "location_info": None,
                "human_text": f"Event: Vehicle Detection\nCount: {total_vehicles} vehicles detected"
            }
            events.append(vehicle_event)

        # Add alert events
        for alert in alerts:
            alert_event = {
                "type": alert.get("type", "license_plate_alert"),
                "stream_time": datetime.now(timezone.utc).strftime("%Y-%m-%d-%H:%M:%S UTC"),
                "level": alert.get("severity", "warning"),
                "intensity": 8.0,
                "config": {
                    "min_value": 0,
                    "max_value": 10,
                    "level_settings": {"info": 2, "warning": 5, "critical": 7}
                },
                "application_name": "License Plate Alert System",
                "application_version": "1.2",
                "location_info": None,
                "human_text": "License plate alert triggered"
            }
            events.append(alert_event)

        return events

    def _generate_tracking_stats(self, license_summary: Dict, vehicle_summary: Dict, insights: List[str], summary: str, config: LicensePlateConfig) -> List[Dict]:
        """Generate structured tracking stats for the output format."""
        from datetime import datetime, timezone
        
        tracking_stats = []
        total_plates = license_summary.get("total_objects", 0)
        total_vehicles = vehicle_summary.get("total_objects", 0)
        
        if total_plates > 0 or total_vehicles > 0:
            # Create main tracking stats entry
            tracking_stat = {
                "all_results_for_tracking": {
                    "total_license_plates": total_plates,
                    "total_vehicles": total_vehicles,
                    "license_plate_summary": license_summary,
                    "vehicle_summary": vehicle_summary,
                    "detection_rate": (total_plates / config.time_window_minutes * 60) if config.time_window_minutes else 0,
                    "plate_visibility_rate": (total_plates / total_vehicles * 100) if total_vehicles > 0 else 0,
                    "unique_count": self._count_unique_tracks(license_summary)
                },
                "human_text": self._generate_human_text_for_tracking(total_plates, total_vehicles, insights, summary, config)
            }
            tracking_stats.append(tracking_stat)
        
        return tracking_stats
    
    def _generate_human_text_for_tracking(self, total_plates: int, total_vehicles: int, insights: List[str], summary: str, config: LicensePlateConfig) -> str:
        """Generate human-readable text for tracking stats."""
        from datetime import datetime, timezone
        
        text_parts = [
            f"License Plates Detected: {total_plates}"]

        # Add key insights
        # if insights:
        #     text_parts.append("Key Detection Insights:")
        #     for insight in insights[:3]:  # Limit to first 3 insights
        #         text_parts.append(f"  - {insight}")
        
        return "\n".join(text_parts)
    
    def _count_unique_tracks(self, license_summary: Dict) -> Optional[int]:
        """Count unique tracks if tracking is enabled."""
        detections = license_summary.get("detections", [])
        
        if not detections:
            return None
        
        # Count unique track IDs
        unique_tracks = set()
        for detection in detections:
            track_id = detection.get("track_id")
            if track_id is not None:
                unique_tracks.add(track_id)
        
        return len(unique_tracks) if unique_tracks else None
