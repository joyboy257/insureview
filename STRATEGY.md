# Insureview — Business Strategy & Engineering Roadmap

**Version:** 1.0
**Date:** 2026-03-29
**Status:** Approved for execution

---

## 1. Product Vision

Insureview is a Singapore-first insurance portfolio intelligence platform. It gives households a unified, plain-English view of what their insurance actually covers — surfacing gaps, overlaps, and conflicts across every policy they hold.

The long-term product is an **autonomous insurance agent**: a system that monitors life events, queries insurer APIs, and executes coverage changes via the MCP/x402 protocol — acting as a persistent, independent guardian of the user's insurance health.

---

## 2. Business Model

### Revenue

| Stream | Model | Rate |
|---|---|---|
| Subscription | Monthly per household | $14.99 Core / $29.99 Pro |
| Guided placement fee | Flat one-time per purchase | $150–400 |
| Autopilot monitoring (Phase 3) | Monthly per household | $49.99 + usage |

### Subscription Tiers

| Tier | Price | Features |
|---|---|---|
| **Free** | $0 | 1 policy, dashboard view only, static analysis |
| **Core** | $14.99/mo | Unlimited policies, gap analysis, annual report, overlap detection |
| **Pro** | $29.99/mo | Scenario builder, FA booking, priority parsing, life event tracking |
| **Autopilot** | $49.99/mo + usage | Autonomous monitoring, API-triggered reviews, MCP/x402 execution |

### Why this pricing works

- Below the $20/mo "mental commitment threshold" for a non-urgent financial product
- Above $0 free-tier that trains users to expect free insurance data
- Commission-based market makes subscription feel premium — households spending $200–400/mo on premiums don't blink at $15/mo for clarity
- Placement fee ($150–400 flat) is the real near-term revenue driver; subscription sustains the engagement loop
- At 50,000 subscribers: ~$10–12M ARR — viable for Series A

---

## 3. Vertical Expansion Plan

### Tier 1 — Young Families *(Now — Year 1)*
**Target:** Singapore married couples aged 25–40 with children
**Why:** Highest insurance density (life + CI + hospitalisation + personal accident + endowment), most policies in force, most confusion. 140,000+ target households. Zero cold-acquisition cost — they arrive already needing help.
**Product:** Portfolio analysis, gap detection, overlap mapping

### Tier 2 — Expatriates *(Year 2)*
**Target:** EP/SP holders with home-country policies + Singapore policies
**Why:** 3–5x insurance complexity (dual systems, international health, repatriation). English-speaking. Willing to pay premium prices. Very high purchase intent.
**Product:** Tier 1 + bilingual support + expat-specific gap modules

### Tier 3 — Small Business Owners *(Year 3)*
**Target:** SME founders and CFOs managing personal + business coverage
**Why:** Life + key-man + business overhead + personal portfolio. Overlap problem is severe and expensive. CFO-level buyer accepts $200–500/mo.
**Product:** Tier 2 + business entity detection + key-man analysis

### Tier 4 — HNW / Family Offices *(Year 4+)*
**Target:** Ultra-high-net-worth individuals, family office clients
**Why:** Full balance sheet view, estate planning, trust integration. Low volume, ultra-high value ($2,000–10,000/engagement). Autopilot is the only viable delivery mechanism at this scale.
**Product:** Tier 3 + MCP/x402 autopilot + licensed FA integration

---

## 4. Regulatory Strategy

### Phase 1–2: No Licence Required
Insureview is a **portfolio analysis and information tool** — it does not constitute financial advice under Singapore's FAA (Financial Advisers Act). MAS has confirmed this framing is viable.

- Operate under MAS FinTech Regulatory Sandbox (Phase 1) for supervised testing
- One-page sandbox application describing the analysis-only product

### Phase 2: FA Partner for Guided Purchases
Guided purchase recommendations require a licensed FA to sign off.

**Approach:** Referral partnership with one boutique fee-only FA firm
- Revenue share: 10–20% of placement fees
- FA holds the licence; Insureview acts as the information layer
- Time to activate: weeks, not months
- No regulatory liability for Insureview

### Phase 3: Own FAS Licence
Autonomous autopilot agent that queries insurer APIs and places coverage automatically **cannot** operate under a partner's licence — the agent IS the adviser.

**Approach:** Apply through MAS FinTech Fast-Track
- Application cost: ~$1,000–2,500
- Compliance infrastructure: $30,000–100,000/yr (compliance officer, appointed actuary, audit)
- By Phase 3 ARR: $5–10M — compliance cost is <2% of revenue
- The autopilot itself is the defensibility moat; the licence is table stakes

---

## 5. Engineering Roadmap

### Phase 1 — Foundation *(Now — 6 months)*
**Goal:** Ship the analysis engine, onboard 100 beta users, prove parse accuracy

**Frontend:**
- [ ] Policy detail page (`/policy/[id]`) — benefit/exclusion rendering
- [ ] MAS FinTech Sandbox application page (`/sandbox`)
- [ ] Seed script: 10 realistic Singapore policy PDFs for demo
- [ ] Onboarding flow: 3-step wizard (upload → parse → dashboard)
- [ ] Email notifications: parse completion, new gap detected

**Backend:**
- [ ] Parsing accuracy loop: human-in-the-loop validation interface
- [ ] Re-digest endpoint: re-parse a policy with updated LLM prompt
- [ ] Policy CRUD with full benefit/exclusion/supporting_document models
- [ ] Auth: magic link email, session management

**Infrastructure:**
- [ ] Celery task monitoring (flower or equivalent)
- [ ] S3 lifecycle policy: auto-delete uploaded PDFs after 24 hours
- [ ] Parse quality scoring: flag low-confidence extracted fields for review

**Business:**
- [ ] MAS FinTech Office intro meeting
- [ ] 100 beta user signups (organic / community)
- [ ] Parse accuracy target: >90% on top 5 insurers (AIA, GE, Prudential, NTUC Income, Great Eastern)

---

### Phase 2 — Guided Purchase *(6–18 months)*
**Goal:** Closed loop from gap → recommendation → purchase

**Product:**
- Guided purchase flow: gap card → "recommended coverage" → "speak to a partner FA"
- FA partner dashboard: real-time lead intake from Insureview gap analysis
- Life event triggers: birthday (age-based coverage gaps), new child, home purchase
- Email/SMS digest: monthly portfolio health score

**Engineering:**
- [ ] FA partner portal (referral dashboard, client snapshot export)
- [ ] Life event tracking model + trigger engine
- [ ] Coverage recommendation engine (rule-based, MAS-compliant)
- [ ] MAS sandbox submission and approval

**Business:**
- [ ] Sign first FA partner
- [ ] 1,000 paying subscribers
- [ ] First placement fee revenue

---

### Phase 3 — Autopilot *(18 months+)*
**Goal:** Autonomous insurance agent operating via MCP/x402 protocol

**Product:**
- Autopilot mode: persistent monitoring of life events + insurer API feeds
- Natural language portfolio reports (Claude-generated, plain English)
- Automated coverage adjustment requests via MCP to insurer systems
- x402 payment protocol for agent-native transactions

**Engineering:**
- [ ] MCP server implementation for each major insurer
- [ ] x402 payment integration (autonomous billing for agent actions)
- [ ] Life event detection: CPF contributions, property transactions, birth registrations
- [ ] Full FAS licence application (if not already in progress)

**Business:**
- [ ] 10,000+ subscribers
- [ ] Autonomous placements at scale
- [ ] Series A raise ($5–10M)

---

## 6. Competitive Position

| | Insureview | Seedly | MoneySmart | Traditional Agent |
|---|---|---|---|---|
| Portfolio-wide view | Yes | No | No | No |
| Gap detection | Yes | No | No | No |
| Plain English | Yes | Partial | Partial | No |
| Commission-free | Yes | Affiliate | Affiliate | No |
| Autonomous updates | Phase 3 | No | No | No |

---

## 7. Risks & Mitigations

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| MAS reclassifies analysis as advice | Low | High | Sandbox first; partner FA model absorbs liability |
| LLM parse accuracy insufficient | Medium | High | Human-in-loop validation; re-digest endpoint; low-confidence flagging |
| Insurers block API access | Medium | High | MCP is open standard; build precedents first |
| FA partner quality hurts brand | Medium | High | Vet partners; NPS tracking; contract exit clause |
| commoditised by incumbents | Medium | High | First-mover data moat; autopilot is the durable differentiation |
