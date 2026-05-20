const form = document.getElementById("journalForm");
const input = document.getElementById("entryInput");
const charCount = document.getElementById("charCount");
const saveBtn = document.getElementById("saveBtn");
const reflectionEl = document.getElementById("latestReflection");
const rSentiment = document.getElementById("rSentiment");
const rThemes = document.getElementById("rThemes");
const rText = document.getElementById("rText");
const entriesList = document.getElementById("entriesList");

// Char count
input.addEventListener("input", () => {
  charCount.textContent = `${input.value.length} chars`;
});

function formatDate(iso) {
  const d = new Date(iso + "Z"); // backend stores UTC
  return d.toLocaleString("en-IN", {
    day: "numeric",
    month: "short",
    hour: "2-digit",
    minute: "2-digit",
  });
}

async function loadEntries() {
  try {
    const res = await fetch("/api/journal");
    const data = await res.json();

    if (!data.entries || data.entries.length === 0) {
      entriesList.innerHTML = `<p class="muted">No entries yet. Write something above.</p>`;
      return;
    }

    entriesList.innerHTML = "";
    data.entries.forEach(e => {
      const div = document.createElement("div");
      div.className = "entry";
      div.innerHTML = `
        <div class="entry-meta">
          <span>${formatDate(e.created_at)}</span>
          <span class="tag tag-sentiment">${e.sentiment || "—"}</span>
        </div>
        <div class="entry-content">${escapeHtml(e.content)}</div>
        <div class="entry-footer">
          ${(e.themes || "").split(",").map(t => t.trim()).filter(Boolean).map(t =>
            `<span class="tag">${escapeHtml(t)}</span>`
          ).join("")}
        </div>
        <div class="entry-reflection">${escapeHtml(e.ai_reflection || "")}</div>
      `;
      div.addEventListener("click", () => div.classList.toggle("expanded"));
      entriesList.appendChild(div);
    });
  } catch (err) {
    entriesList.innerHTML = `<p class="muted">Couldn't load entries.</p>`;
    console.error(err);
  }
}

function escapeHtml(s) {
  return String(s || "")
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;");
}

form.addEventListener("submit", async e => {
  e.preventDefault();
  const text = input.value.trim();
  if (!text) return;

  saveBtn.disabled = true;
  saveBtn.textContent = "Reflecting...";

  try {
    const res = await fetch("/api/journal", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ content: text }),
    });
    const data = await res.json();

    rSentiment.textContent = data.sentiment;
    rThemes.textContent = data.themes;
    rText.textContent = data.reflection;
    reflectionEl.classList.remove("hidden");
    reflectionEl.scrollIntoView({ behavior: "smooth", block: "center" });

    input.value = "";
    charCount.textContent = "0 chars";
    await loadEntries();
  } catch (err) {
    alert("Couldn't save entry. Check your connection.");
    console.error(err);
  } finally {
    saveBtn.disabled = false;
    saveBtn.textContent = "Save & reflect";
  }
});

loadEntries();