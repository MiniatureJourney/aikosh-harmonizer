# Commercial / Production Readiness

This document summarizes changes for **commercial use**: auth, scalability, smoother experience, and **PDF processing fixes**.

---

## 1. PDF processing fixes (your error)

PDF processing was failing in several places. These are now hardened:

- **Detector** (`pdf_service/detector.py`): Corrupted or invalid PDFs no longer crash the process. Document is always closed in `finally`. Exceptions are wrapped in `RuntimeError` with a clear message.
- **Orchestrator** (`pdf_service/orchestrator.py`): Each stage (detect, text, tables, OCR, clean, semantic, confidence, metadata) runs in its own try/except. One failing step no longer kills the whole job. Errors are collected in `_errors` and returned as `error_message` so the UI shows a clear message (e.g. "OCR: ...", "Metadata generation failed", "No text could be extracted").
- **Metadata generator** (`pdf_service/metadata_generator.py`): Safe handling when the LLM returns no text (blocked/empty). Uses `getattr(response, "text", None)` and skips empty/None before parsing JSON.
- **Empty PDFs**: If no text is extracted, the pipeline no longer calls the LLM with empty content; it returns a structured error: "No text could be extracted from the PDF."
- **Tasks** (`services/tasks.py`): PDF errors from the orchestrator (`_errors` list) are turned into a single `error_message` string for the frontend.

If you still see a specific error message in the UI or logs, that message now comes from one of these stages and should point to the failing step (e.g. OCR, table extraction, or metadata/LLM).

---

## 2. Auth service

- **Endpoints**: `POST /auth/register`, `POST /auth/login`, `GET /auth/me`.
- **Behavior**: When `AUTH_ENABLED=true`, upload, status, download, and synthesize require a valid JWT (Bearer token). When `AUTH_ENABLED=false`, all routes remain open (no auth).
- **Storage**: Users are stored in memory by default. Optional file persistence: set `AUTH_USERS_FILE=data/users.json` (or any path) to save/load users across restarts.
- **Frontend**: Login/Register modal, token in `localStorage`, `Authorization: Bearer <token>` on all relevant requests. On 401, token is cleared and the login modal is shown.

**Env (optional):**

- `AUTH_ENABLED=true` – require login for processing/download.
- `JWT_SECRET` – use a long random secret in production (e.g. `openssl rand -hex 32`).
- `JWT_EXPIRE_MINUTES=60` – token lifetime.
- `AUTH_USERS_FILE=data/users.json` – persist users to a JSON file.

---

## 3. Scalability & commercial behavior

- **Rate limiting**: 30 requests per minute per IP for `POST /harmonize` and `POST /process-pdf` (SlowAPI). Reduces abuse and keeps the service stable.
- **Request ID**: Every response includes `X-Request-ID` for tracing and support (same as request if client sends it, otherwise generated).
- **Health**: `GET /health` returns `auth_enabled` and `max_upload_mb` so the UI can adapt.

---

## 4. Smoother experience

- **Retry**: Failed files in the workspace show a **Retry** button; clicking it re-queues that file without re-uploading.
- **Toasts**: Copy JSON and auth actions use toasts instead of `alert()`.
- **401 handling**: If the server returns 401, the app clears the token, updates the auth UI, and opens the login modal with a “Please sign in” message.

---

## 5. Suggested next steps for production

1. **Secrets**: Set `JWT_SECRET` and `GEMINI_API_KEY` in Render (or your host) env; never commit them.
2. **Auth**: Set `AUTH_ENABLED=true` and optionally `AUTH_USERS_FILE` if you want persistent users without a DB.
3. **DB/Redis**: For multi-instance or heavy load, set `DATABASE_URL` (Postgres) and `REDIS_URL` + `USE_CELERY=true` so processing is offloaded to workers.
4. **Logging**: Add structured logging (e.g. `structlog` or JSON logs) and include `request_id` in every log line for debugging.
5. **Monitoring**: Use `/health` and `X-Request-ID` in your APM or logs to trace failed PDF jobs and rate limits.

---

## Quick reference: env for commercial deploy (e.g. Render)

| Variable           | Required | Description                          |
|--------------------|----------|--------------------------------------|
| `GEMINI_API_KEY`   | Yes      | Gemini API key                       |
| `JWT_SECRET`       | If auth  | Long random secret                   |
| `AUTH_ENABLED`     | No       | `true` to require login              |
| `AUTH_USERS_FILE`  | No       | Path to JSON file to persist users   |
| `MAX_UPLOAD_MB`    | No       | Default 25; lower if you see 413     |
| `DATABASE_URL`     | No       | Postgres for metadata cache          |
| `REDIS_URL`        | No       | For Celery async workers             |
| `USE_CELERY`       | No       | `true` to use Celery                 |
