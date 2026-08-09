const MENTRO_SUBAGENTS = [
    { id: "CANVA_DESIGNER", name: "🎨 Canva Design Studio", role: "Layered Canva-style Graphics & Image AI" },
    { id: "NOTEBOOK_AI", name: "📚 NotebookLM Studio", role: "Document Synthesis & Study Flashcards" },
    { id: "CAREER_SUITE", name: "💼 Career Suite & Resume", role: "Naukri / LinkedIn ATS Resume Builder" },
    { id: "INTERVIEWER_AI", name: "🎙️ AI Mock Interviewer", role: "Role-based Mock Technical Interview Simulator" },
    { id: "GITHUB_STUDIO", name: "🐙 GitHub Code Studio", role: "Repo Telemetry & AI Code Reviewer" }
];

let socket = null;
let availableModels = [];

document.addEventListener("DOMContentLoaded", () => {
    renderSubagents();
    initTabs();
    fetchModels();
    initWebSocket();
    setupEventListeners();
});

function renderSubagents() {
    const list = document.getElementById("subagentsList");
    list.innerHTML = "";
    MENTRO_SUBAGENTS.forEach(ag => {
        const div = document.createElement("div");
        div.className = "subagent-card";
        div.innerHTML = `
            <div class="subagent-name">${ag.name}</div>
            <div class="subagent-role">${ag.role}</div>
        `;
        list.appendChild(div);
    });
}

function initTabs() {
    const tabs = document.querySelectorAll(".nav-tab");
    tabs.forEach(tab => {
        tab.addEventListener("click", () => {
            tabs.forEach(t => t.classList.remove("active"));
            document.querySelectorAll(".tab-pane").forEach(p => p.classList.remove("active"));
            
            tab.classList.add("active");
            const paneId = tab.getAttribute("data-tab");
            document.getElementById(paneId).classList.add("active");
        });
    });
}

async function fetchModels() {
    try {
        const res = await fetch("/api/models");
        const data = await res.json();
        if (data.models) {
            availableModels = data.models;
            const select = document.getElementById("modelSelect");
            select.innerHTML = "";
            data.models.forEach(m => {
                const opt = document.createElement("option");
                opt.value = m.id;
                opt.innerText = `${m.name} [${m.provider}]`;
                select.appendChild(opt);
            });
        }
    } catch (e) {
        console.error("Fetch models error:", e);
    }
}

function getSelectedModel() {
    const select = document.getElementById("modelSelect");
    return select ? select.value : "gemini-3.5-flash-lite";
}

function initWebSocket() {
    const protocol = window.location.protocol === "https:" ? "wss:" : "ws:";
    const wsUrl = `${protocol}//${window.location.host}/ws`;
    
    try {
        socket = new WebSocket(wsUrl);
        socket.onopen = () => {
            appendLog("SYSTEM", `WebSocket stream active on ${window.location.host}.`, "log-success");
        };
        socket.onmessage = (event) => {
            const data = JSON.parse(event.data);
            handleServerEvent(data);
        };
        socket.onclose = () => {
            appendLog("SYSTEM", "HTTP Serverless Mode active.", "log-muted");
        };
    } catch (e) {
        appendLog("SYSTEM", "HTTP Serverless Mode active.", "log-muted");
    }
}

function handleServerEvent(data) {
    if (data.event === "thinking") {
        appendLog(data.agent, `${data.step} (${data.thought})`);
    } else if (data.event === "agent_selected") {
        appendLog("MENTRO", `Delegating workload to [${data.target}]: ${data.reasoning}`);
    } else if (data.event === "completed") {
        appendLog(data.agent, `Result: ${data.final_response}`);
    }
}

function appendLog(agent, text) {
    const consoleElem = document.getElementById("terminalConsole");
    const now = new Date().toLocaleTimeString();
    const div = document.createElement("div");
    div.className = "log-entry";
    div.innerHTML = `<span style="color:#94a3b8">[${now}]</span> <span style="color:#ffd700;font-weight:bold">[${agent}]</span>: ${text}`;
    consoleElem.appendChild(div);
    consoleElem.scrollTop = consoleElem.scrollHeight;
}

function setupEventListeners() {
    // Superagent Terminal Command (WebSocket + HTTP Serverless Fallback)
    const sendBtn = document.getElementById("btnSend");
    const cmdInput = document.getElementById("cmdInput");
    
    const sendCmd = async () => {
        const text = cmdInput.value.trim();
        if (!text) return;
        cmdInput.value = "";
        appendLog("USER", text);

        if (socket && socket.readyState === WebSocket.OPEN) {
            socket.send(JSON.stringify({ type: "command", text: text, model: getSelectedModel() }));
        } else {
            appendLog("MENTRO", `Processing command via HTTP Serverless [${getSelectedModel()}]...`);
            try {
                const res = await fetch("/api/terminal", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ text: text, model: getSelectedModel() })
                });
                const data = await res.json();
                if (data.result) {
                    const agentName = data.result.agent || data.agent || "MENTRO";
                    const msg = data.result.message || data.result.result || JSON.stringify(data.result);
                    appendLog(agentName, msg);
                }
            } catch (e) {
                appendLog("ERROR", `Failed to execute terminal command: ${e}`);
            }
        }
    };

    sendBtn.addEventListener("click", sendCmd);
    cmdInput.addEventListener("keypress", (e) => { if (e.key === "Enter") sendCmd(); });

    // Canva Generator
    document.getElementById("btnGenerateCanva").addEventListener("click", async () => {
        const prompt = document.getElementById("canvaPromptInput").value || "Superagent Platform Poster";
        appendLog("CANVA", `Generating layered canvas for: '${prompt}' with model [${getSelectedModel()}]...`);
        
        try {
            const res = await fetch("/api/canva", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ prompt: prompt, model: getSelectedModel() })
            });
            const data = await res.json();
            if (data.design) {
                renderCanvaDesign(data.design);
                appendLog("CANVA", `Design ready: '${data.design.title}' with ${data.design.layers?.length || 0} editable layers.`);
            }
        } catch (e) {
            console.error("Canva API error:", e);
        }
    });

    // NotebookLM Synthesis
    document.getElementById("btnSummarizeNotebook").addEventListener("click", async () => {
        const content = document.getElementById("notebookInput").value;
        const out = document.getElementById("notebookOutput");
        out.innerText = "Synthesizing document insights...";
        
        const res = await fetch("/api/notebook", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ content: content, action: "summarize", model: getSelectedModel() })
        });
        const data = await res.json();
        out.innerText = data.synthesis || JSON.stringify(data, null, 2);
    });

    document.getElementById("btnFlashcardsNotebook").addEventListener("click", async () => {
        const content = document.getElementById("notebookInput").value;
        const out = document.getElementById("notebookOutput");
        out.innerText = "Extracting flashcards...";
        
        const res = await fetch("/api/notebook", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ content: content, action: "flashcards", model: getSelectedModel() })
        });
        const data = await res.json();
        out.innerText = JSON.stringify(data.result || data, null, 2);
    });

    // Career Suite
    document.getElementById("btnBuildResume").addEventListener("click", async () => {
        const role = document.getElementById("careerRoleInput").value;
        const summary = document.getElementById("resumeInputText").value;
        const out = document.getElementById("careerOutput");
        out.innerText = "Building ATS Resume...";

        const res = await fetch("/api/career", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ action: "build_resume", user_info: `Role: ${role}\nSummary: ${summary}`, model: getSelectedModel() })
        });
        const data = await res.json();
        out.innerText = JSON.stringify(data.resume || data, null, 2);
    });

    document.getElementById("btnATSCheck").addEventListener("click", async () => {
        const resume = document.getElementById("resumeInputText").value;
        const job = document.getElementById("jobDescInputText").value;
        const out = document.getElementById("careerOutput");
        out.innerText = "Calculating ATS Match Score...";

        const res = await fetch("/api/career", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ action: "ats_match", resume: resume, job_description: job, model: getSelectedModel() })
        });
        const data = await res.json();
        out.innerText = JSON.stringify(data.result || data, null, 2);
    });

    // Mock Interviewer
    document.getElementById("btnGetQuestion").addEventListener("click", async () => {
        const role = document.getElementById("interviewRoleSelect").value;
        const qBox = document.getElementById("interviewQuestionBox");
        qBox.innerText = "Generating question...";

        const res = await fetch("/api/interview", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ action: "generate_question", role: role, model: getSelectedModel() })
        });
        const data = await res.json();
        const q = data.interview_question?.question || "Can you describe a complex AI architecture project you designed?";
        qBox.innerText = q;
    });

    document.getElementById("btnSubmitAnswer").addEventListener("click", async () => {
        const role = document.getElementById("interviewRoleSelect").value;
        const q = document.getElementById("interviewQuestionBox").innerText;
        const ans = document.getElementById("candidateAnswerText").value;
        const out = document.getElementById("interviewEvaluationBox");
        out.innerText = "Scoring answer...";

        const res = await fetch("/api/interview", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ action: "evaluate", role: role, question: q, answer: ans, model: getSelectedModel() })
        });
        const data = await res.json();
        out.innerText = JSON.stringify(data.evaluation || data, null, 2);
    });

    // GitHub Code Studio
    document.getElementById("btnInspectRepo").addEventListener("click", async () => {
        const url = document.getElementById("githubRepoUrl").value;
        const out = document.getElementById("githubOutput");
        out.innerText = "Fetching repository telemetry...";

        const res = await fetch("/api/github", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ action: "inspect_repo", repo_url: url, model: getSelectedModel() })
        });
        const data = await res.json();
        out.innerText = JSON.stringify(data.repo_details || data, null, 2);
    });

    document.getElementById("btnReviewCode").addEventListener("click", async () => {
        const code = document.getElementById("codeReviewText").value;
        const out = document.getElementById("githubOutput");
        out.innerText = "Running AI Code Review...";

        const res = await fetch("/api/github", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ action: "review_code", code: code, model: getSelectedModel() })
        });
        const data = await res.json();
        out.innerText = JSON.stringify(data.review || data, null, 2);
    });
}

function renderCanvaDesign(design) {
    const canvas = document.getElementById("canvaCanvas");
    const layersList = document.getElementById("canvaLayersList");
    
    canvas.innerHTML = "";
    layersList.innerHTML = "";
    
    if (design.background) {
        if (design.background.image_url) {
            canvas.style.backgroundImage = `url('${design.background.image_url}')`;
        }
        if (design.background.color) {
            canvas.style.backgroundColor = design.background.color;
        }
    }

    const scale = 400 / (design.width || 1080);

    (design.layers || []).forEach(layer => {
        const item = document.createElement("div");
        item.className = "layer-item";
        item.innerHTML = `<span>[${layer.type.toUpperCase()}] ${layer.text || layer.id}</span> <span style="color:#00e5ff">${layer.fontSize || ''}px</span>`;
        layersList.appendChild(item);

        if (layer.type === "text") {
            const el = document.createElement("div");
            el.className = "canvas-layer-text";
            el.innerText = layer.text;
            el.style.left = `${(layer.x || 540) * scale}px`;
            el.style.top = `${(layer.y || 400) * scale}px`;
            el.style.fontSize = `${(layer.fontSize || 32) * scale}px`;
            el.style.color = layer.color || "#ffffff";
            el.style.fontWeight = layer.fontWeight || "normal";
            
            canvas.appendChild(el);
        }
    });
}
