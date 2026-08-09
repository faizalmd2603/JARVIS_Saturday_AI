# 🧠 MENTRO AI — All-in-One Superagent Platform

> **Live GitHub Repository**: [`https://github.com/faizalmd2603/JARVIS_Saturday_AI`](https://github.com/faizalmd2603/JARVIS_Saturday_AI)  
> **Deployment Ready**: Vercel Serverless (`vercel.json` & `api/index.py`) & Desktop/Mobile  
> **Multi-Model Provider**: 12+ Free AI Models Dropdown Selector (Gemini 3.1 Pro, 3.1 Flash, 3.5 Flash-Lite, 3.6 Flash, Groq Llama 3.3 70B, Pollinations AI)

---

## ⚡ Overview

**Mentro AI** is a unified superagent platform bringing together top AI productivity tools into one interface:

1. 🎨 **Canva Design Studio**: Interactive canvas rendering layered AI graphics with editable text layers, position scaling, custom typography, shape layers, and AI background generation (`Pollinations AI`).
2. 📚 **NotebookLM Studio**: Document synthesis, executive summaries, notes Q&A, and study flashcards.
3. 💼 **Career Suite (Naukri, Internshala, Unstop, LinkedIn)**: ATS-optimized AI Resume Builder, ATS match scoring, keyword gap analysis, and LinkedIn profile headline optimizer.
4. 🎙️ **AI Mock Interviewer**: Role-based mock interview questions (Software Engineer, PM, Data Scientist, UI/UX) with candidate answer scoring, feedback, and follow-up prompts.
5. 🐙 **GitHub Code Studio**: Repository telemetry inspector and AI code reviewer.
6. 🧠 **Multi-Model Provider Hub**: Live dropdown selector to switch dynamically between 12+ models (Gemini, Groq, Pollinations AI).

---

## 📖 Deep Local Execution Guidance

Follow these step-by-step instructions to run Mentro AI locally on your machine:

### Step 1: Clone Repository
```bash
git clone https://github.com/faizalmd2603/JARVIS_Saturday_AI.git
cd JARVIS_Saturday_AI
```

### Step 2: Create & Activate Python Virtual Environment
- **Windows (PowerShell)**:
  ```powershell
  python -m venv .venv
  .\.venv\Scripts\activate
  ```
- **Linux / macOS**:
  ```bash
  python3 -m venv .venv
  source .venv/bin/activate
  ```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Configure Environment Variables (`.env`)
Create a `.env` file in the root directory:
```env
GEMINI_API_KEY=your_gemini_api_key_here
GROQ_API_KEY=your_groq_api_key_here
PORT=7334
```

### Step 5: Start the Mentro AI Server
```bash
python server.py
```

### Step 6: Access the Interfaces
- **Desktop Dashboard**: Open **`http://localhost:7334`** in Chrome.
- **Mobile / iPhone 11**: Open **`http://<YOUR_LOCAL_IP>:7334`** connected to the same Wi-Fi.

### Step 7: Run Automated Verification Suite
```bash
python test_mentro_suite.py
```

---

## 🌐 Deploy to Vercel (24/7 Cloud Uptime)

This platform includes production [`vercel.json`](file:///c:/Users/acer/AI_Automation/vercel.json) and [`api/index.py`](file:///c:/Users/acer/AI_Automation/api/index.py) serverless configuration:

1. Push your latest code repository to GitHub.
2. Sign in to **[Vercel.com](https://vercel.com)**.
3. Click **Add New** ➔ **Project** ➔ Import `faizalmd2603/JARVIS_Saturday_AI`.
4. Configure Environment Variables:
   - `GEMINI_API_KEY`
   - `GROQ_API_KEY`
5. Click **Deploy**!
   - Vercel gives you a live 24/7 HTTPS domain (e.g., `https://jarvis-saturday-ai.vercel.app`) that works permanently on desktop and mobile even when your laptop is powered off!

---

## 📄 License
MIT License. Built for Superagent Enthusiasts.
