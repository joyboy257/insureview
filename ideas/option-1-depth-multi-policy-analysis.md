# Option 1: Depth — Multi-Policy Analysis Engine

**Status:** Most Differentiated | Highest Defensibility

## Core Thesis

Go deeper than any existing tool — including Forgettable — by building a multi-policy analysis engine that does what no other product does: detects overlaps AND conflicts across your existing policies, models complex life scenarios, surfaces hidden coverage redundancies, and optimizes your portfolio like a financial advisor does for investments.

## What Makes This Different from Forgettable

| Feature | Forgettable | This Option |
|---|---|---|
| Portfolio aggregation | ✅ | ✅ |
| Plain language explanations | ✅ | ✅ |
| Gap detection | Future | ✅ Core |
| Overlap/Redundancy detection | ❌ | ✅ Core |
| Multi-policy conflict resolution | ❌ | ✅ Core |
| Scenario modeling (life events) | ❌ | ✅ Core |
| Insurer claims history analysis | ❌ | ✅ Core |
| Portfolio optimization | ❌ | ✅ Core |

## Product Features (Stack)

### Layer 1: Data Ingestion
- [ ] Aggregate policies from email, PDF, portals (Forgettable's core)
- [ ] Parse policy documents using AI contract parsing
- [ ] Build machine-readable policy database across all Singapore insurers
- [ ] Ongoing sync with policy issuers via APIs (where available)

### Layer 2: Analysis Engine
- [ ] Gap detection — what's NOT covered
- [ ] **Overlap detection — where you're paying for redundant coverage**
- [ ] **Conflict detection — where policies contradict each other**
- [ ] Coverage ceiling analysis — when one policy limits another's payout
- [ ] **Insurer claims history analysis — payout ratios by insurer/product**

### Layer 3: Scenario Modeling
- [ ] What-if: spouse dies + income loss
- [ ] What-if: critical illness diagnosis + treatment costs
- [ ] What-if: job loss + coverage continuation
- [ ] Multi-event scenarios (compounding events)
- [ ] Family lifecycle modeling

### Layer 4: Portfolio Optimization
- [ ] "You have $500K in overlapping term life from 2 insurers — consolidate here"
- [ ] "This insurer has historically paid 78% of CI claims — consider switching"
- [ ] "Your coverage ceiling here conflicts with the cap in your other policy"
- [ ] Personalized portfolio score
- [ ] Optimization recommendations ranked by impact

## Key Research Findings

### Multi-Policy Cross-Referencing
- Essentially a **blank market** globally
- No competitor found doing overlap AND conflict detection
- All existing tools focus on "what's missing," not "what's duplicated or contradicting"

### Coverage Redundancy Detection
- **No dedicated product exists anywhere**
- Closest: calculators that measure against benchmarks, not against actual existing portfolio
- "You're paying for overlapping coverage" is a novel concept in product form

### Scenario Modeling
- No tool found models interconnected life events
- Existing tools: single-variable calculators (SmartAsset, Principal, MoneySense)
- Estate planning tools (Wealth.com) come closest but focus on tax/estate, not insurance events
- Gap: "what if my spouse dies AND I get cancer simultaneously" — not modeled anywhere

### Insurer Claims History
- Singapore insurers do NOT publish detailed claims payout ratios publicly
- LIA publishes industry-level data only
- A product surfacing "insurer X paid only 78% of CI claims historically" would be **highly differentiating**
- Data acquisition challenge: requires partnerships or scraping/IRAS filings

### State of AI for This
- AI in insurance today focused on: underwriting automation, claims processing, chatbots, risk scoring
- AI for multi-policy portfolio analysis is **not a visible category** anywhere
- Current AI contract parsing (legal document AI) can be adapted for insurance policies

## Competitive Landscape

- **Forgettable** — aggregation + explanation, gap detection is roadmap
- **PolicyPal** — comparison, not deep analysis
- **MoneyHero/Seedly/MoneySmart** — comparison platforms, sell policies
- **DirectAsia** — own policies only
- **Global** — no "robo-advisor for insurance" exists as a category

## Data Acquisition for Claims History

### What We Learned

Singapore insurers do NOT publish product-level claims payout ratios publicly.

| Data Source | What We Can Get | Insurer-Level? |
|---|---|---|
| LIA Industry Statistics | Aggregate claims ratios, industry-wide | ❌ No |
| IRAS Filings | Confidential corporate tax data | ❌ No |
| Insurer Annual Reports | High-level claims amounts, not by product | Partial |
| MAS Insurance Survey | Industry aggregate only | ❌ No |
| compareFIRST (LIA portal) | Product specs only, no claims data | ❌ No |
| Media | Individual complaint cases, not systematic | ❌ No |

### Viable Path: User-Reported Claims Database

**Most realistic approach — has network effects:**

How it works:
- Users submit their claims experience: insurer, product, claim type, outcome (paid/partial/rejected), payout vs. claimed
- Aggregate into searchable database
- Display: "X% of [insurer] [product type] claims were paid in full"

Requirements:
- Claims reference number (partial) for verification
- Moderation to prevent gaming
- Scale: 500+ submissions per insurer/product before statistically meaningful

Timeline: 3-6 months to MVP for this specific feature

### Partnership Approach (Long Game)

1. Go through LIA first — get industry blessing
2. Start with NTUC Income (most transparent, cooperative model)
3. Offer co-marketing value in return
4. Legal: PDPA compliance required for any user-level data sharing

## MAS Regulatory Requirements

### The Core Distinction

| Activity | License Required? | Notes |
|---|---|---|
| Generic policy explanations | No | Safe zone |
| Portfolio aggregation (describe what exists) | Likely No | Safe zone |
| Gap analysis ("you have a gap") | **Likely Yes** | Crosses into advice |
| Redundancy analysis ("you're overpaying") | **Likely Yes** | Implies disposition action |
| Conflict detection (policies contradict) | **Likely Yes** | Implies restructuring |
| Scenario modeling (personalized) | Gray Area | Depends on framing |
| Specific product recommendation | **Yes** | Red line |

**The test:** If a reasonable person would interpret your output as a recommendation to act = regulated financial advice.

### Safe Architecture for Option 1

The product CAN describe:
- "Your portfolio includes X. It does not include coverage for Y." (description, not recommendation)
- "Typical Singapore households carry X times annual income in life coverage." (benchmark, not personalized advice)
- "Your two policies both pay death benefit — here is how they interact." (factual analysis)

The product CANNOT say:
- "You have a critical illness coverage gap and should fill it." (advice)
- "You're paying for redundant coverage — cancel policy B." (advice)
- "Based on your situation, you need $500K more life coverage." (advice)

**Key architectural decision:** Build the analysis engine to output factual descriptions + benchmarks. Let the USER draw conclusions. This keeps us in "information service" territory.

### Compliance Roadmap

**Pre-Launch (Month 1-3):**
- [ ] Engage Singapore regulatory lawyer (Allen & Gledhill, Rajah & Tann)
- [ ] Schedule pre-submission meeting with MAS FinTech Office
- [ ] Draft PDPA-compliant Privacy Policy + consent flows
- [ ] Implement data processing agreements with LLM providers
- [ ] Build robust disclaimers: "This is not financial advice"

**Launch:**
- [ ] Information-only features (no personalized recommendations)
- [ ] Clear disclaimers on all outputs
- [ ] Structured as "analysis for your consideration"

**Scale:**
- [ ] Consider FA license pathway for recommendation features later
- [ ] Consider MAS sandbox for more advanced auto-purchase features (Option 3)

### MAS FinTech Office

**Critical action:** Schedule a pre-submission meeting with MAS FinTech Office before building. They are approachable and want to support innovation. Get informal guidance on specific product architecture.

## Technology Stack

### Parsing Pipeline

```
User uploads PDF → Born-digital check
  → Born-digital: pypdf2/pdfplumber direct text extraction (100% accuracy)
  → Scanned: Google Document AI OCR (85-93% accuracy)
  → Claude Opus 4 (200K context) per-section chunk parsing
  → JSON schema validation + confidence scoring
  → Low-confidence fields → human review queue
  → Structured policy data stored per-user
```

### Key Technology Decisions

| Component | Choice | Rationale |
|---|---|---|
| OCR | Google Document AI | Best table handling for benefit schedules |
| LLM | Claude Opus 4 | 200K context = full policy in one prompt; superior legal reasoning |
| Fallback LLM | GPT-4o | Faster, cheaper for simpler extractions |
| Data model | Custom JSON schema | No industry standard for policy content; ACORD is transaction-focused |
| Born-digital | pdfplumber | 100% text accuracy, no OCR needed |

### Singapore-Specific Parsing Advantages

- **LIA 37 CI definitions** are standardized across all insurers — CI benefit triggers are comparable
- **MAS Benefit Illustration standard** — mandated format for premium projections
- **English-only requirement** — simplifies parsing vs. multi-language markets
- **~60-70% templatable** — rest needs LLM inference + per-insurer adapters

### Data Model (Proposed Schema)

```json
{
  "policy": {
    "metadata": { "insurer", "product_name", "policy_number", "issue_date" },
    "sum_assured": { "total", "breakdown" },
    "benefits": [
      { "benefit_id", "benefit_type", "trigger_conditions", "amount", "payment_structure", "exclusions", "active" }
    ],
    "riders": [...],
    "exclusions": [...],
    "conditions": { "contestability_months", "free_look_days", "notification_deadline" }
  }
}
```

### Known Parsing Challenges

- Rider naming varies by insurer — requires canonical taxonomy mapping
- Outstanding policy loans reduce net sum assured — extract both gross + loan fields
- Multi-event benefit interactions (CI payout doesn't reduce death benefit in some policies)
- LIA CI definitions updated periodically (last: 2021) — version-stamp extractions

## Singapore Insurance Product Landscape

### Product Taxonomy (For Analysis Engine)

| Category | Key Products | Notes |
|---|---|---|
| **Term Life** | Fixed-term, affordable | Easiest to analyze |
| **Whole Life** | Lifetime + savings | Complex cash value interactions |
| **Endowment** | Savings + protection | |
| **ILP** | Insurance + investment | Fund value affects net insurance cost |
| **Critical Illness** | 37 LIA-standardized conditions | Stage-based payouts (early/intermediate/late) |
| **Hospitalisation** | MediShield Life + IP stacking | Cannot exceed 100% of actual costs |
| **Dread Disease** | More restrictive than CI | Often rider, not standalone |
| **Disability** | Income replacement | |

### MediShield Life + Integrated Shield Plans (Singapore-Specific)

This is uniquely Singapore and a critical analysis layer:

```
Layer 1: MediShield Life (base, CPF-funded)
  → Large bills above S$3-6K deductible, Class B2/C ward

Layer 2: Integrated Shield Plan (private)
  → Ward upgrade (B1/A/private), higher limits, lower co-pay

Analysis challenge: How private IP reduces MediShield Life deductible
```

### Key Multi-Policy Interaction Points

1. **Life + CI stacking**: Both pay independently on death/CI — can double-pay (no cap)
2. **Hospitalisation plans**: Cannot exceed 100% of actual costs across ALL plans
3. **MediShield Life + IP**: IP claims reduce MediShield deductible; patient co-pay is the key number
4. **Term + Whole Life**: Different purposes — term for income replacement, whole for estate
5. **ILP fund value**: Affects net insurance coverage cost

### LIA CI Standardization

- 37 CI conditions have LIA-standardized definitions
- **Core 3** (heart attack, cancer, stroke): consistent across all insurers
- Other 34: insurers may add enhancements, definitions vary
- Stage-based payouts: early (20-50%), intermediate (30-50%), advanced/late (remainder)

### Premium Benchmarks (2025-2026)

| Age | Term Life S$500K/20yr | CI S$100K multiple-pay |
|---|---|---|
| 30M | S$35-55/mo | S$80-150/mo |
| 40M | S$70-120/mo | S$180-350/mo |

## Open Questions

- [x] How do we acquire insurer claims payout data? → **User-reported database is MVP path**
- [x] What is the data model for machine-readable policies? → **Custom JSON schema — no industry standard**
- [x] Singapore-specific: MediShield Life + Integrated Shield Plans + private → **Documented above — hospitalisation stacking rules, ILP interactions**
- [x] MAS licensing: does deep analysis constitute "financial advice"? → **Build as information service — descriptive outputs only**
- [ ] What's the minimum viable policy set to ingest and analyze? → **Term Life + CI + Hospitalisation (3 policies covering main gaps)**
- [ ] How to build per-insurer adapters efficiently? → **Start with top 3 insurers (AIA, Great Eastern, Prudential)**
- [ ] Pilot test parsing accuracy on real Singapore policy documents

## Pricing Model Ideas

- Per-report fee ($X per deep analysis)
- Annual subscription ($X/month for ongoing monitoring)
- Freemium: basic aggregation free, deep analysis paid
- B2B: sell to employers for employee financial wellness

## Next Steps

### Immediate (Month 1)
- [ ] Engage Singapore regulatory lawyer (Allen & Gledhill, Rajah & Tann)
- [ ] Schedule pre-submission meeting with MAS FinTech Office
- [ ] Collect 20 real Singapore policy PDFs across top 3 insurers for accuracy testing
- [ ] Build MVP parsing pipeline (pdfplumber → Document AI → Claude Opus)
- [ ] Design user consent flow + PDPA Privacy Policy

### Month 2-3 (Pre-Launch)
- [ ] Pilot parsing accuracy on 20 documents — measure error rates
- [ ] Build gap/overlap/conflict detection rules engine
- [ ] Build MediShield Life + IP interaction calculator
- [ ] Integrate LIA 37 CI definitions as canonical taxonomy
- [ ] Ship v1: policy aggregation + plain English summary + gap overview

### Month 4-6 (Beta)
- [ ] Launch to 100 beta users (invite-only)
- [ ] Collect claims experience submissions (start user-reported database)
- [ ] Iterate on analysis engine based on user feedback
- [ ] Build scenario modeling (death + CI + job loss)

### Year 1 (Scale)
- [ ] FA license application OR licensed FA partnership
- [ ] Claims database crosses 500 submissions per major insurer
- [ ] Expand to SME group insurance use case (B2B)

