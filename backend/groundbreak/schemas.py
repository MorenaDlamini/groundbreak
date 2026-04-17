from pydantic import BaseModel
from typing import Literal
from datetime import datetime

VehicleType = Literal["haul_truck", "loader", "drill_rig", "service"]
VehicleState = Literal["moving", "idle", "loading", "dumping", "offline"]

class Position(BaseModel):
    x: float
    y: float

class Telemetry(BaseModel):
    """Canonical schema — everything normalizes to this."""
    vehicle_id: str
    vehicle_type: VehicleType
    timestamp: datetime
    position: Position
    engine_temp_c: float
    fuel_pct: float
    engine_hours: int
    state: VehicleState
    source_vendor: Literal["A", "B", "C"]