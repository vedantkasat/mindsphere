const API = "";  // same origin
const messagesEl = document.getElementById("messages");
const form = document.getElementById("chatForm");
const input = document.getElementById("userInput");
const sendBtn = form.querySelector(".send-btn");
const typingEl = document.getElementById("typing");
const ephemeralToggle = document.getElementById("ephemeralToggle");
const clearBtn = document.getElementById("clearBtn");

// Load history on page load
async function loadHistory() {
  try {
    const res = await fetch(`${API}/api/chat/history`);
    const data = await res.json();
    if (data.messages && data.messages.length > 0) {
      messagesEl.innerHTML = "";
      data.messages.forEach(m => addMessage(m.role, m.content, false));
    }
  } catch (e) {
    console.error("Failed to load history:", e);
  }
}

function addMessage(role, content, scroll = true, isCrisis = false) {
  const div = document.createElement("div");
  div.className = `msg msg-${role}` + (isCrisis ? " msg-crisis" : "");
  const bubble = document.createElement("div");
  bubble.className = "bubble";
  bubble.textContent = content;
  div.appendChild(bubble);
  messagesEl.appendChild(div);
  if (scroll) {
    div.scrollIntoView({ behavior: "smooth", block: "end" });
  }
}

function setLoading(loading) {
  sendBtn.disabled = loading;
  sendBtn.textContent = loading ? "..." : "Send";
  typingEl.classList.toggle("hidden", !loading);
  if (loading) {
    typingEl.scrollIntoView({ behavior: "smooth", block: "end" });
  }
}

async function sendMessage(text) {
  addMessage("user", text);
  setLoading(true);

  try {
    const res = await fetch(`${API}/api/chat`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        message: text,
        ephemeral: ephemeralToggle.checked,
      }),
    });
    const data = await res.json();
    addMessage("assistant", data.reply, true, data.crisis);
  } catch (e) {
    addMessage("assistant", "Something went wrong reaching the server. Check your connection and try again.");
    console.error(e);
  } finally {
    setLoading(false);
  }
}

// Form submit
form.addEventListener("submit", e => {
  e.preventDefault();
  const text = input.value.trim();
  if (!text) return;
  input.value = "";
  input.style.height = "auto";
  sendMessage(text);
});

// Enter to send, Shift+Enter for newline
input.addEventListener("keydown", e => {
  if (e.key === "Enter" && !e.shiftKey) {
    e.preventDefault();
    form.requestSubmit();
  }
});

// Auto-grow textarea
input.addEventListener("input", () => {
  input.style.height = "auto";
  input.style.height = Math.min(input.scrollHeight, 120) + "px";
});

// Clear chat
clearBtn.addEventListener("click", async () => {
  if (!confirm("Clear all chat history? This can't be undone.")) return;
  await fetch(`${API}/api/chat/history`, { method: "DELETE" });
  messagesEl.innerHTML = "";
  addMessage("assistant", "Cleared. Fresh start — what's on your mind?");
});

// Init
loadHistory();
input.focus();