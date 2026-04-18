"""
Run with: python -m groundbreak.simulator
Env vars: INGEST_URL (default http://localhost:8000)
"""
import asyncio
import random
import os
import math
from datetime import datetime, timezone
import httpx

INGEST_URL = os.getenv("INGEST_URL", "http://localhost:8000")

# Zone centre coordinates (x, y) in the 400×400 SVG coordinate space
WAYPOINTS = {
    "loading_bay_a": (115, 59),
    "loading_bay_b": (182, 57),
    "dump":          (300, 348),
    "workshop":      (35, 210),
    "pit_centre":    (200, 200),
}

VEHICLES = [
    {"id": "HT-204", "vendor": "A", "route": ["loading_bay_a", "dump"], "progress": 0.0,
     "speed": 0.04, "fuel": 80, "temp": 75, "hours": 8421, "state": "moving"},
    {"id": "HT-205", "vendor": "A", "route": ["loading_bay_b", "dump"], "progress": 0.5,
     "speed": 0.035, "fuel": 60, "temp": 73, "hours": 6102, "state": "moving"},
    {"id": "HT-206", "vendor": "A", "route": ["dump", "loading_bay_a"], "progress": 0.2,
     "speed": 0.045, "fuel": 90, "temp": 71, "hours": 3300, "state": "moving"},
    {"id": "LD-101", "vendor": "B", "route": ["loading_bay_a", "pit_centre"], "progress": 0.0,
     "speed": 0.02, "fuel": 78, "temp": 68, "hours": 5104, "state": "loading"},
    {"id": "LD-102", "vendor": "B", "route": ["loading_bay_b", "pit_centre"], "progress": 0.6,
     "speed": 0.025, "fuel": 45, "temp": 70, "hours": 4800, "state": "moving"},
    {"id": "DR-301", "vendor": "C", "route": ["pit_centre", "workshop"], "progress": 0.0,
     "speed": 0.01, "fuel": 55, "temp": 68, "hours": 11240, "state": "idle"},
    {"id": "DR-302", "vendor": "C", "route": ["pit_centre", "loading_bay_a"], "progress": 0.3,
     "speed": 0.012, "fuel": 72, "temp": 66, "hours": 9870, "state": "moving"},
    {"id": "SV-401", "vendor": "A", "route": ["workshop", "loading_bay_a"], "progress": 0.1,
     "speed": 0.03, "fuel": 95, "temp": 62, "hours": 1200, "state": "moving"},
]

def step_vehicle(v: dict):
    if v["state"] in ("moving", "loading", "dumping"):
        v["progress"] += v["speed"]
        if v["progress"] >= 1.0:
            v["progress"] = 0.0
            v["route"].append(v["route"].pop(0))
        a = WAYPOINTS[v["route"][0]]
        b = WAYPOINTS[v["route"][1]]
        v["pos"] = (
            a[0] + (b[0] - a[0]) * v["progress"],
            a[1] + (b[1] - a[1]) * v["progress"],
        )
        v["fuel"] = max(0, v["fuel"] - 0.05)
    else:
        v["pos"] = WAYPOINTS[v["route"][0]]

    v["temp"] += random.gauss(0, 0.3)
    v["temp"] = max(50, v["temp"])

    # Occasional anomaly injection
    if random.random() < 0.01:
        v["temp"] += random.uniform(20, 35)
    if random.random() < 0.005:
        v["fuel"] = max(0, v["fuel"] - random.uniform(10, 20))

def build_payload_a(v: dict) -> dict:
    state_map = {"moving": "HAULING", "idle": "IDLE", "loading": "LOADING",
                 "dumping": "DUMPING", "offline": "OFFLINE"}
    return {
        "machineId": v["id"],
        "ts": datetime.now(tz=timezone.utc).isoformat(),
        "posX": round(v["pos"][0], 1),
        "posY": round(v["pos"][1], 1),
        "engineTempC": round(v["temp"], 1),
        "fuelPct": round(v["fuel"], 1),
        "engineHours": v["hours"],
        "status": state_map.get(v["state"], "IDLE"),
    }

def build_payload_b(v: dict) -> dict:
    kind_map = {"haul_truck": "haul_truck", "loader": "wheel_loader",
                "drill_rig": "drill_rig", "service": "service"}
    prefix = v["id"].split("-")[0]
    prefix_to_kind = {"HT": "haul_truck", "LD": "wheel_loader", "DR": "drill_rig", "SV": "service"}
    temp_f = v["temp"] * 9 / 5 + 32
    import time
    return {
        "asset": {"id": v["id"], "kind": prefix_to_kind[prefix]},
        "telemetry": {
            "timestamp": int(time.time()),
            "location": {"x": round(v["pos"][0], 1), "y": round(v["pos"][1], 1)},
            "engine": {"temp_f": round(temp_f, 1), "hours": v["hours"]},
            "fuel": {"level_pct": round(v["fuel"], 1)},
        },
        "mode": v["state"],
    }

def build_payload_c(v: dict) -> dict:
    return {
        "eq_id": v["id"],
        "time": datetime.now(tz=timezone.utc).strftime("%Y-%m-%d %H:%M:%S"),
        "pos_x": round(v["pos"][0], 1),
        "pos_y": round(v["pos"][1], 1),
        "eng_temp": round(v["temp"], 1),
        "fuel_remaining": round(v["fuel"] / 100, 4),
        "run_time_hrs": v["hours"],
        "op_state": v["state"],
    }

async def run():
    # Initialise positions
    for v in VEHICLES:
        v["pos"] = WAYPOINTS[v["route"][0]]

    async with httpx.AsyncClient(timeout=5) as client:
        while True:
            for v in VEHICLES:
                step_vehicle(v)
                v["hours"] += 0
                try:
                    if v["vendor"] == "A":
                        await client.post(f"{INGEST_URL}/ingest/a", json=build_payload_a(v))
                    elif v["vendor"] == "B":
                        await client.post(f"{INGEST_URL}/ingest/b", json=build_payload_b(v))
                    elif v["vendor"] == "C":
                        await client.post(f"{INGEST_URL}/ingest/c", json=build_payload_c(v))
                except Exception as e:
                    print(f"[sim] failed to post {v['id']}: {e}")

            await asyncio.sleep(random.uniform(1.0, 2.0))


if __name__ == "__main__":
    asyncio.run(run())