# Requirements Analysis

*Fill in this document with your teacher before/while developing — per the
guidelines, "Teacher support: for eliciting and defining requirements" is
expected for Innovation-driven projects.*

## 1. Stakeholders & need

- Who is this assistant for? (e.g., students, customer-support users, a specific business/societal need)
- What problem does it solve for them?

## 2. Scope of the use case

- What kinds of questions/tasks should the assistant handle?
- What is explicitly out of scope?
- Any domain constraints (e.g., must not give medical/legal advice, must cite sources, must refuse certain topics)?

## 3. Functional requirements

- FR1: The system shall accept a user message and return a relevant reply within N seconds.
- FR2: The system shall maintain conversation context across turns within a session.
- FR3: ...

## 4. Non-functional requirements

- Performance: expected latency/throughput.
- Reliability: what happens when the Hugging Face API is down or rate-limited (see `LLMClientError` → HTTP 502)?
- Security/privacy: is any personal/sensitive data handled? How is the HF token secured (never committed — see `.env.example`, `k8s/02-secret.yaml.example`)?
- Trustworthiness: does this use case need fairness/toxicity/safety evaluation (e.g., Virtual Teacher, Virtual Doctor, Virtual Journalist use cases per the guidelines)? If yes, describe the evaluation plan and add it under `tests/`.

## 5. Design & architectural choices

- Why Streamlit for the frontend / FastAPI for the backend?
- Why this specific Hugging Face model (`HF_MODEL_ID` in `backend/app/config.py`)? Trade-offs vs. alternatives.
- Deployment targets: local (Docker Compose), Kubernetes, Hugging Face Spaces (public demo).

## 6. Evaluation plan (maps to "Continuous Monitoring & Testing")

- ML accuracy/quality assessment: how will you evaluate response quality for your use case?
- Any additional quality dimensions relevant to the domain (safety, fairness, security, ...)?
