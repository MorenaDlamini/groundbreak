import { useEffect, useRef, useState } from "react";

export function useTelemetry(url) {
  const [fleet, setFleet] = useState({}); // keyed by vehicle_id
  const [alerts, setAlerts] = useState([]);
  const wsRef = useRef(null);

  useEffect(() => {
    let cancelled = false;

    function connect() {
      const ws = new WebSocket(url);
      wsRef.current = ws;

      ws.onmessage = (e) => {
        const { telemetry, alerts: newAlerts } = JSON.parse(e.data);
        setFleet((f) => ({ ...f, [telemetry.vehicle_id]: telemetry }));
        if (newAlerts?.length) {
          setAlerts((a) => [...newAlerts, ...a].slice(0, 50));
        }
      };

      ws.onclose = () => {
        if (!cancelled) setTimeout(connect, 1500);
      };
    }

    connect();
    return () => {
      cancelled = true;
      wsRef.current?.close();
    };
  }, [url]);

  return { fleet, alerts };
}
