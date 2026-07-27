import { createClient } from "@/lib/supabase/server";
import { isSupabaseConfigured } from "@/lib/supabase/env";
import { orders as mockOrders } from "@/lib/mock-data";
import type { Order } from "@/lib/types";

interface OrderRow {
  id: string;
  customer_name: string;
  customer_email: string;
  total: number;
  status: Order["status"];
  placed_at: string;
  order_items: { product_name: string; variant: string | null; quantity: number }[];
}

function describeItems(items: OrderRow["order_items"]): string {
  return items
    .map((i) => `${i.product_name}${i.variant ? ` (${i.variant})` : ""}${i.quantity > 1 ? ` x${i.quantity}` : ""}`)
    .join(", ");
}

function fromRow(row: OrderRow): Order {
  return {
    id: row.id,
    customerName: row.customer_name,
    customerEmail: row.customer_email,
    items: describeItems(row.order_items ?? []),
    total: Number(row.total),
    placedAt: row.placed_at,
    status: row.status,
  };
}

export async function getRecentOrders(): Promise<Order[]> {
  if (!isSupabaseConfigured()) return mockOrders;

  const supabase = await createClient();
  const { data, error } = await supabase
    .from("orders")
    .select("*, order_items(product_name, variant, quantity)")
    .order("placed_at", { ascending: false })
    .limit(50);

  if (error || !data) {
    console.error("getRecentOrders: falling back to mock data —", error?.message);
    return mockOrders;
  }
  return data.map(fromRow);
}
