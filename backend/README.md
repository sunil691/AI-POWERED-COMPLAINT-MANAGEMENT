# AI-Powered Customer Complaint Management Backend

FastAPI backend for a pharmaceutical QA complaint workflow. The API owns persistence, document text extraction, and the structured copilot boundary. AI provider calls and complaint extraction are intentionally not enabled in this foundation.

## Run locally

Requires Python 3.12+, PostgreSQL, and the values in `.env`.

```bash
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload
```

OpenAPI is available at `http://localhost:8000/docs`. The health endpoint is `GET /health`.

## Database migrations

Set `DATABASE_URL`, then create and apply migrations with Alembic:

```bash
alembic revision --autogenerate -m "initial complaint schema"
alembic upgrade head
```

The application does not create domain tables at startup; schema changes are owned by Alembic.

## API surface

- `GET /health`
- `GET /complaints`
- `GET /complaints/{id}`
- `POST /complaints`
- `PUT /complaints/{id}`
- `DELETE /complaints/{id}`
- `POST /chat`
- `POST /upload`

The chat endpoint persists the user message and returns an explicit placeholder response. The upload endpoint accepts PDF files, stores them under `UPLOAD_DIRECTORY`, and extracts embedded text with PyMuPDF. OCR is not performed.