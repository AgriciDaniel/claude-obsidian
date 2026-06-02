# JobFilter STICKY-TODO — Manual Founder Actions
**Last updated:** 2026-06-02 23:25 UTC

These are tasks that ONLY the founder can complete — they require login access, secrets, payment setup, or human decisions. Code is already written and waiting for these to be unblocked.

---

## 🔴 URGENT — Intake Engine (unblocks GOLD lead WhatsApp notifications)

- [ ] **Set WhatsApp env vars** — Add to Vercel/hosting environment:
  - `WHATSAPP_PHONE_NUMBER_ID` — from Meta Business Suite → WhatsApp → Phone Numbers
  - `WHATSAPP_ACCESS_TOKEN` — from Meta Business Suite → System Users
  - `WHATSAPP_TO` — your mobile number in E.164 format (e.g. `447700900000`) to receive GOLD lead alerts

- [ ] **Create Supabase `intake_submissions` table** — Run in Supabase SQL editor:
  ```sql
  create table if not exists intake_submissions (
    id text primary key,
    username text not null,
    job_type text not null,
    urgency text not null,
    details text,
    postcode text,
    phone text,
    has_photos boolean default false,
    budget text,
    score integer not null,
    tier text not null,
    area text,
    flags text[],
    created_at timestamptz default now()
  );
  create index on intake_submissions (username, created_at desc);
  ```

- [ ] **Set Supabase server-side key** — Add to Vercel/hosting environment:
  - `SUPABASE_SERVICE_ROLE_KEY` — from Supabase dashboard → Settings → API → service_role (secret key)
  - This enables server-side lead persistence and WhatsApp delivery event logging

- [ ] **Verify intake flow end-to-end** — After setting the env vars:
  1. Go to `/my-link` — copy your intake link
  2. Open the intake link in an incognito window
  3. Submit a test job with Emergency urgency + £5,000+ budget
  4. Check your WhatsApp for a GOLD lead notification
  5. Check Supabase `intake_submissions` table for the record

---

## 🟡 HIGH — Supabase & Database

- [ ] **Set Supabase public keys** (if not already set):
  - `NEXT_PUBLIC_SUPABASE_URL` — from Supabase dashboard → Settings → API
  - `NEXT_PUBLIC_SUPABASE_ANON_KEY` — from Supabase dashboard → Settings → API

- [ ] **Verify `delivery_events` table exists** — Used by WhatsApp service to prevent duplicate GOLD lead notifications. Schema is in `server/services/sms.ts` (look at the insert call for field names).

- [ ] **Verify `leads` table exists** — Used by lead scanner persistence (`server/services/leadPersistence.ts`).

---

## 🟡 HIGH — Stripe / Payments

- [ ] **Create Stripe product** — In Stripe dashboard:
  1. Create product: "JobFilter Founder"
  2. Add price: £39.00/month recurring
  3. Copy the Price ID (starts with `price_`)
  4. Set env var: `STRIPE_PRICE_ID_FOUNDING_MONTHLY=price_...`

- [ ] **Set Stripe keys**:
  - `STRIPE_SECRET_KEY` — from Stripe dashboard → Developers → API Keys
  - `STRIPE_PUBLISHABLE_KEY` — same location (public key)
  - `STRIPE_WEBHOOK_SECRET` — from Stripe dashboard → Webhooks → endpoint secret

- [ ] **Register Stripe webhook endpoint**:
  - URL: `https://jobfilter.uk/api/stripe/webhook`
  - Events to listen for: `checkout.session.completed`, `customer.subscription.deleted`, `invoice.payment_failed`

---

## 🟢 MEDIUM — Security

- [ ] **Protect `/test` page from public access** — The `/test` route (`app/test/page.tsx`) is in the public sitemap. Add auth guard or remove from public routing. Any visitor can access your dev console.

- [ ] **Protect `/dev-portal` page** — Similarly, `/dev-portal` should be behind auth.

---

## 🟢 MEDIUM — Lead Engine & Signals

- [ ] **Add missing API keys for signal sources** — Various lead fetchers fail gracefully but return no data without keys:
  - EPC: `EPC_API_KEY` (DLUHC Open Data Communities)
  - Land Registry: no key required but CORS proxy may be needed
  - Companies House: `COMPANIES_HOUSE_API_KEY`
  - Planning data: `PLANNING_API_KEY` (if using paid tier)

- [ ] **Decide on BRONZE tier definition** — Scorer currently returns GOLD/SILVER/BIN. The `LeadDecision.tier` type includes `'BIN'`. Should low-scoring leads be BRONZE (salvageable) or BIN (discard)? Decision affects how leads are displayed to the tradesperson.

---

## 🔵 LOW — Future Features

- [ ] **Tie intake username to account** — Currently `MyLinkPage` generates a random localStorage username per device. When a tradesperson logs in, their intake link should use their account ID so it's stable across devices.

- [ ] **Build intake leads dashboard** — Tradesperson needs a way to see all submitted intake leads in one place (currently they're scattered in Supabase `intake_submissions` and the customer's localStorage).

- [ ] **Add phone validation to intake form** — Step 4 of `IntakePage.tsx` accepts blank phone number silently. Add a soft warning to encourage customers to include their mobile.

- [ ] **Set up DNS / domain** — If not already pointed: `jobfilter.uk` → Vercel deployment.

- [ ] **Add annual pricing tier** — Currently only monthly. An annual option at ~£390 (1 month free) would improve cashflow and reduce churn.

---

*This file is updated automatically by Claude after each audit/implementation run. Archive old versions in `audits/` folder.*
