from datetime import datetime, timezone
from .schemas import Telemetry, Position

_TYPE_PREFIX = {"HT": "haul_truck", "LD": "loader", "DR": "drill_rig", "SV": "service"}

_A_STATE = {
    "HAULING": "moving", "IDLE": "idle", "LOADING": "loading",
    "DUMPING": "dumping", "OFFLINE": "offline",
}
_B_MODE = {
    "moving": "moving", "idle": "idle", "loading": "loading",
    "dumping": "dumping", "offline": "offline",
}
_B_KIND = {
    "haul_truck": "haul_truck", "wheel_loader": "loader",
    "drill_rig": "drill_rig", "service": "service",
}
_C_STATE = {
    "moving": "moving", "idle": "idle", "loading": "loading",
    "dumping": "dumping", "offline": "offline",
}

def adapt_a(raw: dict) -> Telemetry:
    prefix = raw["machineId"].split("-")[0]
    return Telemetry(
        vehicle_id=raw["machineId"],
        vehicle_type=_TYPE_PREFIX[prefix],
        timestamp=raw["ts"],
        position=Position(x=raw["posX"], y=raw["posY"]),
        engine_temp_c=raw["engineTempC"],
        fuel_pct=raw["fuelPct"],
        engine_hours=raw["engineHours"],
        state=_A_STATE[raw["status"]],
        source_vendor="A",
    )

def adapt_b(raw: dict) -> Telemetry:
    asset = raw["asset"]
    telem = raw["telemetry"]
    temp_c = (telem["engine"]["temp_f"] - 32) * 5 / 9
    ts = datetime.fromtimestamp(telem["timestamp"], tz=timezone.utc)
    return Telemetry(
        vehicle_id=asset["id"],
        vehicle_type=_B_KIND[asset["kind"]],
        timestamp=ts,
        position=Position(x=telem["location"]["x"], y=telem["location"]["y"]),
        engine_temp_c=round(temp_c, 1),
        fuel_pct=telem["fuel"]["level_pct"],
        engine_hours=telem["engine"]["hours"],
        state=_B_MODE[raw["mode"]],
        source_vendor="B",
    )

def adapt_c(raw: dict) -> Telemetry:
    prefix = raw["eq_id"].split("-")[0]
    ts = datetime.strptime(raw["time"], "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc)
    return Telemetry(
        vehicle_id=raw["eq_id"],
        vehicle_type=_TYPE_PREFIX[prefix],
        timestamp=ts,
        position=Position(x=raw["pos_x"], y=raw["pos_y"]),
        engine_temp_c=raw["eng_temp"],
        fuel_pct=raw["fuel_remaining"] * 100,
        engine_hours=raw["run_time_hrs"],
        state=_C_STATE[raw["op_state"]],
        source_vendor="C",
    )