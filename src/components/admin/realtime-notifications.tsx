"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { createClient } from "@/lib/supabase/client";

interface Toast {
  id: number;
  tone: "accent" | "warn";
  title: string;
  body: string;
}

let nextId = 1;

export function AdminRealtimeNotifications() {
  // Next's useRouter() returns a stable object, so it's safe to depend on
  // without re-subscribing the realtime channel on every render.
  const router = useRouter();
  const [toasts, setToasts] = useState<Toast[]>([]);

  function push(toast: Omit<Toast, "id">) {
    const id = nextId++;
    setToasts((prev) => [...prev, { ...toast, id }]);
    setTimeout(() => setToasts((prev) => prev.filter((t) => t.id !== id)), 7000);
  }

  useEffect(() => {
    const supabase = createClient();

    const channel = supabase
      .channel("admin-notifications")
      .on(
        "postgres_changes",
        { event: "INSERT", schema: "public", table: "orders" },
        (payload) => {
          const order = payload.new as { customer_name: string; total: number };
          push({
            tone: "accent",
            title: "New order",
            body: `${order.customer_name} — $${Number(order.total).toFixed(2)}`,
          });
          router.refresh();
        }
      )
      .on(
        "postgres_changes",
        { event: "UPDATE", schema: "public", table: "products" },
        (payload) => {
          const next = payload.new as { name: string; stock_quantity: number; low_stock_threshold: number };
          const prev = payload.old as { stock_quantity: number; low_stock_threshold: number } | undefined;
          const nowLow = next.stock_quantity <= next.low_stock_threshold;
          const wasLow = prev ? prev.stock_quantity <= prev.low_stock_threshold : false;

          if (nowLow && !wasLow) {
            push({
              tone: "warn",
              title: "Running low",
              body: `${next.name} — ${next.stock_quantity} left`,
            });
          }
          router.refresh();
        }
      )
      .subscribe();

    return () => {
      supabase.removeChannel(channel);
    };
  }, [router]);

  if (toasts.length === 0) return null;

  return (
    <div className="fixed inset-x-4 top-4 z-50 flex flex-col gap-2 sm:inset-x-auto sm:right-4 sm:w-80">
      {toasts.map((toast) => (
        <div
          key={toast.id}
          role="status"
          className={`rounded-xl border px-4 py-3 shadow-lg ${
            toast.tone === "warn"
              ? "border-[#e3b98f] bg-[#fbf1e4] text-[#8a5a1f]"
              : "border-[#e9c9bc] bg-[#F6E4DC] text-rose-dark"
          }`}
        >
          <p className="text-xs font-bold uppercase tracking-wide">{toast.title}</p>
          <p className="text-sm text-ink">{toast.body}</p>
        </div>
      ))}
    </div>
  );
}
