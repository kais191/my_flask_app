import { CATEGORY_CHART_COLORS } from "@/lib/category-colors";
import type { CategoryAvailability } from "@/lib/product-utils";

export function CategoryAvailabilityList({ data }: { data: CategoryAvailability[] }) {
  return (
    <ul className="flex flex-col gap-4">
      {data.map((d) => {
        const colors = CATEGORY_CHART_COLORS[d.category];
        return (
          <li key={d.category}>
            <div className="mb-1.5 flex items-center justify-between text-sm">
              <span className="flex items-center gap-2 font-medium text-ink">
                <span
                  aria-hidden
                  className="h-2.5 w-2.5 rounded-full"
                  style={{ backgroundColor: colors.fill }}
                />
                {colors.label}
              </span>
              <span className="font-semibold tabular-nums text-ink">{d.percentOfAvailable}%</span>
            </div>
            <div
              role="meter"
              aria-label={`${colors.label} available products`}
              aria-valuenow={d.percentOfAvailable}
              aria-valuemin={0}
              aria-valuemax={100}
              className="h-2 w-full overflow-hidden rounded-full"
              style={{ backgroundColor: colors.track }}
              title={`${d.availableCount} products available`}
            >
              <div
                className="h-full rounded-full"
                style={{ width: `${d.percentOfAvailable}%`, backgroundColor: colors.fill }}
              />
            </div>
            <p className="mt-1 text-xs text-ink-soft">{d.availableCount} available</p>
          </li>
        );
      })}
    </ul>
  );
}
