"use client";

import { useEffect, useState } from "react";

export default function Home() {
  const [data, setData] = useState<any>(null);

  useEffect(() => {
    const load = async () => {
      const res = await fetch("/api/summary");
      setData(await res.json());
    };

    load();
    const t = setInterval(load, 15000);
    return () => clearInterval(t);
  }, []);

  if (!data) return <div style={{ padding: 20 }}>Loading…</div>;

  const statusColor =
    data.status === "HEALTHY"
      ? "green"
      : data.status === "WARNING"
      ? "orange"
      : "red";

  return (
    <main style={{ padding: 16, fontFamily: "system-ui" }}>
      <h2>📊 Bot Summary</h2>

      {/* SUMMARY */}
      <div
        style={{
          border: "1px solid #ddd",
          borderRadius: 8,
          padding: 12,
          marginBottom: 16,
        }}
      >
        <div>Trades: {data.trades}</div>
        <div>Win / Loss: {data.wins} / {data.losses}</div>
        <div>PnL: <b>{data.totalPnl}%</b></div>
        <div>
          Status:{" "}
          <b style={{ color: statusColor }}>{data.status}</b>
        </div>
      </div>

      {/* LOG */}
      <h3>📝 Recent Log</h3>
      <div style={{ fontFamily: "monospace", fontSize: 13 }}>
        {data.lastLines.map((l: string, i: number) => {
          let color = "#333";
          if (l.includes("BUY")) color = "green";
          if (l.includes("SELL")) color = "red";
          if (l.includes("STOP_LOSS")) color = "orange";

          return (
            <div key={i} style={{ color }}>
              {l}
            </div>
          );
        })}
      </div>
    </main>
  );
}
