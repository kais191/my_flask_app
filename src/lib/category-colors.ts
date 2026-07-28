import type { CategorySlug } from "./types";

/**
 * Categorical chart palette for the three departments. Validated against a
 * white chart surface with the dataviz skill's six-checks script (chroma
 * floor, CVD separation ΔE ≥ 8, normal-vision floor ≥ 15, contrast ≥ 3:1) —
 * all pass all-pairs. Not the storefront's Blush Bloom UI palette: chart
 * color has different constraints (must stay distinguishable under color
 * blindness) than brand chrome, so it's deliberately a separate set.
 */
export const CATEGORY_CHART_COLORS: Record<
  CategorySlug,
  { label: string; fill: string; track: string }
> = {
  makeup: { label: "Makeup", fill: "#B4487A", track: "#F1D8E4" },
  skincare: { label: "Skincare", fill: "#2E7DB8", track: "#D3E5F1" },
  handbags: { label: "Handbags", fill: "#C0862E", track: "#F0DFC1" },
};

export const CATEGORY_ORDER: CategorySlug[] = ["makeup", "skincare", "handbags"];
