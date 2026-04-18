import { useState } from "react";
import { useTelemetry } from "./hooks/useTelemetry";
import MineMap from "./components/MineMap";
import KpiCards from "./components/KpiCards";
import AlertFeed from "./components/AlertFeed";
import VehicleDetail from "./components/VehicleDetail";
import FleetTable from "./components/FleetTable";

const WS_URL = import.meta.env.VITE_WS_URL || "ws://localhost:8000/live";

export default function App() {
  const { fleet, alerts } = useTelemetry(WS_URL);
  const [selectedId, setSelectedId] = useState(null);

  const vehicles = Object.values(fleet);

  return (
    <div className="min-h-screen bg-gray-950 text-gray-100 flex flex-col">
      <header className="px-6 py-3 border-b border-gray-800 flex items-center gap-4">
        <h1 className="text-xl font-semibold tracking-tight">Groundbreak</h1>
        <span className="text-sm text-gray-400">
          {vehicles.filter((v) => v.state !== "offline").length} active vehicles
        </span>
      </header>

      <div className="flex flex-1 overflow-hidden">
        {/* Left: map */}
        <div className="flex-1 p-4">
          <MineMap
            fleet={fleet}
            selectedId={selectedId}
            onSelect={setSelectedId}
          />
        </div>

        {/* Right: panels */}
        <div className="w-80 flex flex-col gap-4 p-4 border-l border-gray-800 overflow-y-auto">
          <KpiCards fleet={fleet} alerts={alerts} />
          <AlertFeed alerts={alerts} />
          {selectedId && (
            <VehicleDetail
              vehicle={fleet[selectedId]}
              onClose={() => setSelectedId(null)}
            />
          )}
        </div>
      </div>

      <FleetTable
        fleet={fleet}
        selectedId={selectedId}
        onSelect={setSelectedId}
      />
    </div>
  );
}
