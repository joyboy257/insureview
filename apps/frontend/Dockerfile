# ── Stage 1: dependencies ────────────────────────────────────────────────────────
FROM node:20-alpine AS deps
WORKDIR /app

COPY package.json pnpm-lock.yaml pnpm-workspace.yaml ./
COPY packages/package.json packages/
COPY apps/frontend/package.json apps/frontend/
COPY apps/backend/package.json apps/backend/ || true

RUN corepack enable pnpm && pnpm install --frozen-lockfile

# ── Stage 2: build ───────────────────────────────────────────────────────────────
FROM deps AS builder
WORKDIR /app

COPY . .
COPY apps/frontend/next.config.js apps/frontend/next.config.js
COPY apps/frontend/tsconfig.base.json tsconfig.base.json

WORKDIR /app/apps/frontend
RUN pnpm build

# ── Stage 3: runtime ─────────────────────────────────────────────────────────────
FROM node:20-alpine AS runtime
WORKDIR /app

ENV NODE_ENV=production

RUN addgroup -g 1001 -S nodejs && adduser -S nextjs -u 1001

COPY --from=builder --chown=nextjs:nodejs /app/apps/frontend/public ./public
COPY --from=builder --chown=nextjs:nodejs /app/apps/frontend/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/apps/frontend/.next/static ./.next/static

USER nextjs
EXPOSE 3000

ENV PORT=3000
ENV HOSTNAME="0.0.0.0"

CMD ["node", "server.js"]
