/**
 * ==========================================================================
 * VINUNI QC REACT AGENT - FRONTEND LOGIC (Vanilla ES6+)
 * ==========================================================================
 */

document.addEventListener("DOMContentLoaded", () => {
    // DOM Elements
    const chatStream = document.getElementById("chat-stream");
    const chatForm = document.getElementById("chat-form");
    const userInput = document.getElementById("user-input");
    const sendBtn = document.getElementById("send-btn");
    const clearChatBtn = document.getElementById("clear-chat-btn");
    const testCasesContainer = document.getElementById("test-cases-container");
    const dbCardsContainer = document.getElementById("db-cards-container");
    const providerNameDisplay = document.getElementById("provider-name-display");
    const openWaterfallBtn = document.getElementById("open-waterfall-btn");
    const closeWaterfallBtn = document.getElementById("close-waterfall-btn");
    const waterfallModal = document.getElementById("waterfall-modal");
    const waterfallTimeline = document.getElementById("waterfall-timeline");

    // Initialize
    fetchSystemStatus();
    fetchTestCases();
    fetchMockDatabase();

    // Auto-resize textarea
    userInput.addEventListener("input", () => {
        userInput.style.height = "auto";
        userInput.style.height = Math.min(userInput.scrollHeight, 120) + "px";
    });

    // Enter to submit (Shift+Enter for newline)
    userInput.addEventListener("keydown", (e) => {
        if (e.key === "Enter" && !e.shiftKey) {
            e.preventDefault();
            chatForm.dispatchEvent(new Event("submit"));
        }
    });

    // Chat Form Submit
    chatForm.addEventListener("submit", async (e) => {
        e.preventDefault();
        const query = userInput.value.trim();
        if (!query) return;

        // Clear input
        userInput.value = "";
        userInput.style.height = "auto";
        userInput.disabled = true;
        sendBtn.disabled = true;

        // Hide welcome banner if exists
        const welcomeCard = document.getElementById("welcome-card");
        if (welcomeCard) welcomeCard.style.display = "none";

        // Append User Message
        appendUserMessage(query);

        // Append Loading Indicator
        const typingEl = appendTypingIndicator();

        try {
            const response = await fetch("/api/chat", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ query: query })
            });

            const data = await response.json();
            typingEl.remove();

            if (data.status === "SUCCESS") {
                renderReActSequence(data.trace_logs, data.final_answer);
            } else {
                appendAgentBubble("error", "Lỗi xử lý", data.message || "Không thể nhận phản hồi từ Agent.");
            }
        } catch (err) {
            typingEl.remove();
            appendAgentBubble("error", "Lỗi kết nối", `Không thể kết nối với Web Server: ${err.message}`);
        } finally {
            userInput.disabled = false;
            sendBtn.disabled = false;
            userInput.focus();
        }
    });

    // Clear Chat
    clearChatBtn.addEventListener("click", () => {
        chatStream.innerHTML = `
            <div class="welcome-card" id="welcome-card">
                <div class="welcome-icon">🤖</div>
                <h3>Xin chào, Kiểm định viên QC!</h3>
                <p>Tôi là <strong>Trợ lý Tác tử Kiểm định Chất lượng Thông minh (ReAct QC Assistant)</strong>. Tôi được tích hợp sẵn 2 công cụ qua giao thức MCP:</p>
                <div class="tools-showcase">
                    <div class="tool-tag"><code>qc_query</code>: Tra cứu thông tin & lịch sử ca lỗi 2D/3D</div>
                    <div class="tool-tag"><code>create_rework_ticket</code>: Tạo phiếu Rework gửi đội gán nhãn</div>
                </div>
                <p class="welcome-tip">👉 Chọn một Test Case ở thanh bên trái hoặc nhập yêu cầu kiểm định bên dưới để bắt đầu!</p>
            </div>
        `;
    });

    // Modal Waterfall Trace Log
    openWaterfallBtn.addEventListener("click", async () => {
        waterfallModal.classList.add("open");
        await loadWaterfallTrace();
    });

    closeWaterfallBtn.addEventListener("click", () => {
        waterfallModal.classList.remove("open");
    });

    waterfallModal.addEventListener("click", (e) => {
        if (e.target === waterfallModal) {
            waterfallModal.classList.remove("open");
        }
    });

    // =========================================================================
    // API CALLS & RENDERING HELPERS
    // =========================================================================

    async function fetchSystemStatus() {
        try {
            const res = await fetch("/api/status");
            const data = await res.json();
            providerNameDisplay.textContent = `${data.provider} (${data.model})`;
        } catch {
            providerNameDisplay.textContent = "Sẵn sàng (Local)";
        }
    }

    async function fetchTestCases() {
        try {
            const res = await fetch("/api/test-cases");
            const testCases = await res.json();
            testCasesContainer.innerHTML = "";

            testCases.forEach(tc => {
                const card = document.createElement("div");
                card.className = "tc-card";
                card.innerHTML = `
                    <div class="tc-card-top">
                        <span class="tc-id">[${tc.id}]</span>
                        <span class="tc-badge ${tc.complexity.toLowerCase()}">${tc.complexity}</span>
                    </div>
                    <div class="tc-question">${tc.question}</div>
                `;
                card.addEventListener("click", () => {
                    userInput.value = tc.question;
                    userInput.focus();
                    chatForm.dispatchEvent(new Event("submit"));
                });
                testCasesContainer.appendChild(card);
            });
        } catch (err) {
            testCasesContainer.innerHTML = `<p style="font-size:11px; color:var(--text-muted);">Không thể tải test cases</p>`;
        }
    }

    async function fetchMockDatabase() {
        try {
            const res = await fetch("/api/database");
            const db = await res.json();
            dbCardsContainer.innerHTML = "";

            Object.values(db).forEach(item => {
                const card = document.createElement("div");
                card.className = "db-card";
                card.innerHTML = `
                    <div class="db-card-header">
                        <span class="db-code">${item.qc_id}</span>
                        <span class="db-status ${item.status.toLowerCase()}">${item.status}</span>
                    </div>
                    <div class="db-desc">${item.task_type} • ${item.defect_type}</div>
                `;
                card.addEventListener("click", () => {
                    userInput.value = `Hãy tra cứu thông tin ca lỗi ${item.qc_id}.`;
                    userInput.focus();
                    chatForm.dispatchEvent(new Event("submit"));
                });
                dbCardsContainer.appendChild(card);
            });
        } catch (err) {
            dbCardsContainer.innerHTML = `<p style="font-size:11px; color:var(--text-muted);">Không thể tải CSDL</p>`;
        }
    }

    async function loadWaterfallTrace() {
        waterfallTimeline.innerHTML = "<p style='font-size:12px; color:var(--text-muted);'>Đang tải trace log...</p>";
        try {
            const res = await fetch("/api/waterfall");
            const logs = await res.json();
            if (!logs || logs.length === 0) {
                waterfallTimeline.innerHTML = "<p style='font-size:12px; color:var(--text-muted);'>Chưa có sự kiện Waterfall nào được ghi.</p>";
                return;
            }

            waterfallTimeline.innerHTML = "";
            logs.slice(-15).reverse().forEach(log => {
                const item = document.createElement("div");
                item.className = "timeline-item";
                
                const actionBadge = log.action_type || "EVENT";
                const latency = log.latency_ms !== undefined ? `${log.latency_ms} ms` : "";
                
                let desc = "";
                if (log.tool_name) {
                    desc = `Tool: <code>${log.tool_name}</code> ${JSON.stringify(log.arguments || {})}`;
                } else if (log.output) {
                    desc = log.output;
                } else if (log.thought) {
                    desc = log.thought;
                }

                item.innerHTML = `
                    <div class="timeline-header">
                        <span>Step ${log.step || 1}: <strong>${actionBadge}</strong></span>
                        <span class="timeline-latency">${latency}</span>
                    </div>
                    ${log.query ? `<div class="timeline-query">Prompt: "${log.query}"</div>` : ""}
                    <div class="timeline-desc">${desc}</div>
                `;
                waterfallTimeline.appendChild(item);
            });
        } catch {
            waterfallTimeline.innerHTML = "<p style='font-size:12px; color:var(--accent-rose);'>Lỗi đọc file docs/trace_waterfall.json</p>";
        }
    }

    function appendUserMessage(text) {
        const row = document.createElement("div");
        row.className = "chat-row user";
        row.innerHTML = `<div class="user-bubble">${escapeHtml(text)}</div>`;
        chatStream.appendChild(row);
        scrollToBottom();
    }

    function appendTypingIndicator() {
        const row = document.createElement("div");
        row.className = "chat-row agent";
        row.innerHTML = `
            <div class="typing-indicator">
                <div class="typing-dot"></div>
                <div class="typing-dot"></div>
                <div class="typing-dot"></div>
                <span style="font-size:12px; color:var(--text-muted); margin-left:8px;">Agent đang suy luận ReAct...</span>
            </div>
        `;
        chatStream.appendChild(row);
        scrollToBottom();
        return row;
    }

    function renderReActSequence(traceLogs, finalAnswer) {
        const agentRow = document.createElement("div");
        agentRow.className = "chat-row agent";

        if (Array.isArray(traceLogs)) {
            traceLogs.forEach(step => {
                if (step.thought && step.action_type !== "FINAL_ANSWER") {
                    const card = document.createElement("div");
                    card.className = "react-step-card thought";
                    card.innerHTML = `
                        <div class="step-header thought-header">🧠 Thought (Suy luận)</div>
                        <div class="step-content">${escapeHtml(step.thought)}</div>
                    `;
                    agentRow.appendChild(card);
                }

                if (step.action_type === "TOOL_EXECUTION") {
                    const actionCard = document.createElement("div");
                    actionCard.className = "react-step-card action";
                    actionCard.innerHTML = `
                        <div class="step-header action-header">🛠️ Action (Gọi MCP Tool)</div>
                        <div class="step-content">
                            Kích hoạt công cụ <code>${step.tool_name}</code>
                            <div class="code-block">${JSON.stringify(step.arguments || {}, null, 2)}</div>
                        </div>
                    `;
                    agentRow.appendChild(actionCard);

                    if (step.observation) {
                        const obsCard = document.createElement("div");
                        obsCard.className = "react-step-card observation";
                        obsCard.innerHTML = `
                            <div class="step-header obs-header">👁️ Observation (Phản hồi từ MCP Server)</div>
                            <div class="step-content">
                                <div class="code-block">${JSON.stringify(step.observation, null, 2)}</div>
                            </div>
                        `;
                        agentRow.appendChild(obsCard);
                    }
                }
            });
        }

        // Final Answer
        const finalCard = document.createElement("div");
        finalCard.className = "react-step-card final";
        finalCard.innerHTML = `
            <div class="step-header final-header">🏁 Final Answer (Kết quả cho Kiểm định viên)</div>
            <div class="step-content">${formatMarkdown(finalAnswer || "Đã xử lý xong yêu cầu.")}</div>
        `;
        agentRow.appendChild(finalCard);

        chatStream.appendChild(agentRow);
        scrollToBottom();
    }

    function appendAgentBubble(type, title, message) {
        const agentRow = document.createElement("div");
        agentRow.className = "chat-row agent";
        const card = document.createElement("div");
        card.className = `react-step-card ${type}`;
        card.innerHTML = `
            <div class="step-header final-header">${escapeHtml(title)}</div>
            <div class="step-content">${escapeHtml(message)}</div>
        `;
        agentRow.appendChild(card);
        chatStream.appendChild(agentRow);
        scrollToBottom();
    }

    function scrollToBottom() {
        chatStream.scrollTop = chatStream.scrollHeight;
    }

    function escapeHtml(str) {
        if (!str) return "";
        return str
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;")
            .replace(/'/g, "&#039;");
    }

    function formatMarkdown(text) {
        if (!text) return "";
        let formatted = escapeHtml(text);
        // Bold
        formatted = formatted.replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>");
        // Inline code
        formatted = formatted.replace(/`([^`]+)`/g, "<code>$1</code>");
        // Line breaks
        formatted = formatted.replace(/\n/g, "<br>");
        return formatted;
    }
});
