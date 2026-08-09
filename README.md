# 🚀 JARVIS AI — A.V.E.N.G.E.R.S Protocol Multi-Agent System

> **Lead Architect**: Built with Google Antigravity SDK (`google.antigravity`)  
> **Interface**: Dark Sci-Fi Avengers HUD Dashboard (`http://localhost:7334` & Mobile Wi-Fi)  
> **Dual Engine**: Google Gemini 2.5 Flash (Primary) + Groq Llama 3.3 70B & Whisper Large v3 (Fallback)

---

## ⚡ Overview

**JARVIS AI** is an advanced, production-ready multi-agent AI system inspired by Marvel's Avengers protocol. It combines desktop OS taskbar automation, browser tab controller primitives, dynamic AI graphic design generation, voice-to-text transcription, text-to-speech vocal feedback, and dual-LLM fallback logic under a unified command center.

---

## 🛡️ A.V.E.N.G.E.R.S Sub-Agent Roster

| Agent | Icon | Role & Capabilities | Module File |
| :--- | :---: | :--- | :--- |
| **JARVIS** | 🤖 | **Prime Orchestrator**: Intent routing, streaming thinking traces, and Antigravity safety policy evaluation (`allow`, `ask_user`). | [`main_orchestrator.py`](file:///c:/Users/acer/AI_Automation/main_orchestrator.py) |
| **FRIDAY** | 📋 | **Tactical Intelligence**: Daily intelligence briefings, task logging, and calendar reminders. | [`agents/friday.py`](file:///c:/Users/acer/AI_Automation/agents/friday.py) |
| **STARK** | 💻 | **OS & Desktop Control**: Universal Windows app launcher (WhatsApp, Spotify, Notepad, Calc) & Win+1..9 taskbar shortcuts. | [`agents/stark.py`](file:///c:/Users/acer/AI_Automation/agents/stark.py) |
| **SPECTRE**| 🌐 | **Browser Controller**: Web tab manager (`playwright` CDP / desktop engine) for searching, opening, listing, & closing tabs. | [`agents/spectre.py`](file:///c:/Users/acer/AI_Automation/agents/spectre.py) |
| **HERALD** | 🎙️ | **Voice Interface**: Ultra-fast Groq Whisper STT voice parsing & non-blocking background daemon thread TTS (`pyttsx3`). | [`agents/herald.py`](file:///c:/Users/acer/AI_Automation/agents/herald.py) |
| **BANNER** | 🎨 | **Creative Design**: Fetches AI base imagery via Pollinations AI and renders Pillow (PIL) HUD layouts & typography overlays. | [`agents/banner.py`](file:///c:/Users/acer/AI_Automation/agents/banner.py) |
| **HULK** | 💥 | **Offline Engine**: Emergency failover agent executing local rules, system health diagnostics, and offline math calculations. | [`agents/hulk.py`](file:///c:/Users/acer/AI_Automation/agents/hulk.py) |

---

## 📂 Files to Upload to GitHub

When creating your repository on GitHub, upload the following files and folders:

```text
AI_Automation/
├── agents/
│   ├── __init__.py
│   ├── friday.py
│   ├── stark.py
│   ├── spectre.py
│   ├── herald.py
│   ├── banner.py
│   └── hulk.py
├── ui/
│   ├── index.html
│   ├── style.css
│   └── app.js
├── main_orchestrator.py
├── api_router.py
├── server.py
├── verify_all_agents.py
├── test_suite.py
├── requirements.txt
├── Dockerfile
├── .gitignore
├── start_jarvis_background.bat
├── start_jarvis_daemon.vbs
└── README.md
```

### 🔒 DO NOT Upload (Excluded via `.gitignore`):
- `.env` *(Contains your private `GEMINI_API_KEY` and `GROQ_API_KEY`)*
- `.venv/` *(Python virtual environment folder)*
- `__pycache__/`
- `ui/generated_designs/` *(Cached images)*
- `ui/temp_audio/` *(Cached voice clips)*

---

## 🔄 Dual API Router & Fallback Engine

JARVIS features automatic failure detection and failover logic in [`api_router.py`](file:///c:/Users/acer/AI_Automation/api_router.py):
- **Primary LLM**: Google Gemini API (`gemini-2.5-flash`) for complex orchestrations, multimodal input, and tool calling.
- **Secondary / Fast Engine**: Groq API (`llama-3.3-70b-versatile` & `whisper-large-v3`) for low-latency Whisper STT and instant failover if Gemini hits rate limits (429) or network timeouts.

---

## 📱 Mobile & iPhone 11 Integration

JARVIS includes **Device-Aware App Routing** and is accessible from your mobile phone:

1. **Local Wi-Fi Connection**: Open Chrome on your iPhone 11 connected to the same Wi-Fi network and navigate to `http://<YOUR_LOCAL_IP>:7334`.
2. **Native iOS Deep Links**: When commanded from iPhone 11, JARVIS triggers native iOS app schemes (`whatsapp://`, `youtube://`, `spotify://`, `maps://`).
3. **Optional Siri Integration (Apple Shortcuts)**: Create a shortcut in iPhone Shortcuts app with POST to `http://<YOUR_LOCAL_IP>:7334/api/command` with body `{ "command": "Ask Each Time" }`.

---

## 🚀 Getting Started

### 1. Prerequisites
- Python 3.10+
- Google Chrome Browser

### 2. Environment Setup
Create a `.env` file in the root directory:
```env
GEMINI_API_KEY=your_gemini_api_key
GROQ_API_KEY=your_groq_api_key
```

### 3. Virtual Environment & Dependencies
```bash
# Create virtual environment
python -m venv .venv

# Activate environment (Windows PowerShell)
.\.venv\Scripts\activate

# Install dependencies
pip install google-antigravity groq google-genai pyautogui playwright pillow fastapi uvicorn websockets requests pyttsx3 python-dotenv
```

### 4. Playwright Browser Setup
```bash
python -m playwright install chromium
```

### 5. Running the Application Server
```bash
python server.py
```
- Open **`http://localhost:7334`** in Google Chrome.

---

## 🧪 Verification & Automated Testing

Run the comprehensive 7-agent diagnostic verification suite:

```bash
# Run complete sub-agent capability test
python verify_all_agents.py

# Run unit & integration test suite
python test_suite.py
```

---

## 🌐 24/7 Cloud Deployment

A production-grade [`Dockerfile`](file:///c:/Users/acer/AI_Automation/Dockerfile) is included for 1-click deployment to **Render**, **Railway**, or **Google Cloud Run**:

1. Push code repository to GitHub.
2. Connect repository to [Render.com](https://render.com) or [Railway.app].
3. Set environment variables `GEMINI_API_KEY` and `GROQ_API_KEY`.
4. Deploy for a permanent `https://...` 24/7 cloud URL accessible worldwide!

---

## 📄 License
Licensed under the MIT License. Built for Marvel & AI Automation Enthusiasts.
