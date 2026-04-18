import { STATE_COLORS } from "../lib/state-colors";
import { ZONES } from "../lib/zones";

const TYPE_ICONS = {
  haul_truck: "▲",
  loader: "■",
  drill_rig: "◆",
  service: "●",
};

export default function MineMap({ fleet, selectedId, onSelect }) {
  const vehicles = Object.values(fleet);

  return (
    <svg
      viewBox="0 0 400 400"
      className="w-full h-full rounded-lg border border-gray-800 bg-gray-900"
      style={{ maxHeight: "calc(100vh - 120px)" }}
    >
      {/* Pit rings */}
      {[160, 120, 80, 40].map((rx, i) => (
        <ellipse
          key={i}
          cx={200}
          cy={200}
          rx={rx}
          ry={rx * 0.6}
          fill="none"
          stroke="#374151"
          strokeWidth={1}
        />
      ))}

      {/* Zones */}
      {ZONES.map((z) => (
        <g key={z.name}>
          <rect
            x={z.rect.x}
            y={z.rect.y}
            width={z.rect.w}
            height={z.rect.h}
            fill="#1f2937"
            stroke="#4b5563"
            strokeWidth={1}
            rx={3}
          />
          <text
            x={z.rect.x + z.rect.w / 2}
            y={z.rect.y + z.rect.h / 2 + 4}
            textAnchor="middle"
            fontSize={8}
            fill="#9ca3af"
          >
            {z.name}
          </text>
        </g>
      ))}

      {/* Vehicles */}
      {vehicles.map((v) => {
        const x = v.position?.x ?? 0;
        const y = v.position?.y ?? 0;
        const color = STATE_COLORS[v.state] ?? "#6b7280";
        const isSelected = v.vehicle_id === selectedId;

        return (
          <g
            key={v.vehicle_id}
            transform={`translate(${x}, ${y})`}
            style={{ transition: "transform 1.2s linear", cursor: "pointer" }}
            onClick={() => onSelect(v.vehicle_id)}
          >
            {isSelected && (
              <circle
                r={12}
                fill="none"
                stroke="white"
                strokeWidth={1.5}
                opacity={0.6}
              />
            )}
            <circle r={7} fill={color} opacity={0.9} />
            <text
              textAnchor="middle"
              fontSize={7}
              y={3}
              fill="white"
              style={{ pointerEvents: "none", userSelect: "none" }}
            >
              {TYPE_ICONS[v.vehicle_type] ?? "?"}
            </text>
            <text
              textAnchor="middle"
              fontSize={6}
              y={18}
              fill="#d1d5db"
              style={{ pointerEvents: "none", userSelect: "none" }}
            >
              {v.vehicle_id}
            </text>
          </g>
        );
      })}
    </svg>
  );
}
