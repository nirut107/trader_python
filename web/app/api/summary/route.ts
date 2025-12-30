import fs from "fs";
import path from "path";
import { NextResponse } from "next/server";

type Trade = {
  type: "BUY" | "SELL" | "STOP_LOSS" | "TAKE_PROFIT" | "TIME_EXIT" | "TRAIL_STOP";
  pnl?: number;
};

export async function GET() {
  const logPath = path.join(process.cwd(), "..", "bot", "trade.log");

  try {
    const content = fs.readFileSync(logPath, "utf-8");
    const lines = content.trim().split("\n");

    let trades: Trade[] = [];
    let totalPnl = 0;
    let wins = 0;
    let losses = 0;

    for (const line of lines) {
      if (line.includes("BUY")) {
        trades.push({ type: "BUY" });
      }

      if (
        line.includes("SELL") ||
        line.includes("STOP_LOSS") ||
        line.includes("TAKE_PROFIT") ||
        line.includes("TIME_EXIT") ||
        line.includes("TRAIL_STOP")
      ) {
        const m = line.match(/PnL=([\-0-9.]+)/);
        const pnl = m ? parseFloat(m[1]) : 0;

        totalPnl += pnl;
        pnl >= 0 ? wins++ : losses++;

        if (line.includes("STOP_LOSS"))
          trades.push({ type: "STOP_LOSS", pnl });
        else if (line.includes("TAKE_PROFIT"))
          trades.push({ type: "TAKE_PROFIT", pnl });
        else if (line.includes("TIME_EXIT"))
          trades.push({ type: "TIME_EXIT", pnl });
        else if (line.includes("TRAIL_STOP"))
          trades.push({ type: "TRAIL_STOP", pnl });
        else trades.push({ type: "SELL", pnl });
      }
    }

    // ---- Health logic ----
    let status: "HEALTHY" | "WARNING" | "DANGER" = "HEALTHY";

    const recent = trades.slice(-10);
    const stopCount = recent.filter(t => t.type === "STOP_LOSS").length;

    if (stopCount >= 3 || totalPnl < -1) status = "DANGER";
    else if (stopCount >= 2 || totalPnl < 0) status = "WARNING";

    return NextResponse.json({
      trades: trades.length,
      wins,
      losses,
      totalPnl: totalPnl.toFixed(2),
      status,
      lastLines: lines.slice(-30).reverse(),
    });
  } catch (err) {
    return NextResponse.json({
      trades: 0,
      wins: 0,
      losses: 0,
      totalPnl: "0.00",
      status: "UNKNOWN",
      lastLines: [],
    });
  }
}
