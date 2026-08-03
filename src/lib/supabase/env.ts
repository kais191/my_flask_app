/**
 * Phase 1/2 run side by side: pages call the functions in `src/lib/data/`,
 * which read from Supabase when it's configured and fall back to the typed
 * mock catalog (`src/lib/mock-data.ts`) otherwise. That keeps the site
 * working today and makes flipping to real data a matter of setting these
 * two env vars — no code changes. See README.md for the Supabase setup steps.
 */
export function isSupabaseConfigured(): boolean {
  return Boolean(
    process.env.NEXT_PUBLIC_SUPABASE_URL && process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY
  );
}
