@echo off
echo Creating .env.local file...
echo.

(
echo # WatchPower API Credentials
echo USERNAMES=Ahmarjb
echo PASSWORD=Ahmar123
echo SERIAL_NUMBER=96342404600319
echo WIFI_PN=W0034053928283
echo DEV_CODE=2488
echo DEV_ADDR=1
echo.
echo # Email Configuration
echo EMAIL_USER=chbitug@gmail.com
echo EMAIL_PASSWORD=qbmkptoyswqofrel
echo ALERT_EMAIL=chbitug@gmail.com
echo EMAIL_HOST=smtp.gmail.com
echo EMAIL_PORT=587
echo.
echo # Telegram Configuration
echo TELEGRAM_BOT_TOKEN=6762994932:AAFUdwfusQyQ5ZpOOp3CDEIL2cY4kt-UpjM
echo TELEGRAM_CHAT_ID=5677544633
echo.
echo # Discord Configuration
echo DISCORD_WEBHOOK_URL=https://discordapp.com/api/webhooks/1425686982838714500/mGBwR_cxPi_ql2FETq3-xTg9By0etPsSDYurSv1vtzwjge1OWahWMsW_meeBieVKuTnK
echo.
echo # Cron Job Security
echo CRON_SECRET=solar-monitoring-secret-key-12345
echo.
echo # Alert Configuration
echo GRID_FEED_ALERT_INTERVAL_HOURS=1
echo LOAD_SHEDDING_VOLTAGE_THRESHOLD=180
echo SYSTEM_OFFLINE_THRESHOLD_MINUTES=10
echo LOW_PRODUCTION_THRESHOLD_WATTS=500
) > .env.local

echo .env.local file created successfully!
echo.
echo You can now run: npm run dev
pause

echo Creating .env.local file...
echo.

(
echo # WatchPower API Credentials
echo USERNAMES=Ahmarjb
echo PASSWORD=Ahmar123
echo SERIAL_NUMBER=96342404600319
echo WIFI_PN=W0034053928283
echo DEV_CODE=2488
echo DEV_ADDR=1
echo.
echo # Email Configuration
echo EMAIL_USER=chbitug@gmail.com
echo EMAIL_PASSWORD=qbmkptoyswqofrel
echo ALERT_EMAIL=chbitug@gmail.com
echo EMAIL_HOST=smtp.gmail.com
echo EMAIL_PORT=587
echo.
echo # Telegram Configuration
echo TELEGRAM_BOT_TOKEN=6762994932:AAFUdwfusQyQ5ZpOOp3CDEIL2cY4kt-UpjM
echo TELEGRAM_CHAT_ID=5677544633
echo.
echo # Discord Configuration
echo DISCORD_WEBHOOK_URL=https://discordapp.com/api/webhooks/1425686982838714500/mGBwR_cxPi_ql2FETq3-xTg9By0etPsSDYurSv1vtzwjge1OWahWMsW_meeBieVKuTnK
echo.
echo # Cron Job Security
echo CRON_SECRET=solar-monitoring-secret-key-12345
echo.
echo # Alert Configuration
echo GRID_FEED_ALERT_INTERVAL_HOURS=1
echo LOAD_SHEDDING_VOLTAGE_THRESHOLD=180
echo SYSTEM_OFFLINE_THRESHOLD_MINUTES=10
echo LOW_PRODUCTION_THRESHOLD_WATTS=500
) > .env.local

echo .env.local file created successfully!
echo.
echo You can now run: npm run dev
pause

