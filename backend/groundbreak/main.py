from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from .adapters import adapt_a, adapt_b, adapt_c
from .storage import init_db, save_telemetry, get_history
from .rules import evaluate
from .broadcast import broadcaster
from .geofence import apply_geofence

app = FastAPI(title="Groundbreak")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup():
    init_db()


async def _ingest(canonical):
    canonical = apply_geofence(canonical)
    save_telemetry(canonical)
    alerts = evaluate(canonical)
    await broadcaster.push({
        "telemetry": canonical.model_dump(mode="json"),
        "alerts": [a.model_dump() for a in alerts],
    })
    return {"ok": True}


@app.post("/ingest/a")
async def ingest_a(payload: dict):
    return await _ingest(adapt_a(payload))


@app.post("/ingest/b")
async def ingest_b(payload: dict):
    return await _ingest(adapt_b(payload))


@app.post("/ingest/c")
async def ingest_c(payload: dict):
    return await _ingest(adapt_c(payload))


@app.get("/vehicles/{vehicle_id}/history")
def history(vehicle_id: str, limit: int = 60):
    return get_history(vehicle_id, limit)


@app.websocket("/live")
async def live(ws: WebSocket):
    await broadcaster.connect(ws)
    try:
        while True:
            await ws.receive_text()
    except WebSocketDisconnect:
        await broadcaster.disconnect(ws)