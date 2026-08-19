#!/usr/bin/env bash
# Launches the FastAPI backend in the background, waits for it to be
# healthy, then runs the Streamlit frontend in the foreground (required so
# the container's main process stays alive for HF Spaces).
set -euo pipefail

cd /app/backend
uvicorn app.main:app --host 0.0.0.0 --port "${BACKEND_PORT}" &
BACKEND_PID=$!

echo "Waiting for backend to become healthy..."
for i in $(seq 1 30); do
  if curl -sf "http://localhost:${BACKEND_PORT}/health" > /dev/null; then
    echo "Backend is up."
    break
  fi
  sleep 1
done

cd /app/frontend
streamlit run app.py --server.port="${FRONTEND_PORT}" --server.address=0.0.0.0 &
FRONTEND_PID=$!

# If either process dies, stop the container so HF Spaces reports failure
# instead of silently serving a half-working app.
wait -n "$BACKEND_PID" "$FRONTEND_PID"
