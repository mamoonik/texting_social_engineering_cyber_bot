# # # from dotenv import load_dotenv, find_dotenv
# # # load_dotenv(dotenv_path=find_dotenv(), override=True)
# # # from ghosteye.store import init_db, add_message, fetch_recent, get_summary, save_summary
# # # from ghosteye.llm import generate_recruiter_reply, summarize_for_memory
# # # init_db()  # ensure tables exist at boot

# # # # TEMP debug to confirm it's loaded (remove later)
# # # import os
# # # print("[BOOT] OPENAI_API_KEY loaded:", bool(os.getenv("OPENAI_API_KEY")))
# # # from ghosteye.llm import generate_recruiter_reply
# # # # if we are c using the typing/jitter helpers:
# # # from ghosteye.jitter_core import schedule_messages  # (only if still used)
# # # import math
# # # import random
# # # from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect, Form
# # # from fastapi.responses import HTMLResponse, FileResponse
# # # from fastapi.staticfiles import StaticFiles
# # # from fastapi.templating import Jinja2Templates
# # # import asyncio, os, uuid
# # # from datetime import datetime, timedelta
# # # from typing import Dict, Any

# # # app = FastAPI(title="GhostEye Minimal Demo")

# # # def human_delay_secs(user_text: str) -> float:
# # #     """Realistic compose + think delay using lognormal WPM + tiny pauses."""
# # #     words = max(1, len([w for w in user_text.split() if w.strip()]))
# # #     # WPM ~ lognormal(mean≈45, sigma≈0.35)
# # #     wpm = math.exp(random.gauss(math.log(45.0), 0.35))
# # #     base = words / (wpm / 60.0)            # seconds to "read/think"
# # #     # random micro-pauses
# # #     pauses = 0.0
# # #     while random.random() < 0.30:
# # #         pauses += random.gammavariate(2.0, 0.8)  # Gamma(k=2, θ=0.8)
# # #     # small floor/ceiling
# # #     return max(1.2, min(base + pauses + random.uniform(0.2, 1.0), 9.0))
# # # def human_delay_secs_before_reading(user_text: str) -> float:
# # #     """Realistic compose + think delay using lognormal WPM + tiny pauses."""
# # #     words = max(1, len([w for w in user_text.split() if w.strip()]))
# # #     # WPM ~ lognormal(mean≈45, sigma≈0.35)
# # #     wpm = math.exp(random.gauss(math.log(45.0), 0.35))
# # #     base = words / (wpm / 60.0)            # seconds to "read/think"
# # #     # random micro-pauses
# # #     pauses = 0.0
# # #     while random.random() < 0.30:
# # #         pauses += random.gammavariate(2.0, 0.8)  # Gamma(k=2, θ=0.8)
# # #     # small floor/ceiling
# # #     return max(1.2, min(base + pauses + random.uniform(0.2, 1.0), 9.0))

# # # #
# # # #  Serve frontend files
# # # app.mount("/static", StaticFiles(directory="static"), name="static")
# # # templates = Jinja2Templates(directory="templates")

# # # # In-memory conversation store (simple; demo only)
# # # CONVERSATIONS: Dict[str, list] = {}  # key -> list of events
# # # WS_CONNECTIONS: Dict[str, WebSocket] = {}  # one ws connection per employee session id

# # # # --- Helper to append event
# # # def log_event(conv_id: str, actor: str, text: str):
# # #     ev = {"ts": datetime.utcnow().isoformat() + "Z", "actor": actor, "text": text}
# # #     CONVERSATIONS.setdefault(conv_id, []).append(ev)
# # #     return ev

# # # # --- Simple jittered recruiter response (safe, demo only)
# # # # async def recruiter_reply(conv_id: str, incoming_text: str):
# # # #     # Wait 1-6 seconds to simulate thinking/jitter
# # # #     await asyncio.sleep(1 + (uuid.uuid4().int % 6))
# # # #     reply = ("Thanks for your response — sounds great. "
# # # #              "Please share your best email so I can send the (demo) job description PDF.")
# # # #     ev = log_event(conv_id, "recruiter", reply)
# # # #     # push to websocket if connected
# # # #     ws = WS_CONNECTIONS.get(conv_id)
# # # #     if ws:
# # # #         await ws.send_json(ev)

# # # # async def recruiter_reply(conv_id: str, incoming_text: str):
# # # #     """
# # # #     Generate a context-aware reply using an LLM (or fallback).
# # # #     Sends the reply to the connected websocket (if present) and logs it.
# # # #     """
# # # #     # build conv_history as a list of events (we use CONVERSATIONS from app)
# # # #     conv_history = CONVERSATIONS.get(conv_id, []).copy()

# # # #     # generate reply text (LLM or fallback)
# # # #     reply_text = generate_recruiter_reply(conv_history, incoming_text,
# # # #                                           role_name="Senior Software Engineer",
# # # #                                           tone="friendly, professional",
# # # #                                           max_tokens=140,
# # # #                                           temperature=0.6)

# # # #     # ensure reply includes invitation to use the safe demo PDF rather than an attachment
# # # #     if "job description" not in reply_text.lower():
# # # #         reply_text = reply_text.rstrip() + " I'll send the job description (demo PDF)."

# # # #     ev = log_event(conv_id, "recruiter", reply_text)
# # # #     # push to websocket if connected
# # # #     ws = WS_CONNECTIONS.get(conv_id)
# # # #     if ws:
# # # #         await ws.send_json(ev)
# # # async def recruiter_reply(conv_id: str, incoming_text: str):
# # #     # 1) wait before the system starts typing
# # #     await asyncio.sleep(human_delay_secs_before_reading(incoming_text))
# # #     # Send "typing" event
# # #     ws = WS_CONNECTIONS.get(conv_id)
# # #     if ws:
# # #         await ws.send_json({
# # #             "actor": "recruiter",
# # #             "typing": True,
# # #             "ts": datetime.utcnow().isoformat() + "Z"
# # #         })

# # #     # Add human-like jitter delay
# # #     await asyncio.sleep(human_delay_secs(incoming_text))
# # #     # 2) build short history + get LLM/template reply
# # #     conv_history = CONVERSATIONS.get(conv_id, []).copy()
# # #     reply_text = generate_recruiter_reply(
# # #         conv_history, incoming_text,
# # #         role_name="Senior Software Engineer",
# # #         tone="friendly, professional",
# # #         max_tokens=140,
# # #         temperature=0.6
# # #     )

# # #     # 3) ensure safe phrasing
# # #     if "job description" not in reply_text.lower():
# # #         reply_text = reply_text.rstrip() + " I’ll send the job description (demo PDF)."

# # #     ev = log_event(conv_id, "recruiter", reply_text)
# # #     ws = WS_CONNECTIONS.get(conv_id)
# # #     if ws:
# # #         await ws.send_json(ev)
# # # # --- Routes

# # # @app.get("/", response_class=HTMLResponse)
# # # def index(request: Request):
# # #     # conv_id lets multiple demos run at once in different browser tabs
# # #     conv_id = request.query_params.get("conv", "demo-1")
# # #     return templates.TemplateResponse("index.html", {"request": request, "conv_id": conv_id})

# # # @app.post("/recruiter/send")
# # # async def recruiter_send(conv_id: str = Form(...)):
# # #     """
# # #     Trigger the initial recruiter message to employee UI.
# # #     This simulates the recruiter sending the first phishing-like message.
# # #     """
# # #     text = ("Hi — I'm Aaron from FuturePath Recruiting. I saw your profile and "
# # #             "have an excellent role that would be a great fit. Are you available for a quick chat? "
# # #             "If yes, share your email and I will forward the job details.")
# # #     ev = log_event(conv_id, "recruiter", text)
# # #     # push via WS if connected
# # #     ws = WS_CONNECTIONS.get(conv_id)
# # #     if ws:
# # #         await ws.send_json(ev)
# # #     return {"status": "sent", "event": ev}

# # # # @app.post("/assets/job_description")
# # # # def get_job_description():
# # # #     """
# # # #     Serve a benign, local PDF (no malware). This PDF should clearly state it's a simulation.
# # # #     """
# # # #     return FileResponse("benign_assets/job_description.pdf", media_type="application/pdf", filename="job_description_demo.pdf")

# # # # @app.get("/assets/job_description")
# # # # def get_job_description():
# # # #     return FileResponse("benign_assets/job_description.pdf", media_type="application/pdf",
# # # #                         filename="job_description_demo.pdf")
# # # @app.get("/assets/job_description")
# # # def get_job_description():
# # #     from fastapi.responses import FileResponse
# # #     return FileResponse(
# # #         "assets/job_description.pdf",
# # #         media_type="application/pdf",
# # #         filename="job_description_demo.pdf"
# # #     )


# # # # WebSocket for employee UI (send/receive live)
# # # @app.websocket("/ws/{conv_id}")
# # # async def websocket_endpoint(websocket: WebSocket, conv_id: str):
# # #     await websocket.accept()
# # #     WS_CONNECTIONS[conv_id] = websocket
# # #     try:
# # #         # send existing history
# # #         history = CONVERSATIONS.get(conv_id, [])
# # #         for ev in history:
# # #             await websocket.send_json(ev)
# # #         while True:
# # #             msg = await websocket.receive_json()
# # #             # expected shape: {"actor":"employee","text":"..."}
# # #             actor = msg.get("actor", "employee")
# # #             text = msg.get("text", "")
# # #             ev = log_event(conv_id, actor, text)
# # #             # echo back to UI
# # #             await websocket.send_json(ev)
# # #             # trigger recruiter reply when employee messages
# # #             if actor == "employee":
# # #                 # schedule asynchronous recruiter reply (non-blocking)
# # #                 asyncio.create_task(recruiter_reply(conv_id, text))
# # #     except WebSocketDisconnect:
# # #         WS_CONNECTIONS.pop(conv_id, None)
# # #     except Exception as e:
# # #         WS_CONNECTIONS.pop(conv_id, None)
# # #         raise

# # # # Simple API to fetch conversation history (for server-driven demos)
# # # @app.get("/conversation/{conv_id}")
# # # def get_conversation(conv_id: str):
# # #     return {"conversation": CONVERSATIONS.get(conv_id, [])}


# # # app.py
# # from __future__ import annotations
# # import asyncio, json, os, random, math
# # from datetime import datetime, timedelta
# # from typing import Dict, Any
# # from typing import Optional


# # from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect, Form
# # from fastapi.responses import HTMLResponse, FileResponse, PlainTextResponse
# # from fastapi.staticfiles import StaticFiles
# # from fastapi.templating import Jinja2Templates

# # from dotenv import load_dotenv, find_dotenv
# # load_dotenv(dotenv_path=find_dotenv(), override=True)

# # from ghosteye.store import (
# #     init_db, add_message, fetch_recent, get_summary, save_summary
# # )
# # from ghosteye.llm import generate_recruiter_reply, summarize_for_memory

# # # --- boot
# # init_db()
# # print("[BOOT] OPENAI_API_KEY loaded:", bool(os.getenv("OPENAI_API_KEY")))

# # app = FastAPI()

# # app.mount("/static", StaticFiles(directory="static"), name="static")
# # templates = Jinja2Templates(directory="templates")

# # # In-memory WebSocket connection map
# # WS_CONNECTIONS: Dict[str, WebSocket] = {}
# # def human_delay_secs_before_reading(user_text: str) -> float:
# #     """Realistic compose + think delay using lognormal WPM + tiny pauses."""
# #     words = max(1, len([w for w in user_text.split() if w.strip()]))
# #     # WPM ~ lognormal(mean≈45, sigma≈0.35)
# #     wpm = math.exp(random.gauss(math.log(45.0), 0.35))
# #     base = words / (wpm / 60.0)            # seconds to "read/think"
# #     # random micro-pauses
# #     pauses = 0.0
# #     while random.random() < 0.30:
# #         pauses += random.gammavariate(2.0, 0.8)  # Gamma(k=2, θ=0.8)
# #     # small floor/ceiling
# #     return max(1.2, min(base + pauses + random.uniform(0.2, 1.0), 9.0))

# # # --- tiny human-delay model (lognormal typing + small pauses)
# # def human_delay_secs(text: str) -> float:
# #     words = max(1, len([t for t in text.split() if t.strip()]))
# #     wpm = math.exp(random.gauss(math.log(45.0), 0.35))  # ~lognormal
# #     base = words / (wpm / 60.0)
# #     # occasional micro-pauses
# #     pauses = 0.0
# #     while random.random() < 0.28:
# #         pauses += random.gammavariate(2.0, 0.9)
# #     return max(1.2, base + pauses)

# # # --- helpers
# # def now_iso() -> str:
# #     return datetime.utcnow().isoformat() + "Z"

# # async def ws_send(conv_id: str, payload: Dict[str, Any]):
# #     ws = WS_CONNECTIONS.get(conv_id)
# #     if ws:
# #         await ws.send_json(payload)

# # # --- routes
# # # @app.get("/", response_class=HTMLResponse)
# # # async def index(request: Request, conv: str | None = None):
# # #     conv_id = conv or "demo-1"
# # #     return templates.TemplateResponse(
# # #         "index.html",
# # #         {"request": request, "conv_id": conv_id}
# # #     )
# # @app.get("/", response_class=HTMLResponse)
# # async def index(request: Request, conv: Optional[str] = None):
# #     conv_id = conv or "demo-1"
# #     return templates.TemplateResponse("index.html", {"request": request, "conv_id": conv_id})

# # @app.get("/assets/job_description")
# # async def job_pdf():
# #     # safe demo file
# #     return FileResponse("assets/job_description.pdf", media_type="application/pdf")

# # # Recruiter initial nudge via button
# # @app.post("/recruiter/send")
# # async def recruiter_send(conv_id: str = Form(...)):
# #     # log first recruiter line + push to client
# #     line = ("Hi — I’m Aaron from FuturePath Recruiting. I saw your profile and have an excellent role that "
# #             "would be a great fit. Are you available for a quick chat? If yes, share your email and I will "
# #             "forward the job details.")
# #     add_message(conv_id, "recruiter", line)
# #     await ws_send(conv_id, {"actor": "recruiter", "text": line, "ts": now_iso()})
# #     return PlainTextResponse("ok")

# # @app.websocket("/ws/{conv_id}")
# # async def websocket_endpoint(ws: WebSocket, conv_id: str):
# #     await ws.accept()
# #     WS_CONNECTIONS[conv_id] = ws
# #     try:
# #         while True:
# #             raw = await ws.receive_text()
# #             payload = json.loads(raw)
# #             actor = payload.get("actor")
# #             text = (payload.get("text") or "").strip()
# #             if not text:
# #                 continue

# #             # echo employee to log/db
# #             if actor == "employee":
# #                 add_message(conv_id, "employee", text)
# #                 await ws_send(conv_id, {"actor": "employee", "text": text, "ts": now_iso()})

# #                 # kick recruiter task
# #                 asyncio.create_task(handle_recruiter(conv_id))
# #     except WebSocketDisconnect:
# #         pass
# #     finally:
# #         WS_CONNECTIONS.pop(conv_id, None)
# # async def handle_recruiter(conv_id: str):
# #     await asyncio.sleep(human_delay_secs_before_reading("ok"))

# #     # 1) show "typing..." right away
# #     await ws_send(conv_id, {"actor": "recruiter", "typing": True, "ts": now_iso()})

# #     # 2) find the most recent employee message (if any)
# #     recent = fetch_recent(conv_id, limit=16)
# #     last_user_msg = ""
# #     for m in reversed(recent):
# #         if m["actor"] == "employee":
# #             last_user_msg = m["text"]
# #             break

# #     # 3) human-like thinking/typing delay (safe even if no user msg yet)
# #     await asyncio.sleep(human_delay_secs(last_user_msg or "ok"))

# #     # 4) load running summary and generate the reply
# #     summary, last_id = get_summary(conv_id)
# #     reply = generate_recruiter_reply(
# #         conv_history=recent,
# #         last_user_msg=last_user_msg,
# #         summary=summary,
# #     )

# #     # 5) store and push the real recruiter message (typing indicator will be cleared by client on real msg)
# #     add_message(conv_id, "recruiter", reply)
# #     await ws_send(conv_id, {"actor": "recruiter", "text": reply, "ts": now_iso()})

# #     # 6) periodically refresh the rolling summary (every ~10 new turns since last summary)
# #     recent = fetch_recent(conv_id, limit=24)
# #     new_ids = [m["id"] for m in recent if m["id"] > last_id]
# #     if len(new_ids) >= 10:
# #         turns_text = "\n".join(f"{m['actor']}: {m['text']}" for m in recent if m["id"] > last_id)
# #         new_summary = summarize_for_memory(turns_text, prev_summary=summary)
# #         save_summary(conv_id, new_summary, max(new_ids))



# from __future__ import annotations

# import asyncio
# import json
# import os
# import random
# import sqlite3
# from datetime import datetime, timedelta
# from typing import Dict, List, Optional

# from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect, Form
# from fastapi.responses import HTMLResponse, PlainTextResponse, FileResponse
# from fastapi.staticfiles import StaticFiles
# from fastapi.templating import Jinja2Templates

# # -------- time / tz
# from zoneinfo import ZoneInfo

# # -------- local LLM adapter
# from ghosteye.llm import (
#     generate_recruiter_reply,
#     quick_sentiment,
#     summarize_for_memory,
#     job_facts_summary,     # produced from PDF at startup
# )

# # ----------------- ENV / config -----------------
# TZ_NAME = os.getenv("TIMEZONE", "America/New_York")
# TZ = ZoneInfo(TZ_NAME)

# BH_START = int(os.getenv("BUSINESS_HOURS_START", "9"))
# BH_END = int(os.getenv("BUSINESS_HOURS_END", "18"))  # exclusive

# FOLLOWUP_HOURS = int(os.getenv("FOLLOWUP_COOLDOWN_HOURS", "4"))
# TYPO_PROB = float(os.getenv("TYPO_PROB", "0.12"))

# PUBLIC_BASE_URL = os.getenv("PUBLIC_BASE_URL", "http://127.0.0.1:8000")

# # ----------------- FastAPI -----------------
# app = FastAPI()
# app.mount("/static", StaticFiles(directory="static"), name="static")
# templates = Jinja2Templates(directory="templates")

# # ----------------- In-memory “db” -----------------
# # Messages: {conv_id: [ {id, ts_iso, actor, text} , ... ]} (actors: "recruiter"|"employee")
# MSGS: Dict[str, List[Dict]] = {}
# # Rolling summary for each conversation (helps the LLM stay on-topic)
# SUMMARIES: Dict[str, Dict] = {}  # {conv: {"summary": str, "last_msg_id": int}}

# # Active websocket connections per conversation id
# WS_CONNECTIONS: Dict[str, WebSocket] = {}

# # Debounce map: pending async task per conv_id
# PENDING: Dict[str, asyncio.Task] = {}
# # Scheduled softer followups (“check back later”)
# FOLLOWUP_SCHEDULED: Dict[str, datetime] = {}


# # ----------------- Helpers -----------------
# def now_local() -> datetime:
#     return datetime.now(tz=TZ)


# def now_iso() -> str:
#     return now_local().isoformat()


# def is_business_hours(t: Optional[datetime] = None) -> bool:
#     t = t or now_local()
#     return BH_START <= t.hour < BH_END


# def next_business_window_start(t: Optional[datetime] = None) -> datetime:
#     t = t or now_local()
#     start = t.replace(hour=BH_START, minute=0, second=0, microsecond=0)
#     if t.hour >= BH_END:
#         start = start + timedelta(days=1)
#     elif t.hour < BH_START:
#         pass
#     else:
#         return t
#     # (optional) skip weekends can be added here
#     return start


# def add_message(conv: str, actor: str, text: str) -> int:
#     lst = MSGS.setdefault(conv, [])
#     mid = lst[-1]["id"] + 1 if lst else 1
#     lst.append({"id": mid, "ts": now_iso(), "actor": actor, "text": text})
#     return mid


# def fetch_recent(conv: str, limit: int = 20) -> List[Dict]:
#     return MSGS.get(conv, [])[-limit:]


# def save_summary(conv: str, summary: str, last_msg_id: int) -> None:
#     SUMMARIES[conv] = {"summary": summary, "last_msg_id": last_msg_id}


# def get_summary(conv: str) -> (str, int):
#     entry = SUMMARIES.get(conv, {"summary": "", "last_msg_id": 0})
#     return entry["summary"], entry["last_msg_id"]


# async def ws_send(conv: str, ev: Dict) -> None:
#     ws = WS_CONNECTIONS.get(conv)
#     if not ws:
#         return
#     try:
#         await ws.send_text(json.dumps(ev))
#     except RuntimeError:
#         pass


# async def maybe_typo_send(conv: str, text: str) -> None:
#     """Occasionally send a human-ish typo, then a correction."""
#     if random.random() >= TYPO_PROB or len(text.split()) < 3:
#         add_message(conv, "recruiter", text)
#         await ws_send(conv, {"actor": "recruiter", "text": text, "ts": now_iso()})
#         return

#     words = text.split()
#     i = random.randrange(1, len(words) - 1)
#     wrong = words.copy()
#     wrong[i] = (wrong[i][::-1] if len(wrong[i]) > 3 else wrong[i] + wrong[i][-1:])
#     typo_text = " ".join(wrong)

#     # send typo line
#     add_message(conv, "recruiter", typo_text)
#     await ws_send(conv, {"actor": "recruiter", "text": typo_text, "ts": now_iso()})

#     # quick correction
#     await asyncio.sleep(random.uniform(0.5, 1.2))
#     correction = f"*{words[i]}"
#     add_message(conv, "recruiter", correction)
#     await ws_send(conv, {"actor": "recruiter", "text": correction, "ts": now_iso()})


# # ----------------- Recruiter brain -----------------
# async def handle_recruiter(conv_id: str) -> None:
#     # Safety: cancel an older task if any (also done at call-site)
#     prev = PENDING.pop(conv_id, None)
#     if prev and not prev.done():
#         prev.cancel()

#     # Show typing
#     await ws_send(conv_id, {"actor": "recruiter", "typing": True, "ts": now_iso()})

#     # Small debounce window (user may add more text)
#     await asyncio.sleep(random.uniform(0.8, 1.6))

#     # Grab the latest user message
#     recent = fetch_recent(conv_id, limit=24)
#     last_user_msg = ""
#     for m in reversed(recent):
#         if m["actor"] == "employee":
#             last_user_msg = m["text"]
#             break

#     # If outside hours, schedule for next window and return silently
#     if not is_business_hours():
#         when = next_business_window_start()
#         delay_s = max(1, int((when - now_local()).total_seconds()))
#         if conv_id not in FOLLOWUP_SCHEDULED or when > FOLLOWUP_SCHEDULED[conv_id]:
#             FOLLOWUP_SCHEDULED[conv_id] = when

#             async def later():
#                 await asyncio.sleep(delay_s)
#                 await handle_recruiter(conv_id)

#             PENDING[conv_id] = asyncio.create_task(later())
#         return

#     # “read/compose” delay proportional to length
#     await asyncio.sleep(min(2.5, 0.4 + 0.03 * len(last_user_msg)))

#     sentiment = quick_sentiment(last_user_msg)
#     summary, _last = get_summary(conv_id)

#     # Ask LLM for next reply; it already knows the job facts via job_facts_summary
#     reply = generate_recruiter_reply(
#         conv_history=recent,
#         last_user_msg=last_user_msg,
#         summary=summary + ("\n\nJOB FACTS:\n" + job_facts_summary if job_facts_summary else ""),
#     ).strip()

#     if sentiment == "negative":
#         reply = "Understood — thanks for the quick reply. I’ll check back later in case timing is better."
#         await maybe_typo_send(conv_id, reply)
#         when = now_local() + timedelta(hours=FOLLOWUP_HOURS)

#         async def followup():
#             await asyncio.sleep(max(1, int((when - now_local()).total_seconds())))
#             if is_business_hours():
#                 await maybe_typo_send(conv_id, "Just checking back—would a brief overview of the team or stack be helpful?")

#         PENDING[conv_id] = asyncio.create_task(followup())
#         return

#     await maybe_typo_send(conv_id, reply)

#     # opportunistic summary refresh
#     recent2 = fetch_recent(conv_id, limit=24)
#     turns = "\n".join(f"{m['actor']}: {m['text']}" for m in recent2[-10:])
#     if turns and random.random() < 0.25:
#         new_sum = summarize_for_memory(turns, prev_summary=summary)
#         save_summary(conv_id, new_sum, recent2[-1]["id"])


# # ----------------- Routes -----------------
# @app.get("/", response_class=HTMLResponse)
# async def index(request: Request, conv: Optional[str] = None):
#     conv_id = conv or "demo-1"
#     # lazy init
#     if conv_id not in MSGS:
#         MSGS[conv_id] = []
#         add_message(
#             conv_id,
#             "recruiter",
#             "Hi — I’m Aaron from FuturePath Recruiting. I saw your profile and have an excellent role that could be a fit. "
#             "Are you available for a quick chat?",
#         )
#     return templates.TemplateResponse("index.html", {"request": request, "conv_id": conv_id})


# @app.websocket("/ws/{conv_id}")
# async def ws_endpoint(websocket: WebSocket, conv_id: str):
#     await websocket.accept()
#     WS_CONNECTIONS[conv_id] = websocket

#     # stream history down to the client
#     for m in MSGS.get(conv_id, []):
#         await websocket.send_text(json.dumps({"actor": m["actor"], "text": m["text"], "ts": m["ts"]}))

#     try:
#         while True:
#             raw = await websocket.receive_text()
#             try:
#                 payload = json.loads(raw)
#             except json.JSONDecodeError:
#                 continue

#             actor = payload.get("actor")
#             text = (payload.get("text") or "").strip()
#             if not text:
#                 continue

#             add_message(conv_id, actor, text)
#             await ws_send(conv_id, {"actor": actor, "text": text, "ts": now_iso()})

#             if actor == "employee":
#                 # debounce: cancel older pending task, then create a fresh one
#                 prev = PENDING.pop(conv_id, None)
#                 if prev and not prev.done():
#                     prev.cancel()
#                 PENDING[conv_id] = asyncio.create_task(handle_recruiter(conv_id))
#     except WebSocketDisconnect:
#         if WS_CONNECTIONS.get(conv_id) is websocket:
#             WS_CONNECTIONS.pop(conv_id, None)


# @app.post("/recruiter/send")
# async def recruiter_send(conv_id: str = Form(...)):
#     # manual trigger
#     prev = PENDING.pop(conv_id, None)
#     if prev and not prev.done():
#         prev.cancel()
#     PENDING[conv_id] = asyncio.create_task(handle_recruiter(conv_id))
#     return PlainTextResponse("ok")


# # Safe demo “PDF”
# @app.get("/assets/job_description")
# async def serve_pdf():
#     # Serve your demo PDF; place the file here:
#     # assets/job_description.pdf
#     path = os.path.join("assets", "job_description.pdf")
#     return FileResponse(path, filename="job_description.pdf")



from __future__ import annotations

##########################
#########################
##########################
##########################
# --- Telemetry (super light) ---
TELEM = {
    "scheduled": 0,          # jobs scheduled (follow-ups, etc.)
    "sent": 0,               # jobs executed by worker
    "replies": 0,            # employee messages received
    "neg_sentiment": 0,      # counted when we detect negative sentiment
    "avg_jitter_ms": 0.0,    # EWMA of |planned-send - actual-send| in ms
}

def _ewma(prev: float, new: float, alpha: float = 0.25) -> float:
    return (1 - alpha) * prev + alpha * new

# --- In-memory scheduler (min-heap) ---
import heapq
import time as _time

JOBS = []           # heap of (when_epoch, job_id, payload_dict)
JOB_SEQ = 0

def schedule_in(seconds: float, payload: dict):
    """Schedule a coroutine payload['run']() to run ~seconds from now."""
    global JOB_SEQ
    when = _time.time() + max(0.0, seconds)
    JOB_SEQ += 1
    heapq.heappush(JOBS, (when, JOB_SEQ, payload))
    TELEM["scheduled"] += 1

async def scheduler_worker():
    """Single worker: pops due jobs and runs them. MVP on purpose."""
    while True:
        now = _time.time()
        if JOBS and JOBS[0][0] <= now:
            when, _, payload = heapq.heappop(JOBS)
            planned_at = payload.get("planned_at", now)
            planned_ms = int((when - planned_at) * 1000)
            TELEM["avg_jitter_ms"] = _ewma(TELEM["avg_jitter_ms"], abs(planned_ms))
            try:
                await payload["run"]()
            finally:
                TELEM["sent"] += 1
            continue
        await asyncio.sleep(0.2)

##########################
#########################
##########################
##########################
import asyncio, json, os, random, sqlite3
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import math
from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect, Form
from fastapi.responses import HTMLResponse, PlainTextResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from zoneinfo import ZoneInfo

from ghosteye.llm import (
    generate_recruiter_reply,
    quick_sentiment,
    summarize_for_memory,
    job_facts_summary,
)
PDF_PATH = os.getenv("JOB_PDF_PATH", "assets/job_description.pdf")
if not os.path.exists(PDF_PATH):
    print(f"[WARN] JOB_PDF_PATH not found: {PDF_PATH}")

def _log(*args):
    print("[APP]", *args, flush=True)
# ----------------- ENV / config -----------------
TZ_NAME = os.getenv("TIMEZONE", "America/New_York")
TZ = ZoneInfo(TZ_NAME)

BH_START = int(os.getenv("BUSINESS_HOURS_START", "9"))
BH_END = int(os.getenv("BUSINESS_HOURS_END", "18"))  # exclusive

FOLLOWUP_HOURS = int(os.getenv("FOLLOWUP_COOLDOWN_HOURS", "4"))
TYPO_PROB = float(os.getenv("TYPO_PROB", "0.12"))

PUBLIC_BASE_URL = os.getenv("PUBLIC_BASE_URL", "http://127.0.0.1:8000")
ALLOW_AFTER_HOURS = (os.getenv("ALLOW_AFTER_HOURS", "false").lower() == "true")

# ----------------- FastAPI -----------------
app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# ----------------- In-memory “db” -----------------

#################################
#################################
##################################
# --- Conv state machine ---
# "IDLE" (default), "WAITING" (we messaged; awaiting reply), "REPLIED" (employee replied)
STATE: Dict[str, str] = {}

#################################
##################################
###################################
MSGS: Dict[str, List[Dict]] = {}
SUMMARIES: Dict[str, Dict] = {}  # {conv: {"summary": str, "last_msg_id": int}}

WS_CONNECTIONS: Dict[str, WebSocket] = {}
PENDING: Dict[str, asyncio.Task] = {}
FOLLOWUP_SCHEDULED: Dict[str, datetime] = {}

# ----------------- Helpers -----------------
def now_local() -> datetime:
    return datetime.now(tz=TZ)

def now_iso() -> str:
    return now_local().isoformat()

def is_business_hours(t: Optional[datetime] = None) -> bool:
    t = t or now_local()
    return BH_START <= t.hour < BH_END

def next_business_window_start(t: Optional[datetime] = None) -> datetime:
    t = t or now_local()
    start = t.replace(hour=BH_START, minute=0, second=0, microsecond=0)
    if t.hour >= BH_END:
        start = start + timedelta(days=1)
    elif t.hour < BH_START:
        pass
    else:
        return t
    # (weekend skipping could go here)
    return start

def defer_message() -> str:
    window = f"{BH_START}:00–{BH_END}:00 {TZ_NAME}"
    return (
        f"Apologies for the late hour—I'll circle back during business hours ({window}). "
        "If morning works better, I can message you then."
    )

def add_message(conv: str, actor: str, text: str) -> int:
    lst = MSGS.setdefault(conv, [])
    mid = lst[-1]["id"] + 1 if lst else 1
    lst.append({"id": mid, "ts": now_iso(), "actor": actor, "text": text})
    return mid

def fetch_recent(conv: str, limit: int = 20) -> List[Dict]:
    return MSGS.get(conv, [])[-limit:]

def save_summary(conv: str, summary: str, last_msg_id: int) -> None:
    SUMMARIES[conv] = {"summary": summary, "last_msg_id": last_msg_id}

def get_summary(conv: str) -> (str, int):
    entry = SUMMARIES.get(conv, {"summary": "", "last_msg_id": 0})
    return entry["summary"], entry["last_msg_id"]

# async def ws_send(conv: str, ev: Dict) -> None:
    # ws = WS_CONNECTIONS.get(conv)
    # if not ws:
    #     return
    # try:
    #     await ws.send_text(json.dumps(ev))
    # except RuntimeError:
    #     pass
async def ws_send(conv: str, ev: Dict) -> None:
    ws = WS_CONNECTIONS.get(conv)
    if not ws:
        _log("ws_send: no websocket for", conv, "event=", ev)
        return
    try:
        await ws.send_text(json.dumps(ev))
        if "typing" in ev:
            _log("ws_send:", conv, "typing=", ev["typing"])
    except RuntimeError as e:
        _log("ws_send runtime error:", repr(e))

def human_delay_secs_before_reading(txt: str) -> float:
    # ~180 wpm reading speed + small jitter, cap at 3s
    words = max(1, len(txt.split()))
    # words = max(1, len([w for w in user_text.split() if w.strip()]))
    # WPM ~ lognormal(mean≈45, sigma≈0.35)
    wpm = math.exp(random.gauss(math.log(45.0), 0.35))
    seconds = words / (wpm / 60.0)            # seconds to "read/think"
    # seconds = words * (60.0 / 180.0)
    jitter = 0.0
    while random.random() < 0.30:
    # jitter = random.uniform(-0.15, 0.35)
        jitter += random.gammavariate(2.0, 0.8)  # Gamma(k=2, θ=0.8)
    return min(5.0, 0.6 + seconds + jitter)

# def human_delay_secs_before_reading(user_text: str) -> float:
# # #     """Realistic compose + think delay using lognormal WPM + tiny pauses."""
# # #     words = max(1, len([w for w in user_text.split() if w.strip()]))
# # #     # WPM ~ lognormal(mean≈45, sigma≈0.35)
# # #     wpm = math.exp(random.gauss(math.log(45.0), 0.35))
# # #     base = words / (wpm / 60.0)            # seconds to "read/think"
# # #     # random micro-pauses
# # #     pauses = 0.0
# # #     while random.random() < 0.30:
# # #         pauses += random.gammavariate(2.0, 0.8)  # Gamma(k=2, θ=0.8)
# # #     # small floor/ceiling
# # #     return max(1.2, min(base + pauses + random.uniform(0.2, 1.0), 9.0))

async def maybe_typo_send(conv: str, text: str) -> None:
    """Occasionally send a human-ish typo, then a correction."""
    if random.random() >= TYPO_PROB or len(text.split()) < 3:
        add_message(conv, "recruiter", text)
        await ws_send(conv, {"actor": "recruiter", "text": text, "ts": now_iso()})
        ################
        ################
        ################
        ################
        STATE[conv] = "WAITING"  # <-- add this
        ################
        ################
        ################
        ################
        return

    words = text.split()
    if len(words) < 3:
        add_message(conv, "recruiter", text)
        await ws_send(conv, {"actor": "recruiter", "text": text, "ts": now_iso()})
        ################
        ################
        ################
        ################
        STATE[conv] = "WAITING"  # <-- add this
        ################
        ################
        ################
        ################
        return

    i = random.randrange(1, len(words) - 1)
    wrong = words.copy()
    wrong[i] = (wrong[i][::-1] if len(wrong[i]) > 3 else wrong[i] + wrong[i][-1:])
    typo_text = " ".join(wrong)

    # send typo line
    add_message(conv, "recruiter", typo_text)
    await ws_send(conv, {"actor": "recruiter", "text": typo_text, "ts": now_iso()})

    # quick correction
    await asyncio.sleep(random.uniform(0.5, 1.2))
    correction = f"*{words[i]}"
    add_message(conv, "recruiter", correction)
    await ws_send(conv, {"actor": "recruiter", "text": correction, "ts": now_iso()})
    ################
    ################
    ################
    ################
    STATE[conv] = "WAITING"  # <-- add this
    ################
    ################
    ################
    ################

# ----------------- Recruiter brain -----------------
# async def handle_recruiter(conv_id: str) -> None:
#     # cancel any older task
#     prev = PENDING.pop(conv_id, None)
#     if prev and not prev.done():
#         prev.cancel()

#     # 1) show typing now
#     await ws_send(conv_id, {"actor": "recruiter", "typing": True, "ts": now_iso()})

#     # 2) brief debounce (user may add more text)
#     await asyncio.sleep(random.uniform(0.8, 1.6))

#     # 3) grab latest user text
#     recent = fetch_recent(conv_id, limit=24)
#     last_user_msg = ""
#     for m in reversed(recent):
#         if m["actor"] == "employee":
#             last_user_msg = m["text"]
#             break

#     # 4) human-like reading/compose delay
#     await asyncio.sleep(human_delay_secs_before_reading(last_user_msg or "ok"))

#     # 5) after-hours handling (polite defer), unless overridden
#     if not ALLOW_AFTER_HOURS and not is_business_hours():
#         # hide typing before sending defer
#         await ws_send(conv_id, {"actor": "recruiter", "typing": False, "ts": now_iso()})
#         msg = defer_message()
#         add_message(conv_id, "recruiter", msg)
#         await ws_send(conv_id, {"actor": "recruiter", "text": msg, "ts": now_iso()})

#         # schedule a quiet follow-up at next business window
#         when = next_business_window_start()
#         delay_s = max(1, int((when - now_local()).total_seconds()))
#         if conv_id not in FOLLOWUP_SCHEDULED or when > FOLLOWUP_SCHEDULED[conv_id]:
#             FOLLOWUP_SCHEDULED[conv_id] = when

#             async def later():
#                 await asyncio.sleep(delay_s)
#                 # only send if within hours at execution time
#                 if is_business_hours():
#                     await handle_recruiter(conv_id)

#             PENDING[conv_id] = asyncio.create_task(later())
#         return

#     # 6) normal LLM path
#     sentiment = quick_sentiment(last_user_msg)
#     summary, _last = get_summary(conv_id)

#     reply = generate_recruiter_reply(
#         conv_history=recent,
#         last_user_msg=last_user_msg,
#         summary=summary + ("\n\nJOB FACTS:\n" + job_facts_summary if job_facts_summary else ""),
#     ).strip()

#     # hide typing just before the real line
#     await ws_send(conv_id, {"actor": "recruiter", "typing": False, "ts": now_iso()})

#     if sentiment == "negative":
#         reply = "Understood — thanks for the quick reply. I’ll check back later in case timing is better."
#         await maybe_typo_send(conv_id, reply)
#         when = now_local() + timedelta(hours=FOLLOWUP_HOURS)

#         async def followup():
#             await asyncio.sleep(max(1, int((when - now_local()).total_seconds())))
#             if is_business_hours():
#                 await maybe_typo_send(conv_id, "Just checking back—would a brief overview of the team or stack be helpful?")

#         PENDING[conv_id] = asyncio.create_task(followup())
#         return

#     await maybe_typo_send(conv_id, reply)

#     # opportunistic summary refresh
#     recent2 = fetch_recent(conv_id, limit=24)
#     turns = "\n".join(f"{m['actor']}: {m['text']}" for m in recent2[-10:])
#     if turns and random.random() < 0.25:
#         new_sum = summarize_for_memory(turns, prev_summary=summary)
#         save_summary(conv_id, new_sum, recent2[-1]["id"])


async def handle_recruiter(conv_id: str) -> None:
    _log("handle_recruiter: ENTER", conv_id)

    # DO NOT cancel/pop here — the caller already debounces/cancels older tasks.

    # show typing immediately (best-effort)
    try:
        await ws_send(conv_id, {"actor": "recruiter", "typing": True, "ts": now_iso()})
    except Exception as e:
        _log("typing(True) send error:", repr(e))

    try:
        
        # 1) small debounce so user can add text
        # d = random.uniform(0.8, 1.6)
        # _log("debounce_secs:", round(d, 2))
        # await asyncio.sleep(d)

         # <<<<<<<<< HERE >>>>>>>>>>>>>>
        # temporary micro-pause without showing typing
        try:
            await ws_send(conv_id, {"actor": "recruiter", "typing": False, "ts": now_iso()})
            d = random.uniform(3, 10)
            _log("debounce_secs:", round(d, 2))
            await asyncio.sleep(d)

        except Exception:
            pass

        # micro_pause = random.uniform(3, 10)
        # _log("micro_pause (silent):", round(micro_pause, 2))
        # await asyncio.sleep(micro_pause)

        # now resume typing indicator before human-like read
        try:
            await ws_send(conv_id, {"actor": "recruiter", "typing": True, "ts": now_iso()})
        except Exception:
            pass
        # <<<<<<<<< END INSERTION >>>>>>>>>>>>>>

        # 2) latest employee msg (may be empty on first turn)
        recent = fetch_recent(conv_id, limit=32)
        last_user_msg = ""
        for m in reversed(recent):
            if m["actor"] == "employee":
                last_user_msg = m.get("text", "")
                break
        _log("last_user_msg(len):", len(last_user_msg))

        # 3) human reading delay
        h = human_delay_secs_before_reading(last_user_msg or "ok")
        _log("human_delay_secs:", round(h, 2))
        await asyncio.sleep(h)

        # 4) after-hours guard (unless allowed)
        if not ALLOW_AFTER_HOURS and not is_business_hours():
            _log("after-hours: deferring")
            try:
                await ws_send(conv_id, {"actor": "recruiter", "typing": False, "ts": now_iso()})
            except Exception:
                pass
            msg = defer_message()
            add_message(conv_id, "recruiter", msg)
            await ws_send(conv_id, {"actor": "recruiter", "text": msg, "ts": now_iso()})

            when = next_business_window_start()
            FOLLOWUP_SCHEDULED[conv_id] = when
            delay_s = max(1, int((when - now_local()).total_seconds()))

            async def later():
                await asyncio.sleep(delay_s)
                if is_business_hours():
                    await handle_recruiter(conv_id)

            PENDING[conv_id] = asyncio.create_task(later())
            return

        # 5) sentiment + reply (with safe fallback)
        try:
            sentiment = quick_sentiment(last_user_msg)
        except Exception as e:
            _log("sentiment error:", repr(e))
            sentiment = "neutral"

        summary, _ = get_summary(conv_id)
        job_block = f"\n\nJOB FACTS:\n{job_facts_summary}" if job_facts_summary else ""

        reply = (
            "Thanks for the note — happy to share specifics about the team, stack, and compensation. "
            "Would a quick overview help?"
        )
        try:
            llm = generate_recruiter_reply(
                conv_history=recent,
                last_user_msg=last_user_msg,
                summary=summary + job_block,
            )
            if llm and llm.strip():
                reply = llm.strip()
        except Exception as e:
            _log("LLM reply error:", repr(e))

        _log("sentiment:", sentiment, "| reply_preview:", reply[:90])

        # soften if negative + schedule check-back
        if sentiment == "negative":
            try:
                await ws_send(conv_id, {"actor": "recruiter", "typing": False, "ts": now_iso()})
            except Exception:
                pass
            soft = "Totally fair — I’ll check back later in case timing is better."
            await maybe_typo_send(conv_id, soft)

            when = now_local() + timedelta(hours=FOLLOWUP_HOURS)
            async def followup():
                await asyncio.sleep(max(1, int((when - now_local()).total_seconds())))
                if is_business_hours():
                    await maybe_typo_send(
                        conv_id,
                        "Quick check-in — would a one-line summary of the team and stack be useful?"
                    )
            PENDING[conv_id] = asyncio.create_task(followup())
            return

        # 6) send reply
        try:
            await ws_send(conv_id, {"actor": "recruiter", "typing": False, "ts": now_iso()})
        except Exception:
            pass
        await maybe_typo_send(conv_id, reply)

        # 7) opportunistic memory update
        if random.random() < 0.25:
            try:
                recent2 = fetch_recent(conv_id, limit=24)
                turns = "\n".join(f"{m['actor']}: {m['text']}" for m in recent2[-10:])
                if turns:
                    new_sum = summarize_for_memory(turns, prev_summary=summary)
                    save_summary(conv_id, new_sum, recent2[-1]["id"])
                    _log("summary updated")
            except Exception as e:
                _log("summarize error:", repr(e))

        _log("DONE", conv_id)

    except asyncio.CancelledError:
        _log("task cancelled (expected during debounce replace)")
        raise
    except Exception as e:
        _log("UNCAUGHT ERROR:", repr(e))
        try:
            await ws_send(conv_id, {"actor": "recruiter", "typing": False, "ts": now_iso()})
        except Exception:
            pass
        fallback = (
            "Oops—lost my draft for a sec. I can share a concise overview of team, stack, and comp. "
            "Does that help?"
        )
        add_message(conv_id, "recruiter", fallback)
        await ws_send(conv_id, {"actor": "recruiter", "text": fallback, "ts": now_iso()})
    finally:
        try:
            await ws_send(conv_id, {"actor": "recruiter", "typing": False, "ts": now_iso()})
        except Exception:
            pass


# ----------------- Routes -----------------
@app.get("/", response_class=HTMLResponse)
async def index(request: Request, conv: Optional[str] = None):
    conv_id = conv or "demo-1"
    # lazy init
    if conv_id not in MSGS:
        MSGS[conv_id] = []
        add_message(
            conv_id,
            "recruiter",
            "Hi — I’m Mamoon from NetworkVC Recruiting. I saw your profile and have an excellent role that could be a fit. "
            "Are you available for a quick chat?",
        )
        ###########################
        ###########################
        ###########################
        ###########################
        STATE[conv_id] = "WAITING"   # ← expect reply
        ###########################
        ###########################
        ###########################
        ###########################                
    return templates.TemplateResponse("index.html", {"request": request, "conv_id": conv_id})

# @app.websocket("/ws/{conv_id}")
# async def ws_endpoint(websocket: WebSocket, conv_id: str):
#     await websocket.accept()
#     WS_CONNECTIONS[conv_id] = websocket

#     # stream history to client
#     for m in MSGS.get(conv_id, []):
#         await websocket.send_text(json.dumps({"actor": m["actor"], "text": m["text"], "ts": m["ts"]}))

#     try:
#         while True:
#             raw = await websocket.receive_text()
#             try:
#                 payload = json.loads(raw)
#             except json.JSONDecodeError:
#                 continue

#             actor = payload.get("actor")
#             text = (payload.get("text") or "").strip()
#             if not text:
#                 continue

#             add_message(conv_id, actor, text)
#             await ws_send(conv_id, {"actor": actor, "text": text, "ts": now_iso()})

#             if actor == "employee":
#                 # debounce: cancel older pending task, then create fresh one
#                 prev = PENDING.pop(conv_id, None)
#                 if prev and not prev.done():
#                     prev.cancel()
#                 PENDING[conv_id] = asyncio.create_task(handle_recruiter(conv_id))
#     except WebSocketDisconnect:
#         if WS_CONNECTIONS.get(conv_id) is websocket:
#             WS_CONNECTIONS.pop(conv_id, None)
@app.websocket("/ws/{conv_id}")
async def ws_endpoint(websocket: WebSocket, conv_id: str):
    await websocket.accept()
    _log("WS accepted for", conv_id)
    WS_CONNECTIONS[conv_id] = websocket
    #######################@@@@@@
    #############################
    #############################
    STATE.setdefault(conv_id, "IDLE")  # defensive default

    #############################
    #############################
    # stream history down
    for m in MSGS.get(conv_id, []):
        await websocket.send_text(json.dumps({"actor": m["actor"], "text": m["text"], "ts": m["ts"]}))

    try:
        while True:
            raw = await websocket.receive_text()
            _log("WS recv", conv_id, "raw:", raw[:200])
            try:
                payload = json.loads(raw)
            except json.JSONDecodeError:
                _log("WS bad JSON for", conv_id, "raw:", raw[:200])
                continue

            actor = payload.get("actor")
            text = (payload.get("text") or "").strip()
            _log("WS message", conv_id, "actor=", actor, "text=", text)

            if not text:
                continue

            add_message(conv_id, actor, text)
            await ws_send(conv_id, {"actor": actor, "text": text, "ts": now_iso()})

            if actor == "employee":
            ##############################
            # ###########################
            # ############################
            # --- state + telemetry on reply ---
                STATE[conv_id] = "REPLIED"
                TELEM["replies"] += 1
                try:
                    if quick_sentiment(text) == "negative":
                        TELEM["neg_sentiment"] += 1
                except Exception:
                    pass
                # STATE[conv_id] = "REPLIED"
                _log("STATE[", conv_id, "] =", STATE[conv_id])
            # ############################
            # ############################
            # ###########################
            # ##########################                
                prev = PENDING.pop(conv_id, None)
                if prev and not prev.done():
                    prev.cancel()
                _log("Scheduling recruiter for", conv_id)
                PENDING[conv_id] = asyncio.create_task(handle_recruiter(conv_id))
    except WebSocketDisconnect:
        _log("WS disconnect for", conv_id)
        if WS_CONNECTIONS.get(conv_id) is websocket:
            WS_CONNECTIONS.pop(conv_id, None)

@app.post("/recruiter/send")
async def recruiter_send(conv_id: str = Form(...)):
    prev = PENDING.pop(conv_id, None)
    if prev and not prev.done():
        prev.cancel()
    PENDING[conv_id] = asyncio.create_task(handle_recruiter(conv_id))
    return PlainTextResponse("ok")

@app.get("/assets/job_description")
async def serve_pdf():
    path = os.path.join("assets", "job_description.pdf")
    return FileResponse(path, filename="job_description.pdf")

##########################
##########################
##########################
##########################
##########################
##########################
@app.on_event("startup")
async def _boot_scheduler():
    asyncio.create_task(scheduler_worker())

@app.get("/debug/metrics", response_class=PlainTextResponse)
async def metrics():
    # trivial plaintext snapshot; could be JSON if you prefer
    lines = [f"{k}: {v}" for k, v in TELEM.items()]
    return "\n".join(lines)
##########################
##########################
##########################
##########################
##########################
##########################