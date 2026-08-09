import os
import sys
import json
import base64
import logging
import asyncio

# Ensure project root is in sys.path for Cloud Linux Containers (Render/Railway/CloudRun)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, UploadFile, File
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
import uvicorn
from dotenv import load_dotenv

from main_orchestrator import orchestrator

load_dotenv()

app = FastAPI(title="JARVIS AI - AVENGERS HUD Server")

TEMP_AUDIO_DIR = os.path.join("ui", "temp_audio")
os.makedirs(TEMP_AUDIO_DIR, exist_ok=True)
os.makedirs(os.path.join("ui", "generated_designs"), exist_ok=True)

app.mount("/ui", StaticFiles(directory="ui"), name="ui")
app.mount("/generated_designs", StaticFiles(directory=os.path.join("ui", "generated_designs")), name="generated_designs")

@app.get("/")
async def get_index():
    return FileResponse(os.path.join("ui", "index.html"))

@app.get("/api/status")
async def get_status():
    return {
        "system": "JARVIS AI Core",
        "port": int(os.getenv("PORT", 7334)),
        "agents": list(orchestrator.agents.keys()),
        "status": "ONLINE"
    }

@app.post("/api/command")
async def process_command(payload: dict):
    command_text = payload.get("command", "")
    result = orchestrator.execute_command_sync(command_text)
    return result

@app.post("/api/voice")
async def process_voice_file(file: UploadFile = File(...)):
    audio_path = os.path.join(TEMP_AUDIO_DIR, f"voice_{file.filename}")
    with open(audio_path, "wb") as f:
        f.write(await file.read())
    
    transcription_res = orchestrator.agents["HERALD"].process_voice_audio(audio_path)
    transcribed_text = transcription_res.get("transcription", "")
    
    if transcribed_text and not transcribed_text.startswith("["):
        orch_res = orchestrator.execute_command_sync(transcribed_text)
        return {"transcription": transcribed_text, "execution": orch_res}
    return {"transcription": transcribed_text, "error": "Transcription failed"}

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    logging.info("[Server] Client WebSocket connected.")
    try:
        while True:
            data = await websocket.receive_text()
            payload = json.loads(data)
            msg_type = payload.get("type", "command")
            
            if msg_type == "command":
                cmd_text = payload.get("text", "").strip()
                if cmd_text:
                    async for step in orchestrator.route_and_execute_stream(cmd_text):
                        await websocket.send_text(json.dumps(step))
                        await asyncio.sleep(0.05)

            elif msg_type == "audio":
                audio_b64 = payload.get("data", "")
                if audio_b64:
                    audio_bytes = base64.b64decode(audio_b64.split(",")[-1])
                    audio_path = os.path.join(TEMP_AUDIO_DIR, "live_voice.wav")
                    with open(audio_path, "wb") as f:
                        f.write(audio_bytes)
                    
                    await websocket.send_text(json.dumps({
                        "event": "thinking",
                        "agent": "HERALD",
                        "step": "Processing audio through Groq Whisper STT API...",
                        "thought": "Transcribing voice command buffer."
                    }))

                    trans_res = orchestrator.agents["HERALD"].process_voice_audio(audio_path)
                    text_cmd = trans_res.get("transcription", "")
                    
                    await websocket.send_text(json.dumps({
                        "event": "voice_transcribed",
                        "agent": "HERALD",
                        "transcription": text_cmd,
                        "step": f"Voice Command Transcribed: '{text_cmd}'"
                    }))

                    if text_cmd and not text_cmd.startswith("["):
                        async for step in orchestrator.route_and_execute_stream(text_cmd):
                            await websocket.send_text(json.dumps(step))
                            await asyncio.sleep(0.05)

    except WebSocketDisconnect:
        logging.info("[Server] Client WebSocket disconnected.")
    except Exception as e:
        logging.error(f"[Server] WebSocket error: {e}")

if __name__ == "__main__":
    import socket
    local_ip = "127.0.0.1"
    try:
        local_ip = socket.gethostbyname(socket.gethostname())
    except Exception:
        pass

    port = int(os.getenv("PORT", 7334))

    print("\n=======================================================")
    print(" [+] JARVIS AI - AVENGERS HUD SERVER ONLINE")
    print(f" [+] Local Desktop URL : http://localhost:{port}")
    print(f" [+] iPhone 11 Wi-Fi URL: http://{local_ip}:{port}")
    print("=======================================================\n")
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")
