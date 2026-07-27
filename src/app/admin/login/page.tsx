import { redirect } from "next/navigation";
import { createClient } from "@/lib/supabase/server";
import { isSupabaseConfigured } from "@/lib/supabase/env";

async function signIn(formData: FormData) {
  "use server";

  const email = String(formData.get("email") ?? "");
  const password = String(formData.get("password") ?? "");
  const next = String(formData.get("next") ?? "/admin");

  const supabase = await createClient();
  const { error } = await supabase.auth.signInWithPassword({ email, password });

  if (error) {
    redirect(`/admin/login?error=${encodeURIComponent(error.message)}&next=${encodeURIComponent(next)}`);
  }

  redirect(next);
}

export default async function AdminLoginPage({
  searchParams,
}: {
  searchParams: Promise<{ next?: string; error?: string }>;
}) {
  const { next = "/admin", error } = await searchParams;

  if (!isSupabaseConfigured()) {
    return (
      <div className="mx-auto flex min-h-[70vh] max-w-md flex-col justify-center px-4">
        <h1 className="mb-2 text-xl">Admin sign-in isn&rsquo;t needed yet</h1>
        <p className="text-sm text-ink-soft">
          Supabase isn&rsquo;t configured, so <code className="text-ink">/admin</code>{" "}
          is open by default (Phase 1 mock-data mode). Add{" "}
          <code className="text-ink">NEXT_PUBLIC_SUPABASE_URL</code> and{" "}
          <code className="text-ink">NEXT_PUBLIC_SUPABASE_ANON_KEY</code> to{" "}
          <code className="text-ink">.env.local</code> to turn on real sign-in.
        </p>
      </div>
    );
  }

  return (
    <div className="mx-auto flex min-h-[70vh] max-w-md flex-col justify-center px-4">
      <p className="font-display mb-1 text-lg italic text-ink">Beauty House</p>
      <h1 className="mb-6 text-xl">Admin sign-in</h1>

      {error && (
        <p className="mb-4 rounded-xl border border-[#e3b98f] bg-[#fbf1e4] px-4 py-3 text-sm text-[#8a5a1f]">
          {error}
        </p>
      )}

      <form action={signIn} className="flex flex-col gap-3">
        <input type="hidden" name="next" value={next} />
        <input
          type="email"
          name="email"
          required
          placeholder="Email"
          className="rounded-xl border border-line bg-surface px-4 py-3 text-sm text-ink placeholder:text-ink-soft"
        />
        <input
          type="password"
          name="password"
          required
          placeholder="Password"
          className="rounded-xl border border-line bg-surface px-4 py-3 text-sm text-ink placeholder:text-ink-soft"
        />
        <button className="mt-1 w-full rounded-full bg-rose py-3.5 text-sm font-bold text-white transition-transform hover:scale-[1.01]">
          Sign in
        </button>
      </form>
    </div>
  );
}
