# Insureview

**See your entire insurance picture — in plain English — for the first time.**

Insureview is a web app for Singapore residents that ingests insurance policy documents (PDF), parses them into structured data, and reveals what no other tool reveals: where your policies overlap, where they conflict, and what gaps exist across your full portfolio.

## The Problem

Most Singapore households hold multiple insurance policies — term life, critical illness, hospitalisation, Integrated Shield Plans — bought over years from different agents. Almost nobody can answer:

- Do I have gaps in my coverage?
- Am I paying for coverage I already have twice?
- Do my policies contradict each other on what they pay out?

Existing tools (PolicyPal, Forgettable, MoneyHero) show what's in **one** policy. Insureview shows how **all** your policies **interact**.

## How It Works

```
Upload your policies (PDF)
    → AI parses each policy into structured data
    → Analysis engine detects gaps, overlaps, and conflicts
    → Portfolio dashboard shows your full coverage picture
```

## Features

| Feature | Description |
|---|---|
| **Gap Detection** | What coverage types you don't have at all (death, CI, hospitalisation, disability) |
| **Overlap Map** | Where multiple policies double-cover the same risk |
| **Conflict Alerts** | Where policies have contradictory terms (e.g. different survival periods for CI) |
| **Plain English** | Every policy translated into simple explanations, not insurance jargon |
| **Scenario Modeling** | "What if my spouse dies AND I get cancer?" — multi-event compounding |
| **MediShield + IP Calculator** | How MediShield Life and your Integrated Shield Plan stack together |

## Regulatory Positioning

Insureview is an **information service**, not financial advice. It describes what your portfolio contains and how policies interact — it never tells you to buy, cancel, or switch. All outputs carry the mandatory MAS disclaimer.

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | Next.js 14, React 18, TypeScript, Tailwind CSS |
| Backend | Python FastAPI, SQLAlchemy 2.0 (async) |
| Database | PostgreSQL 15+ with row-level security |
| PDF parsing | pdfplumber (born-digital) + Google Document AI (scanned) |
| LLM | Claude Opus 4 (200K context window) |
| File storage | S3-compatible (raw PDFs auto-deleted after parsing) |
| Auth | NextAuth.js (email magic link) |
| Task queue | Celery + Redis |

## Architecture

```
intent-economy/
├── apps/
│   ├── frontend/          # Next.js 14 (App Router, 5 routes)
│   └── backend/          # Python FastAPI (26 modules)
├── packages/
│   └── shared/           # Canonical policy JSON schema
├── infrastructure/         # Docker Compose (PostgreSQL, Redis, LocalStack)
└── docs/                  # MAS disclaimer, PDPA policy, ToS
```

## Getting Started

### Prerequisites

- Node.js >= 20.0.0
- pnpm >= 9.0.0
- Docker and Docker Compose
- Python >= 3.11

### Setup

```bash
# Install dependencies
pnpm install

# Start infrastructure (PostgreSQL, Redis, LocalStack)
cd infrastructure && docker compose up -d && cd ..

# Configure environment
cp .env.example .env.local
# Edit .env.local with your API keys

# Run development servers
pnpm dev
```

- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API docs: http://localhost:8000/docs

## MAS Compliance

All analysis outputs include the mandatory MAS disclaimer: *"This analysis is for informational purposes only. It is not financial advice."* See `docs/mas-disclaimer.md`.

## PDPA Compliance

- PDFs are **deleted immediately** after parsing unless the secure vault is opted into
- Consent is recorded with versioned, hashed agreement text
- All personal data is encrypted at rest using Fernet
- Users can export or delete all their data at any time
- See `docs/privacy-policy.md` and `docs/data-retention-policy.md`

## Pre-Launch Items (Legal)

Several items require legal input before public launch:

- [ ] MAS pre-submission meeting — confirm gap/overlap/conflict framing as info service
- [ ] Engagement letter with Singapore regulatory lawyer
- [ ] DPAs signed with Anthropic and OpenAI
- [ ] MediShield Life + IP ward data sourced from CPF/MAS official publications

See `docs/` for full legal documentation.

## License

Proprietary — all rights reserved.
