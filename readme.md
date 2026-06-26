# TicketAnalyzer

TicketAnalyzer is a FastAPI service that analyzes customer complaints together with transaction history and returns a structured AI-assisted case summary. It can translate non-English complaints before analysis and uses Gemini to produce the final response.

## The Pitch (video  on project architectural overview)

https://drive.google.com/drive/folders/1xvAqBzVRgudgvBxGf0q1GDv8A3WmOQY8?usp=drive_link

## Live API Endpoint

https://ticketanalyzer-2iph.onrender.com/

## Features

- `POST /analyze_ticket` for structured ticket analysis
- `GET /health` for health checks
- `GET /` for a simple app status response
- Complaint translation to English when the request language is not `en`
- Structured JSON output based on the `AnalyzeTicketResponse` model
- Containerized with Docker and Docker Compose, including a built-in container healthcheck

## Requirements

- Python 3.10+
- A Google Gemini API key

## Setup

1. Create and activate a virtual environment.

```bash
python -m venv .venv
.venv\Scripts\activate
```

2. Install dependencies.

```bash
pip install -r requirements.txt
```

3. Create a `.env` file in the project root.

```env
GOOGLE_API_KEY=your_google_api_key_here
```

4. Start the API server.

```bash
uvicorn app.main:app --reload
```

The interactive API docs are available at `http://127.0.0.1:8000/docs`.

## Docker

The app ships with a multi-ready `Dockerfile` (Python 3.12-slim, non-root user, container healthcheck) and a `docker-compose.yml` for one-command local runs.

### Prerequisites

- Docker 20.10+ and Docker Compose v2

### Run with Docker Compose

1. Create a `.env` file in the project root with your Gemini key:

```env
GOOGLE_API_KEY=your_google_api_key_here
```

2. Build the image and start the container:

```bash
docker compose up --build
```

The API will be available at `http://127.0.0.1:8000` and the interactive docs at `http://127.0.0.1:8000/docs`. Compose will read `GOOGLE_API_KEY` from your `.env` file (or shell environment) and refuse to start if it is missing.

Stop the container with `docker compose down`. To rebuild after code changes, run `docker compose up --build` again.

### Run with plain Docker

Useful for CI or when you do not want Compose.

```bash
docker build -t ticketanalyzer:latest .
docker run --rm -p 8000:8000 --env-file .env ticketanalyzer:latest
```

### Container Details

- Image base: `python:3.12-slim`
- Exposed port: `8000`
- Entrypoint: `uvicorn app.main:app --host 0.0.0.0 --port 8000`
- Healthcheck: `curl http://127.0.0.1:8000/health` every 30s, with a 10s start period
- Runs as the non-root `appuser` (UID 1000)

Override the host port with `-p 8080:8000` (Docker) or by editing the `ports` mapping in `docker-compose.yml`.

## API

### `POST /analyze_ticket`

Example request:

```json
{
  "ticket_id": "TKT-001",
  "complaint": "I sent 5000 taka to the wrong number.",
  "language": "en",
  "channel": "in_app_chat",
  "user_type": "customer",
  "transaction_history": [
    {
      "transaction_id": "TXN-9101",
      "timestamp": "2026-04-14T14:08:22Z",
      "type": "transfer",
      "amount": 5000,
      "counterparty": "+8801719876543",
      "status": "completed"
    }
  ]
}
```

The response follows the `AnalyzeTicketResponse` schema and includes fields such as:

- `relevant_transaction_id`
- `evidence_verdict`
- `case_type`
- `severity`
- `department`
- `agent_summary`
- `recommended_next_action`
- `customer_reply`
- `human_review_required`

### `GET /health`

Returns:

```json
{ "status": "ok" }
```

## Project Structure

```text
app/
  main.py
  models.py
  config/
    const.py
  utils/
    google_ai.py
    utils_method.py
```

## Notes

- The app reads the Gemini key from `GOOGLE_API_KEY`.
- `system_prompts_for_analyze_ticket` defines the analysis rules and safety constraints.
- The service is stateless; each request should include the complaint and any relevant transaction history.
