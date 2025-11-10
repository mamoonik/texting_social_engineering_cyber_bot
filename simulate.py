# simulate.py
from datetime import datetime
from jitter_core import schedule_messages

if __name__ == "__main__":
    now = datetime.utcnow()
    msgs = [
        ("m1", "Hey team—quick update on Q4 metrics, deck coming soon."),
        ("m2", "Following up on the vendor invoice—did AP receive it?"),
        ("m3", "Heads up: deploying the patch around 3pm ET."),
        ("m4", "Can you share last week’s numbers when you get a chance?"),
        ("m5", "Thx! Also, lunch tomorrow?")
    ]
    plan = schedule_messages(msgs, now_ts=now, history=[])
    for d in plan:
        print(d.message_id, "→", d.scheduled_for.isoformat(), "|", d.rationale)
