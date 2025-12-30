"use client";

import { useEffect, useState } from "react";

export default function Home() {
  const [lines, setLines] = useState<string[]>([]);

  useEffect(() => {
    const load = async () => {
      const res = await fetch("/api/log");
      const data = await res.json();
      setLines(data.lines || []);
    };

    load();
    const t = setInterval(load, 10000); // refresh ทุก 10 วิ
    return () => clearInterval(t);
  }, []);

  return (
    <main style={{ padding: 20, fontFamily: "monospace" }}>
      <h2>📊 Trade Log (5m Bot)</h2>

      <div style={{ whiteSpace: "pre-wrap", fontSize: 14 }}>
        {lines.map((l, i) => (
          <div key={i}>{l}</div>
        ))}
      </div>
    </main>
  );
}
