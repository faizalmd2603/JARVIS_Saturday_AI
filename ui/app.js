const AGENTS = [
    { id: "JARVIS", name: "JARVIS PRIME", role: "Main Orchestrator & Strategy", state: "ONLINE" },
    { id: "FRIDAY", name: "FRIDAY", role: "Daily Briefs & Tasks Log", state: "ONLINE" },
    { id: "STARK", name: "STARK / OS", role: "Taskbar & Desktop Installed Apps", state: "ONLINE" },
    { id: "SPECTRE", name: "SPECTRE", role: "Browser & Playwright Tabs", state: "ONLINE" },
    { id: "HERALD", name: "HERALD", role: "Whisper Voice & Speech", state: "ONLINE" },
    { id: "BANNER", name: "BANNER", role: "AI Design & Pillow Layout", state: "ONLINE" },
    { id: "HULK", name: "HULK", role: "Offline Failover Engine", state: "STANDBY" }
];

let socket = null;
let mediaRecorder = null;
let audioChunks = [];
let isRecording = false;

document.addEventListener("DOMContentLoaded", () => {
    renderAgents();
    initWebSocket();
    setupEventListeners();
});

function renderAgents() {
    const grid = document.getElementById("agentsGrid");
    grid.innerHTML = "";

    AGENTS.forEach(ag => {
        const card = document.createElement("div");
        card.className = "agent-card";
        card.id = `card-${ag.id}`;
        card.innerHTML = `
            <div class="agent-header">
                <span class="agent-name">${ag.name}</span>
                <span class="agent-state" id="state-${ag.id}">${ag.state}</span>
            </div>
            <div class="agent-role">${ag.role}</div>
        `;
        grid.appendChild(card);
    });
}

let reconnectTimer = null;

function initWebSocket() {
    if (socket && (socket.readyState === WebSocket.CONNECTING || socket.readyState === WebSocket.OPEN)) {
        return;
    }

    const protocol = window.location.protocol === "https:" ? "wss:" : "ws:";
    const wsUrl = `${protocol}//${window.location.host}/ws`;
    
    try {
        socket = new WebSocket(wsUrl);

        socket.onopen = () => {
            if (reconnectTimer) {
                clearTimeout(reconnectTimer);
                reconnectTimer = null;
            }
            const badge = document.querySelector(".status-badge span");
            if (badge) badge.innerText = "CORE ONLINE (" + window.location.host + ")";
            appendLog("SYSTEM", `WebSocket channel connected on ${window.location.host}.`, "log-success");
        };

        socket.onmessage = (event) => {
            try {
                const data = JSON.parse(event.data);
                handleServerEvent(data);
            } catch (e) {
                console.error("Log JSON parse error:", e);
            }
        };

        socket.onclose = () => {
            const badge = document.querySelector(".status-badge span");
            if (badge) badge.innerText = "RECONNECTING...";
            if (!reconnectTimer) {
                reconnectTimer = setTimeout(() => {
                    reconnectTimer = null;
                    initWebSocket();
                }, 2000);
            }
        };

        socket.onerror = (err) => {
            socket.close();
        };
    } catch (e) {
        if (!reconnectTimer) {
            reconnectTimer = setTimeout(() => {
                reconnectTimer = null;
                initWebSocket();
            }, 2000);
        }
    }
}

function handleServerEvent(data) {
    const orb = document.getElementById("voiceOrb");

    if (data.event === "thinking") {
        orb.classList.add("listening");
        highlightAgent(data.agent);
        appendLog(data.agent, `${data.step} (${data.thought})`, "log-step");
    } 
    else if (data.event === "voice_transcribed") {
        appendLog("HERALD", `Voice Transcribed: "${data.transcription}"`, "log-success");
    }
    else if (data.event === "agent_selected") {
        highlightAgent(data.target);
        appendLog("JARVIS", `Delegated to ${data.target}: ${data.reasoning}`);
    } 
    else if (data.event === "executing") {
        highlightAgent(data.agent);
        appendLog(data.agent, `Executing workload: ${data.command}`);
    } 
    else if (data.event === "completed") {
        orb.classList.remove("listening");
        resetAgentCards();
        appendLog(data.agent, `Result: ${data.final_response}`, "log-success");

        if (data.result && data.result.web_url) {
            renderDesignPreview(data.result.web_url);
        }

        if (data.result && data.result.url && data.agent === "SPECTRE") {
            appendLog("SPECTRE", `Opening browser tab for: ${data.result.url}`, "log-step");
            try {
                window.open(data.result.url, "_blank");
            } catch (e) {
                console.log("Browser window.open Note:", e);
            }
        }

        // Mobile Deep Link handler for iPhone 11 native iOS app launching
        const isMobile = /iPhone|iPad|iPod|Android/i.test(navigator.userAgent);
        if (isMobile && data.result && data.result.app) {
            const appName = data.result.app.toLowerCase();
            const mobileDeepLinks = {
                "whatsapp": "whatsapp://",
                "youtube": "youtube://",
                "spotify": "spotify://",
                "maps": "maps://",
                "mail": "mailto:",
                "gmail": "googlegmail://"
            };
            if (mobileDeepLinks[appName]) {
                appendLog("STARK", `Triggering iPhone native app link: ${mobileDeepLinks[appName]}`, "log-step");
                window.location.href = mobileDeepLinks[appName];
            }
        }
    }
}

function highlightAgent(agentId) {
    resetAgentCards();
    const card = document.getElementById(`card-${agentId}`);
    const state = document.getElementById(`state-${agentId}`);
    if (card) {
        card.classList.add("active");
    }
    if (state) {
        state.innerText = "PROCESSING";
        state.style.background = "rgba(255, 153, 0, 0.2)";
        state.style.color = "#ff9900";
    }
}

function resetAgentCards() {
    AGENTS.forEach(ag => {
        const card = document.getElementById(`card-${ag.id}`);
        const state = document.getElementById(`state-${ag.id}`);
        if (card) card.classList.remove("active");
        if (state) {
            state.innerText = ag.id === "HULK" ? "STANDBY" : "ONLINE";
            state.style.background = "rgba(0, 255, 136, 0.15)";
            state.style.color = "#00ff88";
        }
    });
}

function appendLog(agent, text, cssClass = "") {
    const consoleElem = document.getElementById("terminalConsole");
    const now = new Date().toLocaleTimeString();
    
    const div = document.createElement("div");
    div.className = `log-entry ${cssClass}`;
    div.innerHTML = `<span class="log-time">[${now}]</span> <span class="log-agent">[${agent}]</span>: ${text}`;
    
    consoleElem.appendChild(div);
    consoleElem.scrollTop = consoleElem.scrollHeight;
}

function renderDesignPreview(imageUrl) {
    const viewport = document.getElementById("designViewport");
    viewport.innerHTML = `<img src="${imageUrl}?t=${Date.now()}" alt="JARVIS Generated Design">`;
}

function setupEventListeners() {
    const input = document.getElementById("cmdInput");
    const btn = document.getElementById("btnSend");
    const orb = document.getElementById("voiceOrb");

    const sendCmd = () => {
        const cmd = input.value.trim();
        if (!cmd) return;
        
        if (socket && socket.readyState === WebSocket.OPEN) {
            socket.send(JSON.stringify({ type: "command", text: cmd }));
            appendLog("USER", cmd, "log-step");
            input.value = "";
        } else {
            alert("WebSocket connection offline.");
        }
    };

    btn.addEventListener("click", sendCmd);
    input.addEventListener("keypress", (e) => {
        if (e.key === "Enter") sendCmd();
    });

    // Touch & Click Voice Recording Toggle
    const handleVoiceClick = async (e) => {
        e.preventDefault();
        if (!isRecording) {
            startAudioRecording();
        } else {
            stopAudioRecording();
        }
    };

    orb.addEventListener("click", handleVoiceClick);
}

async function startAudioRecording() {
    try {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        
        let options = {};
        if (MediaRecorder.isTypeSupported('audio/webm')) {
            options = { mimeType: 'audio/webm' };
        } else if (MediaRecorder.isTypeSupported('audio/mp4')) {
            options = { mimeType: 'audio/mp4' };
        }

        mediaRecorder = new MediaRecorder(stream, options);
        audioChunks = [];

        mediaRecorder.ondataavailable = (event) => {
            if (event.data.size > 0) audioChunks.push(event.data);
        };

        mediaRecorder.onstop = async () => {
            const audioBlob = new Blob(audioChunks, { type: options.mimeType || 'audio/wav' });
            const reader = new FileReader();
            reader.readAsDataURL(audioBlob);
            reader.onloadend = () => {
                const base64Audio = reader.result;
                if (socket && socket.readyState === WebSocket.OPEN) {
                    socket.send(JSON.stringify({ type: "audio", data: base64Audio }));
                    appendLog("USER", "[Voice Audio Command Sent]", "log-step");
                }
            };
        };

        mediaRecorder.start();
        isRecording = true;
        document.getElementById("voiceOrb").classList.add("listening");
        appendLog("HERALD", "Listening... Speak command, then click orb to execute.", "log-step");
    } catch (err) {
        appendLog("HERALD", `Mic Note: ${err.message}. Type command below if mic permission denied.`, "log-time");
    }
}

function stopAudioRecording() {
    if (mediaRecorder && isRecording) {
        mediaRecorder.stop();
        isRecording = false;
        document.getElementById("voiceOrb").classList.remove("listening");
    }
}
