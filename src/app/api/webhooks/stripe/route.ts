import { NextResponse, type NextRequest } from "next/server";
import Stripe from "stripe";
import { getStripe } from "@/lib/stripe/server";
import { createServiceClient } from "@/lib/supabase/service";

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

  if (event.type === "checkout.session.completed") {
    const session = event.data.object as Stripe.Checkout.Session;
    const paymentIntentId =
      typeof session.payment_intent === "string" ? session.payment_intent : session.payment_intent?.id;

    let preorderId = session.metadata?.preorder_id;
    let kind = session.metadata?.kind;

    // Deposit checkouts (created directly in src/app/reserve/page.tsx) carry
    // metadata on the Session. Balance checkouts (created via a Stripe
    // Payment Link in the admin panel) only propagate metadata onto the
    // PaymentIntent, not the Session — fetch it in that case.
    if (!preorderId && paymentIntentId) {
      const paymentIntent = await getStripe().paymentIntents.retrieve(paymentIntentId);
      preorderId = paymentIntent.metadata?.preorder_id;
      kind = paymentIntent.metadata?.kind;
    }

    if (preorderId) {
      const supabase = createServiceClient();
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
  }

  return NextResponse.json({ received: true });
}
