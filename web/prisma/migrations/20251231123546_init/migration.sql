-- CreateTable
CREATE TABLE "Trade" (
    "id" SERIAL NOT NULL,
    "time" TIMESTAMP(3) NOT NULL,
    "signal" TEXT NOT NULL,
    "price" DOUBLE PRECISION NOT NULL,
    "pnl" DOUBLE PRECISION,
    "regime" TEXT NOT NULL,
    "note" TEXT,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "Trade_pkey" PRIMARY KEY ("id")
);

-- CreateIndex
CREATE INDEX "Trade_time_idx" ON "Trade"("time");

-- CreateIndex
CREATE INDEX "Trade_signal_idx" ON "Trade"("signal");

-- CreateIndex
CREATE INDEX "Trade_regime_idx" ON "Trade"("regime");
