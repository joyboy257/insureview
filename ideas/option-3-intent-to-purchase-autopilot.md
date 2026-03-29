# Option 3: Intent-to-Purchase Autopilot

**Status:** BLOCKED — Regulatory | Long-Term Vision Only

## Core Thesis

Our insurance autopilot not only analyzes your coverage and tells you what's missing — it **automatically purchases** the right policy for you, with your consent. Like a "set it and forget it" insurance manager that monitors your life situation and executes purchases when gaps are identified.

## The Vision

```
User signs up → Gives consent + budget + constraints
     ↓
AI monitors life situation (family, income, health signals)
     ↓
AI identifies coverage gap
     ↓
AI auto-purchases appropriate policy (under proper MAS license)
     ↓
AI handles renewals, adjusts coverage as life changes
     ↓
User pays transparent fee or small commission
```

## Current Regulatory Reality (Singapore)

### What's Required

- **Financial Advisers Act (FAA):** Recommending insurance = "financial advice" → requires FA license
- **Insurance Act:** Conduct of insurance business regulated; auto-arrangement likely requires license
- **MAS AI Governance (FEAT Principles):** Fairness, Ethics, Accountability, Transparency
- **MAS Veritas Framework:** AI decisions must be explainable and auditable
- **PDPA:** Using personal data (wearables, health indicators) requires explicit consent
- **Liability:** No AI liability law exists — if AI buys wrong policy, unclear who bears loss

### What's NOT Clear

- Whether "consent + budget + constraints" model constitutes regulated advice
- Whether auto-purchase with user consent bypasses licensing
- MAS has not issued autonomous purchase guidelines

## MAS Sandbox Path

**Possibility:** Apply for MAS fintech sandbox (time-limited exemptions)

**What this enables:** Test auto-purchase with real users, real policies, under regulatory supervision

**Timeline:** 6-18 months approval, limited scope, post-sandbox path unclear

**Precedent:** Payment services sandboxes exist; insurance sandbox less established

## Competitive Landscape

| Company | Auto-Purchase? | Notes |
|---|---|---|
| Lemonade | No | AI handles claims/customer service, user selects |
| Policygenius | No | Comparison + guided purchase, not autopilot |
| Root Insurance | Partial | Usage-based auto premium adjustment, not auto-purchase |
| Slice | Partial | Pay-per-use, auto-renewal, not auto-purchase |
| Singapore digital insurers | No | Online purchase exists but manual initiation |

**No true autonomous insurance purchase exists anywhere in the world.**

## What Would Enable This

1. **MAS regulatory clarity** — explicit pathway for automated advisory + arrangement
2. **FA License** — obtain directly or partner with licensed FA
3. **Open Insurance API** — insurer policy issuance APIs for machine purchase
4. **AI liability framework** — Singapore law defining responsibility for AI decisions
5. **Consumer trust** — demonstrated track record of AI recommendations outperforming humans

## Open Questions

- [ ] Can we partner with a licensed FA instead of obtaining our own license?
- [ ] What's the minimum viable auto-purchase product?
- [ ] How do insurers feel about machine-initiated purchases? (Product distribution agreements)
- [ ] What does the user consent flow look like?
- [ ] How do we handle claims when WE purchased the policy on user's behalf?
- [ ] What happens if the AI purchases wrong coverage — liability, recourse?

## The MCP Parallel

Model Context Protocol (MCP) in the AI agent world:
- AI agents pay for capabilities via x402/MPP
- The "insurance autopilot" would be an AI agent that:
  - Discovers it needs coverage via MCP
  - Queries insurer endpoints for policy availability
  - Executes purchase via payment protocol
  - Registers policy in user's portfolio

**This aligns directly with the intent economy thesis from our PLAN.md.**

## Recommended Near-Term Strategy

1. **Phase 1 (Year 1):** Analysis only — gap detection, scenario modeling, portfolio optimization. No auto-purchase.
2. **Phase 2 (Year 2):** Guided purchase — AI recommends, human confirms. Build track record.
3. **Phase 3 (Year 3+):** Apply for sandbox or partner with licensed FA for auto-purchase.

**The intent-to-purchase model is the end state, not the starting point.**

## Open Questions for Near-Term

- [ ] Should we structure as a "FA software provider" partnering with licensed advisors?
- [ ] How does Forgettable's planned in-app purchase feature affect our timeline?
- [ ] What insurers in Singapore are API-ready for programmatic policy issuance?

## Next Steps

- [ ] Meeting with MAS FinTech Office to understand auto-purchase pathway
- [ ] Interview potential FA partners about white-label relationship
- [ ] Map insurer API capabilities in Singapore
