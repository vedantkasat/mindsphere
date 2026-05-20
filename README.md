# 🧠 MindSphere

A privacy-first mental wellness companion built for Indian college students.

Originally developed as a concept for **Smart India Hackathon 2025** (Problem Statement 25092 — Digital Mental Health and Psychological Support System for Students in Higher Education).

---

## What it does

- **AI Companion** — Chat about stress, placements, family pressure, exams. Powered by Google Gemini, with a system prompt tuned for Indian higher-ed context.
- **Reflective Journal** — Write freely. Get a gentle AI-generated reflection with sentiment and themes.
- **Mood Tracker** — Log daily mood on a 1–5 scale. Visualize trends over time with charts.

## Why it's different

Most AI mental wellness apps treat your data as theirs. MindSphere is built on three honest principles:

- **Local-first** — Your data lives in a SQLite file on your machine, not on someone's cloud.
- **No account, no email, no tracking** — Zero PII collected. Use it without leaving a trail.
- **Anonymization before AI** — Names, emails, phone numbers, and IDs are stripped from your messages before they're sent to Gemini.
- **Ephemeral chat mode** — Toggle on to talk without anything being saved.
- **One-click wipe** — Nuke all your data instantly from the home page.
- **Crisis-aware** — Detects self-harm language and surfaces Indian mental health helplines (Tele Manas, Vandrevala, iCall, AASRA).

## Tech stack

- **Backend:** FastAPI (Python), SQLite, Google Gemini API (`gemini-2.5-flash`)
- **Frontend:** Vanilla HTML/CSS/JS, Chart.js
- **Desktop:** PyInstaller + pywebview, packaged as `.app` (macOS) / `.exe` (Windows)
- **No build tools, no Node, no Docker required**

---

## Installation

### Option 1: Desktop App (Recommended)

1. Download the latest `MindSphere.dmg` from [Releases](https://github.com/vedantkasat/mindsphere/releases)
2. Double-click the DMG, drag MindSphere to Applications
3. **First launch:** Right-click MindSphere → Open (required once because the app isn't code-signed)
4. Paste your free [Gemini API key](https://aistudio.google.com/apikey) when prompted
5. Done — opens in your default browser

Your data lives in `~/Library/Application Support/MindSphere/` (macOS) or `%APPDATA%\MindSphere\` (Windows).

### Option 2: Run from Source

```bash
git clone https://github.com/vedantkasat/mindsphere.git
cd mindsphere

python3 -m venv venv
source venv/bin/activate          # macOS/Linux
# venv\Scripts\activate           # Windows

pip install -r backend/requirements.txt

echo "GEMINI_API_KEY=your_key_here" > .env

cd backend
uvicorn main:app --reload --port 8000
```

Open http://127.0.0.1:8000

---

## Privacy honesty

This isn't end-to-end encrypted — Gemini has to read your messages to respond. We don't claim otherwise.

What we actually do:
- Anonymize PII before any external call
- Store data locally only, never on a remote server
- Give you total control to wipe everything
- Keep the code open so you can verify exactly what we do

If you want zero AI involvement, use the journal as a plain text log — the AI reflection is optional infrastructure, not the core.

---

## Crisis resources (India)

- **Tele Manas:** 1-800-891-4416 (24/7)
- **Vandrevala Foundation:** 1860-2662-345 (24/7) · WhatsApp: +91 9999666555
- **iCall:** 9152987821
- **AASRA:** +91-22-27546669 (24/7)

This app is **not** a substitute for professional help. If you're struggling, please reach out.

---

## Roadmap

- [ ] Encrypted journal entries (SQLCipher with user passphrase)
- [ ] Pattern detection across journal entries (weekly themes, mood correlations)
- [ ] Export your data as Markdown / JSON
- [ ] Self-hosted Ollama mode for fully local AI (no Gemini dependency)

---

## Author

Built by **Vedant Kasat & Vaishnav Shinde** — 3rd-year E&TC student at AISSMS IOIT, Pune.

## License

MIT
