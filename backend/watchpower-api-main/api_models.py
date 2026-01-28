from pydantic import BaseModel, Field, EmailStr
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


class AuthLoginRequest(BaseModel):
    username: str
    password: str
    secret: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class AuthenticatedUser(BaseModel):
    username: str
    notification_email: Optional[EmailStr] = None


class NotificationEmailUpdate(BaseModel):
    notification_email: Optional[EmailStr] = Field(
        default=None,
        description="Email address that should receive alerts. Null disables alerts.",
    )


class AdminUserCreateRequest(BaseModel):
    username: str
    password: str
    secret: str
    watchpower_username: str
    watchpower_password: str
    serial_number: str
    wifi_pn: str
    dev_code: int
    dev_addr: int
    notification_email: Optional[EmailStr] = None
    is_active: bool = True

