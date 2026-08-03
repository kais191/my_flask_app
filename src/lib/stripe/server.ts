import Stripe from "stripe";

let stripe: Stripe | null = null;

/** Throws if called without STRIPE_SECRET_KEY set — always check isStripeConfigured() first. */
export function getStripe(): Stripe {
  if (!process.env.STRIPE_SECRET_KEY) {
    throw new Error("STRIPE_SECRET_KEY is not set");
  }
  if (!stripe) {
    stripe = new Stripe(process.env.STRIPE_SECRET_KEY);
  }
  return stripe;
}
