import pytest
from groundbreak.adapters import adapt_a, adapt_b, adapt_c

PAYLOAD_A = {
    "machineId": "HT-204", "ts": "2026-04-17T10:23:15Z",
    "posX": 115, "posY": 60, "engineTempC": 78,
    "fuelPct": 64, "engineHours": 8421, "status": "HAULING",
}

PAYLOAD_B = {
    "asset": {"id": "LD-101", "kind": "wheel_loader"},
    "telemetry": {
        "timestamp": 1713348195,
        "location": {"x": 182.4, "y": 56.7},
        "engine": {"temp_f": 161, "hours": 5104},
        "fuel": {"level_pct": 78},
    },
    "mode": "loading",
}

PAYLOAD_C = {
    "eq_id": "DR-301", "time": "2026-04-17 10:23:15",
    "pos_x": 220, "pos_y": 200, "eng_temp": 68,
    "fuel_remaining": 0.55, "run_time_hrs": 11240, "op_state": "idle",
}

def test_adapt_a_basic():
    t = adapt_a(PAYLOAD_A)
    assert t.vehicle_id == "HT-204"
    assert t.vehicle_type == "haul_truck"
    assert t.state == "moving"
    assert t.source_vendor == "A"
    assert t.engine_temp_c == 78
    assert t.fuel_pct == 64


def test_adapt_b_fahrenheit_conversion():
    t = adapt_b(PAYLOAD_B)
    assert t.vehicle_id == "LD-101"
    assert t.vehicle_type == "loader"
    assert t.state == "loading"
    assert t.source_vendor == "B"
    assert abs(t.engine_temp_c - 71.7) < 0.2  # 161°F → ~71.7°C

def test_adapt_c_decimal_fuel():
    t = adapt_c(PAYLOAD_C)
    assert t.vehicle_id == "DR-301"
    assert t.vehicle_type == "drill_rig"
    assert t.state == "idle"
    assert t.source_vendor == "C"
    assert abs(t.fuel_pct - 55.0) < 0.01  # 0.55 → 55%


def test_adapt_a_state_mapping():
    for status, expected in [("HAULING", "moving"), ("IDLE", "idle"),
                              ("LOADING", "loading"), ("DUMPING", "dumping"),
                              ("OFFLINE", "offline")]:
        t = adapt_a({**PAYLOAD_A, "status": status})
        assert t.state == expected


def test_adapt_a_vehicle_type_prefix():
    for prefix, vtype in [("HT", "haul_truck"), ("LD", "loader"),
                           ("DR", "drill_rig"), ("SV", "service")]:
        t = adapt_a({**PAYLOAD_A, "machineId": f"{prefix}-001"})
        assert t.vehicle_type == vtype