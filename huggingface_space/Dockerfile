# Hugging Face Spaces (Docker SDK) image.
#
# Runs BOTH services in a single container, since a Space only exposes one
# port: FastAPI backend on localhost:8000 (internal only) and Streamlit
# frontend on 7860 (the port HF Spaces routes to), talking to each other
# over localhost. This keeps the exact same backend/frontend codebase used
# for local Docker Compose and Kubernetes -- only the process supervisor
# differs.
FROM python:3.11-slim

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/*

COPY backend/requirements.txt ./backend-requirements.txt
COPY frontend/requirements.txt ./frontend-requirements.txt
RUN pip install --no-cache-dir -r backend-requirements.txt -r frontend-requirements.txt

COPY backend/app ./backend/app
COPY frontend/app.py ./frontend/app.py
COPY huggingface_space/start.sh ./start.sh
RUN chmod +x ./start.sh

ENV PYTHONUNBUFFERED=1 \
    BACKEND_PORT=8000 \
    FRONTEND_PORT=7860 \
    BACKEND_URL=http://localhost:8000 \
    API_PREFIX=/api/v1

# Hugging Face Spaces (Docker SDK) routes external traffic to port 7860 by default.
EXPOSE 7860

CMD ["./start.sh"]
