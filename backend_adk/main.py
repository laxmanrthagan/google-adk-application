from __future__ import annotations

import os
import logging

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

load_dotenv()

from backend_adk.adk_agents import run_with_adk
from backend_adk.catalog import AGENT_BY_ID, AGENTS
from backend_adk.models import RunRequest, RunResponse

logger = logging.getLogger(__name__)

app = FastAPI(title="Interview Studio API", version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ORIGINS", "http://localhost:5173").split(","),
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)


def active_provider() -> str:
    requested = os.getenv("AI_PROVIDER", "mock").strip().lower()
    if requested not in {"mock", "gemini", "vertex"}:
        return "mock"
    return requested


@app.get("/api/health")
async def health() -> dict[str, str]:
    return {"status": "ok", "provider": active_provider()}


@app.get("/api/agents")
async def list_agents() -> dict[str, list[dict[str, str]]]:
    return {"agents": AGENTS}


@app.post("/api/run", response_model=RunResponse)
async def run_agent(request: RunRequest) -> dict[str, object]:
    if request.agent_id not in AGENT_BY_ID:
        raise HTTPException(status_code=404, detail="Unknown agent type.")

    provider = active_provider()
    payload = request.model_dump()
    try:
        return await run_with_adk(request.agent_id, payload, provider)
    except Exception:
        logger.exception("ADK execution failed for agent %s", request.agent_id)
        raise HTTPException(
            status_code=502,
            detail="Agent execution failed. Check server logs and provider configuration.",
        ) from None