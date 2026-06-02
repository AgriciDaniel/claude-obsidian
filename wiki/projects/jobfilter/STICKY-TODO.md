# JobFilter STICKY-TODO
Last updated: 2026-06-02 23:21 UTC

**MANUAL tasks only — things only the founder can do.**

---

## 🔴 URGENT: Intake Engine — Env Vars Required

The intake engine code is now fixed (lead persistence + WhatsApp now implemented). But it will silently fall back to no-op without these secrets set in your hosting environment (Vercel / wherever you deploy):

- [ ] **Set `SUPABASE_SERVICE_ROLE_KEY`** — needed for server-side Supabase writes (lead persistence). This is different from the anon key. Get it from Supabase dashboard → Settings → API.
- [ ] **Set `NEXT_PUBLIC_SUPABASE_URL`** — needed for client-side Supabase auth.
- [ ] **Set `NEXT_PUBLIC_SUPABASE_ANON_KEY`** — needed for client-side Supabase auth.
- [ ] **Set `WHATSAPP_PHONE_NUMBER_ID`** — your Meta WhatsApp Business phone number ID.
- [ ] **Set `WHATSAPP_ACCESS_TOKEN`** — your Meta WhatsApp permanent or temp access token.
- [ ] **Set `WHATSAPP_TO`** — your personal WhatsApp number (in E.164 format, e.g. `447700900000`) for GOLD lead notifications. Or pass `phone` from the lead.
- [ ] **Register a WhatsApp message template** called `gold_lead_alert` in Meta Business Manager. The current code sends free-form text — this only works within 24h of a user-initiated conversation. For proactive notifications you need an approved template (see BUILD PROMPT BP-5 in the audit).

---

## 🟡 HIGH PRIORITY: Supabase Schema

The intake engine now calls `persistLeads()` which upserts into the `leads` table. Verify these tables exist in Supabase:

- [ ] **Check `leads` table exists** with columns: `id`, `title`, `trade`, `location`, `postcode_outward`, `estimated_value`, `urgency`, `source`, `source_confidence`, `contact_signal`, `status`, `score`, `fusion_key`, `source_url`, `buyer_name`, `published_at`, `deadline_at`, `quality_label`, `ghost_risk`, `signal_class`, `signal_stack`, `evidence_badges`, `score_reasons`, `recommended_action`, `contact_path`, `opportunity_atoms`, `why_this_is_a_job`, `is_commercial`, `payload`, `updated_at`
- [ ] **Check `delivery_events` table exists** with columns: `id`, `lead_id`, `phone`, `provider`, `channel`, `message_body`, `status`, `delivery_status`, `sent_at`, `error`, `is_duplicate`, `next_action`, `score_at_delivery`, `score_reasons_at_delivery`, `contact_path_used`, `delivery_lock_key`
- [ ] Run the Supabase migration files in `/home/user/JobFilterV1/supabase/migrations/` if these tables don't exist.

---

## 🟡 HIGH PRIORITY: Stripe Setup

- [ ] **Set `STRIPE_SECRET_KEY`** — from Stripe dashboard.
- [ ] **Set `STRIPE_WEBHOOK_SECRET`** — from Stripe dashboard after creating a webhook endpoint pointing to `https://yourdomain.com/api/stripe/webhook`.
- [ ] **Set `STRIPE_PRICE_*` env vars** — the founding monthly price ID. Check `app/api/stripe/checkout/route.ts` or `server/routes/stripe.ts` for the exact var names needed.
- [ ] **Set `NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY`** — for the client-side Stripe checkout.
- [ ] **Test a £0.01 checkout end-to-end** before going live.

---

## 🟡 HIGH PRIORITY: Tradesman → Lead linking

- [ ] **Decide on intake routing model**: When a customer submits at `/intake/[username]`, the lead should be visible to that tradesman. This requires a `profiles` table with `username → user_id` mapping. Does this table exist? If not, create it. Then implement BP-2 from the audit build prompts.

---

## 🟠 MEDIUM: API Keys for Lead Sources

Without these, the scan engine returns empty/demo results:

- [ ] **`COMPANIES_HOUSE_API_KEY`** — Companies House API for business registrations. Free at api.company-information.service.gov.uk
- [ ] **`EPC_BEARER_TOKEN`** — Energy Performance Certificate API. Register at epc.opendatacommunities.org
- [ ] **Planning API** — check `leadEngine/fetchers/` for what planning source is used and what key it needs
- [ ] **`GEMINI_API_KEY`** or **`OPENAI_API_KEY`** — for AI lead enrichment (document extraction). Optional but improves lead quality.
- [ ] **`N8N_WEBHOOK_URL`** and **`N8N_API_KEY`** — for n8n automation workflows. Only needed if you're using n8n.

---

## 🟠 MEDIUM: Domain & Deployment

- [ ] **Confirm primary domain** — `jobfilter.uk` or `jobfilter.co.uk`? The `.env.example` has `VITE_SITE_URL=https://jobfilter.uk`. Update all references to match.
- [ ] **Set `NEXT_PUBLIC_APP_URL`** and `APP_URL` in Vercel env vars.
- [ ] **Verify Vercel deployment config** — `vercel.json` is present. Confirm it's deploying the Next.js build, not the Express server.

---

## 🟢 LOW PRIORITY: Manual Content

- [ ] **Add customer testimonials** — at least 2-3 on the pricing page and homepage. No code changes needed — just write them and add to `PricingPage.tsx`.
- [ ] **Create a `profiles` table** in Supabase with `username` column if it doesn't exist — needed for intake-to-tradesman routing.
- [ ] **Review the `/test` page** at `/app/test/page.tsx` — it's publicly accessible. If it contains dev tools, move it behind the admin guard.
- [ ] **Register WhatsApp Business Account** if not already done — required for the WhatsApp notification feature.
- [ ] **Apply for Resend production access** — `RESEND_API_KEY` is in `.env.example`. Free tier has sending limits.

---

## ✅ Done This Run (2026-06-02)

- Fixed intake engine: leads now persist to Supabase, GOLD leads trigger WhatsApp
- Fixed `'BIN'` → `'BRONZE'` tier label throughout
- Expanded Express intake route job type whitelist (4 → 9 types)
- Fixed `Budget` vs `GoodBudget` flag display bug
- Polished intake form copy (step titles, placeholders, CTA)
- Fixed nav subtitle "Construction Intelligence" → "UK Trade Leads"
- Reordered public nav: Pricing now in position 3 for better conversion
