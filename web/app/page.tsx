"use client";

import { useEffect, useMemo, useState } from "react";

type Event = {
  time?: string;
  price?: number;
  signal?: string;
  pnl?: number;
};

export default function Page() {
  const [latest, setLatest] = useState<Event | null>(null);
  const [history, setHistory] = useState<Event[]>([]);
  const [loading, setLoading] = useState(true);
  const [dark, setDark] = useState(false);
  const [sell, setSell] = useState<Event[]>([]);

  async function load() {
    const res = await fetch("/api/push", { cache: "no-store" });
    const json = await res.json();
    setLatest(json.latest ?? null);
    setHistory(json.history ?? []);
    const sell = json.history.filter(
      (e: Event) => e.signal != "BUY" && e.signal != "HOLD"
    );
    setSell(sell);
    setLoading(false);
  }

  useEffect(() => {
    load();
    const t = setInterval(load, 15000);
    return () => clearInterval(t);
  }, []);

  /* ===== PnL TODAY ===== */
  const pnlToday = useMemo(() => {
    const today = new Date().toISOString().slice(0, 10);
    return history
      .filter((e) => e.pnl !== undefined && e.time && e.time.startsWith(today))
      .reduce((s, e) => s + (e.pnl ?? 0), 0);
  }, [history]);

  const regimeSell = useMemo(() => calcRegimeStats(sell), [sell]);
  const regimeStats = useMemo(() => calcRegimeStats(history), [history]);

  type Regime = "UPTREND" | "SIDEWAYS" | "DOWNTREND";

  type RegimeStat = {
    trades: number;
    wins: number;
    totalPnl: number;
  };

  function calcRegimeStats(history: any[]) {
    const stats: Record<Regime, RegimeStat> = {
      UPTREND: { trades: 0, wins: 0, totalPnl: 0 },
      SIDEWAYS: { trades: 0, wins: 0, totalPnl: 0 },
      DOWNTREND: { trades: 0, wins: 0, totalPnl: 0 },
    };

    history.forEach((e) => {
      if (e.pnl === undefined || !e.regime) return;

      const r = e.regime as Regime;
      stats[r].trades += 1;
      stats[r].totalPnl += e.pnl;
      if (e.pnl > 0) stats[r].wins += 1;
    });

    return stats;
  }

  if (loading) {
    return <div style={{ padding: 20 }}>Loading…</div>;
  }

  const bg = dark ? "#0f172a" : "#fff";
  const fg = dark ? "#e5e7eb" : "#111";
  const card = dark ? "#020617" : "#fff";
  const border = dark ? "#1e293b" : "#ddd";

  const signalColor =
    latest?.signal === "BUY"
      ? "#22c55e"
      : latest?.signal?.includes("STOP")
      ? "#ef4444"
      : latest?.signal?.includes("TAKE")
      ? "#3b82f6"
      : "#9ca3af";

  return (
    <main
      style={{
        padding: 16,
        fontFamily: "system-ui",
        maxWidth: 480,
        margin: "0 auto",
        background: bg,
        color: fg,
        minHeight: "100vh",
      }}
    >
      {/* HEADER */}
      <div style={{ display: "flex", justifyContent: "space-between" }}>
        <h2>🤖 Trading Bot</h2>
        <button
          onClick={() => setDark(!dark)}
          style={{
            border: `1px solid ${border}`,
            background: card,
            color: fg,
            borderRadius: 8,
            padding: "6px 10px",
            cursor: "pointer",
          }}
        >
          {dark ? "☀️ Light" : "🌙 Dark"}
        </button>
      </div>

      {/* ===== LAST STATUS ===== */}
      {latest && (
        <>
          {/* 🔔 LAST SIGNAL (highlight) */}
          <div
            style={{
              border: `2px solid ${signalColor}`,
              borderRadius: 12,
              padding: 16,
              marginBottom: 16,
              textAlign: "center",
              background: card,
            }}
          >
            <div style={{ fontSize: 12, opacity: 0.7 }}>Latest</div>
            <div
              style={{
                fontSize: 32,
                fontWeight: "bold",
                color: signalColor,
              }}
            >
              {latest.signal ?? "HOLD"}
            </div>
            <div style={{ fontSize: 12, opacity: 0.7 }}>{latest.time}</div>
          </div>

          {/* PRICE + PNL */}
          <div
            style={{
              display: "grid",
              gridTemplateColumns: "1fr 1fr",
              gap: 12,
              marginBottom: 20,
            }}
          >
            <div
              style={{
                border: `1px solid ${border}`,
                borderRadius: 10,
                padding: 16,
                background: card,
              }}
            >
              <div style={{ fontSize: 12, opacity: 0.7 }}>Price</div>
              <div style={{ fontSize: 20 }}>{latest.price?.toFixed(2)}</div>
            </div>

            <div
              style={{
                border: `1px solid ${border}`,
                borderRadius: 10,
                padding: 16,
                background: card,
              }}
            >
              <div style={{ fontSize: 12, opacity: 0.7 }}>Last PnL</div>
              <div
                style={{
                  fontSize: 20,
                  color:
                    latest.pnl !== undefined
                      ? latest.pnl > 0
                        ? "#22c55e"
                        : "#ef4444"
                      : fg,
                }}
              >
                {latest.pnl !== undefined && latest.pnl !== null
                  ? `${Number(latest.pnl).toFixed(2)} %`
                  : "-"}
              </div>
            </div>
          </div>
        </>
      )}

      {/* 📊 PnL TODAY */}
      <div
        style={{
          border: `1px solid ${border}`,
          borderRadius: 10,
          padding: 16,
          marginBottom: 24,
          background: card,
        }}
      >
        <div style={{ fontSize: 12, opacity: 0.7 }}>📊 PnL Today</div>
        <div
          style={{
            fontSize: 24,
            fontWeight: "bold",
            color: pnlToday >= 0 ? "#22c55e" : "#ef4444",
          }}
        >
          {pnlToday.toFixed(2)} %
        </div>
      </div>
      <h3>📊 Regime Stats</h3>

      <div style={{ fontSize: 14, marginBottom: 24 }}>
        {Object.entries(regimeSell).map(([regime, s]) => {
          if (s.trades === 0) return null;
          console.log(regime);
          const winRate = (s.wins / s.trades) * 100;
          const avgPnl = s.totalPnl / s.trades;

          return (
            <div
              key={regime}
              style={{
                border: `1px solid ${border}`,
                borderRadius: 10,
                padding: 12,
                marginBottom: 8,
                background: card,
              }}
            >
              <b>{regime}</b>
              <div>Trades: {s.trades}</div>
              <div>Win rate: {winRate.toFixed(0)}%</div>
              <div>
                Avg PnL:{" "}
                <span
                  style={{
                    color: avgPnl >= 0 ? "#22c55e" : "#ef4444",
                  }}
                >
                  {avgPnl.toFixed(2)}%
                </span>
              </div>
              <div>
                Total:{" "}
                <span
                  style={{
                    color: s.totalPnl >= 0 ? "#22c55e" : "#ef4444",
                  }}
                >
                  {s.totalPnl.toFixed(2)}%
                </span>
              </div>
            </div>
          );
        })}
      </div>

      {/* 📜 TRADE HISTORY */}
      <h3>📜 Trade History</h3>

      <div style={{ fontSize: 14 }}>
        {history
          .slice()
          .reverse()
          .map((e, i) => (
            <div
              key={i}
              style={{
                borderBottom: `1px solid ${border}`,
                padding: "8px 0",
                opacity: i === 0 ? 1 : 0.85,
                fontWeight: i === 0 ? "bold" : "normal",
              }}
            >
              <div>
                {e.signal} {e.price && `@ ${Number(e.price).toFixed(2)}`}
              </div>

              {e.pnl !== undefined && e.signal != "HOLD" && e.signal != "BUY"  && (
                <div
                  style={{
                    color: e.pnl >= 0 ? "#22c55e" : "#ef4444",
                  }}
                >
                  PnL: {Number(e.pnl).toFixed(2)}%
                </div>
              )}

              <div style={{ fontSize: 11, opacity: 0.6 }}>{e.time}</div>
            </div>
          ))}
      </div>
    </main>
  );
}
