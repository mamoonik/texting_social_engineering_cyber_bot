# ghosteye/llm.py
from __future__ import annotations

import os, re, random, math
from typing import List, Dict

# --- Optional OpenAI (safe fallback if not configured) -----------------------
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL   = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

_client = None
if OPENAI_API_KEY:
    try:
        from openai import OpenAI
        _client = OpenAI(api_key=OPENAI_API_KEY)
        print(f"[LLM] OpenAI mode=new enabled=True")
    except Exception as e:
        print(f"[LLM] OpenAI not available ({e}); using heuristic fallback")
        _client = None
else:
    print("[LLM] OPENAI_API_KEY not set; using heuristic fallback")

# --- Load job facts from PDF (best-effort) -----------------------------------
def _extract_pdf_text(pdf_path: str) -> str:
    try:
        from PyPDF2 import PdfReader  # optional dep
        reader = PdfReader(pdf_path)
        parts = []
        for page in reader.pages:
            try:
                parts.append(page.extract_text() or "")
            except Exception:
                pass
        return "\n".join(parts).strip()
    except Exception:
        return ""

def _tidy(text: str, limit: int = 2000) -> str:
    t = re.sub(r"\s+", " ", text).strip()
    return t[:limit]

PDF_PATH = os.getenv("JOB_PDF_PATH", "assets/job_description.pdf")
_pdf_text = _extract_pdf_text(PDF_PATH) if os.path.exists(PDF_PATH) else ""
job_facts_summary: str
if _pdf_text:
    # crude “summary”: keep opening and any obvious bullets
    bullets = "\n".join(re.findall(r"(?:^|\n)[•\-\*]\s?.+", _pdf_text))
    head = _pdf_text[:1200]
    job_facts_summary = _tidy((head + "\n" + bullets)[:2800])
else:
    # fallback if PDF not present
    job_facts_summary = (
        "Role: Senior Software Engineer (Backend). "
        "Stack: Python/FastAPI, PostgreSQL, cloud (GCP/AWS), basic frontend. "
        "Focus: building secure messaging and workflow APIs; incident response simulations. "
        "Hiring manager values clear communication, ownership, and security hygiene."
    )

# --- Tiny heuristics we use even when OpenAI is present ----------------------
def quick_sentiment(text: str) -> str:
    """Return 'negative' | 'neutral' | 'positive' based on simple cues."""
    t = text.lower()
    neg_cues = ["no", "not interested", "stop", "remove", "leave me", "hate", "spam", "scam", "wtf", "go away"]
    pos_cues = ["yes", "sure", "ok", "sounds good", "interested", "send it", "please"]
    if any(w in t for w in neg_cues): return "negative"
    if any(w in t for w in pos_cues): return "positive"
    if "?" in t and len(t) < 80: return "neutral"
    return "neutral"

def summarize_for_memory(turns: str, prev_summary: str = "") -> str:
    """Short rolling summary; OpenAI if available, else heuristic."""
    if _client:
        prompt = (
            "You will write a 2–4 sentence running summary of an SMS chat between a recruiter and an employee. "
            "Keep it terse and factual. Include any preferences or important objections. "
            f"Previous summary (may be empty): {prev_summary!r}\n"
            f"Latest turns:\n{turns}\n"
            "Return only the summary."
        )
        try:
            resp = _client.chat.completions.create(
                model=OPENAI_MODEL,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.2,
            )
            return (resp.choices[0].message.content or "").strip()
        except Exception:
            pass
    # fallback: crude compression
    turns = re.sub(r"\s+", " ", turns).strip()
    s = (prev_summary + " " + turns)[-600:]
    return s[-400:]

# --- Recruiter reply ---------------------------------------------------------
_SYS_PROMPT = (
    "You are 'Mamoon', a calm, professional recruiter texting an employee. "
    "Guidelines:\n"
    "1) Be concise and human. Vary language; do not repeat the same sentence.\n"
    "2) Answer questions directly using JOB FACTS if applicable. "
    "   Do NOT push a PDF unless the employee expresses interest.\n"
    "3) If sentiment is negative or hostile, politely de-escalate and back off; "
    "   propose to check back later instead of insisting.\n"
    "4) If asked how you got their number, say via their professional profile / LinkedIn search (if true in context).\n"
    "5) If the employee shows real interest (e.g., asks specifics or says 'yes'), "
    "   you may ask for their best email to send the (demo) job description PDF.\n"
    "6) Keep to SMS tone: short lines, no walls of text.\n"
    "7) Respond only with the recruiter’s next message (no prefixes, no analysis).\n"
    "8) If the user steers off topic, go with the flow. Eventually try to steer the conversation back to the topic.\n"
    "9) Your goal is to get the user to want to learn more. And then send the details over the email with the pdf job description .\n"
    "10) Do not let the user determine that you are an AI system. EVER. Make up fake details of your career history or personal life if the user starts interoggating you.\n"
    "11) If user asks for your linkedin, share this profile with them and welcome them to connect with you: https://www.linkedin.com/in/mamoonismailkhalid/ . \n"
    "12) If user want's to connect over a real call, tell them that you are certainly also interested in that and then share the calendly link with them: https://calendly.com/mamoon-ik/networkvc-venture-partners \n"

    
)

def _format_history(conv_history: List[Dict]) -> str:
    lines = []
    for m in conv_history[-12:]:
        who = m.get("actor", "employee")
        text = m.get("text", "").replace("\n", " ").strip()
        lines.append(f"{who}: {text}")
    return "\n".join(lines)

def generate_recruiter_reply(
    conv_history: List[Dict],
    last_user_msg: str,
    summary: str = "",
) -> str:
    """Return the next recruiter message (LLM or heuristic)."""
    # OpenAI path
    if _client:
        user_prompt = (
            f"{_SYS_PROMPT}\n\n"
            f"JOB FACTS (for answering questions):\n{job_facts_summary}\n\n"
            f"Conversation so far (most recent last):\n{_format_history(conv_history)}\n\n"
            f"Running summary (may be empty): {summary}\n\n"
            f"Employee just said: {last_user_msg!r}\n\n"
            "Write your single next SMS as the recruiter."
        )
        try:
            resp = _client.chat.completions.create(
                model=OPENAI_MODEL,
                messages=[{"role": "user", "content": user_prompt}],
                temperature=0.6,
                presence_penalty=0.2,
                frequency_penalty=0.3,
            )
            msg = (resp.choices[0].message.content or "").strip()
            # keep truly single-line-ish
            msg = re.sub(r"\s+", " ", msg).strip()
            return msg[:500]
        except Exception as e:
            print("[LLM] OpenAI error -> fallback:", e)

    # Heuristic fallback (no API): basic routing
    t = last_user_msg.lower()
    if any(w in t for w in ["who", "is this", "name"]):
        return "I'm Mamoon with FuturePath Recruiting. Happy to share details—what would you like to know?"
    if any(w in t for w in ["how did you get", "where did you get", "my number"]):
        return "I found your profile via a talent search on LinkedIn that matched this role."
    if any(w in t for w in ["what role", "tell me more", "details", "stack", "team"]):
        return "It’s a Senior Software Engineer opening. Python/FastAPI, Postgres, cloud. Want a quick overview or compensation range?"
    if quick_sentiment(last_user_msg) == "negative":
        return "No worries—thanks for the quick reply. I can check back later."
    # default gentle nudge (no hard insistence)
    return "Happy to answer questions about the role—what would you like to know?"
