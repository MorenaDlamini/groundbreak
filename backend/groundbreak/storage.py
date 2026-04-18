import sqlite3
from pathlib import Path
from .schemas import Telemetry

DB_PATH = Path(__file__).parent.parent / "groundbreak.db"


def _conn():
    return sqlite3.connect(DB_PATH)


def init_db():
    with _conn() as con:
        con.executescript("""
            CREATE TABLE IF NOT EXISTS telemetry (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                vehicle_id TEXT NOT NULL,
                vehicle_type TEXT,
                timestamp TEXT NOT NULL,
                pos_x REAL, pos_y REAL,
                engine_temp_c REAL,
                fuel_pct REAL,
                engine_hours INTEGER,
                state TEXT,
                source_vendor TEXT
            );
            CREATE INDEX IF NOT EXISTS idx_vehicle_time ON telemetry (vehicle_id, timestamp);
            CREATE TABLE IF NOT EXISTS alerts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                rule TEXT NOT NULL,
                severity TEXT NOT NULL,
                message TEXT,
                vehicle_id TEXT NOT NULL,
                timestamp TEXT NOT NULL
            );
        """)


def save_telemetry(t: Telemetry):
    with _conn() as con:
        con.execute(
            """INSERT INTO telemetry
               (vehicle_id, vehicle_type, timestamp, pos_x, pos_y,
                engine_temp_c, fuel_pct, engine_hours, state, source_vendor)
               VALUES (?,?,?,?,?,?,?,?,?,?)""",
            (t.vehicle_id, t.vehicle_type, t.timestamp.isoformat(),
             t.position.x, t.position.y, t.engine_temp_c, t.fuel_pct,
             t.engine_hours, t.state, t.source_vendor),
        )


def get_history(vehicle_id: str, limit: int = 60) -> list[dict]:
    with _conn() as con:
        con.row_factory = sqlite3.Row
        rows = con.execute(
            """SELECT * FROM telemetry WHERE vehicle_id=?
               ORDER BY timestamp DESC LIMIT ?""",
            (vehicle_id, limit),
        ).fetchall()
    return [dict(r) for r in rows]
