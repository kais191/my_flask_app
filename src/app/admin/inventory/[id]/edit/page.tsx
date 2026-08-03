import Link from "next/link";
import { notFound, redirect } from "next/navigation";
import { ProductFormFields } from "@/components/admin/product-form-fields";
import { ConfirmSubmitButton } from "@/components/confirm-submit-button";
import { createClient } from "@/lib/supabase/server";
import { isSupabaseConfigured } from "@/lib/supabase/env";
import { getProductById } from "@/lib/data/products";
import { slugify } from "@/lib/slug";

async function updateProduct(id: string, formData: FormData) {
  "use server";

  const name = String(formData.get("name") ?? "").trim();
  const slugInput = String(formData.get("slug") ?? "").trim();
  const category = String(formData.get("category") ?? "makeup");
  const brand = String(formData.get("brand") ?? "").trim();
  const price = Number(formData.get("price"));
  const cost = Number(formData.get("cost"));
  const stockQuantity = Number(formData.get("stockQuantity"));
  const lowStockThreshold = Number(formData.get("lowStockThreshold"));
  const bestseller = formData.get("bestseller") === "on";
  const imageUrl = String(formData.get("imageUrl") ?? "").trim();
  const variants = String(formData.get("variants") ?? "")
    .split(",")
    .map((v) => v.trim())
    .filter(Boolean);
  const concerns = String(formData.get("concerns") ?? "")
    .split(",")
    .map((c) => c.trim())
    .filter(Boolean);

  if (!name || !Number.isFinite(price) || price < 0 || !Number.isFinite(cost) || cost < 0) {
    redirect(`/admin/inventory/${id}/edit?error=invalid`);
  }

  const slug = slugify(slugInput || name);
  const supabase = await createClient();

  const { data: categoryRow } = await supabase
    .from("categories")
    .select("id")
    .eq("slug", category)
    .single();

  if (!categoryRow) {
    redirect(`/admin/inventory/${id}/edit?error=invalid`);
  }

  const { error } = await supabase
    .from("products")
    .update({
      slug,
      name,
      category_id: categoryRow.id,
      brand: brand || null,
      price,
      cost,
      stock_quantity: Number.isFinite(stockQuantity) ? stockQuantity : 0,
      low_stock_threshold: Number.isFinite(lowStockThreshold) ? lowStockThreshold : 10,
      bestseller,
      image_url: imageUrl || null,
      variants: variants.length ? variants : null,
      concerns: concerns.length ? concerns : null,
    })
    .eq("id", id);

  if (error) {
    console.error("updateProduct: update failed —", error.message);
    redirect(`/admin/inventory/${id}/edit?error=save`);
  }

  redirect("/admin/inventory?updated=1");
}

async function deleteProduct(id: string) {
  "use server";

  const supabase = await createClient();
  const { error } = await supabase.from("products").delete().eq("id", id);

  if (error) {
    console.error("deleteProduct: delete failed —", error.message);
    redirect(`/admin/inventory/${id}/edit?error=save`);
  }

  redirect("/admin/inventory?deleted=1");
}

const ERRORS: Record<string, string> = {
  invalid: "Please check the required fields (name, price, cost) and try again.",
  save: "Couldn't save that product — check the Supabase logs.",
};

export default async function EditProductPage({
  params,
  searchParams,
}: {
  params: Promise<{ id: string }>;
  searchParams: Promise<{ error?: string }>;
}) {
  const { id } = await params;
  const { error } = await searchParams;

  if (!isSupabaseConfigured()) {
    return (
      <div>
        <h1 className="mb-2 text-2xl">Edit product</h1>
        <p className="text-sm text-ink-soft">
          Connect Supabase first — see README.md — the mock catalog isn&rsquo;t
          editable.
        </p>
      </div>
    );
  }

  const product = await getProductById(id);
  if (!product) notFound();

  const updateWithId = updateProduct.bind(null, id);
  const deleteWithId = deleteProduct.bind(null, id);

  return (
    <div className="max-w-xl">
      <Link href="/admin/inventory" className="mb-4 inline-block text-xs text-ink-soft hover:text-ink">
        ← Inventory
      </Link>
      <h1 className="mb-6 text-2xl">Edit {product.name}</h1>

      {error && (
        <p className="mb-4 rounded-xl border border-[#e3b98f] bg-[#fbf1e4] px-4 py-3 text-sm text-[#8a5a1f]">
          {ERRORS[error] ?? ERRORS.save}
        </p>
      )}

      <form action={updateWithId} className="mb-4 flex flex-col gap-6">
        <ProductFormFields product={product} />
        <button className="rounded-full bg-rose py-3.5 text-sm font-bold text-white transition-transform hover:scale-[1.01]">
          Save changes
        </button>
      </form>

      <form action={deleteWithId}>
        <ConfirmSubmitButton
          confirmMessage={`Delete ${product.name}? This can't be undone.`}
          className="w-full rounded-full border border-line py-3 text-sm font-semibold text-rose-dark hover:border-rose-dark"
        >
          Delete product
        </ConfirmSubmitButton>
      </form>
    </div>
  );
}
