import  prisma  from "@/lib/prisma";

export async function POST(req: Request) {
  const data = await req.json();

  await prisma.trade.create({
    data: {
      time: new Date(data.time),
      signal: data.signal,
      price: data.price,
      pnl: data.pnl ?? null,
      regime: data.regime,
      note: data.note,
    },
  });

  return Response.json({ ok: true });
}

export async function GET() {
  const trades = await prisma.trade.findMany({
    orderBy: { time: "desc" },
    take: 200,
  });

  return Response.json({
    latest: trades[0] ?? null,
    history: trades,
  });
}
