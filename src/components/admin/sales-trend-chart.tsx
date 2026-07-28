"use client";

import { useState } from "react";
import type { WeeklySales } from "@/lib/mock-data";

function formatCompact(n: number): string {
  return `$${n.toLocaleString()}`;
}

function niceMax(value: number): number {
  const step = value < 5000 ? 500 : 1000;
  return Math.ceil(value / step) * step;
}

const LINE_COLOR = "#C17A8B"; // brand rose — single series, so no separate chart-categorical color needed
const PLOT_HEIGHT = 180;

export function SalesTrendChart({ data }: { data: WeeklySales[] }) {
  const [hoverIndex, setHoverIndex] = useState<number | null>(null);
  const values = data.map((d) => d.amount);
  const max = niceMax(Math.max(...values) * 1.15);
  const ticks = [0, 0.25, 0.5, 0.75, 1].map((f) => Math.round(max * f));

  const points = data.map((d, i) => ({
    xPct: (i / (data.length - 1)) * 100,
    yPct: 100 - (d.amount / max) * 100,
    ...d,
  }));

  const linePath = points.map((p) => `${p.xPct},${p.yPct}`).join(" ");
  const areaPath = `0,100 ${linePath} 100,100`;

  const active = hoverIndex !== null ? points[hoverIndex] : points[points.length - 1];
  const totalSales = values.reduce((sum, v) => sum + v, 0);

  return (
    <div>
      <div className="mb-4 flex items-baseline justify-between">
        <p className="text-xs text-ink-soft">
          Total, last {data.length} weeks: <span className="font-semibold text-ink">{formatCompact(totalSales)}</span>
        </p>
        <p className="text-xs text-ink-soft">
          {active.weekLabel}: <span className="font-semibold text-rose-dark">{formatCompact(active.amount)}</span>
        </p>
      </div>

      <div className="grid grid-cols-[auto_1fr] gap-x-2">
        <div
          className="flex flex-col-reverse justify-between text-right text-[10px] text-ink-soft"
          style={{ height: PLOT_HEIGHT }}
        >
          {ticks.map((t) => (
            <span key={t} className="leading-none tabular-nums">
              {formatCompact(t)}
            </span>
          ))}
        </div>

        <div
          className="relative"
          style={{ height: PLOT_HEIGHT }}
          onMouseLeave={() => setHoverIndex(null)}
          onMouseMove={(e) => {
            const rect = e.currentTarget.getBoundingClientRect();
            const frac = (e.clientX - rect.left) / rect.width;
            const index = Math.min(data.length - 1, Math.max(0, Math.round(frac * (data.length - 1))));
            setHoverIndex(index);
          }}
        >
          {ticks.map((t) => (
            <div
              key={t}
              aria-hidden
              className="absolute inset-x-0 border-t border-line"
              style={{ bottom: `${(t / max) * 100}%` }}
            />
          ))}

          <svg
            viewBox="0 0 100 100"
            preserveAspectRatio="none"
            className="absolute inset-0 h-full w-full overflow-visible"
            aria-hidden
          >
            <polygon points={areaPath} fill={LINE_COLOR} fillOpacity={0.1} stroke="none" />
            <polyline
              points={linePath}
              fill="none"
              stroke={LINE_COLOR}
              strokeWidth={2}
              vectorEffect="non-scaling-stroke"
              strokeLinejoin="round"
              strokeLinecap="round"
            />
          </svg>

          {hoverIndex !== null && (
            <div
              aria-hidden
              className="absolute top-0 bottom-0 w-px bg-line"
              style={{ left: `${points[hoverIndex].xPct}%` }}
            />
          )}

          {points.map((p, i) => {
            const isEnd = i === points.length - 1;
            const isActive = hoverIndex === i;
            return (
              <div
                key={p.weekLabel}
                className="absolute -translate-x-1/2 -translate-y-1/2 rounded-full bg-surface"
                style={{
                  left: `${p.xPct}%`,
                  top: `${p.yPct}%`,
                  width: isEnd || isActive ? 10 : 8,
                  height: isEnd || isActive ? 10 : 8,
                  border: `2px solid ${LINE_COLOR}`,
                  opacity: isEnd || isActive ? 1 : 0,
                }}
              />
            );
          })}

          {/* invisible, keyboard-focusable hit targets — one per week, ≥24px */}
          <div className="absolute inset-0 flex">
            {points.map((p, i) => (
              <button
                key={p.weekLabel}
                type="button"
                aria-label={`${p.weekLabel}: ${formatCompact(p.amount)}`}
                className="h-full flex-1"
                onFocus={() => setHoverIndex(i)}
                onBlur={() => setHoverIndex(null)}
              />
            ))}
          </div>

          <span
            className="absolute -translate-x-1/2 -translate-y-full whitespace-nowrap pb-2 text-[11px] font-semibold text-ink tabular-nums"
            style={{ left: `${points[points.length - 1].xPct}%`, top: `${points[points.length - 1].yPct}%` }}
          >
            {formatCompact(points[points.length - 1].amount)}
          </span>
        </div>

        <div />
        <div className="mt-2 flex justify-between text-[10px] text-ink-soft">
          {data.map((d, i) => (
            <span key={d.weekLabel} className={i % 2 === 0 ? "" : "invisible sm:visible"}>
              {d.weekLabel}
            </span>
          ))}
        </div>
      </div>

      <table className="sr-only">
        <caption>Total sales, last {data.length} weeks</caption>
        <thead>
          <tr>
            <th>Week</th>
            <th>Sales</th>
          </tr>
        </thead>
        <tbody>
          {data.map((d) => (
            <tr key={d.weekLabel}>
              <td>{d.weekLabel}</td>
              <td>{formatCompact(d.amount)}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
