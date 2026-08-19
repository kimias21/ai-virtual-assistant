---
title: AI Virtual Assistant
emoji: 🤖
colorFrom: blue
colorTo: indigo
sdk: docker
app_port: 7860
pinned: false
---

# AI Virtual Assistant — Hugging Face Space

This Space runs the full stack (FastAPI backend + Streamlit frontend) in one
Docker container so you get a single public demo link, as required by the
course guidelines ("online link" via Hugging Face).

## How to deploy this Space

1. Create a new Space on https://huggingface.co/new-space with **SDK = Docker**.
2. In the Space's **Settings → Repository secrets**, add:
   - `HF_API_TOKEN` — a Hugging Face access token (read scope) so the backend
     can call the Inference API for the chat model.
   - Optionally `HF_MODEL_ID`, `SYSTEM_PROMPT`, `MAX_NEW_TOKENS`, `TEMPERATURE`
     to override the defaults in `backend/app/config.py`.
3. Push the contents of this repository to the Space's git remote, using
   `huggingface_space/Dockerfile` as the root Dockerfile (see below), or use
   the Hugging Face CLI:

   ```bash
   pip install huggingface_hub
   huggingface-cli login
   huggingface-cli upload <your-username>/ai-virtual-assistant . \
     --repo-type=space
   ```

   Note: Spaces build from a `Dockerfile` at the repo root. Since this
   project keeps backend/frontend/Space files in one GitHub repo, either:
   - point the Space at a separate deployment branch where
     `huggingface_space/Dockerfile` has been copied to `./Dockerfile`, or
   - mirror this folder's contents (Dockerfile, plus ../backend and
     ../frontend) into a dedicated Space repo.
   The `.github/workflows/ci-cd.yml` can be extended with a step that syncs
   to the HF Space automatically on every push to `main` (see comment at the
   bottom of that workflow).

4. The Space builds and starts; once healthy, the chat UI is live at
   `https://huggingface.co/spaces/<your-username>/ai-virtual-assistant`.

## Local test of this exact image

```bash
cd ..   # repo root
docker build -f huggingface_space/Dockerfile -t ai-va-space .
docker run -p 7860:7860 -e HF_API_TOKEN=hf_xxx ai-va-space
# open http://localhost:7860
```
