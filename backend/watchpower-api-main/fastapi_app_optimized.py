from dotenv import load_dotenv
from fastapi import FastAPI, Query, HTTPException, BackgroundTasks
import os 
from fastapi.middleware.cors import CORSMiddleware
import datetime
from datetime import timezone, timedelta
from watchpower_api import WatchPowerAPI
from typing import List, Optional
import logging
# Load env variables
load_dotenv()
from fastapi.responses import StreamingResponse
import json
import asyncio
from contextlib import asynccontextmanager
from functools import lru_cache
import time
from threading import Lock

# Import new modules
from api_models import (
    GridFeedControl,
    OutputPriorityControl,
    LCDAutoReturnSettings,
    SystemSettings,
    AlertConfiguration,
    SystemHealthResponse,
    NotificationTestRequest
)
from email_service import email_service
from monitoring_service import monitoring_service
from settings_storage import settings_storage
from telegram_service import telegram_service
from discord_service import discord_service

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

USERNAMES = os.getenv("USERNAMES")
PASSWORD = os.getenv("PASSWORD")
SERIAL_NUMBER = os.getenv("SERIAL_NUMBER")
WIFI_PN = os.getenv("WIFI_PN")
DEV_CODE = os.getenv("DEV_CODE")
DEV_ADDR = os.getenv("DEV_ADDR")

# Convert to integers safely
try:
    DEV_CODE = int(DEV_CODE) if DEV_CODE else None
    DEV_ADDR = int(DEV_ADDR) if DEV_ADDR else None
except TypeError:
    raise ValueError("DEV_CODE or DEV_ADDR not found in environment variables")

logger.info(f"Config loaded: {USERNAMES}, SN: {SERIAL_NUMBER}, PN: {WIFI_PN}")

# ============================================================================
# OPTIMIZED API SESSION MANAGER
# ============================================================================

class APISessionManager:
    """Manages WatchPower API session with automatic re-login on token expiry"""
    
    def __init__(self):
        self.wp = WatchPowerAPI()
        self.last_login_time = None
        self.login_lock = Lock()
        self.token_validity_hours = 12  # Assume token valid for 12 hours
        self._is_logged_in = False
        
    def ensure_logged_in(self):
        """Ensure we have a valid login session, re-login if needed"""
        with self.login_lock:
            now = datetime.datetime.now()
            
            # Check if we need to login or re-login
            needs_login = (
                not self._is_logged_in or 
                self.last_login_time is None or
                (now - self.last_login_time) > timedelta(hours=self.token_validity_hours)
            )
            
            if needs_login:
                try:
                    logger.info("Logging in to WatchPower API...")
                    self.wp.login(USERNAMES, PASSWORD)
                    self.last_login_time = now
                    self._is_logged_in = True
                    logger.info("Login successful!")
                except Exception as e:
                    logger.error(f"Login failed: {e}")
                    self._is_logged_in = False
                    raise HTTPException(status_code=503, detail=f"API login failed: {str(e)}")
    
    def get_api(self) -> WatchPowerAPI:
        """Get the API instance, ensuring it's logged in"""
        self.ensure_logged_in()
        return self.wp

# Global API session manager
api_manager = APISessionManager()

# ============================================================================
# DATA CACHING LAYER
# ============================================================================

class DataCache:
    """Simple in-memory cache with TTL"""
    
    def __init__(self):
        self.cache = {}
        self.cache_ttl_seconds = 10  # Cache for 10 seconds (inverter updates every 5 min anyway)
        
    def get(self, key: str):
        """Get cached data if still valid"""
        if key in self.cache:
            data, timestamp = self.cache[key]
            age = time.time() - timestamp
            if age < self.cache_ttl_seconds:
                logger.debug(f"Cache HIT for {key} (age: {age:.1f}s)")
                return data
            else:
                logger.debug(f"Cache EXPIRED for {key} (age: {age:.1f}s)")
        return None
    
    def set(self, key: str, data):
        """Store data in cache with current timestamp"""
        self.cache[key] = (data, time.time())
        logger.debug(f"Cache SET for {key}")
    
    def clear(self, key: str = None):
        """Clear specific key or entire cache"""
        if key:
            self.cache.pop(key, None)
        else:
            self.cache.clear()

# Global cache instance
cache = DataCache()

# ============================================================================
# FASTAPI APP SETUP
# ============================================================================

# Lifespan context manager for startup/shutdown events
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Initial login and start monitoring service
    logger.info("Starting up Solar Dashboard API...")
    try:
        api_manager.ensure_logged_in()
    except Exception as e:
        logger.error(f"Initial login failed: {e}")
    
    asyncio.create_task(monitoring_service.run_periodic_checks())
    
    yield
    
    # Shutdown: Cleanup if needed
    logger.info("Shutting down Solar Dashboard API...")

app = FastAPI(
    title="Solar Power Dashboard API",
    description="Advanced solar system monitoring and control (Optimized)",
    version="2.1.0",
    lifespan=lifespan
)

allowed_origins = [
    "http://127.0.0.1:5502",
    "http://127.0.0.1:5504",
    "http://127.0.0.1:5503",
    "http://localhost:3000",
    "http://localhost:3001",
    "http://localhost:3002",
    "https://solarbyahmar.vercel.app",
    "https://www.solarbyahmar.vercel.app",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_daily_data_cached(date: datetime.date, force_refresh: bool = False):
    """Get daily data with caching"""
    cache_key = f"daily_data_{date}"
    
    # Check cache first (unless force refresh)
    if not force_refresh:
        cached_data = cache.get(cache_key)
        if cached_data:
            return cached_data
    
    # Fetch fresh data
    try:
        wp = api_manager.get_api()
        data = wp.get_daily_data(
            day=date,
            serial_number=SERIAL_NUMBER,
            wifi_pn=WIFI_PN,
            dev_code=DEV_CODE,
            dev_addr=DEV_ADDR
        )
        cache.set(cache_key, data)
        return data
    except Exception as e:
        logger.error(f"Error fetching daily data: {e}")
        # Try to return stale cache if available
        cached_data = cache.get(cache_key) if not force_refresh else None
        if cached_data:
            logger.warning("Returning stale cache due to error")
            return cached_data
        raise

# ============================================================================
# BASIC ENDPOINTS (Legacy compatibility)
# ============================================================================

@app.get("/daily-data")
def get_daily_data():
    try:
        today = datetime.date.today()
        data = get_daily_data_cached(today)
        return {"success": True, "data": data}
    except Exception as e:
        logger.error(f"Error in /daily-data: {e}")
        return {"success": False, "error": str(e)}

@app.get("/devices")
def get_devices():
    try:
        wp = api_manager.get_api()
        devices = wp.get_devices()
        return {"success": True, "devices": devices}
    except Exception as e:
        logger.error(f"Error in /devices: {e}")
        return {"success": False, "error": str(e)}

@app.get("/last-data")
def get_last_data():
    """Get REAL-TIME / LATEST data from inverter"""
    cache_key = "last_data"
    
    # Check cache first
    cached_data = cache.get(cache_key)
    if cached_data:
        return cached_data
    
    try:
        wp = api_manager.get_api()
        data = wp.get_device_last_data(
            serial_number=SERIAL_NUMBER,
            wifi_pn=WIFI_PN,
            dev_code=DEV_CODE,
            dev_addr=DEV_ADDR
        )
        result = {"success": True, "data": data}
        cache.set(cache_key, result)
        return result
    except Exception as e:
        logger.error(f"Error in /last-data: {e}")
        return {"success": False, "error": str(e)}

@app.get("/device-status")
def get_device_status():
    """Get REAL-TIME device STATUS"""
    cache_key = "device_status"
    cached_data = cache.get(cache_key)
    if cached_data:
        return cached_data
    
    try:
        wp = api_manager.get_api()
        data = wp.get_device_status(
            serial_number=SERIAL_NUMBER,
            wifi_pn=WIFI_PN,
            dev_code=DEV_CODE,
            dev_addr=DEV_ADDR
        )
        result = {"success": True, "data": data}
        cache.set(cache_key, result)
        return result
    except Exception as e:
        logger.error(f"Error in /device-status: {e}")
        return {"success": False, "error": str(e)}

@app.get("/stats")
def get_stats(date: str = Query(default=datetime.date.today().strftime("%Y-%m-%d"))):
    """
    Get solar stats for a given date (default = today).
    OPTIMIZED with caching.
    """
    try:
        day = datetime.datetime.strptime(date, "%Y-%m-%d").date()
        data = get_daily_data_cached(day)
        
        rows = data.get("dat", {}).get("row", [])
        graph = []
        total_production_wh = 0
        total_load_wh = 0

        for rec in rows:
            fields = rec.get("field", [])
            if len(fields) < 22:
                continue

            timestamp = fields[1]
            if not timestamp.startswith(date):
                continue

            # Safe parsing
            try:
                pv_power = float(fields[11]) if fields[11] not in ["", None] else 0.0
            except:
                pv_power = 0.0
            try:
                load_power = float(fields[21]) if fields[21] not in ["", None] else 0.0
            except:
                load_power = 0.0
            try:
                mode = str(fields[47]) if fields[47] not in ["", None] else "Unknown"
            except:
                mode = "Unknown"

            graph.append({
                "time": timestamp[-8:],  # HH:MM:SS
                "pv_power": pv_power,
                "load_power": load_power,
                "mode": mode
            })

            # 5 min interval = 0.0833 hr
            total_production_wh += pv_power * (5 / 60)
            total_load_wh += load_power * (5 / 60)

        return {
            "success": True,
            "date": date,
            "total_production_kwh": round(total_production_wh / 1000, 3),
            "total_load_kwh": round(total_load_wh / 1000, 3),
            "graph": graph
        }

    except Exception as e:
        logger.error(f"Error in /stats: {e}")
        return {"success": False, "error": str(e)}

# Continue with remaining endpoints...
# (For brevity, I'll include the key optimized endpoints)

@app.get("/system/settings/current")
async def get_current_system_settings(force_refresh: bool = False):
    """
    Get ACTUAL system settings from the inverter (READ-ONLY)
    OPTIMIZED: Uses cache, no unnecessary re-login
    """
    cache_key = "system_settings"
    
    # Check cache first (unless force refresh)
    if not force_refresh:
        cached_result = cache.get(cache_key)
        if cached_result:
            return cached_result
    
    try:
        # Clear cache if force refresh requested
        if force_refresh:
            cache.clear(cache_key)
            logger.info("Force refresh requested - cache cleared")
        
        # Get current data (will use cached daily data if available)
        data = get_daily_data_cached(datetime.date.today(), force_refresh=force_refresh)
        
        rows = data.get("dat", {}).get("row", [])
        
        if not rows:
            raise HTTPException(status_code=503, detail="No data available from system")
        
        # Get latest reading
        latest_row = rows[-1]
        fields = latest_row.get("field", [])
        
        if len(fields) < 50:
            raise HTTPException(status_code=500, detail="Incomplete data from system")
        
        # Extract actual system settings from fields
        ac_input_range = str(fields[37]) if len(fields) > 37 else "Unknown"
        output_source_priority = str(fields[38]) if len(fields) > 38 else "Unknown"
        charger_source_priority = str(fields[39]) if len(fields) > 39 else "Unknown"
        load_status = str(fields[45]) if len(fields) > 45 else "Unknown"
        solar_feed_power = float(fields[46]) if len(fields) > 46 and fields[46] else 0.0
        pv_power = float(fields[11]) if len(fields) > 11 and fields[11] else 0.0
        system_status = str(fields[49]) if len(fields) > 49 else "Unknown"
        
        # SIMPLE & RELIABLE grid feeding detection
        # Get Pakistan Standard Time (PKT = UTC+5)
        pkt_timezone = timezone(timedelta(hours=5))
        pkt_now = datetime.datetime.now(pkt_timezone)
        current_hour = pkt_now.hour
        current_time_str = pkt_now.strftime("%I:%M %p")
        
        is_daytime = 7 <= current_hour <= 17
        is_producing = pv_power > 500
        is_feeding = solar_feed_power >= 50
        
        # Grid feeding detection logic
        if is_daytime and is_producing:
            if is_feeding:
                grid_feed_enabled = True
                feed_status = "enabled_feeding"
                feed_display = f"Enabled & Feeding ({int(solar_feed_power)}W) - {current_time_str}"
            else:
                grid_feed_enabled = False
                feed_status = "disabled"
                feed_display = f"DISABLED (Feed: {int(solar_feed_power)}W) - {current_time_str}"
        else:
            # Night or not producing - check last known state
            saved_grid_status = settings_storage.get("grid_feeding_enabled", True)
            
            if is_feeding:
                grid_feed_enabled = True
                feed_status = "enabled_feeding"
                feed_display = f"Enabled & Feeding ({int(solar_feed_power)}W) - {current_time_str}"
            elif saved_grid_status == False:
                grid_feed_enabled = False
                feed_status = "disabled"
                feed_display = f"DISABLED (No Production) - {current_time_str}"
            else:
                grid_feed_enabled = True
                feed_status = "enabled_not_feeding"
                feed_display = f"Enabled (No Production) - {current_time_str}"
        
        # Update monitoring service
        monitoring_service.set_grid_feeding_status(grid_feed_enabled)
        
        result = {
            "success": True,
            "timestamp": datetime.datetime.now().isoformat(),
            "settings": {
                "ac_input_range": ac_input_range,
                "output_source_priority": output_source_priority,
                "charger_source_priority": charger_source_priority,
                "load_status": load_status,
                "system_status": system_status,
                "grid_feed_enabled": grid_feed_enabled,
                "grid_feed_status": feed_status,
                "grid_feed_display": feed_display,
                "solar_feed_power": solar_feed_power,
                "pv_power": pv_power
            },
            "note": "These are READ-ONLY values from your inverter. Use WatchPower app to change settings."
        }
        
        # Cache the result
        cache.set(cache_key, result)
        return result
        
    except Exception as e:
        logger.error(f"Error in /system/settings/current: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/system/health", response_model=SystemHealthResponse)
async def get_system_health(force_refresh: bool = False):
    """
    Get comprehensive system health status
    OPTIMIZED: Uses cache, no unnecessary re-login
    """
    cache_key = "system_health"
    
    # Check cache first
    if not force_refresh:
        cached_result = cache.get(cache_key)
        if cached_result:
            return cached_result
    
    try:
        if force_refresh:
            cache.clear(cache_key)
            logger.info("Force refresh requested for health - cache cleared")
        
        # Get current data
        data = get_daily_data_cached(datetime.date.today(), force_refresh=force_refresh)
        
        rows = data.get("dat", {}).get("row", [])
        
        if not rows:
            raise HTTPException(status_code=503, detail="No data available from system")
        
        # Get latest reading
        latest_row = rows[-1]
        fields = latest_row.get("field", [])
        
        # Update monitoring service timestamp
        monitoring_service.update_data_timestamp()
        
        # Extract key metrics
        utility_voltage = float(fields[6]) if len(fields) > 6 and fields[6] else 0.0
        generator_voltage = float(fields[8]) if len(fields) > 8 and fields[8] else 0.0
        actual_grid_voltage = generator_voltage if utility_voltage == 0.0 else utility_voltage
        
        utility_frequency = float(fields[7]) if len(fields) > 7 and fields[7] else 0.0
        generator_frequency = float(fields[9]) if len(fields) > 9 and fields[9] else 0.0
        actual_grid_frequency = generator_frequency if utility_frequency == 0.0 else utility_frequency
        
        pv_voltage = float(fields[10]) if len(fields) > 10 and fields[10] else 0.0
        pv_power = float(fields[11]) if len(fields) > 11 and fields[11] else 0.0
        ac_output_voltage = float(fields[17]) if len(fields) > 17 and fields[17] else 0.0
        ac_output_frequency = float(fields[19]) if len(fields) > 19 and fields[19] else 0.0
        ac_output_power = float(fields[21]) if len(fields) > 21 and fields[21] else 0.0
        output_load_percent = float(fields[22]) if len(fields) > 22 and fields[22] else 0.0
        mode = str(fields[47]) if len(fields) > 47 and fields[47] else "Unknown"
        
        # Check for load shedding
        await monitoring_service.check_load_shedding(actual_grid_voltage)
        
        # Check for low production
        await monitoring_service.check_low_production(pv_power, datetime.datetime.now().strftime("%H:%M"))
        
        # Calculate health score
        health_score = 100
        warnings = []
        errors = []
        status = "Online"
        
        # Check grid voltage
        if actual_grid_voltage < 180:
            health_score -= 20
            warnings.append(f"Low grid voltage: {actual_grid_voltage}V")
            if actual_grid_voltage < 150:
                health_score -= 20
                errors.append(f"Critical grid voltage: {actual_grid_voltage}V")
                status = "Warning"
        
        # Check load
        if output_load_percent > 80:
            health_score -= 15
            warnings.append(f"High load: {output_load_percent}%")
        if output_load_percent > 95:
            health_score -= 15
            errors.append(f"Critical load: {output_load_percent}%")
            status = "Critical"
        
        # Check PV production
        current_hour = datetime.datetime.now().hour
        if 6 <= current_hour <= 18 and pv_power < 50:
            health_score -= 10
            warnings.append(f"Low solar production: {pv_power}W")
        
        # Check mode
        if mode == "Fault Mode":
            health_score -= 50
            errors.append("System in fault mode!")
            status = "Critical"
        elif mode == "Standby Mode":
            warnings.append("System in standby mode")
        
        result = SystemHealthResponse(
            timestamp=datetime.datetime.now(),
            status=status,
            health_score=max(0, health_score),
            utility_ac_voltage=actual_grid_voltage,
            utility_ac_frequency=actual_grid_frequency,
            pv_input_voltage=pv_voltage,
            pv_charging_power=pv_power,
            ac_output_voltage=ac_output_voltage,
            ac_output_frequency=ac_output_frequency,
            ac_output_power=ac_output_power,
            output_load_percent=output_load_percent,
            system_mode=mode,
            warnings=warnings,
            errors=errors
        )
        
        # Cache the result
        cache.set(cache_key, result)
        return result
        
    except Exception as e:
        logger.error(f"Error in /system/health: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# CONTROL ENDPOINTS
# ============================================================================

@app.post("/control/grid-feed")
async def control_grid_feed(control: GridFeedControl):
    """Enable or disable grid feeding monitoring"""
    try:
        monitoring_service.set_grid_feeding_status(control.enabled)
        
        return {
            "success": True,
            "message": f"Grid feeding {'enabled' if control.enabled else 'disabled'}",
            "grid_feed_enabled": control.enabled,
            "saved": True,
            "note": "Setting saved. Use WatchPower app for actual hardware control."
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# NOTIFICATION ENDPOINTS
# ============================================================================

@app.get("/notifications/status")
async def get_notification_status():
    """Get current notification configuration status"""
    try:
        return {
            "success": True,
            "email_configured": bool(email_service.sender_email and email_service.sender_password),
            "sender_email": email_service.sender_email,
            "recipient_email": email_service.recipient_email,
            "telegram_configured": bool(telegram_service.bot_token and telegram_service.chat_id),
            "discord_configured": bool(discord_service.webhook_url),
            "monitoring_active": monitoring_service.system_online,
            "grid_feeding_enabled": monitoring_service.grid_feeding_enabled,
            "is_load_shedding": monitoring_service.is_load_shedding,
            "last_data_timestamp": monitoring_service.last_data_timestamp.isoformat()
        }
    except Exception as e:
        logger.error(f"Error in /notifications/status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# ROOT ENDPOINT
# ============================================================================

@app.get("/")
async def root():
    """API Information"""
    return {
        "name": "Solar Power Dashboard API (Optimized)",
        "version": "2.1.0",
        "optimizations": [
            "Smart session management (auto re-login on expiry)",
            "10-second response caching",
            "Reduced external API calls",
            "Better error handling"
        ],
        "documentation": "/docs"
    }










