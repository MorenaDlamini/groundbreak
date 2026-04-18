export default function KpiCards({ fleet, alerts }) {
  const vehicles = Object.values(fleet);
  const total = vehicles.length;
  const active = vehicles.filter((v) => v.state !== "offline").length;
  const utilized = vehicles.filter(
    (v) => v.state === "moving" || v.state === "loading",
  ).length;
  const utilization = total > 0 ? Math.round((utilized / total) * 100) : 0;
  const avgFuel =
    total > 0
      ? Math.round(vehicles.reduce((s, v) => s + v.fuel_pct, 0) / total)
      : 0;

  const cards = [
    { label: "Active", value: `${active}/${total}` },
    { label: "Utilization", value: `${utilization}%` },
    { label: "Avg Fuel", value: `${avgFuel}%` },
    { label: "Alerts", value: alerts.length },
  ];

  return (
    <div className="grid grid-cols-2 gap-2">
      {cards.map((c) => (
        <div
          key={c.label}
          className="bg-gray-900 border border-gray-800 rounded-lg p-3"
        >
          <div className="text-xs text-gray-500 mb-1">{c.label}</div>
          <div className="text-2xl font-semibold tabular-nums">{c.value}</div>
        </div>
      ))}
    </div>
  );
}
