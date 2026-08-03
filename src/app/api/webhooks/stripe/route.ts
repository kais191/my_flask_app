import { NextResponse, type NextRequest } from "next/server";
import Stripe from "stripe";
import { getStripe } from "@/lib/stripe/server";
import { createServiceClient } from "@/lib/supabase/service";

interface CartMetaItem {
  s: string; // product slug
  v?: string; // variant
  q: number; // quantity
}

export async function POST(request: NextRequest) {
  const signature = request.headers.get("stripe-signature");
  const webhookSecret = process.env.STRIPE_WEBHOOK_SECRET;

  if (!signature || !webhookSecret) {
    return NextResponse.json({ error: "Webhook not configured" }, { status: 400 });
  }

  const body = await request.text();
  let event: Stripe.Event;

  try {
    event = getStripe().webhooks.constructEvent(body, signature, webhookSecret);
  } catch (err) {
    console.error("Stripe webhook: signature verification failed —", err);
    return NextResponse.json({ error: "Invalid signature" }, { status: 400 });
  }

  if (event.type !== "checkout.session.completed") {
    return NextResponse.json({ received: true });
  }

  const session = event.data.object as Stripe.Checkout.Session;
  const paymentIntentId =
    typeof session.payment_intent === "string" ? session.payment_intent : session.payment_intent?.id;

  let metadata = session.metadata;

  // Deposit/cart checkouts (created directly in src/app/reserve/page.tsx and
  // src/app/api/checkout/route.ts) carry metadata on the Session. Balance
  // checkouts (created via a Stripe Payment Link in the admin panel) only
  // propagate metadata onto the PaymentIntent, not the Session — fetch it.
  if (!metadata?.kind && paymentIntentId) {
    const paymentIntent = await getStripe().paymentIntents.retrieve(paymentIntentId);
    metadata = paymentIntent.metadata;
  }

  const kind = metadata?.kind;
  const supabase = createServiceClient();

  if (kind === "cart") {
    let cart: CartMetaItem[] = [];
    try {
      cart = JSON.parse(metadata?.cart ?? "[]");
    } catch (err) {
      console.error("Stripe webhook: could not parse cart metadata —", err);
    }

    const { data: order, error: orderError } = await supabase
      .from("orders")
      .insert({
        customer_name: session.customer_details?.name ?? "Guest",
        customer_email: session.customer_details?.email ?? "",
        total: session.amount_total ? session.amount_total / 100 : 0,
        status: "new",
        stripe_payment_intent_id: paymentIntentId ?? null,
      })
      .select("id")
      .single();

    if (orderError || !order) {
      console.error("Stripe webhook: failed to create order —", orderError?.message);
      return NextResponse.json({ error: "Database update failed" }, { status: 500 });
    }

    for (const item of cart) {
      const { data: product } = await supabase
        .from("products")
        .select("id, name, price")
        .eq("slug", item.s)
        .maybeSingle();

      await supabase.from("order_items").insert({
        order_id: order.id,
        product_id: product?.id ?? null,
        product_name: product?.name ?? item.s,
        variant: item.v ?? null,
        quantity: item.q,
        unit_price: product?.price ?? 0,
      });
    }

    return NextResponse.json({ received: true });
  }

  const preorderId = metadata?.preorder_id;
  if (preorderId) {
    const update =
      kind === "balance"
        ? { status: "balance_paid", stripe_balance_payment_intent_id: paymentIntentId ?? null }
        : { status: "deposit_paid", stripe_deposit_payment_intent_id: paymentIntentId ?? null };

    const { error } = await supabase.from("preorders").update(update).eq("id", preorderId);

    if (error) {
      console.error("Stripe webhook: failed to update preorder —", error.message);
      return NextResponse.json({ error: "Database update failed" }, { status: 500 });
    }
  }

  return NextResponse.json({ received: true });
}
