import { useEffect, useState } from "react";
import { LineChart, Line, ResponsiveContainer } from "recharts";

const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

export default function VehicleDetail({ vehicle: v, onClose }) {
  const [history, setHistory] = useState([]);

  useEffect(() => {
    if (!v) return;
    fetch(`${API_URL}/vehicles/${v.vehicle_id}/history`)
      .then((r) => r.json())
      .then(setHistory)
      .catch(() => {});
  }, [v?.vehicle_id]);

  if (!v) return null;

  return (
    <div className="bg-gray-900 border border-gray-800 rounded-lg p-3 text-sm">
      <div className="flex justify-between items-start mb-3">
        <div>
          <div className="font-semibold">{v.vehicle_id}</div>
          <div className="text-xs text-gray-500">
            {v.vehicle_type} · Vendor {v.source_vendor}
          </div>
        </div>
        <button onClick={onClose} className="text-gray-500 hover:text-white">
          ✕
        </button>
      </div>

      <div className="space-y-2">
        <div className="flex justify-between">
          <span className="text-gray-400">State</span>
          <span className="capitalize">{v.state}</span>
        </div>
        <div>
          <div className="flex justify-between mb-1">
            <span className="text-gray-400">Fuel</span>
            <span>{v.fuel_pct?.toFixed(0)}%</span>
          </div>
          <div className="w-full bg-gray-700 rounded-full h-1.5">
            <div
              className="bg-green-500 h-1.5 rounded-full"
              style={{ width: `${v.fuel_pct}%` }}
            />
          </div>
        </div>
        <div className="flex justify-between">
          <span className="text-gray-400">Engine Temp</span>
          <span className={v.engine_temp_c > 100 ? "text-red-400" : ""}>
            {v.engine_temp_c?.toFixed(1)} °C
          </span>
        </div>

        {history.length > 1 && (
          <div className="pt-2">
            <div className="text-xs text-gray-500 mb-1">Temp (last 60)</div>
            <ResponsiveContainer width="100%" height={40}>
              <LineChart data={history}>
                <Line
                  type="monotone"
                  dataKey="engine_temp_c"
                  stroke="#f97316"
                  dot={false}
                  strokeWidth={1.5}
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
        )}
      </div>
    </div>
  );
}
