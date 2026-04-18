from .schemas import Telemetry

ZONES = [
    {"name": "loading_bay_a", "polygon": [(70,40),(160,40),(160,78),(70,78)], "derived_state": "loading"},
    {"name": "dump",          "polygon": [(250,330),(350,330),(350,366),(250,366)], "derived_state": "dumping"},
    {"name": "workshop",      "polygon": [(10,180),(60,180),(60,240),(10,240)], "derived_state": "idle"},
]


def _point_in_polygon(px: float, py: float, polygon: list[tuple]) -> bool:
    inside = False
    n = len(polygon)
    j = n - 1
    for i in range(n):
        xi, yi = polygon[i]
        xj, yj = polygon[j]
        if ((yi > py) != (yj > py)) and (px < (xj - xi) * (py - yi) / (yj - yi) + xi):
            inside = not inside
        j = i
    return inside


def apply_geofence(t: Telemetry) -> Telemetry:
    for zone in ZONES:
        if _point_in_polygon(t.position.x, t.position.y, zone["polygon"]):
            return t.model_copy(update={"state": zone["derived_state"]})
    return t
