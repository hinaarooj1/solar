from pydantic import BaseModel, Field
from typing import Optional, Literal
from datetime import datetime


class GridFeedControl(BaseModel):
    """Model for controlling grid feeding"""
    enabled: bool = Field(..., description="Enable or disable grid feeding")
    
    
class OutputPriorityControl(BaseModel):
    """Model for output source priority"""
    priority: Literal["Solar_first", "Grid_first", "SBU"] = Field(
        ..., 
        description="Output source priority: Solar_first, Grid_first, or SBU (Solar-Battery-Utility)"
    )


class LCDAutoReturnSettings(BaseModel):
    """Model for LCD auto return settings"""
    enabled: bool = Field(..., description="Enable auto return to default screen")
    timeout_seconds: Optional[int] = Field(
        default=60,
        ge=10,
        le=300,
        description="Timeout in seconds (10-300)"
    )


class SystemSettings(BaseModel):
    """Model for general system settings"""
    output_voltage: Optional[Literal[220, 230, 240]] = Field(
        None,
        description="AC output voltage (220V, 230V, or 240V)"
    )
    output_frequency: Optional[Literal[50, 60]] = Field(
        None,
        description="AC output frequency (50Hz or 60Hz)"
    )
    max_ac_charging_current: Optional[int] = Field(
        None,
        ge=0,
        le=100,
        description="Max AC charging current in Amperes"
    )
    max_charging_current: Optional[int] = Field(
        None,
        ge=0,
        le=100,
        description="Max total charging current in Amperes"
    )
    charger_source_priority: Optional[Literal["Solar_first", "Grid_first", "Solar_and_Grid"]] = Field(
        None,
        description="Charger source priority"
    )
    ac_input_voltage_range: Optional[Literal["Appliance", "UPS"]] = Field(
        None,
        description="AC input voltage range mode"
    )


class AlertConfiguration(BaseModel):
    """Model for alert configuration"""
    grid_feed_reminder_enabled: bool = Field(
        default=True,
        description="Enable periodic grid feed reminders"
    )
    grid_feed_interval_hours: int = Field(
        default=6,
        ge=1,
        le=24,
        description="Hours between grid feed reminders"
    )
    load_shedding_alerts_enabled: bool = Field(
        default=True,
        description="Enable load shedding detection alerts"
    )
    load_shedding_voltage_threshold: float = Field(
        default=180.0,
        ge=100.0,
        le=240.0,
        description="Voltage threshold for load shedding detection (V)"
    )
    system_offline_alerts_enabled: bool = Field(
        default=True,
        description="Enable system offline alerts"
    )
    system_offline_threshold_minutes: int = Field(
        default=10,
        ge=5,
        le=60,
        description="Minutes of no data before offline alert"
    )
    low_production_alerts_enabled: bool = Field(
        default=False,
        description="Enable low production warnings"
    )
    low_production_threshold_watts: float = Field(
        default=500.0,
        ge=0.0,
        description="Minimum expected production during peak hours (W)"
    )
    low_production_check_hours: str = Field(
        default="11:00-15:00",
        description="Time range for production check (HH:MM-HH:MM)"
    )
    notification_email: str = Field(
        ...,
        description="Email address for notifications"
    )


class SystemHealthResponse(BaseModel):
    """Model for system health response"""
    timestamp: datetime
    status: Literal["Online", "Offline", "Warning", "Critical"]
    health_score: int = Field(..., ge=0, le=100)
    utility_ac_voltage: float
    utility_ac_frequency: float
    pv_input_voltage: float
    pv_charging_power: float
    ac_output_voltage: float
    ac_output_frequency: float
    ac_output_power: float
    output_load_percent: float
    system_mode: str
    warnings: list[str] = []
    errors: list[str] = []


class NotificationTestRequest(BaseModel):
    """Model for testing notifications"""
    notification_type: Literal[
        "test",
        "grid_feed_reminder",
        "load_shedding",
        "system_shutdown",
        "low_production",
        "system_reset"
    ] = Field(
        default="test",
        description="Type of notification to test"
    )


class ModeAlertRequest(BaseModel):
    """Model for system mode change alerts"""
    mode: Literal["Battery Mode", "Line Mode", "Standby Mode"] = Field(
        ...,
        description="System mode that triggered the alert"
    )
    message: str = Field(
        ...,
        description="Alert message describing the mode change"
    )
    timestamp: datetime = Field(
        ...,
        description="Timestamp when the mode change occurred"
    )

