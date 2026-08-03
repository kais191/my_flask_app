import { createClient } from "@/lib/supabase/server";
import { isSupabaseConfigured } from "@/lib/supabase/env";
import { preorders as mockPreorders } from "@/lib/mock-data";
import type { Preorder, PreorderStatus } from "@/lib/types";

interface PreorderRow {
  id: string;
  customer_name: string;
  customer_email: string;
  brand: string;
  style_reference: string | null;
  item_price: number;
  deposit_amount: number;
  status: PreorderStatus;
  created_at: string;
}

function fromRow(row: PreorderRow): Preorder {
  return {
    id: row.id,
    customerName: row.customer_name,
    customerEmail: row.customer_email,
    brand: row.brand,
    styleReference: row.style_reference ?? undefined,
    itemPrice: Number(row.item_price),
    depositAmount: Number(row.deposit_amount),
    status: row.status,
    createdAt: row.created_at,
  };
}

export async function getPreorders(): Promise<Preorder[]> {
  if (!isSupabaseConfigured()) return mockPreorders;

  const supabase = await createClient();
  const { data, error } = await supabase
    .from("preorders")
    .select("*")
    .order("created_at", { ascending: false });

  if (error || !data) {
    console.error("getPreorders: falling back to mock data —", error?.message);
    return mockPreorders;
  }
  return data.map(fromRow);
}
