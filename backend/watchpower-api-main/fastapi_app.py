from dotenv import load_dotenv
from fastapi import (
    FastAPI,
    Query,
    HTTPException,
    Depends,
    Header,
    status,
    Body,
)
import os 
from fastapi.middleware.cors import CORSMiddleware
import datetime
from datetime import timezone, timedelta
from watchpower_api import WatchPowerAPI
from typing import List, Optional, Dict, Any
import logging
import time
from threading import Lock
# Load env variables
load_dotenv()
from fastapi.responses import StreamingResponse
import json
import asyncio
from contextlib import asynccontextmanager
from fastapi.security import OAuth2PasswordBearer

# Import new msdodules
from api_models import (
    GridFeedControl,
    OutputPriorityControl,
    LCDAutoReturnSettings,
    SystemSettings,
    SystemHealthResponse,
    NotificationTestRequest,
    AuthLoginRequest,
    TokenResponse,
    AuthenticatedUser,
    NotificationEmailUpdate,
    AdminUserCreateRequest,
)
from email_service import email_service
from monitoring_service import monitoring_service
from database import get_database, get_connection_manager
from repositories import UserRepository
from auth_utils import (
    verify_password,
    get_password_hash,
    create_access_token,
    decode_access_token,
)
from user_utils import get_device_identifiers, get_watchpower_credentials

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

ADMIN_SECRET = os.getenv("ADMIN_SECRET")

db = get_database()
user_repository = UserRepository(db)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

# ============================================================================
# OPTIMIZED API SESSION MANAGER
# ============================================================================

class UserSession:
    def __init__(self):
        self.api = WatchPowerAPI()
        self.lock = Lock()
        self.logged_in_credentials: Optional[tuple[str, str]] = None


class APISessionManager:
    """Per-user WatchPower session cache with automatic re-login."""
    
    def __init__(self):
        self.sessions: Dict[str, UserSession] = {}

    def _get_session(self, user_id: str) -> UserSession:
        if user_id not in self.sessions:
            self.sessions[user_id] = UserSession()
        return self.sessions[user_id]

    def ensure_logged_in(self, user_id: str, credentials: Dict[str, str], force: bool = False):
        session = self._get_session(user_id)
        with session.lock:
            creds_tuple = (credentials["username"], credentials["password"])
            needs_login = force or session.logged_in_credentials != creds_tuple
            if needs_login:
                try:
                    logger.info(f"🔐 Logging in to WatchPower API for user {user_id}...")
                    session.api.login(credentials["username"], credentials["password"])
                    session.logged_in_credentials = creds_tuple
                    logger.info("✅ Login successful!")
                except Exception as e:
                    session.logged_in_credentials = None
                    logger.error(f"❌ Login failed for {user_id}: {e}")
                    raise HTTPException(status_code=503, detail=f"API login failed: {str(e)}")
    
    def handle_api_call(self, user_id: str, credentials: Dict[str, str], method_name: str, *args, **kwargs):
        session = self._get_session(user_id)
        self.ensure_logged_in(user_id, credentials)
        api_function = getattr(session.api, method_name)
        try:
            return api_function(*args, **kwargs)
        except RuntimeError as e:
            error_str = str(e).lower()
            if any(token in error_str for token in ["token", "auth", "login"]):
                logger.warning(f"⚠️ Auth error detected for {user_id}, retrying login...")
                self.ensure_logged_in(user_id, credentials, force=True)
                api_function = getattr(session.api, method_name)
                return api_function(*args, **kwargs)
                raise


api_manager = APISessionManager()

# ============================================================================
# DATA CACHING LAYER (10-second cache)
# ============================================================================

class DataCache:
    """Simple in-memory cache with TTL"""
    
    def __init__(self):
        self.cache = {}
        self.cache_ttl_seconds = 10  # Cache for 10 seconds
        
    def get(self, key: str):
        """Get cached data if still valid"""
        if key in self.cache:
            data, timestamp = self.cache[key]
            age = time.time() - timestamp
            if age < self.cache_ttl_seconds:
                return data
        return None
    
    def set(self, key: str, data):
        """Store data in cache with current timestamp"""
        self.cache[key] = (data, time.time())
    
    def clear(self, key: str = None):
        """Clear specific key or entire cache"""
        if key:
            self.cache.pop(key, None)
        else:
            self.cache.clear()

# Global cache instance
cache = DataCache()

# Lifespan context manager for startup/shutdown events
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Initial login and start monitoring service
    logger.info("🚀 Starting Solar Dashboard API...")
    
    monitoring_service.configure(user_repository, api_manager)
    
    # Start monitoring service in background
    logger.info("🔄 Starting background monitoring service...")
    try:
        monitoring_task = asyncio.create_task(monitoring_service.run_periodic_checks())
        logger.info("✅ Background monitoring service started successfully")
    except Exception as e:
        logger.error(f"❌ Failed to start monitoring service: {str(e)}")
        # Create a dummy task to prevent shutdown issues
        monitoring_task = asyncio.create_task(asyncio.sleep(3600))  # Sleep for 1 hour
    
    yield
    
    # Shutdown: Cleanup if needed
    logger.info("👋 Shutting down Solar Dashboard API...")
    
    # Request graceful shutdown of monitoring service
    monitoring_service.request_shutdown()
    
    # Cancel monitoring task gracefully
    if not monitoring_task.done():
        monitoring_task.cancel()
        try:
            await asyncio.wait_for(monitoring_task, timeout=5.0)
        except (asyncio.CancelledError, asyncio.TimeoutError):
            logger.info("Monitoring task cancelled or timed out during shutdown")
        except Exception as e:
            logger.error(f"Error during monitoring task shutdown: {e}")
    
    await get_connection_manager().close()
    logger.info("✅ Shutdown complete")

app = FastAPI(
    title="Solar Power Dashboard API (Optimized)",
    description="Advanced solar system monitoring and control with smart caching",
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

def call_watchpower(user: Dict[str, Any], method_name: str, **kwargs):
    credentials = get_watchpower_credentials(user)
    return api_manager.handle_api_call(user["_id"], credentials, method_name, **kwargs)


def call_watchpower_with_device(user: Dict[str, Any], method_name: str, **kwargs):
    device_params = get_device_identifiers(user)
    params = {**device_params, **kwargs}
    return call_watchpower(user, method_name, **params)


def safe_float(value):
    try:
        if value in ("", None):
            return 0.0
        return float(value)
    except (TypeError, ValueError):
        return 0.0


async def get_current_user(token: str = Depends(oauth2_scheme)):
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authentication token",
        )
    try:
        payload = decode_access_token(token)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"
        )
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token payload"
        )
    user = await user_repository.get_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found"
        )
    return user


def require_admin(secret: str = Header(..., alias="X-Admin-Secret")):
    if not ADMIN_SECRET or secret != ADMIN_SECRET:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Invalid admin secret"
        )


# ============================================================================
# Authentication & User Profile Endpoints
# ============================================================================


@app.post("/auth/login", response_model=TokenResponse)
async def auth_login(payload: AuthLoginRequest):
    user = await user_repository.get_by_username(payload.username)
    if not user or not verify_password(payload.password, user.get("password_hash", "")):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    if user.get("secret") != payload.secret:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    if user.get("is_active") is False:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Account disabled")

    token = create_access_token({"sub": user["_id"]})
    return TokenResponse(access_token=token)


@app.get("/auth/me", response_model=AuthenticatedUser)
async def auth_me(current_user: Dict[str, Any] = Depends(get_current_user)):
    return AuthenticatedUser(
        username=current_user["username"],
        notification_email=current_user.get("notification_email"),
    )


@app.get("/user/notification-email", response_model=AuthenticatedUser)
async def get_notification_email(current_user: Dict[str, Any] = Depends(get_current_user)):
    return AuthenticatedUser(
        username=current_user["username"],
        notification_email=current_user.get("notification_email"),
    )


@app.put("/user/notification-email", response_model=AuthenticatedUser)
async def update_notification_email(
    payload: NotificationEmailUpdate,
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    await user_repository.update_notification_email(current_user["_id"], payload.notification_email)
    current_user["notification_email"] = payload.notification_email
    return AuthenticatedUser(
        username=current_user["username"],
        notification_email=current_user.get("notification_email"),
    )


@app.post("/admin/users")
async def admin_create_user(
    payload: AdminUserCreateRequest,
    _: None = Depends(require_admin),
):
    existing = await user_repository.get_by_username(payload.username)
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="User already exists")

    user_document = {
        "_id": payload.username,
        "username": payload.username,
        "password_hash": get_password_hash(payload.password),
        "secret": payload.secret,
        "watchpower": {
            "username": payload.watchpower_username,
            "password": payload.watchpower_password,
            "serial_number": payload.serial_number,
            "wifi_pn": payload.wifi_pn,
            "dev_code": payload.dev_code,
            "dev_addr": payload.dev_addr,
        },
        "notification_email": payload.notification_email,
        "is_active": payload.is_active,
        "created_at": datetime.datetime.utcnow().isoformat(),
    }

    await user_repository.create_user(user_document)
    return {
        "success": True,
        "user": {
            "username": payload.username,
            "notification_email": payload.notification_email,
            "is_active": payload.is_active,
        },
    }


@app.get("/admin/users")
async def admin_list_users(_: None = Depends(require_admin)):
    return {
        "success": True,
        "users": await user_repository.list_users(),
    }

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,  # multiple domains here
    allow_methods=["*"],
    allow_headers=["*"],
)
# NOTE: We now use api_manager.get_api() instead of global wp instance
# This provides automatic re-login on token expiry


@app.get("/daily-data")
async def get_daily_data(current_user: Dict[str, Any] = Depends(get_current_user)):
    try:
        today = datetime.date.today()
        data = call_watchpower_with_device(current_user, "get_daily_data", day=today)
        return {"success": True, "data": data}
    except Exception as e:
        logger.error(f"Error in /daily-data: {e}")
        return {"success": False, "error": str(e)}
# 👇 New endpoint to fetch device info
@app.get("/devices")
async def get_devices(current_user: Dict[str, Any] = Depends(get_current_user)):
    try:
        devices = call_watchpower(current_user, "get_devices")
        return {"success": True, "devices": devices}
    except Exception as e:
        logger.error(f"Error in /devices: {e}")
        return {"success": False, "error": str(e)}


@app.get("/last-data")
async def get_last_data(current_user: Dict[str, Any] = Depends(get_current_user)):
    """Get REAL-TIME / LATEST data from inverter (updates every 5 min)"""
    try:
        data = call_watchpower_with_device(current_user, "get_device_last_data")
        return {"success": True, "data": data}
    except Exception as e:
        return {"success": False, "error": str(e)}


@app.get("/device-status")
async def get_device_status(current_user: Dict[str, Any] = Depends(get_current_user)):
    """Get REAL-TIME device STATUS (ShineMonitor API 1.6.14 - might be faster!)"""
    try:
        data = call_watchpower_with_device(current_user, "get_device_status")
        return {"success": True, "data": data}
    except Exception as e:
        return {"success": False, "error": str(e)}


@app.get("/realtime-data")
async def get_realtime_data(current_user: Dict[str, Any] = Depends(get_current_user)):
    """Get REAL-TIME RAW data (ShineMonitor API 1.6.6 - latest raw data!)"""
    try:
        data = call_watchpower_with_device(current_user, "get_device_realtime_data")
        return {"success": True, "data": data}
    except Exception as e:
        return {"success": False, "error": str(e)}


@app.get("/collector-info")
async def get_collector_info(current_user: Dict[str, Any] = Depends(get_current_user)):
    """Get data collector info - includes datFetch (upload interval!)"""
    try:
        identifiers = get_device_identifiers(current_user)
        data = call_watchpower(
            current_user,
            "get_collector_info",
            wifi_pn=identifiers["wifi_pn"],
        )
        return {"success": True, "data": data}
    except Exception as e:
        return {"success": False, "error": str(e)}


@app.get("/device-info")
async def get_device_info(current_user: Dict[str, Any] = Depends(get_current_user)):
    """Get device INFO - basic device information (might cache differently)"""
    try:
        data = call_watchpower_with_device(current_user, "get_device_info")
        return {"success": True, "data": data}
    except Exception as e:
        return {"success": False, "error": str(e)}


@app.get("/device-raw-data")
async def get_device_raw_data(current_user: Dict[str, Any] = Depends(get_current_user)):
    """Get device RAW DATA - latest raw data (Section 1.6.6)"""
    try:
        data = call_watchpower_with_device(current_user, "get_device_raw_data")
        return {"success": True, "data": data}
    except Exception as e:
        return {"success": False, "error": str(e)}


@app.get("/today-total")
async def today_total(current_user: Dict[str, Any] = Depends(get_current_user)):
    try:
        today = datetime.date.today().strftime("%Y-%m-%d")
        data = call_watchpower_with_device(
            current_user,
            "get_daily_data",
            day=datetime.date.today(),
        )

        today_records = [rec for rec in data.get("records", []) if rec.get("date") == today]
        total = sum(float(rec.get("production", 0)) for rec in today_records)

        return {
            "success": True,
            "date": today,
            "total_production": total,
            "records": today_records
        }
    except Exception as e:
        return {"success": False, "error": str(e)}
@app.get("/today-stats")
async def today_stats(current_user: Dict[str, Any] = Depends(get_current_user)):
    try:
        data = call_watchpower_with_device(
            current_user,
            "get_daily_data",
            day=datetime.date.today(),
        )

        rows = data.get("dat", {}).get("row", [])
        today_str = datetime.date.today().strftime("%Y-%m-%d")

        graph = []
        total_production_wh = 0

        for rec in rows:
            fields = rec.get("field", [])
            if len(fields) < 22:
                continue

            timestamp = fields[1]  # "2025-09-14 00:02:18"
            if not timestamp.startswith(today_str):
                continue

            pv_power = float(fields[11]) if fields[11] else 0.0  # PV1 Charging Power (W)
            load_power = float(fields[21]) if fields[21] else 0.0  # AC Output Active Power (W)

            # graph ke liye
            graph.append({
                "time": timestamp[-8:],  # sirf HH:MM:SS
                "pv_power": pv_power,
                "load_power": load_power
            })

            # 5 min interval assume karke Wh calculate
            total_production_wh += pv_power * (5 / 60)

        return {
            "success": True,
            "date": today_str,
            "total_production_kwh": round(total_production_wh / 1000, 3),
            "graph": graph
        }

    except Exception as e:
        return {"success": False, "error": str(e)}


@app.get("/raw-data")
async def raw_data(current_user: Dict[str, Any] = Depends(get_current_user)):
    """Return raw WatchPower API daily data for today"""
    try:
        data = call_watchpower_with_device(
            current_user,
            "get_daily_data",
            day=datetime.date.today(),
        )
        return data
    except Exception as e:
        return {"error": str(e)}
@app.get("/stats")
async def get_stats(
    date: str = Query(default=datetime.date.today().strftime("%Y-%m-%d")),
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """Get solar stats for a given date (default = today). OPTIMIZED with caching."""
    try:
        day = datetime.datetime.strptime(date, "%Y-%m-%d").date()
        data = call_watchpower_with_device(
            current_user,
            "get_daily_data",
            day=day,
        )

        rows = data.get("dat", {}).get("row", [])
        graph = []
        total_production_wh = 0
        total_load_wh = 0

        for rec in rows:
            fields = rec.get("field", [])
            if len(fields) < 22:
                continue

            timestamp = fields[1]  # e.g. "2025-09-10 12:34:56"
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
                mode = str(fields[47]) if fields[47] not in ["", None] else 0.0
            except:
                mode = 0.0

            graph.append({
                "time": timestamp[-8:],  # HH:MM:SS
                "pv_power": pv_power,
                "load_power": load_power,
                "mode":mode
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
        return {"success": False, "error": str(e)}

 
@app.get("/stats-range")
async def stats_range(
    from_date: str = Query(...),
    to_date: str = Query(...),
    current_user: Dict[str, Any] = Depends(get_current_user),
):

    def generate_stats():
        try:
            start = datetime.datetime.strptime(from_date, "%Y-%m-%d").date()
            end = datetime.datetime.strptime(to_date, "%Y-%m-%d").date()

            if start > end:
                yield json.dumps({"success": False, "error": "from_date must be <= to_date"}) + "\n"
                return

            total_days = (end - start).days + 1
            total_prod_wh = 0
            total_load_wh = 0
            daily_stats = []

            current = start
            while current <= end:
                try:
                    # Retry logic with exponential backoff
                    max_retries = 3
                    retry_delay = 1.0  # seconds
                    data = None
                    last_error = None
                    
                    for attempt in range(max_retries):
                        try:
                            data = call_watchpower_with_device(
                                current_user,
                                "get_daily_data",
                                day=current,
                            )
                            break  # Success, exit retry loop
                        except Exception as e:
                            last_error = e
                            error_str = str(e).lower()
                            
                            # Don't retry on certain errors (like no data available)
                            if "no record" in error_str or "err_no_record" in error_str or "err 12" in error_str:
                                raise e
                            
                            # If this is the last attempt, raise the error
                            if attempt == max_retries - 1:
                                raise e
                            
                            # Exponential backoff: 1s, 2s, 4s
                            delay = retry_delay * (2 ** attempt)
                            logger.warning(f"⚠️ Retry attempt {attempt + 1}/{max_retries} after {delay}s for {current}: {str(e)}")
                            import time
                            time.sleep(delay)
                    
                    if data is None:
                        raise last_error if last_error else Exception("Failed to fetch data after retries")

                    rows = data.get("dat", {}).get("row", [])
                    pv_wh = 0
                    load_wh = 0
                    interval_hours = 5 / 60

                    for rec in rows:
                        fields = rec.get("field", [])
                        if len(fields) < 22:
                            continue

                        timestamp = fields[1]
                        if not timestamp.startswith(str(current)):
                            continue

                        pv_power = float(fields[11]) if fields[11] else 0.0
                        load_power = float(fields[21]) if fields[21] else 0.0
                        pv_wh += pv_power * interval_hours
                        load_wh += load_power * interval_hours

                    total_prod_wh += pv_wh
                    total_load_wh += load_wh

                    daily_data = {
                        "date": str(current),
                        "production_kwh": round(pv_wh / 1000, 2),
                        "load_kwh": round(load_wh / 1000, 2)
                    }
                    daily_stats.append(daily_data)

                except Exception as e:
                    daily_data = {
                        "date": str(current),
                        "production_kwh": None,
                        "load_kwh": None,
                        "error": str(e)
                    }
                    daily_stats.append(daily_data)

                # ✅ Yield progress for frontend
                progress = len(daily_stats) / total_days * 100
                yield json.dumps({
                    "success": True,
                    "progress": round(progress, 2),
                    "daily": daily_data,
                    "total_production_kwh": round(total_prod_wh / 1000, 2),
                    "total_load_kwh": round(total_load_wh / 1000, 2)
                }) + "\n"

                current += datetime.timedelta(days=1)

        except Exception as e:
            yield json.dumps({"success": False, "error": str(e)}) + "\n"

    return StreamingResponse(generate_stats(), media_type="application/json")


@app.post("/stats-range/refetch")
async def refetch_missing_dates(
    request: Dict[str, Any] = Body(...),
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    dates = request.get("dates", [])
    """Refetch specific dates with retry logic"""
    
    def generate_refetch():
        try:
            if not dates or len(dates) == 0:
                yield json.dumps({"success": False, "error": "dates list is required"}) + "\n"
                return

            total_prod_wh = 0
            total_load_wh = 0
            interval_hours = 5 / 60

            for i, date_str in enumerate(dates):
                try:
                    current = datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
                    
                    # Retry logic with exponential backoff
                    max_retries = 3
                    retry_delay = 1.0
                    data = None
                    last_error = None
                    
                    for attempt in range(max_retries):
                        try:
                            data = call_watchpower_with_device(
                                current_user,
                                "get_daily_data",
                                day=current,
                            )
                            break
                        except Exception as e:
                            last_error = e
                            error_str = str(e).lower()
                            
                            if "no record" in error_str or "err_no_record" in error_str or "err 12" in error_str:
                                raise e
                            
                            if attempt == max_retries - 1:
                                raise e
                            
                            delay = retry_delay * (2 ** attempt)
                            logger.warning(f"⚠️ Retry attempt {attempt + 1}/{max_retries} after {delay}s for {date_str}: {str(e)}")
                            time.sleep(delay)
                    
                    if data is None:
                        raise last_error if last_error else Exception("Failed to fetch data after retries")

                    rows = data.get("dat", {}).get("row", [])
                    
                    if len(rows) == 0:
                        daily_data = {
                            "date": date_str,
                            "production_kwh": None,
                            "load_kwh": None,
                            "success": False,
                            "error": "No data available"
                        }
                    else:
                        pv_wh = 0
                        load_wh = 0
                        has_valid_data = False

                        for rec in rows:
                            fields = rec.get("field", [])
                            if len(fields) < 22:
                                continue

                            timestamp = fields[1]
                            if not timestamp.startswith(date_str):
                                continue

                            pv_power = float(fields[11]) if fields[11] else 0.0
                            load_power = float(fields[21]) if fields[21] else 0.0
                            pv_wh += pv_power * interval_hours
                            load_wh += load_power * interval_hours
                            has_valid_data = True

                        if not has_valid_data:
                            daily_data = {
                                "date": date_str,
                                "production_kwh": None,
                                "load_kwh": None,
                                "success": False,
                                "error": "No valid records found"
                            }
                        else:
                            total_prod_wh += pv_wh
                            total_load_wh += load_wh
                            daily_data = {
                                "date": date_str,
                                "production_kwh": round(pv_wh / 1000, 2),
                                "load_kwh": round(load_wh / 1000, 2),
                                "success": True
                            }

                except Exception as e:
                    logger.error(f"❌ Error refetching {date_str}: {str(e)}")
                    daily_data = {
                        "date": date_str,
                        "production_kwh": None,
                        "load_kwh": None,
                        "success": False,
                        "error": str(e)
                    }

                # Yield progress update
                progress = ((i + 1) / len(dates)) * 100
                yield json.dumps({
                    "success": True,
                    "progress": round(progress, 2),
                    "daily": daily_data,
                    "completed": i + 1,
                    "total": len(dates)
                }) + "\n"

        except Exception as e:
            yield json.dumps({"success": False, "error": str(e)}) + "\n"

    return StreamingResponse(generate_refetch(), media_type="application/json")


# ============================================================================
# NEW FEATURES: System Control & Monitoring Endpoints
# ============================================================================

# Quick Access Controls
@app.post("/control/grid-feed")
async def control_grid_feed(control: GridFeedControl):
    raise HTTPException(
        status_code=501,
        detail="Manual inverter control is not supported via this API. Use the WatchPower app.",
    )


@app.post("/control/output-priority")
async def control_output_priority(control: OutputPriorityControl):
    raise HTTPException(
        status_code=501,
        detail="Manual inverter control is not supported via this API. Use the WatchPower app.",
    )


@app.post("/control/lcd-auto-return")
async def control_lcd_auto_return(settings: LCDAutoReturnSettings):
    raise HTTPException(
        status_code=501,
        detail="Manual inverter control is not supported via this API. Use the WatchPower app.",
    )


@app.get("/system/settings/current")
async def get_current_system_settings(
    force_refresh: bool = False,
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """
    Get ACTUAL system settings from the inverter (READ-ONLY)
    
    Returns real-time values from the hardware, not user preferences.
    Use WatchPower app to change these settings.
    force_refresh: If True, re-login to API to get fresh data
    """
    try:
        # Force refresh: Clear cache if requested
        cache_key = f"system_settings:{current_user['_id']}"
        if force_refresh:
            cache.clear(cache_key)
            logger.info("Force refresh - cache cleared")
        
        # Check cache first (unless force refresh)
        if not force_refresh:
            cached_result = cache.get(cache_key)
            if cached_result:
                return cached_result
        
        # Get current data using smart API wrapper
        data = call_watchpower_with_device(
            current_user,
            "get_daily_data",
            day=datetime.date.today(),
        )
        
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
        load_power = float(fields[21]) if len(fields) > 21 and fields[21] else 0.0  # AC Output Active Power
        system_status = str(fields[49]) if len(fields) > 49 else "Unknown"
        
        # SMART grid feeding detection
        # Simple approach: Feed power + saved status
        # 
        # Key rules:
        # 1. Feed >0W → ENABLED (100% certain)
        # 2. Feed =0W → Use saved status (can't determine from hardware alone)
        # 3. Only detect DISABLED if saved status says so
        
        # Get Pakistan Standard Time (PKT = UTC+5)
        pkt_timezone = timezone(timedelta(hours=5))
        pkt_now = datetime.datetime.now(pkt_timezone)
        current_hour = pkt_now.hour
        current_time_str = pkt_now.strftime("%I:%M %p")  # Format: "10:30 AM"
        
        is_daytime = 7 <= current_hour <= 17  # 7 AM - 5 PM PKT
        is_feeding = solar_feed_power >= 10  # Any feed power (even 10W means enabled)
        
        if is_feeding:
            grid_feed_enabled = True
            feed_status = "enabled_feeding"
            feed_display = f"Enabled & Feeding ({int(solar_feed_power)}W) - {current_time_str}"
        elif is_daytime and pv_power >= 50:
            grid_feed_enabled = True
            feed_status = "enabled_not_feeding"
            feed_display = f"Enabled (PV: {int(pv_power)}W, Load: {int(load_power)}W) - {current_time_str}"
        else:
            grid_feed_enabled = False
            feed_status = "disabled_or_idle"
            reason = "Night" if not is_daytime else "No feed detected"
            feed_display = f"{reason} - {current_time_str}"
        
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
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/control/settings")
async def get_saved_settings():
    """
    Get ACTUAL system settings (not saved preferences)
    
    This endpoint now returns real hardware values instead of user preferences.
    """
    return await get_current_system_settings()


@app.post("/control/system-settings")
async def update_system_settings(settings: SystemSettings):
    raise HTTPException(
        status_code=501,
        detail="Manual inverter control is not supported via this API. Use the WatchPower app.",
    )


# System Health & Monitoring
@app.get("/system/check-reset")
async def check_system_reset(
    force_refresh: bool = False,
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """
    Check if inverter Output Priority has changed from normal "Solar Utility Bat"
    
    Detects ANY change from "Solar Utility Bat" to other values
    Sends alert when changed.
    """
    try:
        # Force refresh: Clear cache if requested
        cache_key = f"system_reset:{current_user['_id']}"
        if force_refresh:
            cache.clear(cache_key)
            logger.info("Force refresh for reset check - cache cleared")
        
        # Check cache first
        if not force_refresh:
            cached_result = cache.get(cache_key)
            if cached_result:
                return cached_result
        
        # Get current system data
        data = call_watchpower_with_device(
            current_user,
            "get_daily_data",
            day=datetime.date.today(),
        )
        
        rows = data.get("dat", {}).get("row", [])
        
        if not rows:
            raise HTTPException(status_code=503, detail="No data available from system")
        
        # Get latest reading
        latest_row = rows[-1]
        fields = latest_row.get("field", [])
        
        if len(fields) < 39:
            raise HTTPException(status_code=500, detail="Incomplete data from system")
        
        # Extract settings
        output_source_priority = str(fields[38]) if len(fields) > 38 else "Unknown"
        
        # Determine reset status
        EXPECTED_OUTPUT_PRIORITY = "Solar Utility Bat"
        reset_detected = False
        reset_reasons = []
        
        # Check: Alert on ANY change from "Solar Utility Bat"
        if output_source_priority != EXPECTED_OUTPUT_PRIORITY and output_source_priority != "Unknown":
            reset_detected = True
            reset_reasons.append(f"Output Priority changed from '{EXPECTED_OUTPUT_PRIORITY}' to '{output_source_priority}'")
        
        result = {
            "success": True,
            "timestamp": datetime.datetime.now().isoformat(),
            "reset_detected": reset_detected,
            "reset_reasons": reset_reasons,
            "settings": {
                "output_source_priority": output_source_priority,
                "expected_output_priority": EXPECTED_OUTPUT_PRIORITY
            },
            "recommendations": [
                "Open WatchPower app",
                "Set Output Priority back to 'Solar Utility Bat'",
                "Disable LCD Auto Return if enabled",
                "Enable Grid Feeding if it was disabled"
            ] if reset_detected else [],
            "note": "Alerts sent via Email, Telegram, and Discord when reset is detected"
        }
        
        # Cache the result
        cache.set(cache_key, result)
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/system/health", response_model=SystemHealthResponse)
async def get_system_health(
    force_refresh: bool = False,
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """
    Get comprehensive system health status
    """
    try:
        # Force refresh: Clear cache if requested
        cache_key = f"system_health:{current_user['_id']}"
        if force_refresh:
            cache.clear(cache_key)
            logger.info("Force refresh for health - cache cleared")
        
        # Check cache first
        if not force_refresh:
            cached_result = cache.get(cache_key)
            if cached_result:
                return cached_result
        
        # Get current data
        data = call_watchpower_with_device(
            current_user,
            "get_daily_data",
            day=datetime.date.today(),
        )
        
        rows = data.get("dat", {}).get("row", [])
        
        if not rows:
            raise HTTPException(status_code=503, detail="No data available from system")
        
        # Get latest reading
        latest_row = rows[-1]
        fields = latest_row.get("field", [])
        
        # Extract key metrics (based on data.json field indices)
        utility_voltage = float(fields[6]) if len(fields) > 6 and fields[6] else 0.0
        generator_voltage = float(fields[8]) if len(fields) > 8 and fields[8] else 0.0
        
        # Use generator voltage if utility is 0 (common in Pakistan - grid through generator input)
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
        output_source_priority = str(fields[38]) if len(fields) > 38 and fields[38] else "Unknown"
        
        # Calculate health score
        health_score = 100
        warnings = []
        errors = []
        status = "Online"
        
        # Check grid voltage (use actual grid voltage - generator or utility)
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
        
        # Check PV production (during daylight hours 6 AM - 6 PM)
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
            utility_ac_voltage=actual_grid_voltage,  # Use actual grid voltage (generator or utility)
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
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/notifications/test")
async def test_notification(
    request: NotificationTestRequest | None = None,
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """Send a test email notification for the authenticated user."""
    email = current_user.get("notification_email")
    if not email:
        raise HTTPException(status_code=400, detail="No notification email configured")

    try:
        email_service.send_test_email(recipient_email=email)
        return {
            "success": True,
            "message": "Test email sent successfully",
            "recipient": email,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/notifications/status")
async def get_notification_status(current_user: Dict[str, Any] = Depends(get_current_user)):
    """Return notification status for the authenticated user."""
    email = current_user.get("notification_email")
    return {
        "success": True,
        "email_configured": bool(email),
        "notification_email": email,
    }


def _build_daily_summary(rows: list[dict], date_str: str) -> dict:
    interval_hours = 5 / 60
    pv_wh = 0.0
    load_wh = 0.0

    for rec in rows:
        fields = rec.get("field", [])
        if len(fields) < 22:
            continue
        timestamp = fields[1]
        if not timestamp.startswith(date_str):
            continue
        pv_power = safe_float(fields[11])
        load_power = safe_float(fields[21])
        pv_wh += pv_power * interval_hours
        load_wh += load_power * interval_hours

    grid_contribution = max(pv_wh - load_wh, 0)
    return {
        "date": date_str,
        "total_production_kwh": round(pv_wh / 1000, 2),
        "total_load_kwh": round(load_wh / 1000, 2),
        "grid_contribution_kwh": round(grid_contribution / 1000, 2),
        "battery_runtime_hours": 0,
        "standby_hours": 0,
        "missing_data_hours": 0,
    }


@app.post("/notifications/test-daily-summary")
async def test_daily_summary(current_user: Dict[str, Any] = Depends(get_current_user)):
    """Send yesterday's summary email to the authenticated user."""
    email = current_user.get("notification_email")
    if not email:
        raise HTTPException(status_code=400, detail="No notification email configured")

    from datetime import date, timedelta

    yesterday = (date.today() - timedelta(days=1)).strftime("%Y-%m-%d")
    data = call_watchpower_with_device(
        current_user,
        "get_daily_data",
        day=datetime.datetime.strptime(yesterday, "%Y-%m-%d").date(),
    )
    rows = data.get("dat", {}).get("row", [])
    summary = _build_daily_summary(rows, yesterday)

    try:
        email_service.send_daily_summary(summary, recipient_email=email)
        return {
            "success": True,
            "message": "Daily summary email sent",
            "date": yesterday,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# ROOT ENDPOINT
# ============================================================================

@app.get("/")
async def root():
    """API Information and available endpoints"""
    return {
        "name": "Solar Power Dashboard API (Optimized)",
        "version": "2.1.0",
        "status": "online",
        "features": [
            "Real-time solar monitoring",
            "System control and configuration",
            "Email notifications and alerts",
            "Health monitoring",
            "Historical data analysis",
            "Smart session management",
            "10-second response caching"
        ],
        "endpoints": {
            "monitoring": [
                "GET /stats",
                "GET /stats-range",
                "GET /system/health",
                "GET /system/check-reset",
                "GET /devices"
            ],
            "control": [
                "POST /control/grid-feed",
                "POST /control/output-priority",
                "POST /control/lcd-auto-return",
                "POST /control/system-settings"
            ],
            "notifications": [
                "POST /notifications/test",
                "GET /notifications/status"
            ],
            "alerts": [
                "GET /alerts/config",
                "POST /alerts/config"
            ]
        },
        "documentation": "/docs"
    }

@app.get("/health")
@app.head("/health")
async def health_check():
    """
    Health check endpoint for uptime monitoring services.
    Use this with UptimeRobot, Cron-Job.org, or similar services
    to prevent Render.com from spinning down.
    Supports both GET and HEAD methods.
    """
    return {
        "status": "healthy",
        "timestamp": datetime.datetime.now().isoformat(),
        "api_version": "2.1.0",
        "uptime": "online"
    }

@app.get("/ping")
@app.head("/ping")
async def ping():
    """Simple ping endpoint (alternative to /health). Supports GET and HEAD."""
    return {"ping": "pong", "timestamp": datetime.datetime.now().isoformat()}
