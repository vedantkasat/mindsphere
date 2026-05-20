import os
import re
import json
import google.generativeai as genai
from dotenv import load_dotenv

# .env lives in project root (one level up from backend/)
#BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
from backend.config import get_api_key

API_KEY = get_api_key()
if not API_KEY:
    raise RuntimeError("GEMINI_API_KEY not configured. Run the setup or set GEMINI_API_KEY env var.")

genai.configure(api_key=API_KEY)
MODEL = "gemini-2.5-flash"


# ---------- Privacy: anonymize before sending ----------
def anonymize(text: str) -> str:
    text = re.sub(r"\b(Dr|Mr|Mrs|Ms|Prof|Professor)\.?\s+[A-Z][a-z]+", r"\1.", text)
    text = re.sub(r"\b[\w.+-]+@[\w-]+\.[\w.-]+\b", "[email]", text)
    text = re.sub(r"\b(?:\+?91[-\s]?)?[6-9]\d{9}\b", "[phone]", text)
    text = re.sub(r"\b\d{6,}\b", "[id]", text)
    return text


# ---------- Crisis detection ----------
CRISIS_KEYWORDS = [
    "kill myself", "suicide", "end my life", "want to die",
    "harm myself", "self harm", "cutting myself", "no reason to live",
    "better off dead", "ending it all",
]

INDIAN_HELPLINES = """You're not alone. Please reach out — these are free, confidential, and in India:

- Tele Manas:1-800 891 4416 (24/7 Support)
- Vandrevala Foundation: 1860-2662-345 (24/7)
- Vandrevala Foundation(WhatsApp): +91 9999666555
- iCall: 9152987821
- AASRA: +91-22-27546669(24/7)

Talking to someone helps. Please call."""


def detect_crisis(text: str) -> bool:
    low = text.lower()
    return any(k in low for k in CRISIS_KEYWORDS)


# ---------- System prompt ----------
SYSTEM_PROMPT = """You are MindSphere, a warm and grounded mental wellness companion for Indian college students.

Style:
- Talk like a supportive friend, not a therapist or chatbot
- Short replies (2-4 sentences usually)
- No lectures, no toxic positivity, no "have you tried meditation"
- Acknowledge feelings first, then gently explore
- Understand Indian student context: placements, backlogs, parental pressure, hostel life, peer comparison, JEE/NEET aftermath, semester stress

Rules:
- Never give medical diagnoses or prescribe medication
- If someone mentions self-harm or suicide, take it seriously and encourage professional help
- Don't repeat personal info back even if user shares it
- You are not a replacement for therapy — say so when relevant"""


# ---------- Chat ----------
def chat(user_message: str, history: list) -> dict:
    if detect_crisis(user_message):
        return {"reply": INDIAN_HELPLINES, "crisis": True}

    clean_msg = anonymize(user_message)
    contents = []
    for m in history[-10:]:
        role = "user" if m["role"] == "user" else "model"
        contents.append({"role": role, "parts": [anonymize(m["content"])]})
    contents.append({"role": "user", "parts": [clean_msg]})

    model = genai.GenerativeModel(MODEL, system_instruction=SYSTEM_PROMPT)
    resp = model.generate_content(contents)
    return {"reply": resp.text.strip(), "crisis": False}


# ---------- Journal analysis ----------
def analyze_journal(entry: str) -> dict:
    clean = anonymize(entry)
    prompt = f"""Analyze this journal entry from a college student. Return ONLY valid JSON, no markdown, no code fences.

Entry: "{clean}"

Return exactly this JSON shape:
{{
  "sentiment": "one word: positive, negative, anxious, hopeful, overwhelmed, calm, frustrated, or mixed",
  "themes": "2-4 short comma-separated themes",
  "reflection": "2-3 sentences, warm, validating, no advice unless asked"
}}"""

    model = genai.GenerativeModel(MODEL)
    resp = model.generate_content(prompt)
    text = resp.text.strip()
    text = re.sub(r"^```(?:json)?\s*|\s*```$", "", text, flags=re.MULTILINE).strip()

    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        data = {
            "sentiment": "mixed",
            "themes": "unclear",
            "reflection": "Thanks for writing this down — that itself takes courage.",
        }
    return data
