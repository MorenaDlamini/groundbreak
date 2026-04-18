const SEVERITY_STYLES = {
  danger: "bg-red-900/50 text-red-300 border-red-700",
  warning: "bg-yellow-900/50 text-yellow-300 border-yellow-700",
  anomaly: "bg-purple-900/50 text-purple-300 border-purple-700",
};

function relativeTime(iso) {
  const diff = Math.floor((Date.now() - new Date(iso)) / 1000);
  if (diff < 60) return `${diff}s ago`;
  if (diff < 3600) return `${Math.floor(diff / 60)}m ago`;
  return `${Math.floor(diff / 3600)}h ago`;
}

export default function AlertFeed({ alerts }) {
  if (!alerts.length)
    return (
      <div className="bg-gray-900 border border-gray-800 rounded-lg p-3 text-sm text-gray-500">
        No alerts
      </div>
    );

  return (
    <div className="bg-gray-900 border border-gray-800 rounded-lg p-3 space-y-2 max-h-48 overflow-y-auto">
      <div className="text-xs text-gray-500 mb-2 font-medium">ALERTS</div>
      {alerts.map((a, i) => (
        <div
          key={i}
          className={`text-xs border rounded px-2 py-1 ${SEVERITY_STYLES[a.severity]}`}
        >
          <div>{a.message}</div>
          <div className="opacity-60 mt-0.5">{relativeTime(a.timestamp)}</div>
        </div>
      ))}
    </div>
  );
}
