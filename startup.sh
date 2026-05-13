#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$PROJECT_ROOT/.venv"
BACKEND_PORT="${BACKEND_PORT:-8000}"
STREAMLIT_PORT="${STREAMLIT_PORT:-8501}"
LOG_DIR="$PROJECT_ROOT/logs"
BACKEND_PID=""
STREAMLIT_PID=""

cd "$PROJECT_ROOT"
mkdir -p "$LOG_DIR"
touch "$LOG_DIR/backend.log" "$LOG_DIR/streamlit.log"

log() {
  echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*"
}

fail() {
  log "ERROR: $*"
  exit 1
}

is_listening() {
  local port="$1"
  python3 - "$port" <<'PY'
import socket
import sys

port = int(sys.argv[1])
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
    sock.settimeout(0.5)
    sys.exit(0 if sock.connect_ex(("127.0.0.1", port)) == 0 else 1)
PY
}

wait_for_http() {
  local url="$1"
  local name="$2"
  local log_file="$3"

  for attempt in {1..30}; do
    if python3 - "$url" <<'PY' >/dev/null 2>&1
import sys
import urllib.request

urllib.request.urlopen(sys.argv[1], timeout=1)
PY
    then
      log "$name is ready."
      return 0
    fi

    sleep 1
  done

  log "$name did not become ready in time. Last logs:"
  tail -n 80 "$log_file" 2>/dev/null || true
  return 1
}

if [ -f "$PROJECT_ROOT/backend/.env" ]; then
  log "Loading backend/.env..."
  set -a
  # shellcheck disable=SC1091
  source "$PROJECT_ROOT/backend/.env"
  set +a
fi

BACKEND_PORT="${BACKEND_PORT:-8000}"
STREAMLIT_PORT="${STREAMLIT_PORT:-8501}"

if [ ! -d "$VENV_DIR" ]; then
  log "Creating virtual environment..."
  python3 -m venv "$VENV_DIR"
fi

source "$VENV_DIR/bin/activate"

log "Installing dependencies..."
pip install -r requirements.txt || fail "Dependency installation failed."

if is_listening "$BACKEND_PORT"; then
  log "FastAPI port $BACKEND_PORT is already listening. Reusing existing backend."
else
  log "Starting FastAPI backend on http://127.0.0.1:$BACKEND_PORT"
  uvicorn agent:app --reload --host 127.0.0.1 --port "$BACKEND_PORT" > "$LOG_DIR/backend.log" 2>&1 &
  BACKEND_PID=$!
fi

cleanup() {
  echo
  if [ -n "$STREAMLIT_PID" ]; then
    log "Stopping Streamlit..."
    kill "$STREAMLIT_PID" 2>/dev/null || true
  fi
  if [ -n "$BACKEND_PID" ]; then
    log "Stopping backend..."
    kill "$BACKEND_PID" 2>/dev/null || true
  fi
}
trap cleanup EXIT

wait_for_http "http://127.0.0.1:$BACKEND_PORT/health" "Backend" "$LOG_DIR/backend.log" || fail "Backend health check failed."

if is_listening "$STREAMLIT_PORT"; then
  fail "Streamlit port $STREAMLIT_PORT is already in use. Stop that process or set STREAMLIT_PORT to another port."
fi

log "Starting Streamlit frontend on http://127.0.0.1:$STREAMLIT_PORT"
HOME="$PROJECT_ROOT" \
API_BASE_URL="http://127.0.0.1:$BACKEND_PORT" \
STREAMLIT_BROWSER_GATHER_USAGE_STATS="${STREAMLIT_BROWSER_GATHER_USAGE_STATS:-false}" \
streamlit run backend/streamlit_app.py \
  --server.address "${STREAMLIT_SERVER_ADDRESS:-127.0.0.1}" \
  --server.port "$STREAMLIT_PORT" \
  --browser.serverAddress "${STREAMLIT_BROWSER_SERVER_ADDRESS:-localhost}" \
  --server.enableCORS "${STREAMLIT_ENABLE_CORS:-false}" \
  --server.enableXsrfProtection "${STREAMLIT_ENABLE_XSRF_PROTECTION:-false}" \
  --browser.gatherUsageStats "${STREAMLIT_BROWSER_GATHER_USAGE_STATS:-false}" > "$LOG_DIR/streamlit.log" 2>&1 &
STREAMLIT_PID=$!

wait_for_http "http://127.0.0.1:$STREAMLIT_PORT" "Streamlit" "$LOG_DIR/streamlit.log" || fail "Streamlit startup failed."

log "App is running."
log "Open http://127.0.0.1:$STREAMLIT_PORT"
log "Backend logs: $LOG_DIR/backend.log"
log "Streamlit logs: $LOG_DIR/streamlit.log"
log "Press Ctrl+C to stop services started by this script."

tail -f "$LOG_DIR/backend.log" "$LOG_DIR/streamlit.log"
