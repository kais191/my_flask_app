import { headers } from "next/headers";
import { NextResponse, type NextRequest } from "next/server";
import { getAllProducts } from "@/lib/data/products";
import { isSupabaseConfigured } from "@/lib/supabase/env";
import { isStripeConfigured } from "@/lib/stripe/env";
import { getStripe } from "@/lib/stripe/server";

interface CheckoutRequestItem {
  slug: string;
  variant?: string;
  quantity: number;
}

export async function POST(request: NextRequest) {
  if (!isSupabaseConfigured() || !isStripeConfigured()) {
    return NextResponse.json(
      { error: "Checkout isn't set up yet — connect Supabase and Stripe first (see README)." },
      { status: 503 }
    );
  }

  const { items } = (await request.json()) as { items: CheckoutRequestItem[] };

  if (!Array.isArray(items) || items.length === 0) {
    return NextResponse.json({ error: "Your bag is empty." }, { status: 400 });
  }

  // Prices always come from the server's product catalog, never the client —
  // a tampered request body can't change what gets charged.
  const products = await getAllProducts();
  const lineItems: Array<{
    price_data: {
      currency: string;
      product_data: { name: string };
      unit_amount: number;
    };
    quantity: number;
  }> = [];
  const cartMeta: { s: string; v?: string; q: number }[] = [];

  for (const item of items) {
    const product = products.find((p) => p.slug === item.slug);
    const quantity = Math.max(1, Math.floor(item.quantity));
    if (!product || quantity < 1) continue;

    lineItems.push({
      price_data: {
        currency: "usd",
        product_data: {
          name: item.variant ? `${product.name} (${item.variant})` : product.name,
        },
        unit_amount: Math.round(product.price * 100),
      },
      quantity,
    });
    cartMeta.push({ s: product.slug, v: item.variant, q: quantity });
  }

  if (lineItems.length === 0) {
    return NextResponse.json({ error: "None of the items in your bag are available." }, { status: 400 });
  }

  const origin = (await headers()).get("origin") ?? "http://localhost:3000";
  const stripe = getStripe();
  const session = await stripe.checkout.sessions.create({
    mode: "payment",
    line_items: lineItems,
    metadata: { kind: "cart", cart: JSON.stringify(cartMeta) },
    success_url: `${origin}/order/success?session_id={CHECKOUT_SESSION_ID}`,
    cancel_url: `${origin}/cart`,
  });

  return NextResponse.json({ url: session.url });
}
