const MENTRO_SUBAGENTS = [
    { id: "CANVA_DESIGNER", name: "🎨 Canva Graphic Studio", role: "Visual SVG Poster & Graphic Generator" },
    { id: "NOTEBOOK_AI", name: "📚 NotebookLM Studio", role: "Document Synthesis & Search Citation" },
    { id: "ACCOUNTANCY", name: "📊 Indian Accountancy Suite", role: "Class 11/12, B.Com, M.Com & Corporate Financial Statements" },
    { id: "LINGUA_DUO", name: "🦉 Duolingo Language Coach", role: "Tamil, English, Hindi, Urdu & French Language Tutor" },
    { id: "CAREER_SUITE", name: "💼 Career Suite & Resume", role: "Naukri / LinkedIn ATS Resume Builder" },
    { id: "INTERVIEWER_AI", name: "🎙️ AI Mock Interviewer", role: "Role-based Mock Technical Interview Simulator" },
    { id: "GITHUB_STUDIO", name: "🐙 GitHub Code Studio", role: "Repo Telemetry & AI Code Reviewer" }
];

let socket = null;
let currentSVGData = null;

document.addEventListener("DOMContentLoaded", () => {
    renderSubagents();
    initTabs();
    fetchModels();
    initWebSocket();
    setupEventListeners();
});

function renderSubagents() {
    const list = document.getElementById("subagentsList");
    if (!list) return;
    list.innerHTML = "";
    MENTRO_SUBAGENTS.forEach(ag => {
        const div = document.createElement("div");
        div.className = "subagent-pill";
        div.innerHTML = `
            <div class="name">${ag.name}</div>
            <div class="desc">${ag.role}</div>
        `;
        list.appendChild(div);
    });
}

function initTabs() {
    const tabs = document.querySelectorAll(".nav-item");
    tabs.forEach(tab => {
        tab.addEventListener("click", () => {
            tabs.forEach(t => t.classList.remove("active"));
            document.querySelectorAll(".tab-pane").forEach(p => p.classList.remove("active"));
            
            tab.classList.add("active");
            const paneId = tab.getAttribute("data-tab");
            const targetPane = document.getElementById(paneId);
            if (targetPane) targetPane.classList.add("active");
        });
    });
}

async function fetchModels() {
    try {
        const res = await fetch("/api/models");
        const data = await res.json();
        if (data.models) {
            const select = document.getElementById("modelSelect");
            if (!select) return;
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
            appendLog("SYSTEM", `WebSocket streaming active on ${window.location.host}.`);
        };
        socket.onmessage = (event) => {
            const data = JSON.parse(event.data);
            handleServerEvent(data);
        };
        socket.onclose = () => {
            appendLog("SYSTEM", "HTTP Serverless Mode active.");
        };
    } catch (e) {
        appendLog("SYSTEM", "HTTP Serverless Mode active.");
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
    if (!consoleElem) return;
    const now = new Date().toLocaleTimeString();
    const div = document.createElement("div");
    div.style.marginBottom = "6px";
    div.innerHTML = `<span style="color:#94a3b8">[${now}]</span> <span style="color:#38bdf8;font-weight:bold">[${agent}]</span>: ${text}`;
    consoleElem.appendChild(div);
    consoleElem.scrollTop = consoleElem.scrollHeight;
}

function renderMarkdown(elementId, markdownText) {
    const el = document.getElementById(elementId);
    if (!el) return;
    if (window.marked) {
        el.innerHTML = window.marked.parse(markdownText || "");
    } else {
        el.innerText = markdownText;
    }
}

function setupEventListeners() {
    // Superagent Terminal
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
                    const msg = data.result.message || data.result.result_markdown || data.result.result || JSON.stringify(data.result);
                    appendLog(agentName, msg);
                }
            } catch (e) {
                appendLog("ERROR", `Failed to execute terminal command: ${e}`);
            }
        }
    };

    if (sendBtn) sendBtn.addEventListener("click", sendCmd);
    if (cmdInput) cmdInput.addEventListener("keypress", (e) => { if (e.key === "Enter") sendCmd(); });

    // Canva Generator & Downloader
    const btnCanva = document.getElementById("btnGenerateCanva");
    if (btnCanva) {
        btnCanva.addEventListener("click", async () => {
            const prompt = document.getElementById("canvaPromptInput").value || "Modern MNC Corporate AI Cloud Architecture Poster";
            appendLog("CANVA", `Generating visual graphic for: '${prompt}'...`);
            
            try {
                const res = await fetch("/api/canva", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ prompt: prompt, model: getSelectedModel() })
                });
                const data = await res.json();
                if (data.svg_graphic) {
                    currentSVGData = data.svg_graphic;
                    const viewport = document.getElementById("canvaViewport");
                    viewport.innerHTML = data.svg_graphic;
                    renderCanvaLayers(data.design);
                    appendLog("CANVA", `Visual Graphic Ready: '${data.design?.title}'`);
                }
            } catch (e) {
                console.error("Canva API error:", e);
            }
        });
    }

    const btnDownloadCanva = document.getElementById("btnDownloadCanva");
    if (btnDownloadCanva) {
        btnDownloadCanva.addEventListener("click", () => {
            if (!currentSVGData) return;
            const blob = new Blob([currentSVGData], { type: "image/svg+xml" });
            const url = URL.createObjectURL(blob);
            const a = document.createElement("a");
            a.href = url;
            a.download = "Mentro_Canva_Graphic.svg";
            a.click();
            URL.revokeObjectURL(url);
        });
    }

    // NotebookLM Synthesis & Flashcards
    document.getElementById("btnSummarizeNotebook")?.addEventListener("click", async () => {
        const content = document.getElementById("notebookInput").value;
        const flashView = document.getElementById("flashcardsContainer");
        if (flashView) flashView.style.display = "none";
        
        renderMarkdown("notebookOutput", "Synthesizing document insights...");
        const res = await fetch("/api/notebook", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ content: content, action: "summarize", model: getSelectedModel() })
        });
        const data = await res.json();
        renderMarkdown("notebookOutput", data.synthesis_markdown || data.message);
    });

    document.getElementById("btnSearchNotebook")?.addEventListener("click", async () => {
        const query = document.getElementById("notebookSearchQuery").value || document.getElementById("notebookInput").value;
        const flashView = document.getElementById("flashcardsContainer");
        if (flashView) flashView.style.display = "none";

        renderMarkdown("notebookOutput", "Searching Google & synthesizing citations...");
        const res = await fetch("/api/notebook", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ query: query, action: "search_synthesis", model: getSelectedModel() })
        });
        const data = await res.json();
        renderMarkdown("notebookOutput", data.synthesis_markdown || data.message);
    });

    document.getElementById("btnFlashcardsNotebook")?.addEventListener("click", async () => {
        const content = document.getElementById("notebookInput").value;
        renderMarkdown("notebookOutput", "Extracting interactive flashcards...");

        const res = await fetch("/api/notebook", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ content: content, action: "flashcards", model: getSelectedModel() })
        });
        const data = await res.json();
        if (data.result && data.result.flashcards) {
            render3DFlashcards("flashcardsContainer", data.result.flashcards);
            renderMarkdown("notebookOutput", `### 🎴 ${data.result.title || 'Interactive Study Flashcards'}\nClick cards below to flip and reveal answers.`);
        }
    });

    // Indian Accountancy Solver
    document.getElementById("btnSolveAccountancy")?.addEventListener("click", async () => {
        const problem = document.getElementById("accountancyInput").value;
        renderMarkdown("accountancyOutput", "Solving accounting statement & generating balance sheets...");

        const res = await fetch("/api/accountancy", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ problem: problem, model: getSelectedModel() })
        });
        const data = await res.json();
        renderMarkdown("accountancyOutput", data.accountancy_solution || data.message);
    });

    // Duolingo Language Learning Sub-Agent
    document.getElementById("btnDuoLesson")?.addEventListener("click", async () => {
        const lang = document.getElementById("duoLanguageSelect").value;
        const topic = document.getElementById("duoTopicInput").value;
        const quizContainer = document.getElementById("duoQuizContainer");
        if (quizContainer) quizContainer.style.display = "none";

        renderMarkdown("duoLessonOutput", "Generating interactive language lesson...");
        const res = await fetch("/api/duolingo", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ action: "lesson", language: lang, topic: topic, model: getSelectedModel() })
        });
        const data = await res.json();
        renderMarkdown("duoLessonOutput", data.lesson_markdown || data.message);
    });

    document.getElementById("btnDuoQuiz")?.addEventListener("click", async () => {
        const lang = document.getElementById("duoLanguageSelect").value;
        const topic = document.getElementById("duoTopicInput").value;

        renderMarkdown("duoLessonOutput", "Generating interactive quiz challenge...");
        const res = await fetch("/api/duolingo", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ action: "quiz", language: lang, topic: topic, model: getSelectedModel() })
        });
        const data = await res.json();
        if (data.quiz) {
            renderDuolingoQuiz("duoQuizContainer", data.quiz);
            renderMarkdown("duoLessonOutput", `### 🎯 Quiz Challenge: ${data.quiz.language}\nComplete the interactive quiz above to earn +${data.quiz.xp_reward || 15} XP!`);
        }
    });

    // Career Suite
    document.getElementById("btnBuildResume")?.addEventListener("click", async () => {
        const role = document.getElementById("careerRoleInput").value;
        const summary = document.getElementById("resumeInputText").value;
        renderMarkdown("careerOutput", "Building ATS Resume...");

        const res = await fetch("/api/career", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ action: "build_resume", user_info: `Role: ${role}\nSummary: ${summary}`, model: getSelectedModel() })
        });
        const data = await res.json();
        const r = data.resume;
        if (r) {
            const md = `# 📄 ${r.name} - ${r.title}\n\n### Summary\n${r.summary}\n\n### Skills\n${(r.skills || []).map(s => `\`${s}\``).join(' ')}\n\n### Experience\n${(r.experience || []).map(e => `#### ${e.role} @ ${e.company} (${e.duration})\n` + (e.highlights || []).map(h => `- ${h}`).join('\n')).join('\n')}`;
            renderMarkdown("careerOutput", md);
        } else {
            renderMarkdown("careerOutput", data.message);
        }
    });

    document.getElementById("btnATSCheck")?.addEventListener("click", async () => {
        const resume = document.getElementById("resumeInputText").value;
        const job = document.getElementById("jobDescInputText").value;
        renderMarkdown("careerOutput", "Calculating ATS Match Score...");

        const res = await fetch("/api/career", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ action: "ats_match", resume: resume, job_description: job, model: getSelectedModel() })
        });
        const data = await res.json();
        const r = data.result;
        if (r) {
            const md = `# 📊 ATS Score: ${r.match_score}/100\n\n### Missing Keywords\n${(r.missing_keywords || []).map(k => `- ❌ ${k}`).join('\n')}\n\n### Strengths\n${(r.strengths || []).map(s => `- ✅ ${s}`).join('\n')}\n\n### Suggested LinkedIn Headline\n> ${r.linkedin_headline}`;
            renderMarkdown("careerOutput", md);
        } else {
            renderMarkdown("careerOutput", data.message);
        }
    });

    // Mock Interviewer
    document.getElementById("btnGetQuestion")?.addEventListener("click", async () => {
        const role = document.getElementById("interviewRoleSelect").value;
        const qBox = document.getElementById("interviewQuestionBox");
        if (qBox) qBox.innerText = "Generating question...";

        const res = await fetch("/api/interview", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ action: "generate_question", role: role, model: getSelectedModel() })
        });
        const data = await res.json();
        const q = data.interview_question?.question || "Can you describe a complex AI architecture project you designed?";
        if (qBox) qBox.innerText = q;
    });

    document.getElementById("btnSubmitAnswer")?.addEventListener("click", async () => {
        const role = document.getElementById("interviewRoleSelect").value;
        const q = document.getElementById("interviewQuestionBox").innerText;
        const ans = document.getElementById("candidateAnswerText").value;
        renderMarkdown("interviewEvaluationBox", "Scoring candidate answer...");

        const res = await fetch("/api/interview", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ action: "evaluate", role: role, question: q, answer: ans, model: getSelectedModel() })
        });
        const data = await res.json();
        const ev = data.evaluation;
        if (ev) {
            const md = `# 🏆 Verdict: ${ev.verdict} (Score: ${ev.score}/100)\n\n### Feedback\n${ev.feedback}\n\n### Key Strengths\n${(ev.key_strengths || []).map(s => `- ✅ ${s}`).join('\n')}\n\n### Follow-Up Question\n> ${ev.follow_up_question || 'None'}`;
            renderMarkdown("interviewEvaluationBox", md);
        } else {
            renderMarkdown("interviewEvaluationBox", data.message);
        }
    });

    // GitHub Code Studio
    document.getElementById("btnInspectRepo")?.addEventListener("click", async () => {
        const url = document.getElementById("githubRepoUrl").value;
        renderMarkdown("githubOutput", "Fetching repository telemetry...");

        const res = await fetch("/api/github", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ action: "inspect_repo", repo_url: url, model: getSelectedModel() })
        });
        const data = await res.json();
        const d = data.repo_details;
        if (d) {
            const md = `# 🐙 ${d.name}\n- **Stars**: ⭐ ${d.stars}\n- **Primary Language**: 💻 ${d.language}\n- **Description**: ${d.description}\n\n### AI Repository Summary\n${d.ai_summary}`;
            renderMarkdown("githubOutput", md);
        } else {
            renderMarkdown("githubOutput", data.message);
        }
    });

    document.getElementById("btnReviewCode")?.addEventListener("click", async () => {
        const code = document.getElementById("codeReviewText").value;
        renderMarkdown("githubOutput", "Running AI Code Review...");

        const res = await fetch("/api/github", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ action: "review_code", code: code, model: getSelectedModel() })
        });
        const data = await res.json();
        const r = data.review;
        if (r) {
            const md = `# 🔍 Code Quality Score: ${r.code_quality_score}/100\n\n### Summary\n${r.summary}\n\n### Refactored Code\n\`\`\`python\n${r.refactored_code || code}\n\`\`\``;
            renderMarkdown("githubOutput", md);
        } else {
            renderMarkdown("githubOutput", data.message);
        }
    });
}

function renderCanvaLayers(design) {
    const list = document.getElementById("canvaLayersList");
    if (!list || !design) return;
    list.innerHTML = "";
    (design.layers || []).forEach(l => {
        const item = document.createElement("div");
        item.style.fontSize = "0.8rem";
        item.style.padding = "6px";
        item.style.background = "rgba(255,255,255,0.03)";
        item.style.borderRadius = "4px";
        item.style.marginBottom = "4px";
        item.innerText = `[${(l.type || 'layer').toUpperCase()}] ${l.text || l.id}`;
        list.appendChild(item);
    });
}

function render3DFlashcards(containerId, cards) {
    const container = document.getElementById(containerId);
    if (!container) return;
    container.innerHTML = "";
    container.style.display = "flex";

    cards.forEach(card => {
        const cardElem = document.createElement("div");
        cardElem.className = "flashcard-3d";
        cardElem.innerHTML = `
            <div class="flashcard-inner">
                <div class="flashcard-front">
                    <div style="font-size:0.75rem;color:#38bdf8;margin-bottom:4px;">${card.category || 'Flashcard'} (Click to Flip)</div>
                    <div>${card.front}</div>
                </div>
                <div class="flashcard-back">
                    <div style="font-size:0.75rem;color:#10b981;margin-bottom:4px;">Answer</div>
                    <div>${card.back}</div>
                </div>
            </div>
        `;
        cardElem.addEventListener("click", () => {
            cardElem.classList.toggle("flipped");
        });
        container.appendChild(cardElem);
    });
}

function renderDuolingoQuiz(containerId, quiz) {
    const container = document.getElementById(containerId);
    if (!container) return;
    container.innerHTML = "";
    container.style.display = "block";

    const title = document.createElement("div");
    title.style.fontWeight = "bold";
    title.style.color = "#38bdf8";
    title.style.marginBottom = "10px";
    title.innerText = `🦉 ${quiz.language} Quiz Challenge (+${quiz.xp_reward || 15} XP)`;
    container.appendChild(title);

    (quiz.questions || []).forEach(q => {
        const qBox = document.createElement("div");
        qBox.style.background = "#0b0f19";
        qBox.style.border = "1px solid #27354f";
        qBox.style.padding = "10px";
        qBox.style.borderRadius = "6px";
        qBox.style.marginBottom = "8px";

        qBox.innerHTML = `
            <div style="font-weight:600;font-size:0.85rem;color:#fff;margin-bottom:6px;">Q${q.id}: ${q.question}</div>
            <div style="font-size:0.75rem;color:#94a3b8;margin-bottom:6px;">Guide: ${q.pronunciation_guide || ''} (${q.english_translation || ''})</div>
            <div style="display:flex;gap:6px;flex-wrap:wrap;">
                ${(q.options || []).map(opt => `<button class="mnc-btn btn-sm btn-outline opt-btn" data-correct="${opt === q.correct_answer}">${opt}</button>`).join('')}
            </div>
        `;
        container.appendChild(qBox);
    });

    container.querySelectorAll(".opt-btn").forEach(btn => {
        btn.addEventListener("click", () => {
            const isCorrect = btn.getAttribute("data-correct") === "true";
            if (isCorrect) {
                btn.style.background = "#10b981";
                btn.style.color = "#fff";
                btn.innerText += " ✅ Correct!";
            } else {
                btn.style.background = "#ef4444";
                btn.style.color = "#fff";
                btn.innerText += " ❌ Try Again";
            }
        });
    });
}
