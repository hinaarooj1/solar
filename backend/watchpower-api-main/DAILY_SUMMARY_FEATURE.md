# Daily Summary Feature 📊

## Overview

Automatically sends a comprehensive daily solar system performance summary to all configured alert channels (Email, Telegram, Discord) every day at **12:00 AM PKT (GMT+5)**.

## Features ✨

### Automated Daily Reports
- **Timing**: Sends automatically at midnight (12:00 AM) Pakistan Time (PKT/GMT+5)
- **Frequency**: Once per day
- **Content**: Full summary of previous day's solar system performance

### Summary Includes 📋

1. **☀️ Solar Production**
   - Total energy generated in kWh

2. **⚡ Energy Usage**
   - Total energy consumed in kWh

3. **🔋 Grid Contribution**
   - Energy fed back to the grid in kWh
   - Calculated as: Production - Consumption

4. **🔌 Load Shedding**
   - Total time system ran on battery/solar (no grid)
   - Formatted as: "X hr Y min"

5. **⏸️ System Off Time**
   - Total time system was completely off
   - Breakdown:
     - Standby Mode hours
     - Missing Data hours (when API didn't respond)

## Implementation Details 🔧

### Files Modified

#### 1. `monitoring_service.py`
**Added:**
- `last_daily_summary_date`: Tracks when last summary was sent
- `pkt_timezone`: PKT timezone object for accurate time checking
- `fetch_daily_stats(date_str)`: Fetches and calculates daily statistics
- `check_and_send_daily_summary()`: Checks if it's midnight and sends summary

**Logic:**
- Runs every 5 minutes as part of periodic checks
- Checks if current time is between 00:00 and 00:05 PKT
- Ensures summary is sent only once per day
- Fetches previous day's data (since it runs at midnight)
- Sends to all three notification channels with error handling

#### 2. `email_service.py`
**Added:**
```python
def send_daily_summary(self, summary_data: dict) -> bool
```
- Formats summary data into email format
- Includes all key metrics with clear sections
- Uses Unicode characters for visual clarity

#### 3. `telegram_service.py`
**Added:**
```python
def send_daily_summary(self, summary_data: dict) -> bool
```
- Formats summary data with Telegram Markdown
- Uses bold formatting for key numbers
- Includes emojis for quick visual scanning

#### 4. `discord_service.py`
**Added:**
```python
def send_daily_summary(self, summary_data: dict) -> bool
```
- Creates rich Discord embed
- Uses inline fields for compact display
- Blue color theme (#3447003)

#### 5. `requirements.txt`
**Added:**
- `pytz==2024.1` for timezone handling

### Data Calculation Logic

The summary fetches raw data from the WatchPower API and calculates:

```python
# Energy calculations (5-minute intervals)
total_production_wh = sum(pv_power * (5/60))
total_load_wh = sum(load_power * (5/60))
grid_contribution = production - load

# Mode tracking
battery_mode_hours = count_of_battery_mode * (5/60)
standby_mode_hours = count_of_standby_mode * (5/60)

# Missing data
expected_points = 288  # (24 hours * 60 min) / 5 min
missing_points = expected_points - actual_points
missing_hours = (missing_points * 5) / 60
```

### Timezone Handling

Uses `pytz` library for accurate Pakistan timezone:
```python
self.pkt_timezone = pytz.timezone('Asia/Karachi')  # GMT+5
now_pkt = datetime.now(self.pkt_timezone)
```

### Error Handling

Each notification channel is wrapped in try-except:
```python
try:
    email_service.send_daily_summary(summary_data)
    logger.info("✅ Daily summary sent via Email")
except Exception as e:
    logger.error(f"❌ Email summary failed: {str(e)}")
```

This ensures that if one channel fails, others still send successfully.

## Sample Output 📬

### Email Format
```
Daily Solar Summary for 2024-10-08

☀️ SOLAR PRODUCTION
━━━━━━━━━━━━━━━━━━━━━━━━
Total Production: 15.45 kWh

⚡ ENERGY USAGE
━━━━━━━━━━━━━━━━━━━━━━━━
Total Consumption: 12.30 kWh

🔋 GRID CONTRIBUTION
━━━━━━━━━━━━━━━━━━━━━━━━
Energy Fed to Grid: 3.15 kWh

🔌 LOAD SHEDDING
━━━━━━━━━━━━━━━━━━━━━━━━
Battery/Solar Runtime: 4 hr 30 min

⏸️ SYSTEM OFF TIME
━━━━━━━━━━━━━━━━━━━━━━━━
Total Off Duration: 2 hr 15 min
  • Standby Mode: 1 hr 45 min
  • Missing Data: 0 hr 30 min

━━━━━━━━━━━━━━━━━━━━━━━━
Solar Dashboard - Daily Summary
Generated at 2024-10-09 00:01:23 PKT
```

### Telegram Format
Uses Markdown with **bold** for emphasis and Unicode separators.

### Discord Format
Rich embed with:
- Blue color theme
- Inline fields for production, usage, grid contribution
- Separate fields for load shedding and system off time
- Footer with generation timestamp

## Testing 🧪

### Manual Testing

Since the feature runs automatically at midnight, you can test it by:

1. **Temporarily modify the time check** for testing:
   ```python
   # In monitoring_service.py, temporarily change:
   if midnight <= current_time < five_past_midnight:
   # To:
   if True:  # Always send for testing
   ```

2. **Run the monitoring service** and wait for next 5-minute cycle

3. **Check logs** for:
   ```
   🌙 It's midnight PKT! Preparing daily summary for YYYY-MM-DD...
   📊 Sending daily summary for YYYY-MM-DD...
   ✅ Daily summary sent via Email
   ✅ Daily summary sent via Telegram
   ✅ Daily summary sent via Discord
   ```

4. **Revert the changes** after testing

### Production Testing

- Wait for midnight PKT (00:00-00:05)
- Check Render logs for summary sending
- Verify receipt in all three channels

## Monitoring 📈

### Log Messages

**Success:**
```
INFO:monitoring_service:🌙 It's midnight PKT! Preparing daily summary for 2024-10-08...
INFO:monitoring_service:📊 Sending daily summary for 2024-10-08...
INFO:monitoring_service:✅ Daily summary sent via Email
INFO:monitoring_service:✅ Daily summary sent via Telegram
INFO:monitoring_service:✅ Daily summary sent via Discord
INFO:monitoring_service:✅ Daily summary sent successfully for 2024-10-08
```

**Errors:**
```
ERROR:monitoring_service:❌ Email summary failed: [error message]
ERROR:monitoring_service:❌ Failed to fetch daily stats for 2024-10-08
```

## Configuration ⚙️

### Environment Variables

No new environment variables required! Uses existing:
- `SERIAL_NUMBER`
- `WIFI_PN`
- `DEV_CODE`
- `DEV_ADDR`
- All existing email/telegram/discord credentials

### Customization Options

To change the summary time, modify in `monitoring_service.py`:
```python
# Current: midnight to 00:05
midnight = time(0, 0)
five_past_midnight = time(0, 5)

# Example: Change to 1 AM
midnight = time(1, 0)
five_past_midnight = time(1, 5)
```

## Integration with Existing Features ✅

### Does NOT Affect:
- ✅ System reset detection (hourly reminders)
- ✅ Load shedding alerts (5-hour reminders)
- ✅ Grid feed disabled alerts (hourly reminders)
- ✅ System offline alerts
- ✅ Low production alerts
- ✅ All existing API endpoints
- ✅ Frontend functionality

### How It Works:
- Runs as part of the existing 5-minute periodic check loop
- Only sends between 00:00-00:05 PKT
- Uses same notification services as other alerts
- Fetches data using existing API manager
- No impact on other monitoring features

## Benefits 🌟

1. **Automatic**: No manual work required
2. **Comprehensive**: All key metrics in one place
3. **Multi-channel**: Email, Telegram, and Discord
4. **Reliable**: Error handling ensures partial failures don't stop the service
5. **Timezone-aware**: Accurate to Pakistan time
6. **Non-intrusive**: Runs once per day at midnight
7. **Data-rich**: Includes production, consumption, grid feed, load shedding, and system status

## Troubleshooting 🔧

### Summary not received?

1. **Check Render logs** around midnight PKT
2. **Verify timezone**: Ensure system time is correct
3. **Check API connectivity**: Ensure WatchPower API is accessible
4. **Verify credentials**: Ensure Email/Telegram/Discord are configured

### Duplicate summaries?

- Should not happen due to `last_daily_summary_date` tracking
- If occurs, check Render logs for restarts around midnight

### Missing data in summary?

- Check if WatchPower API had data for that day
- Verify SERIAL_NUMBER, WIFI_PN, DEV_CODE, DEV_ADDR are correct
- Check logs for "Failed to fetch daily stats" errors

## Status ✅

**IMPLEMENTED** - Daily summaries will be sent automatically starting from the next midnight (00:00 PKT)!

Push the changes to Render and wait for the next midnight to receive your first automated daily summary! 📊✨


## Overview

Automatically sends a comprehensive daily solar system performance summary to all configured alert channels (Email, Telegram, Discord) every day at **12:00 AM PKT (GMT+5)**.

## Features ✨

### Automated Daily Reports
- **Timing**: Sends automatically at midnight (12:00 AM) Pakistan Time (PKT/GMT+5)
- **Frequency**: Once per day
- **Content**: Full summary of previous day's solar system performance

### Summary Includes 📋

1. **☀️ Solar Production**
   - Total energy generated in kWh

2. **⚡ Energy Usage**
   - Total energy consumed in kWh

3. **🔋 Grid Contribution**
   - Energy fed back to the grid in kWh
   - Calculated as: Production - Consumption

4. **🔌 Load Shedding**
   - Total time system ran on battery/solar (no grid)
   - Formatted as: "X hr Y min"

5. **⏸️ System Off Time**
   - Total time system was completely off
   - Breakdown:
     - Standby Mode hours
     - Missing Data hours (when API didn't respond)

## Implementation Details 🔧

### Files Modified

#### 1. `monitoring_service.py`
**Added:**
- `last_daily_summary_date`: Tracks when last summary was sent
- `pkt_timezone`: PKT timezone object for accurate time checking
- `fetch_daily_stats(date_str)`: Fetches and calculates daily statistics
- `check_and_send_daily_summary()`: Checks if it's midnight and sends summary

**Logic:**
- Runs every 5 minutes as part of periodic checks
- Checks if current time is between 00:00 and 00:05 PKT
- Ensures summary is sent only once per day
- Fetches previous day's data (since it runs at midnight)
- Sends to all three notification channels with error handling

#### 2. `email_service.py`
**Added:**
```python
def send_daily_summary(self, summary_data: dict) -> bool
```
- Formats summary data into email format
- Includes all key metrics with clear sections
- Uses Unicode characters for visual clarity

#### 3. `telegram_service.py`
**Added:**
```python
def send_daily_summary(self, summary_data: dict) -> bool
```
- Formats summary data with Telegram Markdown
- Uses bold formatting for key numbers
- Includes emojis for quick visual scanning

#### 4. `discord_service.py`
**Added:**
```python
def send_daily_summary(self, summary_data: dict) -> bool
```
- Creates rich Discord embed
- Uses inline fields for compact display
- Blue color theme (#3447003)

#### 5. `requirements.txt`
**Added:**
- `pytz==2024.1` for timezone handling

### Data Calculation Logic

The summary fetches raw data from the WatchPower API and calculates:

```python
# Energy calculations (5-minute intervals)
total_production_wh = sum(pv_power * (5/60))
total_load_wh = sum(load_power * (5/60))
grid_contribution = production - load

# Mode tracking
battery_mode_hours = count_of_battery_mode * (5/60)
standby_mode_hours = count_of_standby_mode * (5/60)

# Missing data
expected_points = 288  # (24 hours * 60 min) / 5 min
missing_points = expected_points - actual_points
missing_hours = (missing_points * 5) / 60
```

### Timezone Handling

Uses `pytz` library for accurate Pakistan timezone:
```python
self.pkt_timezone = pytz.timezone('Asia/Karachi')  # GMT+5
now_pkt = datetime.now(self.pkt_timezone)
```

### Error Handling

Each notification channel is wrapped in try-except:
```python
try:
    email_service.send_daily_summary(summary_data)
    logger.info("✅ Daily summary sent via Email")
except Exception as e:
    logger.error(f"❌ Email summary failed: {str(e)}")
```

This ensures that if one channel fails, others still send successfully.

## Sample Output 📬

### Email Format
```
Daily Solar Summary for 2024-10-08

☀️ SOLAR PRODUCTION
━━━━━━━━━━━━━━━━━━━━━━━━
Total Production: 15.45 kWh

⚡ ENERGY USAGE
━━━━━━━━━━━━━━━━━━━━━━━━
Total Consumption: 12.30 kWh

🔋 GRID CONTRIBUTION
━━━━━━━━━━━━━━━━━━━━━━━━
Energy Fed to Grid: 3.15 kWh

🔌 LOAD SHEDDING
━━━━━━━━━━━━━━━━━━━━━━━━
Battery/Solar Runtime: 4 hr 30 min

⏸️ SYSTEM OFF TIME
━━━━━━━━━━━━━━━━━━━━━━━━
Total Off Duration: 2 hr 15 min
  • Standby Mode: 1 hr 45 min
  • Missing Data: 0 hr 30 min

━━━━━━━━━━━━━━━━━━━━━━━━
Solar Dashboard - Daily Summary
Generated at 2024-10-09 00:01:23 PKT
```

### Telegram Format
Uses Markdown with **bold** for emphasis and Unicode separators.

### Discord Format
Rich embed with:
- Blue color theme
- Inline fields for production, usage, grid contribution
- Separate fields for load shedding and system off time
- Footer with generation timestamp

## Testing 🧪

### Manual Testing

Since the feature runs automatically at midnight, you can test it by:

1. **Temporarily modify the time check** for testing:
   ```python
   # In monitoring_service.py, temporarily change:
   if midnight <= current_time < five_past_midnight:
   # To:
   if True:  # Always send for testing
   ```

2. **Run the monitoring service** and wait for next 5-minute cycle

3. **Check logs** for:
   ```
   🌙 It's midnight PKT! Preparing daily summary for YYYY-MM-DD...
   📊 Sending daily summary for YYYY-MM-DD...
   ✅ Daily summary sent via Email
   ✅ Daily summary sent via Telegram
   ✅ Daily summary sent via Discord
   ```

4. **Revert the changes** after testing

### Production Testing

- Wait for midnight PKT (00:00-00:05)
- Check Render logs for summary sending
- Verify receipt in all three channels

## Monitoring 📈

### Log Messages

**Success:**
```
INFO:monitoring_service:🌙 It's midnight PKT! Preparing daily summary for 2024-10-08...
INFO:monitoring_service:📊 Sending daily summary for 2024-10-08...
INFO:monitoring_service:✅ Daily summary sent via Email
INFO:monitoring_service:✅ Daily summary sent via Telegram
INFO:monitoring_service:✅ Daily summary sent via Discord
INFO:monitoring_service:✅ Daily summary sent successfully for 2024-10-08
```

**Errors:**
```
ERROR:monitoring_service:❌ Email summary failed: [error message]
ERROR:monitoring_service:❌ Failed to fetch daily stats for 2024-10-08
```

## Configuration ⚙️

### Environment Variables

No new environment variables required! Uses existing:
- `SERIAL_NUMBER`
- `WIFI_PN`
- `DEV_CODE`
- `DEV_ADDR`
- All existing email/telegram/discord credentials

### Customization Options

To change the summary time, modify in `monitoring_service.py`:
```python
# Current: midnight to 00:05
midnight = time(0, 0)
five_past_midnight = time(0, 5)

# Example: Change to 1 AM
midnight = time(1, 0)
five_past_midnight = time(1, 5)
```

## Integration with Existing Features ✅

### Does NOT Affect:
- ✅ System reset detection (hourly reminders)
- ✅ Load shedding alerts (5-hour reminders)
- ✅ Grid feed disabled alerts (hourly reminders)
- ✅ System offline alerts
- ✅ Low production alerts
- ✅ All existing API endpoints
- ✅ Frontend functionality

### How It Works:
- Runs as part of the existing 5-minute periodic check loop
- Only sends between 00:00-00:05 PKT
- Uses same notification services as other alerts
- Fetches data using existing API manager
- No impact on other monitoring features

## Benefits 🌟

1. **Automatic**: No manual work required
2. **Comprehensive**: All key metrics in one place
3. **Multi-channel**: Email, Telegram, and Discord
4. **Reliable**: Error handling ensures partial failures don't stop the service
5. **Timezone-aware**: Accurate to Pakistan time
6. **Non-intrusive**: Runs once per day at midnight
7. **Data-rich**: Includes production, consumption, grid feed, load shedding, and system status

## Troubleshooting 🔧

### Summary not received?

1. **Check Render logs** around midnight PKT
2. **Verify timezone**: Ensure system time is correct
3. **Check API connectivity**: Ensure WatchPower API is accessible
4. **Verify credentials**: Ensure Email/Telegram/Discord are configured

### Duplicate summaries?

- Should not happen due to `last_daily_summary_date` tracking
- If occurs, check Render logs for restarts around midnight

### Missing data in summary?

- Check if WatchPower API had data for that day
- Verify SERIAL_NUMBER, WIFI_PN, DEV_CODE, DEV_ADDR are correct
- Check logs for "Failed to fetch daily stats" errors

## Status ✅

**IMPLEMENTED** - Daily summaries will be sent automatically starting from the next midnight (00:00 PKT)!

Push the changes to Render and wait for the next midnight to receive your first automated daily summary! 📊✨

