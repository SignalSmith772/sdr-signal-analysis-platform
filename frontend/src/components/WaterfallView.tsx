/**
 * components/WaterfallView.tsx
 * Canvas-based scrolling waterfall (time vs frequency, colour = power).
 * Each new FFT row is drawn at the top; old rows scroll down.
 */
import React, { useRef, useEffect, useCallback } from 'react';

interface WaterfallViewProps {
  powersDb: number[];     // latest FFT row
  noiseFloorDb: number;
  height?: number;
}

// Map dBFS value to an RGBA colour (blue → cyan → green → yellow → red)
function dbToColor(db: number, minDb: number, maxDb: number): [number, number, number] {
  const t = Math.max(0, Math.min(1, (db - minDb) / (maxDb - minDb)));
  // Color stops: deep blue → cyan → green → yellow → red
  if (t < 0.25) {
    const s = t / 0.25;
    return [Math.round(0 + s * 0), Math.round(0 + s * 120), Math.round(180 + s * 75)];
  } else if (t < 0.5) {
    const s = (t - 0.25) / 0.25;
    return [Math.round(0 + s * 0), Math.round(120 + s * 135), Math.round(255 - s * 150)];
  } else if (t < 0.75) {
    const s = (t - 0.5) / 0.25;
    return [Math.round(0 + s * 255), Math.round(255 - s * 55), Math.round(105 - s * 105)];
  } else {
    const s = (t - 0.75) / 0.25;
    return [255, Math.round(200 - s * 200), 0];
  }
}

export default function WaterfallView({
  powersDb,
  noiseFloorDb,
  height = 200,
}: WaterfallViewProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const offscreenRef = useRef<HTMLCanvasElement | null>(null);

  // Draw a single new row at the top, scroll everything else down by 1px
  const drawRow = useCallback((newRow: number[]) => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    const w = canvas.width;
    const H = canvas.height;

    // Create offscreen buffer on first use
    if (!offscreenRef.current) {
      const off = document.createElement('canvas');
      off.width = w;
      off.height = H;
      offscreenRef.current = off;
    }
    const off = offscreenRef.current;
    const offCtx = off.getContext('2d')!;

    // Copy current canvas to offscreen shifted down 1px
    offCtx.clearRect(0, 0, w, H);
    offCtx.drawImage(canvas, 0, 0, w, H - 1, 0, 1, w, H - 1);

    // Draw new row at top
    const minDb = noiseFloorDb - 5;
    const maxDb = noiseFloorDb + 45;
    const step = w / newRow.length;
    for (let i = 0; i < newRow.length; i++) {
      const [r, g, b] = dbToColor(newRow[i], minDb, maxDb);
      offCtx.fillStyle = `rgb(${r},${g},${b})`;
      offCtx.fillRect(Math.floor(i * step), 0, Math.ceil(step), 1);
    }

    // Copy back to visible canvas
    ctx.clearRect(0, 0, w, H);
    ctx.drawImage(off, 0, 0);
  }, [noiseFloorDb]);

  // Redraw whenever we receive a new row
  useEffect(() => {
    if (powersDb.length > 0) drawRow(powersDb);
  }, [powersDb, drawRow]);

  return (
    <div className="bg-slate-900 rounded-xl border border-slate-700 p-4">
      <div className="flex items-center justify-between mb-3">
        <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">
          Waterfall Display
        </span>
        {/* Colour legend */}
        <div className="flex items-center gap-2 text-xs text-slate-500">
          <span className="font-mono">Low</span>
          <div
            style={{
              width: 80,
              height: 8,
              borderRadius: 4,
              background: 'linear-gradient(to right, #0048b4, #00cc66, #ffff00, #ff0000)',
            }}
          />
          <span className="font-mono">High</span>
        </div>
      </div>
      <canvas
        ref={canvasRef}
        width={800}
        height={height}
        className="waterfall-canvas rounded-lg bg-slate-950"
        style={{ height }}
      />
      {powersDb.length === 0 && (
        <div
          className="flex items-center justify-center rounded-lg bg-slate-950"
          style={{ height, marginTop: -height }}
        >
          <p className="text-slate-600 text-sm">Waiting for data…</p>
        </div>
      )}
    </div>
  );
}
