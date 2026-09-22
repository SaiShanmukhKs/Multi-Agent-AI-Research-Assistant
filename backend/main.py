"""
FastAPI Server for Multi-Agent Research Assistant.

Provides REST and SSE endpoints for initiating research, streaming live multi-agent updates,
and fetching completed research reports & visualization datasets.
"""

from __future__ import annotations

import asyncio
import json
import logging
import uuid
from typing import Any, Dict, List, Optional

from fastapi import FastAPI, BackgroundTasks, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

import config
from core.graph import run_research

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("backend")

app = FastAPI(
    title="Multi-Agent Research Assistant API",
    description="Decoupled FastAPI backend powering 4 specialized AI agents with LangGraph & Gemini 2.5",
    version="1.0.0",
)

# Enable CORS for frontend development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory store for active and completed research tasks
# In production, this can be backed by Redis or PostgreSQL
research_tasks: Dict[str, Dict[str, Any]] = {}
event_queues: Dict[str, asyncio.Queue] = {}


class ResearchRequest(BaseModel):
    query: str = Field(..., example="Latest advancements in quantum error correction")
    audience: str = Field(default="business", example="business")


class TaskStatusResponse(BaseModel):
    task_id: str
    status: str
    query: str
    audience: str
    agent_logs: List[str]
    current_node: Optional[str] = None


@app.get("/api/health")
def health_check():
    return {
        "status": "healthy",
        "gemini_model": config.GEMINI_MODEL,
        "embedding_model": config.EMBEDDING_MODEL,
        "tavily_enabled": config.USE_TAVILY,
    }


def _execute_research_task(task_id: str, query: str, audience: str, main_loop: asyncio.AbstractEventLoop):
    """Background worker function executing the LangGraph graph and pushing updates to SSE queues."""
    queue = event_queues.get(task_id)

    def event_callback(node_name: str, log_msg: str):
        if task_id in research_tasks:
            research_tasks[task_id]["current_node"] = node_name
            research_tasks[task_id]["agent_logs"].append(log_msg)
            research_tasks[task_id]["status"] = f"running_{node_name}"

        if queue and main_loop.is_running():
            try:
                payload = {
                    "type": "agent_update",
                    "task_id": task_id,
                    "node": node_name,
                    "log": log_msg,
                }
                main_loop.call_soon_threadsafe(queue.put_nowait, payload)
            except Exception as e:
                logger.warning(f"Failed to queue event for {task_id}: {e}")

    try:
        final_state = run_research(query=query, audience=audience, stream_callback=event_callback)

        research_tasks[task_id]["status"] = "completed"
        research_tasks[task_id]["result"] = final_state

        if queue and main_loop.is_running():
            completion_payload = {
                "type": "completed",
                "task_id": task_id,
                "result": {
                    "query": final_state.get("query"),
                    "audience": final_state.get("audience"),
                    "sub_queries": final_state.get("sub_queries", []),
                    "search_results": final_state.get("search_results", []),
                    "extracted_content_count": len(final_state.get("extracted_content", [])),
                    "synthesis": final_state.get("synthesis", {}),
                    "gaps_identified": final_state.get("gaps_identified", []),
                    "report": final_state.get("report", ""),
                    "report_html": final_state.get("report_html", ""),
                    "visual_data": final_state.get("visual_data", []),
                },
            }
            main_loop.call_soon_threadsafe(queue.put_nowait, completion_payload)

    except Exception as err:
        logger.error(f"Research pipeline failed for task {task_id}: {err}", exc_info=True)
        research_tasks[task_id]["status"] = "failed"
        research_tasks[task_id]["error"] = str(err)

        if queue and main_loop.is_running():
            error_payload = {"type": "error", "task_id": task_id, "error": str(err)}
            main_loop.call_soon_threadsafe(queue.put_nowait, error_payload)


@app.post("/api/research", response_model=TaskStatusResponse)
async def start_research(request: ResearchRequest, background_tasks: BackgroundTasks):
    """
    Start a new multi-agent research task.
    Returns immediately with a task_id for streaming or polling.
    """
    if not request.query.strip():
        raise HTTPException(status_code=400, detail="Query string cannot be empty")

    task_id = f"task_{uuid.uuid4().hex[:10]}"
    research_tasks[task_id] = {
        "task_id": task_id,
        "status": "queued",
        "query": request.query,
        "audience": request.audience,
        "agent_logs": [f"🚀 Task created: {request.query}"],
        "current_node": "init",
        "result": None,
        "error": None,
    }

    event_queues[task_id] = asyncio.Queue()

    loop = asyncio.get_running_loop()
    # Launch in background thread so API call is non-blocking
    background_tasks.add_task(_execute_research_task, task_id, request.query, request.audience, loop)

    return TaskStatusResponse(
        task_id=task_id,
        status="queued",
        query=request.query,
        audience=request.audience,
        agent_logs=research_tasks[task_id]["agent_logs"],
        current_node="init",
    )


@app.get("/api/research/status/{task_id}")
def get_task_status(task_id: str):
    """Get status and current agent logs for a given research task."""
    if task_id not in research_tasks:
        raise HTTPException(status_code=404, detail="Task ID not found")
    
    task = research_tasks[task_id]
    return {
        "task_id": task_id,
        "status": task["status"],
        "query": task["query"],
        "audience": task["audience"],
        "current_node": task.get("current_node"),
        "agent_logs": task["agent_logs"],
        "error": task.get("error"),
        "has_result": task.get("result") is not None,
    }


@app.get("/api/research/result/{task_id}")
def get_task_result(task_id: str):
    """Get the full final output for a completed research task."""
    if task_id not in research_tasks:
        raise HTTPException(status_code=404, detail="Task ID not found")

    task = research_tasks[task_id]
    if task["status"] == "failed":
        raise HTTPException(status_code=500, detail=f"Task failed: {task.get('error')}")

    if task["status"] != "completed" or not task.get("result"):
        raise HTTPException(status_code=202, detail="Research task is still running")

    final_state = task["result"]
    return {
        "task_id": task_id,
        "query": final_state.get("query"),
        "audience": final_state.get("audience"),
        "sub_queries": final_state.get("sub_queries", []),
        "search_results": final_state.get("search_results", []),
        "extracted_content": final_state.get("extracted_content", []),
        "synthesis": final_state.get("synthesis", {}),
        "gaps_identified": final_state.get("gaps_identified", []),
        "report": final_state.get("report", ""),
        "report_html": final_state.get("report_html", ""),
        "visual_data": final_state.get("visual_data", []),
        "agent_logs": task["agent_logs"],
    }


@app.get("/api/research/stream/{task_id}")
async def stream_research_events(task_id: str):
    """
    Server-Sent Events (SSE) stream endpoint for real-time progress updates in the React frontend.
    """
    if task_id not in research_tasks:
        raise HTTPException(status_code=404, detail="Task ID not found")

    queue = event_queues.get(task_id)

    async def event_generator():
        # Send initial status
        initial_data = {
            "type": "init",
            "task_id": task_id,
            "logs": research_tasks[task_id]["agent_logs"],
            "status": research_tasks[task_id]["status"],
        }
        yield f"data: {json.dumps(initial_data)}\n\n"

        while True:
            if not queue:
                break
            try:
                # Wait for next event with timeout to send keep-alive heartbeats
                item = await asyncio.wait_for(queue.get(), timeout=15.0)
                yield f"data: {json.dumps(item)}\n\n"

                if item.get("type") in ("completed", "error"):
                    break
            except asyncio.TimeoutError:
                # Heartbeat ping
                yield f"data: {json.dumps({'type': 'ping'})}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)
