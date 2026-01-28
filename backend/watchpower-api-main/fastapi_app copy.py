from dotenv import load_dotenv
from fastapi import FastAPI, Query
import os 
from fastapi.middleware.cors import CORSMiddleware
import datetime
from watchpower_api import WatchPowerAPI
from typing import List
# Load env variables
load_dotenv()
from fastapi.responses import StreamingResponse
import json

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

print(USERNAMES, PASSWORD, SERIAL_NUMBER, WIFI_PN, DEV_CODE, DEV_ADDR)

app = FastAPI()

 
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
    allow_origins=allowed_origins,  # multiple domains here
    allow_methods=["*"],
    allow_headers=["*"],
)
# WatchPower API instance
wp = WatchPowerAPI()
wp.login(USERNAMES, PASSWORD)  # mandatory login


@app.get("/daily-data")
def get_daily_data():
    try:
        today = datetime.date.today()
        data = wp.get_daily_data(
            day=today,
            serial_number=SERIAL_NUMBER,
            wifi_pn=WIFI_PN,
            dev_code=DEV_CODE,
            dev_addr=DEV_ADDR
        )
        return {"success": True, "data": data}
    except Exception as e:
        return {"success": False, "error": str(e)}
# 👇 New endpoint to fetch device info
@app.get("/devices")
def get_devices():
    try:
        devices = wp.get_devices()
        return {"success": True, "devices": devices}
    except Exception as e:
        return {"success": False, "error": str(e)}


@app.get("/today-total")
def today_total():
    try:
        today = datetime.date.today().strftime("%Y-%m-%d")

        data = wp.get_daily_data(
            day=datetime.date.today(),
            serial_number=SERIAL_NUMBER,
            wifi_pn=WIFI_PN,
            dev_code=DEV_CODE,
            dev_addr=DEV_ADDR
        )

        # filter today's records
        today_records = [rec for rec in data.get("records", []) if rec.get("date") == today]

        # calculate total production (replace "production" with actual key name in JSON)
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
def today_stats():
    try:
        data = wp.get_daily_data(
            day=datetime.date.today(),
            serial_number=SERIAL_NUMBER,
            wifi_pn=WIFI_PN,
            dev_code=DEV_CODE,
            dev_addr=DEV_ADDR
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
def raw_data():
    """Return raw WatchPower API daily data for today"""
    try:
        data = wp.get_daily_data(
            day=datetime.date.today(),
            serial_number=SERIAL_NUMBER,
            wifi_pn=WIFI_PN,
            dev_code=DEV_CODE,
            dev_addr=DEV_ADDR
        )
        return data
    except Exception as e:
        return {"error": str(e)}

def process_data(data: dict, date: str):
    """Convert API raw data into graph format + totals"""
    graph = []
    pv_sum = 0
    load_sum = 0
    interval_hours = 5 / 60  # assume 5min interval = 0.083hr

    for rec in data.get("records", []):
        fields = rec.get("field", [])
        if len(fields) < 22:
            continue

        timestamp = fields[1]
        pv_power = float(fields[11]) if fields[11] not in ["", None] else 0
        load_power = float(fields[21]) if fields[21] not in ["", None] else 0

        # Filter same-day only
        if timestamp.startswith(date):
            graph.append({
                "time": timestamp.split(" ")[1],  # hh:mm:ss
                "pv_power": pv_power,
                "load_power": load_power,
            })
            pv_sum += pv_power * interval_hours
            load_sum += load_power * interval_hours

    return {
        "success": True,
        "date": date,
        "total_production_kwh": round(pv_sum / 1000, 2),
        "total_load_kwh": round(load_sum / 1000, 2),
        "graph": graph,
    }

 

@app.get("/stats")
def get_stats(date: str = Query(default=datetime.date.today().strftime("%Y-%m-%d"))):
    """
    Get solar stats for a given date (default = today).
    Example:
      /stats                → today
      /stats?date=2025-09-10 → specific date
    """
    try:
        day = datetime.datetime.strptime(date, "%Y-%m-%d").date()

        data = wp.get_daily_data(
            day=day,
            serial_number=SERIAL_NUMBER,
            wifi_pn=WIFI_PN,
            dev_code=DEV_CODE,
            dev_addr=DEV_ADDR
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
def stats_range(from_date: str = Query(...), to_date: str = Query(...)):

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
                    data = wp.get_daily_data(
                        day=current,
                        serial_number=SERIAL_NUMBER,
                        wifi_pn=WIFI_PN,
                        dev_code=DEV_CODE,
                        dev_addr=DEV_ADDR
                    )

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
