# Intent Economy — Research & Startup Planning

> **Status:** Research Complete | Planning In Progress
> **Created:** 2026-03-27
> **Sources:** X/Twitter threads (@xydotdot, @nlevine19), Stripe Blog, Tempo.xyz, x402.org, YouTube (Algorand Foundation, AI Product Engineer, MIT Sloan CIO, DeepStation AI), last30days research

---

## Executive Summary

The "intention economy" — where AI agents arrive with budgets and constraints, pay for capabilities directly, and move on — is an emerging paradigm shift in commerce. In the last 30 days: 75M x402 transactions, $24M volume, 913 agents on MPP in week 1, and McKinsey calling it a **trillion-dollar opportunity**. The protocols are live. The rails exist. Now the question is: what do we build?

---

## Research Summary

### The Core Thesis

Simon Taylor coined "intention economy": agents arrive with **intent already formed**, a **budget**, and **constraints**. The merchant's only job is to fulfill it. The payment is the authentication. No storefront, no accounts, no sales team — just an endpoint and a price per call.

**The shift:**
- Old: Commerce happened in *places* (store, website, app)
- New: Commerce happens in *moments* (the instant an agent needs a capability)

### The Data (Last 30 Days)

| Protocol / Metric | Value | Source |
|---|---|---|
| x402 transactions (30 days) | **75M** | x402.org |
| x402 volume (30 days) | **$24M** | x402.org |
| x402 sellers | **22K** | x402.org |
| MPP agents (week 1) | **913** | Noah Levine / Stripe |
| MPP transactions (week 1) | **34K** | Noah Levine / Stripe |
| MPP price range | **$0.003 – $35/request** | Noah Levine |
| AliPay AI txns/week | **$120M** | MIT Sloan CIO |
| McKinsey opportunity | **Trillions** | AI Product Engineer |

### Protocol Landscape (All < 14 Months Old)

| Protocol | Purpose | Established |
|---|---|---|
| **x402** (Coinbase) | Payment settlement on-chain | May 2025 |
| **MPP** (Stripe + Tempo) | Machine Payments Protocol — crypto + fiat | Mar 2026 |
| **A2A** (Google, Anthropic, OpenAI) | Agent-to-agent communication | Apr 2025 |
| **MCP** | Model Context Protocol — agents ↔ blockchain wallets | — |
| **AP2** (Google) | Intent mandates + audit trail | Sep 2025 |
| **ERC-804** | Agent registry/discovery | — |
| **UCP** | Universal Commerce Protocol | — |
| **Agent Pay** (Mastercard) | Card token + agent authorization | — |
| **Tempo** (Paradigm + Stripe L1) | Stablecoin payments, 0.6s finality | Sep 2025 |

### The Three-Layer Opportunity (@xydotdot)

1. **Merchant Creation** — turning any tool/workflow/model into a paid endpoint
2. **Commerce Infrastructure** — metering, pricing, billing, payouts, fraud controls
3. **Discovery** — agents comparing services by reliability, latency, price, success rate ← **BIGGEST**

### Key Insights

- **Discovery is the bottleneck.** Marc Vanlerberghe (Algorand): ERC-804 is "the agentic Yahoo" — a phone book, not a search engine. We need agentic Google.
- **Subscriptions don't work for agents.** AI Product Engineer: "Agents are digital ghosts. They exist to complete a goal, not to stick around." Charging them like long-term customers is flawed.
- **The liability framework is still being figured out.** Bernard Kresby (MIT Sloan): "We're still in an era of human in the middle." Who owns the liability when an agent makes a bad decision? Unknown.
- **First-party fraud is rising.** 6.2x increase (Stripe, Nov 2025 – Feb 2026). Traditional fraud tools have minimum economics that don't work at $0.003-$35/request.
- **Human checkout flows are dead for agents.** Bernard: "Click to buy will be gone. Future is human not present, seamless transactions with audit trail."

---

## Ranked Startup Ideas

### 1. Intent Marketplace ⭐ 85% Confidence
**Two-sided exchange where agents publish purchasing intents and merchants compete to fulfill.**

Why it wins: Directly answers the discovery problem — the biggest beast. Inverts traditional commerce: instead of merchants advertising to buyers, agents advertise intent and merchants bid for the right to fulfill.

Key dynamics:
- Agents publish: budget, constraints, timing
- Merchants compete in real-time
- Reverse auction model

Risks: Chicken-and-egg on both sides. Requires early vertical focus.

---

### 2. Proof-of-Fulfillment Attestations (PoFA) ⭐ 80% Confidence
**Reputation derived from actual payment outcomes, not reviews.**

How it works: Merchants attest to capabilities (uptime, defect rates, delivery windows). Claims are cryptographically verified against actual x402/MPP transaction outcomes. Payment completion = the only honest signal.

Why it wins: In the headless merchant world, the only honest signal is the one that costs money. 75M x402 txns already have the ground truth data — you just build on top of it.

Key insight: "The payment is the authentication" extends to "the payment history is the reputation."

Risks: Needs cooperation from x402/MPP to expose attestation APIs.

---

### 3. Agent-to-Agent Metering & Attribution Hub ⭐ 80% Confidence
**Tracks which agents call which downstream APIs, meters in real-time, splits revenue.**

Why it wins: As agents compose on other agents, nobody can track who used what and who owes whom. This is the analytics + billing layer for the agent supply chain — only makes sense in this world.

Risks: Requires protocol-level instrumentation. Needs cross-protocol adoption.

---

### 4. Micro-Escrow with Automated Dispute Resolution ⭐ 75% Confidence
**Smart escrow for $0.003–$35 range — holds payment until verifiable fulfillment events.**

The problem: At $0.003/transaction, traditional chargeback economics don't work. Existing dispute infrastructure was designed for humans.

How it works: Holds payment until receiving cryptographically-signed fulfillment confirmations (IPN webhooks, multi-sig merchant attestations, tracking confirmations). Automated machine-speed arbitration.

Risks: "Verifiable fulfillment" is category-specific. Image generation differs from physical goods.

---

### 5. Merchant Failure Fallback Router ⭐ 70% Confidence
**Auto-reroute when merchant API fails — preserves agent intent and payment.**

Why: In the intention economy, the agent arrives with payment ready and intent formed. Merchant failure after payment commit = worst outcome. Automatic fallback converts failed commerce into successful commerce.

Risks: Requires real-time merchant health monitoring. Harder for specialized services with no direct substitutes.

---

### 6. Agent Reputation Registry (ARR) ⭐ 70% Confidence
**Portable cryptographic identity for agents — nonce-chain based, merchant-queryable.**

The problem: First-party fraud up 6.2x. Agents operate anonymously but have persistent payment identities. Merchants need to evaluate agents too, not just the other way around.

Key insight: "The payment is the authentication" extends to "the payment history is the reputation." Nonce chains = identity without KYC.

Risks: Needs cross-protocol adoption (x402 + MPP). Privacy implications.

---

### 7. Bid-Ask Engine for B2B Agent Negotiations ⭐ 60% Confidence
**Machine-readable bid-ask spreads — enables automated price negotiation between agents.**

Why: B2B commerce runs on negotiation, not fixed prices. $0.003–$35/request range shows massive price variance. A bid-ask mechanism lets agents find the best price without human back-and-forth.

Risks: Requires standardization of message formats. Only for commodity services initially.

---

## What We Found (Additional)

### Emerging Standards (from Algorand keynote)
- **ERC-804** is "agentic Yahoo" — phone book model, no ranking/discovery
- **ERC-8004** = Algorand's answer — need to differentiate from the Yahoo model
- **A2A + MCP + AP2 + ERC-804 + x402** stack together for end-to-end flow

### Agentic Commerce Stack (from Mastercard demo)
```
User Intent → Card Mandate → Payment
    ↑            ↑             ↑
  Natural     Cryptographic   Token-based
  language     authorization   settlement
```
- Auto-approval limits ($100 demo threshold)
- Token-based (not card numbers passed to agents)
- Audit trail after the fact

### The Liability Question (Unsolved)
- Bernard Kresby: "Who is responsible when an agent makes a bad decision?"
- Irv Vlisha: "Commerce requires determinism. AI is probabilistic by nature."
- No clear answer yet — this is both a risk AND an opportunity

### The Goldilocks Problem (x402)
Buyer and seller must be on same chain + same currency. Atomic grouping (Algorand's answer) solves cross-currency swaps in single block.

---

## Next Steps

- [ ] **Decide which idea to pursue first** — top candidates: Intent Marketplace or PoFA
- [ ] **Identify first-mover advantage** — what can we ship in 30 days?
- [ ] **Evaluate vertical focus** — which industry/sector to target first?
- [ ] **Assess build vs. partner** — do we need x402/MPP/Tempo partnerships?

---

## Appendix: Sources

- @xydotdot (X, Mar 25, 2026) — Three-layer headless merchant framework
- @nlevine19 (X, Mar 24, 2026) — "Entering the Era of the Headless Merchant"
- Stripe Blog (Mar 18, 2026) — Introducing the Machine Payments Protocol
- Stripe Blog (Mar 12, 2026) — 10 Things We Learned Building for the First Generation of Agentic Commerce
- tempo.xyz — Tempo blockchain, Paradigm + Stripe incubated
- x402.org — 75M transactions, $24M volume, 22K sellers (30-day stats)
- Algorand Foundation (Feb 28, 2026) — Agentic Commerce keynote, Marc Vanlerberghe
- AI Product Engineer (Mar 26, 2026) — "The Death of Subscription Models" (6 views, just posted)
- MIT Sloan CIO Symposium (Feb 26, 2026) — "Who Controls Revenue in a Machine-to-Machine Economy"
- DeepStation AI (Feb 25, 2026) — Agentic Payments demo with Mastercard's Agent Pay
