# AI Virtual Assistant

**AI Systems Engineering — Projects Guidelines v1 (Prof. Roberto Pietrantuono)**
Project type: **Innovation-driven**

An LLM-powered virtual assistant with a Streamlit frontend and a FastAPI
backend that calls a hosted Hugging Face model. Ships with Docker,
docker-compose, a GitHub Actions CI/CD pipeline, Kubernetes manifests, and a
Hugging Face Space for a public demo link.

## Architecture

```
┌─────────────┐        HTTP/JSON        ┌──────────────┐       HF Inference API      ┌──────────────┐
│  Streamlit  │ ───────────────────────▶ │   FastAPI     │ ───────────────────────────▶ │ Hugging Face │
│  frontend   │ ◀─────────────────────── │   backend     │ ◀─────────────────────────── │   (hosted    │
│  (chat UI)  │      reply (JSON)        │  /api/v1/chat │        completion            │    LLM)      │
└─────────────┘                          └──────────────┘                              └──────────────┘
```

- **Frontend** (`frontend/`): Streamlit chat UI. Sends the user message + conversation history to the backend.
- **Backend** (`backend/`): FastAPI service. Validates requests, builds the chat prompt (system prompt + history), calls the Hugging Face Inference API, returns the reply.
- **Model**: an existing pretrained conversational LLM hosted on the Hugging Face Hub (default: `HuggingFaceH4/zephyr-7b-beta`, configurable via `HF_MODEL_ID`). No local training/fine-tuning — the project uses an off-the-shelf model, per the "existing models" innovation-driven path.

## Mapping to the course's Innovation-driven steps

| Guideline step | Where it lives |
|---|---|
| Requirements analysis (stakeholder needs) | `docs/requirements.md` *(fill in for your specific use case — e.g. who the assistant serves and what it must/must not do)* |
| Design (architecture & choices) | This README + `backend/app/` module layout (`config.py`, `schemas.py`, `llm_client.py`, `main.py`) |
| Prototype development | `backend/`, `frontend/` — a working, runnable demo |
| Continuous monitoring & testing | `tests/test_api.py` (backend correctness), `/health` endpoints, Docker `HEALTHCHECK`, k8s readiness/liveness probes |
| (Local) deployment | `docker-compose.yml` (local Docker), `k8s/` (Kubernetes), `huggingface_space/` (public online link) |

> This scaffold covers the engineering skeleton. Before submitting, fill in
> the project-specific parts the guidelines call out: the concrete
> stakeholder/use case, the system prompt tailored to that use case, and (if
> the domain calls for it, e.g. a Virtual Teacher/Doctor/Journalist) an
> evaluation of fairness/safety/toxicity for the chosen use case.

## Repository layout

```
.
├── backend/                 # FastAPI service
│   ├── app/
│   │   ├── main.py          # routes: /health, /api/v1/chat
│   │   ├── config.py        # env-var driven settings
│   │   ├── schemas.py       # request/response models
│   │   └── llm_client.py    # Hugging Face Inference API wrapper
│   ├── requirements.txt
│   ├── requirements-dev.txt
│   └── Dockerfile
├── frontend/                 # Streamlit chat UI
│   ├── app.py
│   ├── requirements.txt
│   └── Dockerfile
├── huggingface_space/         # Single-container build for HF Spaces (public demo link)
│   ├── Dockerfile
│   ├── start.sh
│   └── README.md              # Space config (YAML frontmatter) + deploy steps
├── k8s/                        # Kubernetes manifests
│   ├── 00-namespace.yaml
│   ├── 01-configmap.yaml
│   ├── 02-secret.yaml.example
│   ├── 10-backend-deployment.yaml   # Deployment + Service
│   ├── 11-frontend-deployment.yaml  # Deployment + Service
│   └── 20-ingress.yaml
├── tests/                      # pytest suite (mocks the HF call)
├── .github/workflows/ci-cd.yml # lint, test, build+push images, sync HF Space
├── docker-compose.yml          # local deployment
├── .env.example
└── pyproject.toml / pytest.ini # ruff + pytest config
```

## Run it locally (Docker Compose — recommended)

```bash
cp .env.example .env
# edit .env and set HF_API_TOKEN (https://huggingface.co/settings/tokens)

docker compose up --build
# frontend: http://localhost:8501
# backend:  http://localhost:8000/docs
```

## Run it locally without Docker

```bash
# Backend
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements-dev.txt
export HF_API_TOKEN=hf_xxx
uvicorn app.main:app --reload --port 8000

# Frontend (separate terminal)
cd frontend
pip install -r requirements.txt
export BACKEND_URL=http://localhost:8000
streamlit run app.py
```

## Tests

```bash
pip install -r backend/requirements-dev.txt
pytest tests -v
ruff check backend/app frontend/app.py tests
```

## Kubernetes

See `k8s/README.md` for step-by-step `kubectl apply` instructions.

## CI/CD (GitHub Actions)

`.github/workflows/ci-cd.yml` runs on every push/PR to `main`:
1. **lint-and-test** — `ruff check` + `pytest` (always runs).
2. **build-images** — builds & pushes `backend`/`frontend` Docker images to GHCR (`ghcr.io/<owner>/<repo>/...`) on push to `main`.
3. **deploy-hf-space** — optionally syncs `huggingface_space/` + `backend/` + `frontend/` to a Hugging Face Space if the repo secrets `HF_TOKEN` and `HF_SPACE_REPO` are set, keeping the public demo link up to date automatically.

Required GitHub repo secrets (Settings → Secrets and variables → Actions):
- `HF_TOKEN` — Hugging Face token with **write** access (only needed for the Space sync job).
- `HF_SPACE_REPO` — e.g. `your-username/ai-virtual-assistant`.
- `GITHUB_TOKEN` is provided automatically for pushing to GHCR.

## Online demo (Hugging Face Spaces)

See `huggingface_space/README.md` for how to create the Space and get a
public URL like `https://huggingface.co/spaces/<you>/ai-virtual-assistant`.

## Delivery

Per the course rules, submit by pushing this repository to GitHub and
sharing the repo link with the teacher (see the Rules slide: *"Delivery to
the teacher via a GitHub Repository"*).

```bash
git remote add origin https://github.com/<your-username>/<repo-name>.git
git branch -M main
git push -u origin main
```
