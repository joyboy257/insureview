#!/bin/bash
# ──────────────────────────────────────────────────────────────────────────────
# Insureview Celery Worker Startup
# Usage:
#   ./scripts/start_workers.sh          # start all workers in background
#   ./scripts/start_workers.sh --parse  # parse worker only
#   ./scripts/start_workers.sh --analysis  # analysis worker only
#   ./scripts/start_workers.sh --notify  # notification worker only
#   ./scripts/start_workers.sh --foreground  # run all in foreground (ctrl-C to stop)
# ──────────────────────────────────────────────────────────────────────────────

set -e

CDIR="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(cd "$CDIR/.." && pwd)"
export PYTHONPATH="$ROOT:$PYTHONPATH"

FOREGROUND=false
WORKERS=()

while [[ $# -gt 0 ]]; do
  case "$1" in
    --parse)       WORKERS+=("parse"); shift ;;
    --analysis)    WORKERS+=("analysis"); shift ;;
    --notify)      WORKERS+=("notify"); shift ;;
    --foreground)  FOREGROUND=true; shift ;;
    --help)        echo "Usage: $0 [--parse|--analysis|--notify] [--foreground]"; exit 0 ;;
    *)             echo "Unknown option: $1"; exit 1 ;;
  esac
done

# Default to all workers
if [ ${#WORKERS[@]} -eq 0 ]; then
  WORKERS=("parse" "analysis" "notify")
fi

PARSE_Q="parse_queue"
ANALYSIS_Q="analysis_queue"
NOTIFY_Q="notify_queue"

# All queues comma-separated for the worker that subscribes to all
ALL_Q="${PARSE_Q},${ANALYSIS_Q},${NOTIFY_Q}"

start_worker() {
  local name="$1"; shift
  local module="$1"; shift
  local queue="$1"; shift
  local log="$CDIR/logs/${name}.log"

  mkdir -p "$CDIR/logs"
  echo "Starting $name worker → queue: $queue  (log: $log)"
  # -m celery runs the celery worker module; -A app --hostname --queues -l
  # Using nohup /dev/null for stdin so background mode works predictably
  nohup python -m celery \
    -A "$module" \
    worker \
    --hostname="${name}@%h" \
    --queues="$queue" \
    --loglevel=INFO \
    > "$log" 2>&1 &
  echo "  pid $!"
}

echo "🚀 Starting Insureview Celery workers..."
echo ""

if [ "$FOREGROUND" = true ]; then
  # Run sequentially in foreground (first worker runs in this process)
  if [[ " ${WORKERS[*]} " =~ " parse " ]]; then
    echo "─── parse worker (queue: $PARSE_Q) ───"
    python -m celery -A app.workers.parse_worker:celery_app \
      worker --hostname="parse@%h" --queues="$PARSE_Q" --loglevel=INFO
  fi
  if [[ " ${WORKERS[*]} " =~ " analysis " ]]; then
    echo "─── analysis worker (queue: $ANALYSIS_Q) ───"
    python -m celery -A app.workers.analysis_worker:celery_app \
      worker --hostname="analysis@%h" --queues="$ANALYSIS_Q" --loglevel=INFO
  fi
  if [[ " ${WORKERS[*]} " =~ " notify " ]]; then
    echo "─── notify worker (queue: $NOTIFY_Q) ───"
    python -m celery -A app.workers.notification_worker:celery_app \
      worker --hostname="notify@%h" --queues="$NOTIFY_Q" --loglevel=INFO
  fi
else
  # Background mode — spawn each worker as a detached process
  for w in "${WORKERS[@]}"; do
    case "$w" in
      parse)     start_worker "parse"     "app.workers.parse_worker"     "$PARSE_Q" ;;
      analysis)  start_worker "analysis"  "app.workers.analysis_worker"  "$ANALYSIS_Q" ;;
      notify)    start_worker "notify"    "app.workers.notification_worker" "$NOTIFY_Q" ;;
    esac
  done
  echo ""
  echo "✅ All workers started. Logs: $CDIR/logs/"
  echo "   To watch:  tail -f $CDIR/logs/{parse,analysis,notify}.log"
  echo "   To stop:   pkill -f 'celery.*insureview'   # or kill <pid> above"
fi
