const logEl = document.getElementById("log");
const form = document.getElementById("form");
const input = document.getElementById("input");
const sendBtn = document.getElementById("send");
const statusEl = document.getElementById("status");

function addMsg(role, text, trace) {
  const wrap = document.createElement("div");
  wrap.className = `msg ${role}`;
  const roleName = role === "user" ? "你" : "CampusDoc Agent";
  wrap.innerHTML = `<div class="role">${roleName}</div><div class="bubble"></div>`;
  wrap.querySelector(".bubble").textContent = text;
  if (trace && trace.length) {
    const t = document.createElement("div");
    t.className = "trace";
    const tools = trace.filter((x) => x.kind === "tool");
    if (tools.length) {
      t.textContent = "工具调用：\n" + tools.map((x) => {
        const p = x.payload;
        return `• ${p.name}(${JSON.stringify(p.args)}) → ${String(p.result).slice(0, 180)}…`;
      }).join("\n");
    } else {
      t.textContent = `模式：${trace.find((x) => x.kind === "final") ? "完成" : "处理中"}`;
    }
    wrap.appendChild(t);
  }
  logEl.appendChild(wrap);
  logEl.scrollTop = logEl.scrollHeight;
}

async function refreshHealth() {
  try {
    const res = await fetch("/api/health");
    const data = await res.json();
    statusEl.textContent = data.mode === "live"
      ? `Live · DeepSeek Tool-Calling · 工具 ${data.tools.length} 个`
      : `Demo · 本地工具可用（未配置 DEEPSEEK_API_KEY）`;
    statusEl.className = `status ${data.mode}`;
  } catch {
    statusEl.textContent = "服务未连接，请先运行 python app.py";
    statusEl.className = "status demo";
  }
}

form.addEventListener("submit", async (e) => {
  e.preventDefault();
  const message = input.value.trim();
  if (!message) return;
  addMsg("user", message);
  input.value = "";
  sendBtn.disabled = true;
  try {
    const res = await fetch("/api/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message }),
    });
    const data = await res.json();
    addMsg("agent", data.answer || JSON.stringify(data), data.trace || []);
  } catch (err) {
    addMsg("agent", `请求失败：${err}`);
  } finally {
    sendBtn.disabled = false;
  }
});

document.getElementById("prompts").addEventListener("click", (e) => {
  const btn = e.target.closest("button[data-q]");
  if (!btn) return;
  input.value = btn.getAttribute("data-q");
  input.focus();
});

refreshHealth();
addMsg("agent", "你好，我是 CampusDoc Agent。可以帮你检索知识库、清洗表格、总结文档、批改概念题。左侧有快捷示例。");
