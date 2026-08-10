import os
import sys
import json
import logging
import asyncio

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, UploadFile, File
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse
import uvicorn
from dotenv import load_dotenv

from main_orchestrator import orchestrator
from api_router import AVAILABLE_MODELS, router

load_dotenv()

app = FastAPI(title="Mentro AI MNC Corporate Platform", version="3.0.0")

TEMP_AUDIO_DIR = os.path.join("ui", "temp_audio")
os.makedirs(TEMP_AUDIO_DIR, exist_ok=True)
os.makedirs(os.path.join("ui", "generated_designs"), exist_ok=True)

app.mount("/ui", StaticFiles(directory="ui"), name="ui")
app.mount("/generated_designs", StaticFiles(directory=os.path.join("ui", "generated_designs")), name="generated_designs")

@app.get("/")
async def get_index():
    return FileResponse(os.path.join("ui", "index.html"))

@app.get("/api/models")
async def get_models():
    return {"status": "success", "models": AVAILABLE_MODELS}

@app.post("/api/terminal")
async def terminal_command(payload: dict):
    text = payload.get("text", "")
    model = payload.get("model", "gemini-3.5-flash-lite")
    result = orchestrator.execute_command_sync(text, model=model)
    return {"status": "success", "agent": result.get("agent", "MENTRO_PRIME"), "result": result}

@app.post("/api/canva")
async def canva_studio(payload: dict):
    prompt = payload.get("prompt", "Superagent Platform Poster")
    model = payload.get("model", "gemini-3.5-flash-lite")
    return orchestrator.agents["CANVA_DESIGNER"].execute(prompt, model=model)

@app.post("/api/notebook")
async def notebook_studio(payload: dict):
    action = payload.get("action", "summarize")
    model = payload.get("model", "gemini-3.5-flash-lite")
    return orchestrator.agents["NOTEBOOK_AI"].execute(payload, action=action, model=model)

@app.post("/api/accountancy")
async def accountancy_solver(payload: dict):
    problem = payload.get("problem", "Draft a Balance Sheet for ABC Ltd with Share Capital 500000")
    model = payload.get("model", "gemini-3.5-flash-lite")
    return orchestrator.agents["NOTEBOOK_AI"].solve_accountancy(problem, model=model)

@app.post("/api/duolingo")
async def duolingo_tutor(payload: dict):
    action = payload.get("action", "lesson")
    model = payload.get("model", "gemini-3.5-flash-lite")
    return orchestrator.agents["LINGUA_DUO"].execute(payload, action=action, model=model)

@app.post("/api/career")
async def career_suite(payload: dict):
    action = payload.get("action", "build_resume")
    model = payload.get("model", "gemini-3.5-flash-lite")
    return orchestrator.agents["CAREER_SUITE"].execute(payload, action=action, model=model)

@app.post("/api/interview")
async def mock_interview(payload: dict):
    action = payload.get("action", "evaluate")
    model = payload.get("model", "gemini-3.5-flash-lite")
    return orchestrator.agents["INTERVIEWER_AI"].execute(payload, action=action, model=model)

@app.post("/api/github")
async def github_studio(payload: dict):
    action = payload.get("action", "review_code")
    model = payload.get("model", "gemini-3.5-flash-lite")
    return orchestrator.agents["GITHUB_STUDIO"].execute(payload, action=action, model=model)

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    logging.info("[MentroServer] Client WebSocket connected.")
    try:
        while True:
            data = await websocket.receive_text()
            payload = json.loads(data)
            cmd_text = payload.get("text", "").strip()
            selected_model = payload.get("model", "gemini-3.5-flash-lite")

            if cmd_text:
                async for step in orchestrator.route_and_execute_stream(cmd_text, model=selected_model):
                    await websocket.send_text(json.dumps(step))
                    await asyncio.sleep(0.05)

    except WebSocketDisconnect:
        logging.info("[MentroServer] Client WebSocket disconnected.")
    except Exception as e:
        logging.error(f"[MentroServer] WebSocket error: {e}")

if __name__ == "__main__":
    port = int(os.getenv("PORT", 7334))
    print("\n=======================================================")
    print(" [+] MENTRO AI - MNC CORPORATE PLATFORM ONLINE")
    print(f" [+] Local Web App URL : http://localhost:{port}")
    print("=======================================================\n")
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")
