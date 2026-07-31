from __future__ import annotations

import sys
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

# allow `python app.py` from agent/
ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from core.agent import CampusDocAgent  # noqa: E402

app = FastAPI(title="CampusDoc Agent", version="1.0.0")
agent = CampusDocAgent()

static_dir = ROOT / "static"
app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=8000)


@app.get("/")
def index() -> FileResponse:
    return FileResponse(static_dir / "index.html")


@app.get("/api/health")
def health() -> dict:
    import os

    return {
        "ok": True,
        "agent": "CampusDocAgent",
        "mode": "live" if os.environ.get("DEEPSEEK_API_KEY") else "demo",
        "tools": [
            "search_knowledge",
            "clean_tabular_text",
            "summarize_document",
            "grade_concept_answer",
        ],
    }


@app.post("/api/chat")
def chat(req: ChatRequest) -> dict:
    result = agent.run(req.message)
    return result


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app:app", host="127.0.0.1", port=7860, reload=False)
