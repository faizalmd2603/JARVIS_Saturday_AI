const MENTRO_SUBAGENTS = [
    { id: "CORE_AI", name: "🤖 Core AI Agent", role: "Gemini-style Assistant & Camera Gesture Controller" },
    { id: "CANVA_DESIGNER", name: "🎨 Canva Graphic Studio", role: "100+ Typography Fonts & Drag/Move Canvas" },
    { id: "NOTEBOOK_AI", name: "📚 NotebookLM Studio", role: "Document Synthesis & Google Search Citation" },
    { id: "ACCOUNTANCY", name: "📊 Indian Accountancy Suite", role: "Class 11/12, B.Com, M.Com & Corporate Accounting" },
    { id: "LINGUA_DUO", name: "🦉 Duolingo Language Coach", role: "Tamil, English, Hindi, Urdu & French Tutor" },
    { id: "CAREER_SUITE", name: "💼 Career Suite & Resume", role: "Naukri / LinkedIn ATS Resume Builder" },
    { id: "INTERVIEWER_AI", name: "🎙️ AI Mock Interviewer", role: "Role-based Mock Technical Interview Simulator" },
    { id: "GITHUB_STUDIO", name: "🐙 GitHub Code Studio", role: "Repo Telemetry & AI Code Reviewer" }
];

const GOOGLE_FONTS_100 = [
    "Inter", "Roboto", "Outfit", "Poppins", "Montserrat", "Playfair Display", "Cinzel",
    "Fira Code", "Oswald", "Raleway", "Lato", "Nunito", "Merriweather", "Rubik", "Kanit",
    "Bebas Neue", "Lora", "Work Sans", "DM Sans", "Quicksand", "Barlow", "Josefin Sans",
    "PT Sans", "Inconsolata", "Source Code Pro", "Space Grotesk", "Syne", "Urbanist",
    "Plus Jakarta Sans", "Cabin", "Ubuntu", "Pacifico", "Lobster", "Abril Fatface"
];

let socket = null;
let currentSVGData = null;
let activeDesignManifest = null;
let selectedLayerId = null;
let isGestureActive = false;

document.addEventListener("DOMContentLoaded", () => {
    init3DCursor();
    init3DTiltCards();
    renderSubagents();
    initTabs();
    fetchModels();
    populateFontDropdown();
    initWebSocket();
    setupEventListeners();
    setupCoreAIPrompts();
});

// 3D Motion Cursor Trailing
function init3DCursor() {
    const cursor = document.getElementById("cursor3d");
    if (!cursor) return;
    document.addEventListener("mousemove", (e) => {
        cursor.style.left = `${e.clientX}px`;
        cursor.style.top = `${e.clientY}px`;
    });
}

// 3D Product Showcase Card Tilt Effect
function init3DTiltCards() {
    const cards = document.querySelectorAll(".tilt-card");
    cards.forEach(card => {
        card.addEventListener("mousemove", (e) => {
            const rect = card.getBoundingClientRect();
            const x = e.clientX - rect.left - rect.width / 2;
            const y = e.clientY - rect.top - rect.height / 2;
            const rotateX = (-y / rect.height) * 10;
            const rotateY = (x / rect.width) * 10;
            card.style.transform = `perspective(1000px) rotateX(${rotateX}deg) rotateY(${rotateY}deg) scale3d(1.01, 1.01, 1.01)`;
        });
        card.addEventListener("mouseleave", () => {
            card.style.transform = `perspective(1000px) rotateX(0deg) rotateY(0deg) scale3d(1, 1, 1)`;
        });
    });
}

function renderSubagents() {
    const list = document.getElementById("subagentsList");
    if (!list) return;
    list.innerHTML = "";
    MENTRO_SUBAGENTS.forEach(ag => {
        const div = document.createElement("div");
        div.className = "subagent-pill";
        div.innerHTML = `<div class="name">${ag.name}</div><div class="desc">${ag.role}</div>`;
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

function populateFontDropdown() {
    const fontSelect = document.getElementById("canvaFontSelect");
    if (!fontSelect) return;
    fontSelect.innerHTML = "";
    GOOGLE_FONTS_100.forEach(font => {
        const opt = document.createElement("option");
        opt.value = font;
        opt.innerText = font;
        fontSelect.appendChild(opt);
    });
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
        socket.onopen = () => { appendLog("SYSTEM", `WebSocket streaming active on ${window.location.host}.`); };
        socket.onmessage = (event) => { handleServerEvent(JSON.parse(event.data)); };
        socket.onclose = () => { appendLog("SYSTEM", "HTTP Serverless Mode active."); };
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

function setupCoreAIPrompts() {
    const chips = document.querySelectorAll(".prompt-chip");
    chips.forEach(chip => {
        chip.addEventListener("click", () => {
            const promptText = chip.getAttribute("data-prompt");
            const input = document.getElementById("corePromptInput");
            if (input) input.value = promptText;
            document.getElementById("btnSendCore")?.click();
        });
    });
}

function setupEventListeners() {
    // Core AI Agent
    document.getElementById("btnSendCore")?.addEventListener("click", async () => {
        const prompt = document.getElementById("corePromptInput").value;
        if (!prompt) return;
        renderMarkdown("coreOutput", "Core AI Agent processing request...");

        const res = await fetch("/api/core", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ prompt: prompt, model: getSelectedModel() })
        });
        const data = await res.json();
        renderMarkdown("coreOutput", data.response_markdown || data.message);
    });

    // Camera Hand Gesture Toggle
    document.getElementById("btnToggleCameraGesture")?.addEventListener("click", async () => {
        const box = document.getElementById("gestureBox");
        const statusText = document.getElementById("gestureStatusText");

        if (isGestureActive) {
            isGestureActive = false;
            if (box) box.style.display = "none";
            return;
        }

        try {
            const stream = await navigator.mediaDevices.getUserMedia({ video: true });
            const video = document.getElementById("webcamVideo");
            if (video) {
                video.srcObject = stream;
                isGestureActive = true;
                if (box) box.style.display = "flex";
                if (statusText) statusText.innerText = "Camera Motion Sensor ACTIVE: Wave hand left/right to expand or contrast view!";
            }
        } catch (e) {
            alert("Camera access denied or unavailable: " + e.message);
        }
    });

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
                    const agentName = data.result.agent || data.agent || "CORE_AI";
                    const msg = data.result.message || data.result.response_markdown || data.result.result_markdown || JSON.stringify(data.result);
                    appendLog(agentName, msg);
                }
            } catch (e) {
                appendLog("ERROR", `Failed to execute terminal command: ${e}`);
            }
        }
    };

    if (sendBtn) sendBtn.addEventListener("click", sendCmd);
    if (cmdInput) cmdInput.addEventListener("keypress", (e) => { if (e.key === "Enter") sendCmd(); });

    // Canva Generator
    document.getElementById("btnGenerateCanva")?.addEventListener("click", async () => {
        const prompt = document.getElementById("canvaPromptInput").value || "Modern MNC Enterprise Cloud Security Infographic";
        appendLog("CANVA", `Generating graphic for: '${prompt}'...`);
        
        try {
            const res = await fetch("/api/canva", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ prompt: prompt, model: getSelectedModel() })
            });
            const data = await res.json();
            
            const badge = document.getElementById("imageQuotaBadge");
            if (badge && data.quota) {
                badge.innerText = `${data.quota.count}/20 Monthly Quota`;
            }

            if (data.status === "rate_limited") {
                alert(data.message);
                return;
            }

            if (data.svg_graphic) {
                currentSVGData = data.svg_graphic;
                activeDesignManifest = data.design;
                const viewport = document.getElementById("canvaViewport");
                if (viewport) viewport.innerHTML = data.svg_graphic;
                renderCanvaLayers(data.design);
                setupSVGClickListeners();
                appendLog("CANVA", `Visual Graphic Ready: '${data.design?.title}'`);
            }
        } catch (e) {
            console.error("Canva API error:", e);
        }
    });

    // Canva Layer Edit Apply
    document.getElementById("btnApplyLayerChanges")?.addEventListener("click", () => {
        if (!activeDesignManifest || !selectedLayerId) {
            alert("Click a text layer in the canvas preview first to edit.");
            return;
        }

        const newText = document.getElementById("layerTextInput").value;
        const font = document.getElementById("canvaFontSelect").value;

        (activeDesignManifest.layers || []).forEach(l => {
            if (l.id === selectedLayerId) {
                if (newText) l.text = newText;
                if (font) l.fontFamily = font;
            }
        });

        // Re-render SVG
        rebuildAndRenderSVG();
    });

    // Upload Image Element to Canvas
    document.getElementById("imageUploadInput")?.addEventListener("change", (e) => {
        const file = e.target.files[0];
        if (!file || !activeDesignManifest) return;
        const reader = new FileReader();
        reader.onload = (event) => {
            const imgData = event.target.result;
            activeDesignManifest.layers.push({
                id: `img_${Date.now()}`,
                type: "shape",
                x: 300,
                y: 300,
                width: 300,
                height: 200,
                color: "rgba(255,255,255,0.05)"
            });
            rebuildAndRenderSVG();
        };
        reader.readAsDataURL(file);
    });

    // Download SVG
    document.getElementById("btnDownloadCanva")?.addEventListener("click", () => {
        if (!currentSVGData) return;
        const blob = new Blob([currentSVGData], { type: "image/svg+xml" });
        const url = URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url;
        a.download = "Mentro_Graphic_Design.svg";
        a.click();
        URL.revokeObjectURL(url);
    });

    // Download 4K PDF for Graphic Studio
    document.getElementById("btnDownload4KPDF")?.addEventListener("click", () => {
        const viewport = document.getElementById("canvaViewport");
        if (!viewport || !window.html2pdf) return;
        const opt = {
            margin: 0,
            filename: 'Mentro_Graphic_Design_4K.pdf',
            image: { type: 'jpeg', quality: 1.0 },
            html2canvas: { scale: 3 },
            jsPDF: { unit: 'in', format: 'a4', orientation: 'landscape' }
        };
        window.html2pdf().set(opt).from(viewport).save();
    });

    // Download 4K PDF for NotebookLM
    document.getElementById("btnDownloadNotebookPDF")?.addEventListener("click", () => {
        const card = document.getElementById("notebookOutputCard");
        if (!card || !window.html2pdf) return;
        const opt = {
            margin: 0.4,
            filename: 'Mentro_NotebookLM_Report_4K.pdf',
            image: { type: 'jpeg', quality: 1.0 },
            html2canvas: { scale: 3 },
            jsPDF: { unit: 'in', format: 'letter', orientation: 'portrait' }
        };
        window.html2pdf().set(opt).from(card).save();
    });

    // NotebookLM Synthesis
    document.getElementById("btnSummarizeNotebook")?.addEventListener("click", async () => {
        const content = document.getElementById("notebookInput").value;
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
        renderMarkdown("notebookOutput", "Searching Google & synthesizing citations...");
        const res = await fetch("/api/notebook", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ query: query, action: "search_synthesis", model: getSelectedModel() })
        });
        const data = await res.json();
        renderMarkdown("notebookOutput", data.synthesis_markdown || data.message);
    });

    // Accountancy Solver
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

    // Duolingo
    document.getElementById("btnDuoLesson")?.addEventListener("click", async () => {
        const lang = document.getElementById("duoLanguageSelect").value;
        const topic = document.getElementById("duoTopicInput").value;
        renderMarkdown("duoLessonOutput", "Generating interactive language lesson...");

        const res = await fetch("/api/duolingo", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ action: "lesson", language: lang, topic: topic, model: getSelectedModel() })
        });
        const data = await res.json();
        renderMarkdown("duoLessonOutput", data.lesson_markdown || data.message);
    });
}

function renderCanvaLayers(design) {
    const list = document.getElementById("canvaLayersList");
    if (!list || !design) return;
    list.innerHTML = "";
    (design.layers || []).forEach(l => {
        const item = document.createElement("div");
        item.style.fontSize = "0.78rem";
        item.style.padding = "6px";
        item.style.background = "rgba(255,255,255,0.03)";
        item.style.borderRadius = "4px";
        item.style.marginBottom = "4px";
        item.style.cursor = "pointer";
        item.innerText = `[${(l.type || 'layer').toUpperCase()}] ${l.text || l.id} (${l.fontFamily || 'Inter'})`;
        item.addEventListener("click", () => {
            selectedLayerId = l.id;
            document.getElementById("layerTextInput").value = l.text || "";
            document.getElementById("canvaFontSelect").value = l.fontFamily || "Inter";
        });
        list.appendChild(item);
    });
}

function setupSVGClickListeners() {
    const textLayers = document.querySelectorAll(".canva-svg-layer");
    textLayers.forEach(layer => {
        layer.addEventListener("click", () => {
            const id = layer.getAttribute("data-layer-id");
            selectedLayerId = id;
            const found = (activeDesignManifest?.layers || []).find(l => l.id === id);
            if (found) {
                document.getElementById("layerTextInput").value = found.text || "";
                document.getElementById("canvaFontSelect").value = found.fontFamily || "Inter";
            }
        });
    });
}

function rebuildAndRenderSVG() {
    if (!activeDesignManifest) return;
    const bg_url = activeDesignManifest.background?.image_url || "";
    const w = activeDesignManifest.width || 1080;
    const h = activeDesignManifest.height || 1080;

    const svg_parts = [
        `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 ${w} ${h}" width="100%" height="100%" id="activeCanvaSVG">`,
        `<rect width="${w}" height="${h}" fill="${activeDesignManifest.background?.color || '#0f172a'}"/>`,
        `<image href="${bg_url}" width="${w}" height="${h}" opacity="0.35" preserveAspectRatio="xMidYMid slice"/>`
    ];

    (activeDesignManifest.layers || []).forEach(layer => {
        if (layer.type === "shape") {
            svg_parts.append(`<rect x="${layer.x}" y="${layer.y}" width="${layer.width}" height="${layer.height}" rx="16" fill="${layer.color}" stroke="${layer.borderColor || '#38bdf8'}" stroke-width="3"/>`);
        } else if (layer.type === "text") {
            svg_parts.push(`<text x="${layer.x}" y="${layer.y}" font-family="${layer.fontFamily || 'Inter'}, sans-serif" font-size="${layer.fontSize || 40}" font-weight="${layer.fontWeight || 'bold'}" fill="${layer.color || '#ffffff'}" text-anchor="middle" dominant-baseline="middle" class="canva-svg-layer" data-layer-id="${layer.id}">${layer.text}</text>`);
        }
    });

    svg_parts.push('</svg>');
    currentSVGData = svg_parts.join("\n");
    const viewport = document.getElementById("canvaViewport");
    if (viewport) viewport.innerHTML = currentSVGData;
    setupSVGClickListeners();
}
