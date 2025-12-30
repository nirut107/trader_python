import fs from "fs";
import path from "path";
import { NextResponse } from "next/server";

export async function GET() {
  const logPath = path.join(process.cwd(), "..", "bot", "trade.log");

  try {
    const content = fs.readFileSync(logPath, "utf-8");
    const lines = content
      .trim()
      .split("\n")
      .slice(-200)

    return NextResponse.json({ lines });
  } catch (err) {
    return NextResponse.json({ lines: [], error: "no log file" });
  }
}
