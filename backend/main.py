from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from pathlib import Path
import os

from database import (
    init_db,
    save_message, get_chat_history, clear_chat_history,
    save_journal, get_journal_entries,
    save_mood, get_mood_logs,
)
from gemini_service import chat as gemini_chat, analyze_journal

# ---------- App setup ----------
app = FastAPI(title="MindSphere API")

# Allow frontend (different port) to call us
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten in production
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve frontend files
FRONTEND_DIR = Path(__file__).parent.parent / "frontend"
if FRONTEND_DIR.exists():
    app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")

# Init DB on startup
@app.on_event("startup")
def startup():
    init_db()


# ---------- Request/response models ----------
class ChatRequest(BaseModel):
    message: str
    ephemeral: bool = False  # if true, don't save to DB

class JournalRequest(BaseModel):
    content: str

class MoodRequest(BaseModel):
    mood_score: int  # 1-5
    note: str = ""


# ---------- Routes: serve frontend ----------
@app.get("/")
def root():
    index = FRONTEND_DIR / "index.html"
    if index.exists():
        return FileResponse(index)
    return {"message": "MindSphere API running. Frontend not found."}


@app.get("/{page}.html")
def page(page: str):
    f = FRONTEND_DIR / f"{page}.html"
    if f.exists():
        return FileResponse(f)
    raise HTTPException(404, "Page not found")


# ---------- Chat ----------
@app.post("/api/chat")
def api_chat(req: ChatRequest):
    history = [] if req.ephemeral else get_chat_history()
    result = gemini_chat(req.message, history)

    if not req.ephemeral:
        save_message("user", req.message)
        save_message("assistant", result["reply"])

    return result


@app.get("/api/chat/history")
def api_chat_history():
    return {"messages": get_chat_history()}


@app.delete("/api/chat/history")
def api_clear_chat():
    clear_chat_history()
    return {"status": "cleared"}


# ---------- Journal ----------
@app.post("/api/journal")
def api_journal(req: JournalRequest):
    if not req.content.strip():
        raise HTTPException(400, "Entry cannot be empty")
    analysis = analyze_journal(req.content)
    entry_id = save_journal(
        content=req.content,
        sentiment=analysis["sentiment"],
        themes=analysis["themes"],
        ai_reflection=analysis["reflection"],
    )
    return {"id": entry_id, **analysis}


@app.get("/api/journal")
def api_journal_list():
    return {"entries": get_journal_entries()}


# ---------- Mood ----------
@app.post("/api/mood")
def api_mood(req: MoodRequest):
    if not 1 <= req.mood_score <= 5:
        raise HTTPException(400, "mood_score must be 1-5")
    mood_id = save_mood(req.mood_score, req.note)
    return {"id": mood_id, "mood_score": req.mood_score, "note": req.note}


@app.get("/api/mood")
def api_mood_list():
    return {"logs": get_mood_logs()}


# ---------- Privacy: nuke everything ----------
@app.delete("/api/wipe")
def api_wipe():
    """Wipe all user data — chat, journal, mood."""
    from database import get_connection
    conn = get_connection()
    conn.execute("DELETE FROM chat_messages")
    conn.execute("DELETE FROM journal_entries")
    conn.execute("DELETE FROM mood_logs")
    conn.commit()
    conn.close()
    return {"status": "all data wiped"}


# ---------- Health check ----------
@app.get("/api/health")
def health():
    return {"status": "ok", "service": "mindsphere"}