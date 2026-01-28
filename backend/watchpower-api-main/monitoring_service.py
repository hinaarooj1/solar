import asyncio
import logging
import os
from datetime import datetime, timedelta, date
from typing import Any, Dict, Optional

from email_service import email_service
from user_utils import get_device_identifiers, get_watchpower_credentials


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def _safe_float(value: Any, default: float = 0.0) -> float:
    try:
        if value in ("", None):
            return default
        return float(value)
    except (TypeError, ValueError):
        return default


class UserMonitorState:
    def __init__(self):
        self.previous_mode: Optional[str] = None
        self.api_data_failing: bool = False
        self.last_missing_data_alert_time: Optional[datetime] = None
        self.consecutive_api_failures: int = 0


class MonitoringService:
    """Background monitoring service that runs per user."""

    def __init__(self):
        self.shutdown_requested = False
        self.interval_seconds = int(os.getenv("MONITORING_INTERVAL_SECONDS", "400"))
        self.user_repository = None
        self.api_manager = None
        self.user_states: Dict[str, UserMonitorState] = {}

    def configure(self, user_repository, api_manager):
        self.user_repository = user_repository
        self.api_manager = api_manager

    def request_shutdown(self):
        self.shutdown_requested = True

    def _get_state(self, user_id: str) -> UserMonitorState:
        if user_id not in self.user_states:
            self.user_states[user_id] = UserMonitorState()
        return self.user_states[user_id]

    async def run_periodic_checks(self):
        logger.info("🔁 Monitoring service loop started")
        while not self.shutdown_requested:
            try:
                await self._run_cycle()
            except Exception as exc:
                logger.error(f"Monitoring cycle failed: {exc}")
            await asyncio.sleep(self.interval_seconds)
        logger.info("🛑 Monitoring service loop stopped")

    async def _run_cycle(self):
        if not self.user_repository or not self.api_manager:
            logger.warning("Monitoring service not configured with repository or API manager")
            await asyncio.sleep(self.interval_seconds)
            return

        users = await self.user_repository.get_all_active_users()
        if not users:
            logger.debug("No active users to monitor")
            return

        logger.info(f"👀 Running monitoring checks for {len(users)} users")

        for user in users:
            try:
                await self._process_user(user)
            except Exception as exc:
                logger.error(f"Monitoring failed for user {user.get('username')}: {exc}")

    async def _process_user(self, user: Dict[str, Any]):
        user_id = user["_id"]
        state = self._get_state(user_id)

        try:
            latest_row = self._fetch_latest_row(user)
        except Exception as exc:
            logger.error(f"API failure for {user_id}: {exc}")
            await self._handle_api_failure(user, state)
            return

        if latest_row is None:
            logger.warning(f"No data rows returned for {user_id}")
            await self._handle_api_failure(user, state)
            return

        await self._handle_api_success(user, state, latest_row)

    def _fetch_latest_row(self, user: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        wp_creds = get_watchpower_credentials(user)
        device_params = get_device_identifiers(user)
        today = date.today()

        data = self.api_manager.handle_api_call(
            user["_id"],
            wp_creds,
            "get_daily_data",
            day=today,
            **device_params,
        )
        rows = data.get("dat", {}).get("row", [])
        if not rows:
            return None
        return rows[-1]

    async def _handle_api_failure(self, user: Dict[str, Any], state: UserMonitorState):
        state.consecutive_api_failures += 1
        send_alert = False
        now = datetime.utcnow()

        if not state.api_data_failing:
            send_alert = True
            state.api_data_failing = True
            logger.warning(f"🚨 API failure detected for {user['username']}")
        elif state.last_missing_data_alert_time is None:
            send_alert = True
        else:
            elapsed = now - state.last_missing_data_alert_time
            if elapsed >= timedelta(hours=1):
                send_alert = True

        if send_alert:
            minutes = state.consecutive_api_failures * (self.interval_seconds // 60 or 1)
            self._send_api_failure_email(user, minutes, state.consecutive_api_failures)
            state.last_missing_data_alert_time = now

    async def _handle_api_success(
        self,
        user: Dict[str, Any],
        state: UserMonitorState,
        latest_row: Dict[str, Any],
    ):
        if state.api_data_failing:
            self._send_api_recovery_email(user, state.consecutive_api_failures)
        state.api_data_failing = False
        state.consecutive_api_failures = 0
        state.last_missing_data_alert_time = None

        fields = latest_row.get("field", [])
        mode = str(fields[47]) if len(fields) > 47 and fields[47] else "Unknown"
        utility_voltage = _safe_float(fields[6])
        generator_voltage = _safe_float(fields[8])
        grid_voltage = generator_voltage if utility_voltage == 0 else utility_voltage

        if mode != state.previous_mode and mode not in (None, "Unknown"):
            self._send_mode_alert(user, mode, grid_voltage)
            state.previous_mode = mode

    def _send_mode_alert(self, user: Dict[str, Any], mode: str, voltage: float):
        email = user.get("notification_email")
        if not email:
            logger.info(f"Skipping mode alert for {user['username']} - no notification email configured")
            return

        if mode == "Battery Mode":
            message = f"Electricity disconnected. Running on battery. Grid Voltage: {voltage:.1f}V"
        elif mode == "Line Mode":
            message = f"Electricity restored. Grid Voltage: {voltage:.1f}V"
        elif mode == "Standby Mode":
            message = "System entered Standby mode. Power output stopped."
        else:
            message = f"System mode changed to {mode}."

        timestamp = datetime.utcnow().isoformat()
        logger.info(f"Sending mode alert for {user['username']} ({mode})")
        email_service.send_mode_alert(mode, message, timestamp, recipient_email=email)

    def _send_api_failure_email(self, user: Dict[str, Any], minutes: int, failures: int):
        email = user.get("notification_email")
        if not email:
            logger.debug(f"Skipping API failure alert for {user['username']} - no email configured")
            return
        email_service.send_api_failure_alert(
            failure_duration_minutes=minutes,
            consecutive_failures=failures,
            recipient_email=email,
        )

    def _send_api_recovery_email(self, user: Dict[str, Any], failures: int):
        email = user.get("notification_email")
        if not email:
            return
        email_service.send_api_recovery_alert(failures, recipient_email=email)


monitoring_service = MonitoringService()


