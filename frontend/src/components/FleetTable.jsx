import { STATE_COLORS } from "../lib/state-colors";

export default function FleetTable({ fleet, selectedId, onSelect }) {
  const vehicles = Object.values(fleet);

  return (
    <div className="border-t border-gray-800 overflow-x-auto">
      <table className="w-full text-xs">
        <thead>
          <tr className="text-gray-500 bg-gray-900">
            {[
              "ID",
              "Type",
              "State",
              "Fuel %",
              "Temp °C",
              "Vendor",
              "Hours",
            ].map((h) => (
              <th key={h} className="px-4 py-2 text-left font-medium">
                {h}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {vehicles.map((v) => (
            <tr
              key={v.vehicle_id}
              onClick={() => onSelect(v.vehicle_id)}
              className={`border-t border-gray-800 cursor-pointer hover:bg-gray-800 transition-colors ${
                v.vehicle_id === selectedId ? "bg-gray-800" : ""
              }`}
            >
              <td className="px-4 py-2 font-mono">{v.vehicle_id}</td>
              <td className="px-4 py-2 capitalize">
                {v.vehicle_type?.replace("_", " ")}
              </td>
              <td className="px-4 py-2">
                <span
                  className="inline-block w-2 h-2 rounded-full mr-2"
                  style={{ background: STATE_COLORS[v.state] }}
                />
                {v.state}
              </td>
              <td className="px-4 py-2">{v.fuel_pct?.toFixed(0)}</td>
              <td
                className={`px-4 py-2 ${v.engine_temp_c > 100 ? "text-red-400" : ""}`}
              >
                {v.engine_temp_c?.toFixed(1)}
              </td>
              <td className="px-4 py-2">{v.source_vendor}</td>
              <td className="px-4 py-2 tabular-nums">
                {v.engine_hours?.toLocaleString()}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
