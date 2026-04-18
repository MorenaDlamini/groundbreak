from datetime import datetime, timezone
from .schemas import Telemetry, Alert

_last_fired: dict[tuple, datetime] = {}
_DEDUP_SECONDS = 300

_RULES = [
    {
        "name": "engine_overheat",
        "severity": "danger",
        "check": lambda t: t.engine_temp_c > 100,
        "message": lambda t: f"{t.vehicle_id} — engine overheat ({t.engine_temp_c:.0f} °C)",
    },
    {
        "name": "low_fuel",
        "severity": "warning",
        "check": lambda t: t.fuel_pct < 20,
        "message": lambda t: f"{t.vehicle_id} — low fuel ({t.fuel_pct:.0f}%)",
    },
]

_idle_counts: dict[str, int] = {}


def evaluate(t: Telemetry) -> list[Alert]:
    now = datetime.now(timezone.utc)
    alerts: list[Alert] = []

    if t.state == "idle":
        _idle_counts[t.vehicle_id] = _idle_counts.get(t.vehicle_id, 0) + 1
    else:
        _idle_counts[t.vehicle_id] = 0

    candidates = list(_RULES)
    if _idle_counts.get(t.vehicle_id, 0) > 10:
        candidates.append({
            "name": "idle_timeout",
            "severity": "warning",
            "check": lambda _: True,
            "message": lambda t: f"{t.vehicle_id} — idle for {_idle_counts[t.vehicle_id]} readings",
        })

    for rule in candidates:
        if not rule["check"](t):
            continue
        key = (t.vehicle_id, rule["name"])
        last = _last_fired.get(key)
        if last and (now - last).total_seconds() < _DEDUP_SECONDS:
            continue
        _last_fired[key] = now
        alerts.append(Alert(
            rule=rule["name"],
            severity=rule["severity"],
            message=rule["message"](t),
            vehicle_id=t.vehicle_id,
            timestamp=now.isoformat(),
        ))

    return alerts
