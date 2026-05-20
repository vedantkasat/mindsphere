const picker = document.getElementById("moodPicker");
const noteInput = document.getElementById("moodNote");
const logBtn = document.getElementById("logBtn");
const recentList = document.getElementById("recentList");
const avgScoreEl = document.getElementById("avgScore");
const totalCountEl = document.getElementById("totalCount");
const emptyMsg = document.getElementById("emptyMsg");
const canvas = document.getElementById("moodChart");

let selectedScore = null;
let chart = null;

const MOOD_EMOJIS = { 1: "😢", 2: "😕", 3: "😐", 4: "🙂", 5: "😄" };
const MOOD_LABELS = { 1: "Awful", 2: "Low", 3: "Okay", 4: "Good", 5: "Great" };

picker.addEventListener("click", e => {
  const btn = e.target.closest(".mood-btn");
  if (!btn) return;
  document.querySelectorAll(".mood-btn").forEach(b => b.classList.remove("selected"));
  btn.classList.add("selected");
  selectedScore = parseInt(btn.dataset.score, 10);
  logBtn.disabled = false;
});

logBtn.addEventListener("click", async () => {
  if (!selectedScore) return;
  logBtn.disabled = true;
  logBtn.textContent = "Logging...";

  try {
    const res = await fetch("/api/mood", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        mood_score: selectedScore,
        note: noteInput.value.trim(),
      }),
    });
    if (!res.ok) throw new Error("save failed");

    // Reset UI
    document.querySelectorAll(".mood-btn").forEach(b => b.classList.remove("selected"));
    noteInput.value = "";
    selectedScore = null;
    await loadMoods();
  } catch (err) {
    alert("Couldn't save. Check connection.");
    console.error(err);
  } finally {
    logBtn.disabled = true;
    logBtn.textContent = "Log mood";
  }
});

function formatDate(iso, fullDate = false) {
  const d = new Date(iso + "Z");
  if (fullDate) {
    return d.toLocaleString("en-IN", {
      day: "numeric", month: "short", hour: "2-digit", minute: "2-digit",
    });
  }
  return d.toLocaleDateString("en-IN", { day: "numeric", month: "short" });
}

function renderChart(logs) {
  const labels = logs.map(l => formatDate(l.created_at));
  const data = logs.map(l => l.mood_score);

  if (chart) chart.destroy();

  chart = new Chart(canvas, {
    type: "line",
    data: {
      labels,
      datasets: [{
        label: "Mood",
        data,
        borderColor: "#7a9b76",
        backgroundColor: "rgba(122, 155, 118, 0.15)",
        borderWidth: 2.5,
        fill: true,
        tension: 0.35,
        pointBackgroundColor: "##7a9b76",
        pointBorderColor: "#fbf8f3",
        pointBorderWidth: 2,
        pointRadius: 5,
        pointHoverRadius: 7,
      }],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { display: false },
        tooltip: {
          backgroundColor: "#fbf8f3",
          borderColor: "#e0d8c8",
          titleColor: "#2c3530",
          bodyColor: "#2c3530",
          padding: 10,
          callbacks: {
            label: ctx => {
              const score = ctx.parsed.y;
              return `${MOOD_EMOJIS[score]} ${MOOD_LABELS[score]} (${score}/5)`;
            },
          },
        },
      },
      scales: {
        y: {
          min: 0.5,
          max: 5.5,
          ticks: {
            stepSize: 1,
            color: "#6b7770",
            callback: v => MOOD_EMOJIS[v] || "",
          },
          grid: { color: "#e0d8c8" },
        },
        x: {
          ticks: { color: "#6b7770", maxTicksLimit: 8 },
          grid: { display: false },
        },
      },
    },
  });
}

function renderRecent(logs) {
  if (logs.length === 0) {
    recentList.innerHTML = `<p class="muted">Nothing yet.</p>`;
    return;
  }
  const recent = [...logs].reverse().slice(0, 10);
  recentList.innerHTML = recent.map(l => `
    <div class="recent-item">
      <span class="recent-emoji">${MOOD_EMOJIS[l.mood_score]}</span>
      <div class="recent-meta">
        <div class="recent-date">${formatDate(l.created_at, true)}</div>
        ${l.note ? `<div class="recent-note">${escapeHtml(l.note)}</div>` : ""}
      </div>
      <span class="recent-score">${MOOD_LABELS[l.mood_score]}</span>
    </div>
  `).join("");
}

function escapeHtml(s) {
  return String(s || "")
    .replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
}

async function loadMoods() {
  try {
    const res = await fetch("/api/mood");
    const data = await res.json();
    const logs = data.logs || [];

    totalCountEl.textContent = logs.length;
    if (logs.length === 0) {
      avgScoreEl.textContent = "—";
      emptyMsg.classList.remove("hidden");
      canvas.style.display = "none";
      renderRecent([]);
      return;
    }

    emptyMsg.classList.add("hidden");
    canvas.style.display = "block";

    const avg = logs.reduce((a, b) => a + b.mood_score, 0) / logs.length;
    avgScoreEl.textContent = avg.toFixed(1);

    renderChart(logs);
    renderRecent(logs);
  } catch (err) {
    recentList.innerHTML = `<p class="muted">Couldn't load.</p>`;
    console.error(err);
  }
}

loadMoods();