let history: any[] = [];

export async function POST(req: Request) {
  const data = await req.json();

  history.push({
    ...data,
    ts: Date.now(),
  });

  // เก็บแค่ 100 รายการล่าสุด (กัน memory บวม)
  if (history.length > 100) {
    history = history.slice(-100);
  }

  return Response.json({ ok: true });
}

export async function GET() {
  return Response.json({
    latest: history[history.length - 1] ?? null,
    history,
  });
}
