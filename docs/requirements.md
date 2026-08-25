# Requirements Analysis

## 1. Stakeholders & need

- **Who is this assistant for?** General users who want a lightweight,
  always-available conversational assistant — e.g. students who need quick
  explanations, drafting help, or a sounding board while studying, and
  developers/evaluators who want a minimal example of an LLM-backed
  assistant built from an existing (not fine-tuned) model.
- **What problem does it solve for them?** It gives fast, free-text answers
  to general questions without requiring the user to set up or run a model
  themselves — the heavy lifting (hosting the LLM) is delegated to Hugging
  Face's Inference Providers, and the user only interacts with a simple chat
  UI.

*(This is intentionally a general-purpose assistant rather than a narrow
domain persona. If your teacher wants a more specific stakeholder — e.g. a
Virtual Teacher, Virtual Doctor, or Virtual Journalist — narrow this section
and the system prompt in `backend/app/config.py` accordingly, and see the
note on evaluation in Section 4/6 below, since a specialized domain adds
fairness/safety/toxicity evaluation obligations that a general assistant
does not strictly require.)*

## 2. Scope of the use case

- **In scope:** general knowledge questions, explanations, brainstorming,
  short drafting/rewriting tasks, casual conversation — anything a helpful,
  concise general-purpose assistant can reasonably answer from the
  underlying model's training data.
- **Out of scope:** the assistant does not browse the web, does not access
  any private/user-specific data, does not remember anything beyond the
  current chat session (no persistent memory across sessions), and does not
  execute code or take actions outside of returning a text reply.
- **Domain constraints:** the system prompt (`backend/app/config.py`,
  `system_prompt`) instructs the model to "answer clearly and admit when you
  are not sure" — i.e. it should not present speculation as fact. It is not
  positioned as a source of medical, legal, or financial advice; because
  this is a general-purpose assistant rather than a Virtual Doctor/Lawyer
  use case, it does not carry the stricter constraints (mandatory
  disclaimers, refusal policies, citation requirements) that a
  regulated-domain assistant would need — those would be added if the
  stakeholder/use case in Section 1 is narrowed to such a domain.

## 3. Functional requirements

- **FR1:** The system shall accept a user text message and return a
  relevant reply within a reasonable time (typically a few seconds; up to
  ~60s on a cold start of the free-tier backend — see `REQUEST_TIMEOUT` in
  `frontend/app.py`).
- **FR2:** The system shall maintain conversation context across turns
  within a session by resending the full message history with each request
  (`frontend/app.py` builds `history` from `st.session_state.messages`;
  `backend/app/llm_client.py` includes it in the prompt sent to the model).
- **FR3:** The system shall expose a health-check endpoint (`GET /health`)
  reporting service status and the currently configured model, so uptime
  and configuration can be verified without sending a full chat request.
- **FR4:** The system shall reject invalid input (e.g. an empty message)
  with a clear validation error rather than forwarding it to the model
  (see `backend/app/schemas.py` and the corresponding test in
  `tests/test_api.py::test_chat_rejects_empty_message`).
- **FR5:** The user shall be able to clear the current conversation and
  start fresh without restarting the app (the "Clear conversation" button
  in `frontend/app.py`).

## 4. Non-functional requirements

- **Performance:** Typical reply latency is dominated by the upstream
  Hugging Face inference call, not by this project's own code; the frontend
  enforces a client-side timeout (default 60s) after which it reports an
  error rather than hanging indefinitely. Both the current free-tier
  frontend (Streamlit Community Cloud) and backend (Render) hosts sleep
  after inactivity, so the first request after idle time can take 30–60s
  longer than a warm request — this is a known, accepted trade-off of using
  free hosting rather than a product-level requirement.
- **Reliability:** If the Hugging Face Inference API is unavailable, rate
  limited, or the requested model is not supported by any enabled provider,
  `backend/app/llm_client.py` raises an `LLMClientError`, which
  `backend/app/main.py` turns into an HTTP 502 with a message rather than
  crashing the service or returning a silent empty reply. Docker
  `HEALTHCHECK` and Kubernetes readiness/liveness probes (`k8s/`) allow an
  orchestrator to detect and restart an unhealthy backend.
- **Security/privacy:** No personal or sensitive user data is stored — chat
  history lives only in the browser session's memory (`st.session_state`)
  and is discarded when the tab/session ends; nothing is written to a
  database or disk. The Hugging Face API token is never committed to the
  repository: local development reads it from a git-ignored `.env`
  (`.env.example` documents the expected variables), Kubernetes reads it
  from a Secret (`k8s/02-secret.yaml.example`), and the live deployment
  reads it from Render's environment variable store.
- **Trustworthiness:** Because the chosen use case (Section 1) is a
  general-purpose assistant rather than one of the higher-stakes personas
  the course guidelines call out (Virtual Teacher/Doctor/Journalist), a
  formal fairness/toxicity/safety evaluation was judged not strictly
  required for this scope. Basic correctness is covered instead by the
  automated test suite (`tests/test_api.py`, 6 tests: health check, root
  route, a normal chat exchange, a multi-turn exchange with history, input
  validation, and upstream-failure handling), run automatically in CI on
  every push. See Section 6 for how this could be extended if the use case
  is narrowed to a regulated domain.

## 5. Design & architectural choices

- **Why Streamlit for the frontend:** minimal boilerplate for a chat UI
  (built-in `st.chat_message`/`st.chat_input` primitives), fast to iterate
  on, and free to host on Streamlit Community Cloud for the public demo —
  a good fit for a course prototype rather than a production consumer app.
- **Why FastAPI for the backend:** async-friendly, automatic OpenAPI docs
  (`/docs`) for free, Pydantic-based request/response validation
  (`backend/app/schemas.py`) which directly satisfies FR4, and it is
  lightweight enough to run comfortably on a free-tier host.
- **Why this Hugging Face model:** the backend is model-agnostic by design
  (`HF_MODEL_ID` env var, `backend/app/config.py`) so the specific model can
  be swapped without code changes. The live deployment currently uses
  `openai/gpt-oss-20b` served via the **Groq** inference provider — chosen
  because it is one of the providers actually enabled on the deployment's
  Hugging Face account and confirmed to serve that model; earlier attempts
  with `HuggingFaceH4/zephyr-7b-beta` and `google/gemma-2-2b-it` failed
  because neither was served by any enabled provider, which is itself a
  useful illustration of a real operational constraint when depending on a
  third-party hosted model rather than one you control.
- **Deployment targets:** local (`docker-compose.yml`), Kubernetes
  (`k8s/`), and a public online demo. The demo was originally planned as a
  Hugging Face Space (`huggingface_space/`), but Hugging Face now requires
  a paid PRO plan for Docker/Gradio Spaces (only Static Spaces are free),
  so the live public demo runs on Render (backend) + Streamlit Community
  Cloud (frontend) instead — see the root `README.md`, "Online demo (live)"
  section, for the actual links and a fuller explanation of that trade-off.

## 6. Evaluation plan (maps to "Continuous Monitoring & Testing")

- **ML/response-quality assessment:** for this general-purpose scope,
  quality is currently assessed functionally rather than with a formal
  accuracy metric — i.e. via the automated test suite asserting the API
  contract behaves correctly (valid input produces a reply, invalid input
  is rejected, upstream failures degrade gracefully) plus manual
  spot-checking of live replies through the deployed chat UI. There is no
  fixed "correct answer" dataset to score against, since the assistant is
  open-domain rather than task-specific.
- **Additional quality dimensions:** not currently implemented, and judged
  out of scope for a general-purpose assistant (see Section 4). If the
  stakeholder/use case in Section 1 is narrowed to a regulated or
  higher-stakes domain (Virtual Teacher/Doctor/Journalist, etc.), this
  section should be extended with a concrete plan — e.g. a small labeled
  set of adversarial/edge-case prompts checked for toxic, biased, or unsafe
  output, and a documented refusal policy for out-of-scope requests —
  before that version is submitted.
