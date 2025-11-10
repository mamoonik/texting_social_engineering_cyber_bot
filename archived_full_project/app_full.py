# app.py
from __future__ import annotations

import os
import asyncio
from datetime import datetime
from typing import List

from dotenv import load_dotenv
from fastapi import FastAPI, Request, Response
from pydantic import BaseModel

from ghosteye.jitter_core import schedule_messages
from ghosteye.telemetry import EventBus, Telemetry
from ghosteye.sms_adapter import TwilioAdapter
from ghosteye.storage import HistoryStore

# -----------------------------------------------------------------------------
# Boot
# -----------------------------------------------------------------------------
load_dotenv()  # load .env locally for dev

app = FastAPI(title="GhostEye SMS Jitter")

bus = EventBus()
telemetry = Telemetry(bus, logfile="logs.ndjson")
sms = TwilioAdapter()  # honors MOCK_TWILIO=true to mock-send

store = HistoryStore("ghosteye.db")

FROM_NUMBER = os.getenv("TWILIO_FROM_NUMBER", "").strip()
if not FROM_NUMBER:
    # We'll still run (e.g., in full mock), but warn loudly.
    print("[WARN] TWILIO_FROM_NUMBER is not set. Set it in .env for real sends.")

AUTO_REPLY = os.getenv("AUTO_REPLY", "").lower() == "true"  # optional auto-reply on inbound

# -----------------------------------------------------------------------------
# Models
# -----------------------------------------------------------------------------
class InMsg(BaseModel):
    to: str
    id: str
    body: str

class PlanReq(BaseModel):
    messages: List[InMsg]

# -----------------------------------------------------------------------------
# Helpers
# -----------------------------------------------------------------------------
def _history_for(from_number: str) -> List[datetime]:
    """
    Retrieve recent history for a given outbound number so the jitter
    can be history-aware across restarts.
    """
    if not from_number:
        # Fallback bucket for development; won't persist uniquely per number
        from_number = "DEV-FROM"
    return store.get_history(from_number, lookback_hours=24)

async def _send_at(from_number: str, to: str, body: str, when: datetime):
    """
    Sleep until `when`, then send SMS via adapter (mock or real),
    emit telemetry, and persist the send time.
    """
    delay = max(0.0, (when - datetime.utcnow()).total_seconds())
    await asyncio.sleep(delay)

    loop = asyncio.get_running_loop()
    sid = await loop.run_in_executor(None, lambda: sms.send_sms(from_number, to, body))

    bus.emit(
        "DISPATCHED",
        message_id=sid,
        to=to,
        scheduled_for=when.isoformat()
    )
    # Persist the scheduled/actual time used (when) so future runs see this in history
    store.record_send(from_number, when)

# -----------------------------------------------------------------------------
# Endpoints
# -----------------------------------------------------------------------------
@app.post("/plan")
def plan(req: PlanReq):
    """
    Dry-run the jitter scheduler. Returns schedule decisions without sending.
    """
    pairs = [(m.id, m.body) for m in req.messages]
    history = _history_for(FROM_NUMBER)
    decisions = schedule_messages(pairs, now_ts=datetime.utcnow(), history=history)

    out = []
    for m, d in zip(req.messages, decisions):
        bus.emit(
            "SCHEDULED",
            message_id=d.message_id,
            to=m.to,
            scheduled_for=d.scheduled_for.isoformat(),
            why=d.rationale,
        )
        out.append({
            "id": d.message_id,
            "to": m.to,
            "scheduled_for": d.scheduled_for.isoformat(),
            "why": d.rationale,
        })
    return out

@app.post("/dispatch")
async def dispatch(req: PlanReq):
    """
    Schedule and (mock/real) send messages at jittered times.
    In mock mode, logs a MOCK sid; in real mode, hits Twilio.
    """
    if not FROM_NUMBER:
        # We allow mock sends without a from number. Real sends require one.
        if os.getenv("MOCK_TWILIO", "").lower() != "true":
            return {"error": "TWILIO_FROM_NUMBER not set and MOCK_TWILIO is false."}

    pairs = [(m.id, m.body) for m in req.messages]
    history = _history_for(FROM_NUMBER)
    decisions = schedule_messages(pairs, now_ts=datetime.utcnow(), history=history)

    # Emit schedule events and create async tasks for each send
    for m, d in zip(req.messages, decisions):
        bus.emit(
            "SCHEDULED",
            message_id=d.message_id,
            to=m.to,
            scheduled_for=d.scheduled_for.isoformat(),
            why=d.rationale,
        )
        # Schedule background send
        asyncio.create_task(_send_at(FROM_NUMBER or "DEV-FROM", m.to, m.body, d.scheduled_for))

    return {"scheduled": len(decisions)}

@app.post("/twilio/inbound")
async def inbound(request: Request):
    """
    Twilio inbound SMS webhook (application/x-www-form-urlencoded).
    Emits INBOUND telemetry and (optionally) auto-replies.
    """
    form = await request.form()
    frm = form.get("From")
    body = form.get("Body")

    bus.emit("INBOUND", from_=frm, body=body)

    if AUTO_REPLY and FROM_NUMBER:
        # Tiny example: acknowledge select greetings; else generic ack.
        lower = (body or "").strip().lower()
        ack = "Got it! 👋 (GhostEye)"
        if lower in {"hi", "hello", "hey"}:
            ack = "Hey! 👋 GhostEye here — message received."
        # Send reply (mock or real depending on env)
        loop = asyncio.get_running_loop()
        await loop.run_in_executor(None, lambda: sms.send_sms(FROM_NUMBER, frm, ack))

    # Acknowledge Twilio with empty TwiML
    return Response(content="<Response></Response>", media_type="text/xml")

@app.post("/twilio/status")
async def status(request: Request):
    """
    Twilio delivery status webhook.
    Emits DELIVERED telemetry with message status/error code.
    """
    form = await request.form()
    bus.emit(
        "DELIVERED",
        message_sid=form.get("MessageSid"),
        status=form.get("MessageStatus"),   # queued|sent|delivered|undelivered|failed...
        to=form.get("To"),
        frm=form.get("From"),
        error_code=form.get("ErrorCode"),
    )
    return Response(content="<Response></Response>", media_type="text/xml")
