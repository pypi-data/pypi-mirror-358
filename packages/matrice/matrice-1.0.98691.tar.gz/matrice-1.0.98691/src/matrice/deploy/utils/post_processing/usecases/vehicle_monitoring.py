from typing import Any, Dict, List, Optional
from dataclasses import asdict
import time
from datetime import datetime, timezone

from ..core.base import BaseProcessor, ProcessingContext, ProcessingResult, ConfigProtocol, ResultFormat
from ..utils import (
    filter_by_confidence,
    filter_by_categories,
    apply_category_mapping,
    count_objects_by_category,
    count_objects_in_zones,
    calculate_counting_summary,
    match_results_structure
)
from dataclasses import dataclass, field
from ..core.config import BaseConfig, AlertConfig, ZoneConfig

@dataclass
class VehicleMonitoringConfig(BaseConfig):
    """Configuration for license plate detection use case in vehicle monitoring."""

    # Zone configuration
    zone_config: Optional[ZoneConfig] = None

    # Detection settings
    confidence_threshold: float = 0.6

    vehicle_categories: List[str] = field(
        default_factory=lambda: ['army vehicle', 'car', 'bicycle', 'bus', 'auto rickshaw', 'garbagevan', 'truck', 'minibus', 'motorbike', 'pickup', 'policecar', 'rickshaw', 'scooter', 'suv', 'taxi', 'three wheelers -CNG-', 'human hauler', 'van', 'wheelbarrow']
    )

    target_vehicle_categories: List[str] = field(
        default_factory=lambda: ['car', 'bicycle', 'bus', 'garbagevan', 'truck', 'motorbike', 'van']
    )

    # Alert configuration
    alert_config: Optional[AlertConfig] = None

    # Time window configuration
    time_window_minutes: int = 60
    enable_unique_counting: bool = True

    # Category mapping
    index_to_category: Optional[Dict[int, str]] = field(
        default_factory=lambda: {
            1: "bicycle",
            2: "car",
            3: "motorbike",
            4: "auto rickshaw",
            5: "bus",
            6: "garbagevan",
            7: "truck",
            8: "minibus",
            10: "army vehicle",
            11: "pickup",
            12: "policecar",
            13: "rickshaw",
            14: "scooter",
            15: "suv",
            16: "taxi",
            17: "three wheelers -CNG-",
            18: "human hauler",
            19: "van",
            20: "wheelbarrow",
        }
    )

    def _post_init_(self):
        """Post-initialization validation."""
        if self.confidence_threshold < 0.0 or self.confidence_threshold > 1.0:
            raise ValueError("confidence_threshold must be between 0.0 and 1.0")

class VehicleMonitoringUseCase(BaseProcessor):
    """Vehicle monitoring use case with zone analysis and alerting."""
    
    def __init__(self):
        """Initialize vehicle monitoring use case."""
        super().__init__("vehicle_monitoring")
        self.category = "congestion"
    
    def get_config_schema(self) -> Dict[str, Any]:
        """Get configuration schema for vehicle monitoring."""
        return {
            "type": "object",
            "properties": {
                "confidence_threshold": {
                    "type": "number",
                    "minimum": 0.0,
                    "maximum": 1.0,
                    "default": 0.5,
                    "description": "Minimum confidence threshold for vehicle detections"
                },
                "enable_tracking": {
                    "type": "boolean",
                    "default": False,
                    "description": "Enable tracking for unique vehicle counting"
                },
                "zone_config": {
                    "type": "object",
                    "properties": {
                        "zones": {
                            "type": "object",
                            "additionalProperties": {
                                "type": "array",
                                "items": {
                                    "type": "array",
                                    "items": {"type": "number"},
                                    "minItems": 2,
                                    "maxItems": 2
                                },
                                "minItems": 3
                            },
                            "description": "Zone definitions as polygons for congestion monitoring"
                        },
                        "zone_confidence_thresholds": {
                            "type": "object",
                            "additionalProperties": {"type": "number", "minimum": 0.0, "maximum": 1.0},
                            "description": "Per-zone confidence thresholds"
                        }
                    }
                },
                "vehicle_categories": {
                    "type": "array",
                    "items": {"type": "string"},
                    "default": ['army vehicle', 'car', 'bicycle', 'bus', 'auto rickshaw', 'garbagevan', 'truck', 'minibus', 'motorbike', 'pickup', 'policecar', 'rickshaw', 'scooter', 'suv', 'taxi', 'three wheelers -CNG-', 'human hauler', 'van', 'wheelbarrow'],
                    "description": "Category names that represent vehicles"
                },
                "enable_unique_counting": {
                    "type": "boolean",
                    "default": True,
                    "description": "Enable unique vehicle counting using tracking"
                },
                "time_window_minutes": {
                    "type": "integer",
                    "minimum": 1,
                    "default": 60,
                    "description": "Time window for vehicle counting analysis in minutes"
                },
                "alert_config": {
                    "type": "object",
                    "properties": {
                        "count_thresholds": {
                            "type": "object",
                            "additionalProperties": {"type": "integer", "minimum": 1},
                            "description": "Count thresholds for vehicle alerts"
                        },
                        "occupancy_thresholds": {
                            "type": "object", 
                            "additionalProperties": {"type": "integer", "minimum": 1},
                            "description": "Zone occupancy thresholds for vehicle alerts"
                        }
                    }
                }
            },
            "required": ["confidence_threshold"],
            "additionalProperties": False
        }
    
    def create_default_config(self, **overrides) -> VehicleMonitoringConfig:
        """Create default configuration with optional overrides."""
        defaults = {
            "category": self.category,
            "usecase": self.name,
            "confidence_threshold": 0.5,
            "enable_tracking": False,
            "enable_analytics": True,
            "enable_unique_counting": True,
            "time_window_minutes": 60,
            "vehicle_categories":['army vehicle', 'car', 'bicycle', 'bus', 'auto rickshaw', 'garbagevan', 'truck', 'minibus', 'motorbike', 'pickup', 'policecar', 'rickshaw', 'scooter', 'suv', 'taxi', 'three wheelers -CNG-', 'human hauler', 'van', 'wheelbarrow'],
        }
        defaults.update(overrides)
        return VehicleMonitoringConfig(**defaults)
    
    def process(self, data: Any, config: ConfigProtocol, context: Optional[ProcessingContext] = None) -> ProcessingResult:
        """
        Process vehicle monitoring use case.
        
        Args:
            data: Raw model output (detection or tracking format)
            config: Vehicle monitoring configuration
            context: Processing context
            
        Returns:
            ProcessingResult: Processing result with vehicle monitoring analytics
        """
        start_time = time.time()
        
        try:
            # Ensure we have the right config type
            if not isinstance(config, VehicleMonitoringConfig):
                return self.create_error_result(
                    "Invalid configuration type for vehicle monitoring",
                    usecase=self.name,
                    category=self.category,
                    context=context
                )
            
            # Initialize processing context if not provided
            if context is None:
                context = ProcessingContext()
            
            # Detect input format
            input_format = match_results_structure(data)
            context.input_format = input_format
            context.confidence_threshold = config.confidence_threshold
            
            self.logger.info(f"Processing vehicle monitoring with format: {input_format.value}")
            
            # Step 1: Apply confidence filtering
            processed_data = data
            if config.confidence_threshold is not None:
                processed_data = filter_by_confidence(processed_data, config.confidence_threshold)
                self.logger.debug(f"Applied confidence filtering with threshold {config.confidence_threshold}")
            
            # Step 2: Apply category mapping if provided
            if config.index_to_category:
                processed_data = apply_category_mapping(processed_data, config.index_to_category)
                self.logger.debug("Applied category mapping")
            
            # Step 2.5: Filter to only include vehicle categories
            vehicle_processed_data = processed_data
            if config.target_vehicle_categories:
                vehicle_processed_data = filter_by_categories(processed_data.copy(), config.target_vehicle_categories)
                self.logger.debug(f"Applied vehicle category filtering for: {config.target_vehicle_categories}")
            
            # Step 3: Calculate comprehensive counting summary
            zones = config.zone_config.zones if config.zone_config else None
            vehicle_counting_summary = calculate_counting_summary(
                vehicle_processed_data,
                zones=zones
            )
            general_counting_summary = calculate_counting_summary(
                processed_data,
                zones=zones
            )
            
            # Step 4: Zone-based analysis if zones are configured
            zone_analysis = {}
            if config.zone_config and config.zone_config.zones:
                zone_analysis = count_objects_in_zones(
                    vehicle_processed_data, 
                    config.zone_config.zones
                )
                self.logger.debug(f"Analyzed {len(config.zone_config.zones)} zones")
            
            # Step 5: Generate insights and alerts
            insights = self._generate_insights(vehicle_counting_summary, zone_analysis, config)
            alerts = self._check_alerts(vehicle_counting_summary, zone_analysis, config)
            
            # Step 6: Calculate detailed metrics
            metrics = self._calculate_metrics(vehicle_counting_summary, zone_analysis, config, context)
            
            # Step 7: Extract predictions for API compatibility
            predictions = self._extract_predictions(processed_data)
            
            # Step 8: Generate human-readable summary
            summary = self._generate_summary(vehicle_counting_summary, zone_analysis, alerts)
            
            # Step 9: Generate structured events and tracking stats
            events = self._generate_events(vehicle_counting_summary, zone_analysis, alerts, config)
            tracking_stats = self._generate_tracking_stats(vehicle_counting_summary, zone_analysis, insights, summary, config)
            
            # Mark processing as completed
            context.mark_completed()
            
            # Create successful result
            result = self.create_result(
                data={
                    "general_counting_summary": general_counting_summary,
                    "counting_summary": vehicle_counting_summary,
                    "zone_analysis": zone_analysis,
                    "alerts": alerts,
                    "total_vehicles": vehicle_counting_summary.get("total_objects", 0),
                    "zones_count": len(config.zone_config.zones) if config.zone_config else 0,
                    "events": events,
                    "tracking_stats": tracking_stats
                },
                usecase=self.name,
                category=self.category,
                context=context
            )
            
            # Add human-readable information
            result.summary = summary
            result.insights = insights
            result.predictions = predictions
            result.metrics = metrics
            
            # Add warnings for low confidence detections
            if config.confidence_threshold and config.confidence_threshold < 0.3:
                result.add_warning(f"Low confidence threshold ({config.confidence_threshold}) may result in false positives")
            
            processing_time = context.processing_time or time.time() - start_time
            self.logger.info(f"Vehicle monitoring completed successfully in {processing_time:.2f}s")
            return result
            
        except Exception as e:
            self.logger.error(f"Vehicle monitoring failed: {str(e)}", exc_info=True)
            
            if context:
                context.mark_completed()
            
            return self.create_error_result(
                str(e), 
                type(e).__name__,
                usecase=self.name,
                category=self.category,
                context=context
            )
    
    def _generate_insights(self, counting_summary: Dict, zone_analysis: Dict, config: VehicleMonitoringConfig) -> List[str]:
        """Generate human-readable insights from vehicle counting results."""
        insights = []
        
        total_vehicles = counting_summary.get("total_objects", 0)
        
        if total_vehicles == 0:
            insights.append("No vehicles detected in the scene")
            return insights
        
        # Basic count insight
        insights.append(f"EVENT: Detected {total_vehicles} vehicles in the scene")
        
        # Intensity calculation based on threshold percentage
        intensity_threshold = None
        if (config.alert_config and 
            config.alert_config.count_thresholds and 
            "all" in config.alert_config.count_thresholds):
            intensity_threshold = config.alert_config.count_thresholds["all"]
        
        if intensity_threshold is not None:
            # Calculate percentage relative to threshold
            percentage = (total_vehicles / intensity_threshold) * 100
            
            if percentage < 20:
                insights.append(f"INTENSITY: Low congestion in the scene ({percentage:.1f}% of capacity)")
            elif percentage <= 50:
                insights.append(f"INTENSITY: Moderate congestion in the scene ({percentage:.1f}% of capacity)")
            elif percentage <= 70:
                insights.append(f"INTENSITY:  Heavy congestion in the scene ({percentage:.1f}% of capacity)")
            else:
                insights.append(f"INTENSITY: Severe congestion in the scene ({percentage:.1f}% of capacity)")
        else:
            # Fallback to hardcoded thresholds if no alert config is set
            if total_vehicles > 15:
                insights.append(f"INTENSITY: Heavy congestion in the scene with {total_vehicles} vehicles")
            elif total_vehicles == 1:
                insights.append(f"INTENSITY: Low congestion in the scene")
        
        # Zone-specific insights
        if zone_analysis:
            for zone_name, zone_counts in zone_analysis.items():
                zone_total = sum(zone_counts.values()) if isinstance(zone_counts, dict) else zone_counts
                if zone_total > 0:
                    percentage = (zone_total / total_vehicles) * 100
                    insights.append(f"Zone '{zone_name}': {zone_total} vehicles ({percentage:.1f}% of total)")
                    
                    # Density insights
                    if zone_total > 10:
                        insights.append(f" High congestion density in zone '{zone_name}' with {zone_total} vehicles")
                    elif zone_total == 1:
                        insights.append(f"Low congestion in zone '{zone_name}'")
        
        # Category breakdown insights
        if "by_category" in counting_summary:
            category_counts = counting_summary["by_category"]
            for category, count in category_counts.items():
                if count > 0 and category in config.target_vehicle_categories:
                    percentage = (count / total_vehicles) * 100
                    insights.append(f"Category '{category}': {count} detections ({percentage:.1f}% of total)")
        
        # Unique counting insights
        if config.enable_unique_counting:
            unique_count = self._count_unique_tracks(counting_summary)
            if unique_count is not None:
                insights.append(f"Unique vehicle count: {unique_count}")
                if unique_count != total_vehicles:
                    insights.append(f"Detection efficiency: {unique_count}/{total_vehicles} unique tracks")
        
        return insights
    
    def _check_alerts(self, counting_summary: Dict, zone_analysis: Dict, config: VehicleMonitoringConfig) -> List[Dict]:
        """Check for alert conditions and generate vehicle alerts."""
        alerts = []
        
        if not config.alert_config:
            return alerts
        
        total_vehicles = counting_summary.get("total_objects", 0)
        
        # Count threshold alerts
        for category, threshold in config.alert_config.count_thresholds.items():
            if category == "all" and total_vehicles >= threshold:
                alerts.append({
                    "type": "count_threshold",
                    "severity": "warning",
                    "message": f"Total vehicle count ({total_vehicles}) exceeds threshold ({threshold})",
                    "category": category,
                    "current_count": total_vehicles,
                    "threshold": threshold
                })
            elif category in counting_summary.get("by_category", {}):
                count = counting_summary["by_category"][category]
                if count >= threshold:
                    alerts.append({
                        "type": "count_threshold",
                        "severity": "warning",
                        "message": f"{category} count ({count}) exceeds threshold ({threshold})",
                        "category": category,
                        "current_count": count,
                        "threshold": threshold
                    })
        
        # Zone occupancy threshold alerts
        for zone_name, threshold in config.alert_config.occupancy_thresholds.items():
            if zone_name in zone_analysis:
                zone_count = sum(zone_analysis[zone_name].values()) if isinstance(zone_analysis[zone_name], dict) else zone_analysis[zone_name]
                if zone_count >= threshold:
                    alerts.append({
                        "type": "occupancy_threshold",
                        "severity": "warning",
                        "message": f"Zone '{zone_name}' vehicle occupancy ({zone_count}) exceeds threshold ({threshold})",
                        "zone": zone_name,
                        "current_occupancy": zone_count,
                        "threshold": threshold
                    })
        
        return alerts
    
    def _calculate_metrics(self, counting_summary: Dict, zone_analysis: Dict, config: VehicleMonitoringConfig, context: ProcessingContext) -> Dict[str, Any]:
        """Calculate detailed metrics for vehicle analytics."""
        total_vehicles = counting_summary.get("total_objects", 0)
        
        metrics = {
            "total_vehicles": total_vehicles,
            "processing_time": context.processing_time or 0.0,
            "input_format": context.input_format.value,
            "confidence_threshold": config.confidence_threshold,
            "zones_analyzed": len(zone_analysis),
            "detection_rate": 0.0,
            "coverage_percentage": 0.0
        }
        
        # Calculate detection rate
        if config.time_window_minutes and config.time_window_minutes > 0:
            metrics["detection_rate"] = (total_vehicles / config.time_window_minutes) * 60
        
        # Calculate zone coverage
        if zone_analysis and total_vehicles > 0:
            vehicles_in_zones = sum(
                sum(zone_counts.values()) if isinstance(zone_counts, dict) else zone_counts
                for zone_counts in zone_analysis.values()
            )
            metrics["coverage_percentage"] = (vehicles_in_zones / total_vehicles) * 100
        
        # Unique tracking metrics
        if config.enable_unique_counting:
            unique_count = self._count_unique_tracks(counting_summary)
            if unique_count is not None:
                metrics["unique_vehicles"] = unique_count
                metrics["tracking_efficiency"] = (unique_count / total_vehicles) * 100 if total_vehicles > 0 else 0
        
        # Per-zone metrics
        if zone_analysis:
            zone_metrics = {}
            for zone_name, zone_counts in zone_analysis.items():
                zone_total = sum(zone_counts.values()) if isinstance(zone_counts, dict) else zone_counts
                zone_metrics[zone_name] = {
                    "count": zone_total,
                    "percentage": (zone_total / total_vehicles) * 100 if total_vehicles > 0 else 0
                }
            metrics["zone_metrics"] = zone_metrics
        
        return metrics
    
    def _extract_predictions(self, data: Any) -> List[Dict[str, Any]]:
        """Extract predictions from processed data for API compatibility."""
        predictions = []
        
        try:
            if isinstance(data, list):
                # Detection format
                for item in data:
                    prediction = self._normalize_prediction(item)
                    if prediction:
                        predictions.append(prediction)
            
            elif isinstance(data, dict):
                # Frame-based or tracking format
                for frame_id, items in data.items():
                    if isinstance(items, list):
                        for item in items:
                            prediction = self._normalize_prediction(item)
                            if prediction:
                                prediction["frame_id"] = frame_id
                                predictions.append(prediction)
        
        except Exception as e:
            self.logger.warning(f"Failed to extract predictions: {str(e)}")
        
        return predictions
    
    def _normalize_prediction(self, item: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize a single prediction item."""
        if not isinstance(item, dict):
            return {}
        
        # Get the category from the item
        category = item.get("category", item.get("class", "unknown"))
        
        # Skip predictions with category 0 (human) or string 'human'
        if str(category) == "0" or category == "human":
            self.logger.debug(f"Skipping human detection (category: {category})")
            return {}
        
        return {
            "category": category,
            "confidence": item.get("confidence", item.get("score", 0.0)),
            "bounding_box": item.get("bounding_box", item.get("bbox", {})),
            "track_id": item.get("track_id")
        }
    
    def _get_detections_with_confidence(self, counting_summary: Dict) -> List[Dict]:
        """Extract detection items with confidence scores."""
        return counting_summary.get("detections", [])
    
    def _count_unique_tracks(self, counting_summary: Dict) -> Optional[int]:
        """Count unique tracks if tracking is enabled."""
        detections = self._get_detections_with_confidence(counting_summary)
        
        if not detections:
            return None
        
        # Count unique track IDs
        unique_tracks = set()
        for detection in detections:
            track_id = detection.get("track_id")
            if track_id is not None:
                unique_tracks.add(track_id)
        
        return len(unique_tracks) if unique_tracks else None
    
    def _generate_summary(self, counting_summary: Dict, zone_analysis: Dict, alerts: List) -> str:
        """Generate human-readable summary."""
        total_vehicles = counting_summary.get("total_objects", 0)
        
        if total_vehicles == 0:
            return "No vehicles detected in the scene"
        
        summary_parts = [f"{total_vehicles} vehicles detected"]
        
        if zone_analysis:
            zones_with_vehicles = sum(1 for zone_counts in zone_analysis.values() 
                                    if (sum(zone_counts.values()) if isinstance(zone_counts, dict) else zone_counts) > 0)
            summary_parts.append(f"across {zones_with_vehicles}/{len(zone_analysis)} zones")
        
        if alerts:
            alert_count = len(alerts)
            summary_parts.append(f"with {alert_count} alert{'s' if alert_count != 1 else ''}")
        
        return ", ".join(summary_parts)
    
    def _generate_events(self, counting_summary: Dict, zone_analysis: Dict, alerts: List, config: VehicleMonitoringConfig) -> List[Dict]:
        """Generate structured events for the output format."""
        from datetime import datetime, timezone
        
        events = []
        total_vehicles = counting_summary.get("total_objects", 0)
        
        if total_vehicles > 0:
            # Determine event level based on thresholds
            level = "info"
            intensity = 5.0
            
            if config.alert_config and config.alert_config.count_thresholds:
                threshold = config.alert_config.count_thresholds.get("all", 15)
                intensity = min(10.0, (total_vehicles / threshold) * 10)
                
                if intensity >= 7:
                    level = "critical"
                elif intensity >= 5:
                    level = "warning"
                else:
                    level = "info"
            else:
                if total_vehicles > 25:
                    level = "critical"
                    intensity = 9.0
                elif total_vehicles > 15:
                    level = "warning" 
                    intensity = 7.0
                else:
                    level = "info"
                    intensity = min(10.0, total_vehicles / 3.0)
            
            # Main vehicle monitoring event
            event = {
                "type": "vehicle_monitoring",
                "stream_time": datetime.now(timezone.utc).strftime("%Y-%m-%d-%H:%M:%S UTC"),
                "level": level,
                "intensity": round(intensity, 1),
                "config": {
                    "min_value": 0,
                    "max_value": 10,
                    "level_settings": {"info": 2, "warning": 5, "critical": 7}
                },
                "application_name": "Vehicle Monitoring System",
                "application_version": "1.2",
                "location_info": None,
                "human_text": f"{total_vehicles} vehicles detected"
            }
            events.append(event)
        
        # Add zone-specific events if applicable
        if zone_analysis:
            for zone_name, zone_count in zone_analysis.items():
                if isinstance(zone_count, dict):
                    zone_total = sum(zone_count.values())
                else:
                    zone_total = zone_count
                
                if zone_total > 0:
                    zone_intensity = min(10.0, zone_total / 8.0)  # Adjusted for vehicles
                    zone_level = "info"
                    if zone_intensity >= 7:
                        zone_level = "warning"
                    elif zone_intensity >= 5:
                        zone_level = "info"
                    
                    zone_event = {
                        "type": "congestion_zone_monitoring",
                        "stream_time": datetime.now(timezone.utc).strftime("%Y-%m-%d-%H:%M:%S UTC"),
                        "level": zone_level,
                        "intensity": round(zone_intensity, 1),
                        "config": {
                            "min_value": 0,
                            "max_value": 10,
                            "level_settings": {"info": 2, "warning": 5, "critical": 7}
                        },
                        "application_name": "Congestion Zone Monitoring System",
                        "application_version": "1.2",
                        "location_info": zone_name,
                        "human_text": f"Event: Congestion Zone Monitoring\nLevel: {zone_level.title()}\nTime: {datetime.now(timezone.utc).strftime('%Y-%m-%d-%H:%M:%S UTC')}\nZone: {zone_name}\nCount: {zone_total} vehicles"
                    }
                    events.append(zone_event)
        
        # Add alert events with simplified human_text
        for alert in alerts:
            total_vehicles = counting_summary.get("total_objects", 0)
            intensity_message = "Low congestion in the scene"
            if config.alert_config and config.alert_config.count_thresholds:
                threshold = config.alert_config.count_thresholds.get("all", 15)
                percentage = (total_vehicles / threshold) * 100 if threshold > 0 else 0
                if percentage < 20:
                    intensity_message = "Low congestion in the scene"
                elif percentage <= 50:
                    intensity_message = "Moderate congestion in the scene"
                elif percentage <= 70:
                    intensity_message = "Heavy congestion in the scene"
                else:
                    intensity_message = "Severe congestion in the scene"
            else:
                if total_vehicles > 15:
                    intensity_message = "Heavy congestion in the scene"
                elif total_vehicles == 1:
                    intensity_message = "Low congestion in the scene"
                else:
                    intensity_message = "Moderate congestion in the scene"

            alert_event = {
                "type": alert.get("type", "congestion_alert"),
                "stream_time": datetime.now(timezone.utc).strftime("%Y-%m-%d-%H:%M:%S UTC"),
                "level": alert.get("severity", "warning"),
                "intensity": 8.0,
                "config": {
                    "min_value": 0,
                    "max_value": 10,
                    "level_settings": {"info": 2, "warning": 5, "critical": 7}
                },
                "application_name": "Congestion Alert System",
                "application_version": "1.2",
                "location_info": alert.get("zone"),
                "human_text": f"{datetime.now(timezone.utc).strftime('%Y-%m-%d-%H:%M:%S UTC')} : {intensity_message}"
            }
            events.append(alert_event)
        
        return events
    
    def _generate_tracking_stats(self, counting_summary: Dict, zone_analysis: Dict, insights: List[str], summary: str, config: VehicleMonitoringConfig) -> List[Dict]:
        """Generate structured tracking stats for the output format."""
        tracking_stats = []
        total_vehicles = counting_summary.get("total_objects", 0)
        
        if total_vehicles > 0 or zone_analysis:
            # Create main tracking stats entry
            tracking_stat = {
                "all_results_for_tracking": {
                    "total_vehicles": total_vehicles,
                    "zone_analysis": zone_analysis,
                    "counting_summary": counting_summary,
                    "detection_rate": (total_vehicles / config.time_window_minutes * 60) if config.time_window_minutes else 0,
                    "zones_count": len(zone_analysis) if zone_analysis else 0,
                    "unique_count": self._count_unique_tracks(counting_summary),
                    "congestion_flow_rate": (total_vehicles / config.time_window_minutes) if config.time_window_minutes else 0
                },
                "human_text": self._generate_human_text_for_tracking(counting_summary, zone_analysis, insights, summary, config)
            }
            tracking_stats.append(tracking_stat)
        
        return tracking_stats
    
    def _generate_human_text_for_tracking(self, counting_summary: Dict, zone_analysis: Dict, insights: List[str], summary: str, config: VehicleMonitoringConfig) -> str:
        """Generate human-readable text for tracking stats."""
        category_counts = counting_summary.get("by_category", {})
        if not category_counts:
            return "No vehicles detected"
        
        # Generate summary of vehicle counts by category
        parts = []
        for category, count in category_counts.items():
            if count > 0 and category in config.target_vehicle_categories:
                parts.append(f"{count} {category}{'s' if count != 1 else ''}")
        
        return " and ".join(parts) if parts else "No vehicles detected"