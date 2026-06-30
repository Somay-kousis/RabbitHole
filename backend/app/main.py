import os
import json
import uuid
import asyncio
from typing import Dict, Any, List, Optional
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from app.courtroom.graph.builder import courtroom_app
from app.courtroom.seed_cases import CASES_TO_ADD

app = FastAPI(title="RabbitHole Courtroom API", version="1.0.0")

# Enable CORS for the Node frontend dev server
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For local development simplicity
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

HISTORY_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "history.json")
START_PARAMS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "start_params.json")

# In-memory store for initial states of new runs before checkpointer takes over
# Backup to a file so it survives server restarts
def load_json_file(filepath: str, default: Any) -> Any:
    if os.path.exists(filepath):
        try:
            with open(filepath, "r") as f:
                return json.load(f)
        except Exception:
            return default
    return default

def save_json_file(filepath: str, data: Any):
    try:
        with open(filepath, "w") as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        print(f"Error saving file {filepath}: {e}")

# Helper to serialize states (especially LangChain Documents)
def serialize_state(state_values: Dict[str, Any]) -> Dict[str, Any]:
    serialized = {}
    for k, v in state_values.items():
        if k == "final_docs" and v:
            serialized_docs = []
            for doc in v:
                # Handle LangChain Document object or dict-like object
                page_content = getattr(doc, "page_content", "")
                if not page_content and isinstance(doc, dict):
                    page_content = doc.get("page_content", "")
                metadata = getattr(doc, "metadata", {})
                if not metadata and isinstance(doc, dict):
                    metadata = doc.get("metadata", {})
                serialized_docs.append({
                    "page_content": page_content,
                    "metadata": metadata
                })
            serialized[k] = serialized_docs
        elif k == "perspectives" and v:
            serialized[k] = [dict(p) for p in v]
        elif k == "judiciary" and v:
            serialized[k] = dict(v)
        else:
            serialized[k] = v
    return serialized

class StartDebateRequest(BaseModel):
    user_input: str
    number_of_perspectives: Optional[int] = None
    judiciary_corrupt: Optional[bool] = None
    specific_roles: Optional[List[str]] = None

class ResumeDebateRequest(BaseModel):
    action: str  # continue_debate, generate_conclusion, continue_debate_with_input
    in_session_input: Optional[str] = ""

@app.get("/api/cases")
def get_cases():
    return CASES_TO_ADD

@app.get("/api/history")
def get_history():
    return load_json_file(HISTORY_FILE, [])

@app.post("/api/debate/start")
def start_debate(req: StartDebateRequest):
    thread_id = str(uuid.uuid4())
    
    # Construct initial state parameters
    initial_state = {
        "user_input": req.user_input,
        "turn_count": 0,
        "judiciary_corrupt": req.judiciary_corrupt if req.judiciary_corrupt is not None else False,
        "user_commands": {
            "number_of_perspectives": req.number_of_perspectives,
            "judiciary_type": "corrupt" if req.judiciary_corrupt else "neutral",
            "specific_roles": req.specific_roles or []
        }
    }
    
    # Save start parameters
    start_params = load_json_file(START_PARAMS_FILE, {})
    start_params[thread_id] = initial_state
    save_json_file(START_PARAMS_FILE, start_params)
    
    # Save to history list
    history = load_json_file(HISTORY_FILE, [])
    history.insert(0, {
        "thread_id": thread_id,
        "title": req.user_input[:80] + ("..." if len(req.user_input) > 80 else ""),
        "timestamp": os.popen("date").read().strip(),
        "status": "starting"
    })
    save_json_file(HISTORY_FILE, history)
    
    return {"thread_id": thread_id}

@app.get("/api/debate/state/{thread_id}")
def get_debate_state(thread_id: str):
    config = {"configurable": {"thread_id": thread_id}}
    state = courtroom_app.get_state(config)
    if not state or not state.values:
        start_params = load_json_file(START_PARAMS_FILE, {})
        if thread_id in start_params:
            return {"values": start_params[thread_id], "next": ["query_refine_node"]}
        raise HTTPException(status_code=404, detail="Thread not found")
    
    return {
        "values": serialize_state(state.values),
        "next": list(state.next)
    }

@app.post("/api/debate/resume/{thread_id}")
def resume_debate(thread_id: str, req: ResumeDebateRequest):
    config = {"configurable": {"thread_id": thread_id}}
    state = courtroom_app.get_state(config)
    
    if not state or not state.values:
        raise HTTPException(status_code=404, detail="Thread state not found or expired")
    
    # We update the state in LangGraph
    state_update = {
        "next_action": req.action,
        "in_session_input": req.in_session_input or ""
    }
    
    courtroom_app.update_state(config, state_update)
    
    # Update status in history
    history = load_json_file(HISTORY_FILE, [])
    for entry in history:
        if entry["thread_id"] == thread_id:
            if req.action == "generate_conclusion":
                entry["status"] = "concluding"
            else:
                entry["status"] = "resuming"
            break
    save_json_file(HISTORY_FILE, history)
    
    return {"status": "resumed"}

@app.get("/api/debate/stream/{thread_id}")
async def stream_debate(thread_id: str):
    config = {"configurable": {"thread_id": thread_id}}
    
    # Check if thread exists in checkpoints
    state = courtroom_app.get_state(config)
    
    if not state or not state.values:
        # First-time execution, fetch initial state parameters
        start_params = load_json_file(START_PARAMS_FILE, {})
        if thread_id not in start_params:
            raise HTTPException(status_code=404, detail="Thread parameters not found")
        input_data = start_params[thread_id]
    else:
        # Resuming execution
        input_data = None

    async def sse_generator():
        # Update thread status in history
        history = load_json_file(HISTORY_FILE, [])
        for entry in history:
            if entry["thread_id"] == thread_id:
                entry["status"] = "running"
                break
        save_json_file(HISTORY_FILE, history)

        try:
            # We run the LangGraph simulation
            # Since the graph might invoke synchronous models, we run astream as it's async-native
            async for event in courtroom_app.astream(input_data, config=config):
                for node_name, state_update in event.items():
                    # Send node execution start notification
                    yield f"event: node_start\ndata: {json.dumps({'node': node_name})}\n\n"
                    await asyncio.sleep(0.1)
                    
                    # Package details of the node execution
                    payload = {"node": node_name}
                    
                    if "final_docs" in state_update and state_update["final_docs"]:
                        docs = state_update["final_docs"]
                        payload["final_docs"] = [
                            {"page_content": doc.page_content, "metadata": getattr(doc, "metadata", {})}
                            for doc in docs
                        ]
                    
                    if "perspectives" in state_update:
                        payload["perspectives"] = [dict(p) for p in state_update["perspectives"]]
                        
                    if "judiciary" in state_update:
                        payload["judiciary"] = dict(state_update["judiciary"])
                        
                    if "conclusion" in state_update:
                        payload["conclusion"] = state_update["conclusion"]
                        
                    if "latest_overall_round_summary" in state_update:
                        payload["latest_overall_round_summary"] = state_update["latest_overall_round_summary"]
                        
                    # Yield event update
                    yield f"event: node_update\ndata: {json.dumps(payload)}\n\n"
                    await asyncio.sleep(0.1)

            # Execution successfully completed this segment
            # Check if we are at an interrupt (e.g. hitl_node is next)
            current_state = courtroom_app.get_state(config)
            
            if current_state.next:
                # We are paused at an interrupt (usually before hitl_node)
                history = load_json_file(HISTORY_FILE, [])
                for entry in history:
                    if entry["thread_id"] == thread_id:
                        entry["status"] = "waiting_for_input"
                        break
                save_json_file(HISTORY_FILE, history)

                yield f"event: interrupt\ndata: {json.dumps({'next': list(current_state.next), 'state': serialize_state(current_state.values)})}\n\n"
            else:
                # The graph ended completely
                history = load_json_file(HISTORY_FILE, [])
                for entry in history:
                    if entry["thread_id"] == thread_id:
                        entry["status"] = "concluded"
                        break
                save_json_file(HISTORY_FILE, history)

                yield f"event: complete\ndata: {json.dumps({'state': serialize_state(current_state.values)})}\n\n"

        except Exception as e:
            import traceback
            trace_str = traceback.format_exc()
            print(f"Error streaming courtroom thread {thread_id}: {e}\n{trace_str}")
            yield f"event: error\ndata: {json.dumps({'message': str(e), 'trace': trace_str})}\n\n"

    return StreamingResponse(sse_generator(), media_type="text/event-stream")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
