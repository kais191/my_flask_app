"use client";

import { useState } from "react";
import { CATEGORY_CHART_COLORS } from "@/lib/category-colors";
import type { CategorySales } from "@/lib/mock-data";

function formatCompact(n: number): string {
  return `$${n.toLocaleString()}`;
}

/** Round up to a "clean" axis max: nearest 500 below 5k, nearest 1000 above. */
function niceMax(value: number): number {
  const step = value < 5000 ? 500 : 1000;
  return Math.ceil(value / step) * step;
}

const PLOT_HEIGHT = 180;

export function CategoryBarChart({ data }: { data: CategorySales[] }) {
  const [active, setActive] = useState<number | null>(null);
  const max = niceMax(Math.max(...data.map((d) => d.amount), 1));
  const ticks = [0, 0.25, 0.5, 0.75, 1].map((f) => Math.round(max * f));

  return (
    <div className="grid grid-cols-[auto_1fr] gap-x-2">
      {/* y-axis ticks */}
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

      {/* plot area */}
      <div className="relative" style={{ height: PLOT_HEIGHT }}>
        {ticks.map((t) => (
          <div
            key={t}
            aria-hidden
            className="absolute inset-x-0 border-t border-line"
            style={{ bottom: `${(t / max) * 100}%` }}
          />
        ))}

        <div className="absolute inset-0 flex items-end justify-around gap-3 px-2 sm:gap-6">
          {data.map((d, i) => {
            const colors = CATEGORY_CHART_COLORS[d.category];
            const heightPct = Math.max((d.amount / max) * 100, 1.5);
            return (
              <div key={d.category} className="relative flex h-full w-9 flex-col items-center justify-end sm:w-11">
                <div className="relative w-full" style={{ height: `${heightPct}%` }}>
                  <span className="absolute bottom-full mb-1.5 w-full text-center text-[11px] font-semibold text-ink tabular-nums">
                    {formatCompact(d.amount)}
                  </span>
                  <button
                    type="button"
                    aria-label={`${colors.label}: ${formatCompact(d.amount)}`}
                    onMouseEnter={() => setActive(i)}
                    onMouseLeave={() => setActive(null)}
                    onFocus={() => setActive(i)}
                    onBlur={() => setActive(null)}
                    className="h-full w-full rounded-t-[4px] transition-opacity"
                    style={{
                      backgroundColor: colors.fill,
                      opacity: active === null || active === i ? 1 : 0.55,
                    }}
                  />
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* x-axis labels — own grid row, same column as the plot so they stay aligned */}
      <div />
      <div className="mt-2 flex justify-around gap-3 px-2 sm:gap-6">
        {data.map((d) => (
          <span
            key={d.category}
            className="w-9 text-center text-[11px] font-medium text-ink-soft sm:w-11"
          >
            {CATEGORY_CHART_COLORS[d.category].label}
          </span>
        ))}
      </div>

      <table className="sr-only">
        <caption>Sales by category</caption>
        <thead>
          <tr>
            <th>Category</th>
            <th>Sales</th>
          </tr>
        </thead>
        <tbody>
          {data.map((d) => (
            <tr key={d.category}>
              <td>{CATEGORY_CHART_COLORS[d.category].label}</td>
              <td>{formatCompact(d.amount)}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
