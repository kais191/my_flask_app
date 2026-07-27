import type { Product } from "@/lib/types";

const fieldClass =
  "rounded-xl border border-line bg-surface px-4 py-3 text-sm text-ink placeholder:text-ink-soft";
const labelClass = "mb-1.5 block text-xs font-semibold text-ink-soft";

/** Shared fields for the Add and Edit product forms — differ only by defaultValue and the action/buttons around them. */
export function ProductFormFields({ product }: { product?: Product }) {
  return (
    <div className="flex flex-col gap-4">
      <div>
        <label className={labelClass} htmlFor="name">
          Name
        </label>
        <input
          id="name"
          name="name"
          required
          defaultValue={product?.name}
          className={`${fieldClass} w-full`}
          placeholder="Silk Veil Blush"
        />
      </div>

      <div>
        <label className={labelClass} htmlFor="slug">
          URL slug
        </label>
        <input
          id="slug"
          name="slug"
          defaultValue={product?.slug}
          className={`${fieldClass} w-full`}
          placeholder="auto-generated from name if left blank"
        />
      </div>

      <div className="grid gap-4 sm:grid-cols-2">
        <div>
          <label className={labelClass} htmlFor="category">
            Category
          </label>
          <select
            id="category"
            name="category"
            defaultValue={product?.category ?? "makeup"}
            className={`${fieldClass} w-full`}
          >
            <option value="makeup">Makeup</option>
            <option value="skincare">Skincare</option>
            <option value="handbags">Handbags</option>
          </select>
        </div>
        <div>
          <label className={labelClass} htmlFor="brand">
            Brand (optional)
          </label>
          <input
            id="brand"
            name="brand"
            defaultValue={product?.brand}
            className={`${fieldClass} w-full`}
            placeholder="Coach, Michael Kors…"
          />
        </div>
      </div>

      <div className="grid gap-4 sm:grid-cols-3">
        <div>
          <label className={labelClass} htmlFor="price">
            Price ($)
          </label>
          <input
            id="price"
            name="price"
            type="number"
            min="0"
            step="0.01"
            required
            defaultValue={product?.price}
            className={`${fieldClass} w-full`}
          />
        </div>
        <div>
          <label className={labelClass} htmlFor="cost">
            Cost ($)
          </label>
          <input
            id="cost"
            name="cost"
            type="number"
            min="0"
            step="0.01"
            required
            defaultValue={product?.cost}
            className={`${fieldClass} w-full`}
          />
        </div>
        <div>
          <label className={labelClass} htmlFor="stockQuantity">
            In stock
          </label>
          <input
            id="stockQuantity"
            name="stockQuantity"
            type="number"
            min="0"
            step="1"
            required
            defaultValue={product?.stockQuantity}
            className={`${fieldClass} w-full`}
          />
        </div>
      </div>

      <div className="grid gap-4 sm:grid-cols-2">
        <div>
          <label className={labelClass} htmlFor="lowStockThreshold">
            Low-stock alert threshold
          </label>
          <input
            id="lowStockThreshold"
            name="lowStockThreshold"
            type="number"
            min="0"
            step="1"
            required
            defaultValue={product?.lowStockThreshold ?? 10}
            className={`${fieldClass} w-full`}
          />
        </div>
        <label className="flex items-center gap-2 self-end pb-3 text-sm text-ink">
          <input
            type="checkbox"
            name="bestseller"
            defaultChecked={product?.bestseller}
            className="h-4 w-4 rounded border-line accent-[var(--color-rose)]"
          />
          Bestseller
        </label>
      </div>

      <div>
        <label className={labelClass} htmlFor="variants">
          Shades / sizes (comma-separated, optional)
        </label>
        <input
          id="variants"
          name="variants"
          defaultValue={product?.variants?.join(", ")}
          className={`${fieldClass} w-full`}
          placeholder="Petal, Rosewood, Terracotta"
        />
      </div>

      <div>
        <label className={labelClass} htmlFor="concerns">
          Shop-by-look tags (comma-separated, optional)
        </label>
        <input
          id="concerns"
          name="concerns"
          defaultValue={product?.concerns?.join(", ")}
          className={`${fieldClass} w-full`}
          placeholder="everyday-glam, date-night"
        />
      </div>
    </div>
  );
}
