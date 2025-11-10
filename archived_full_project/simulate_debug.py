# simulate_debug.py
from datetime import datetime
# from jitter_core import schedule_messages
from typing import List, Tuple
from ghosteye.jitter_core import schedule_messages

msgs: List[Tuple[str, str]] = [
    ("m1", "Short ping"),
    ("m2", "Following up on the vendor invoice—did AP receive it?"),
    ("m3", "Heads up: deploying the patch around 3pm ET."),
    ("m4", "Can you share last week’s numbers when you get a chance?"),
    ("m5", "Thanks! Also, lunch tomorrow?")
]

if __name__ == "__main__":
    now = datetime.utcnow()
    plan = schedule_messages(msgs, now_ts=now, history=[], seed=7)

    # 1) Print each decision
    for d in plan:
        print(f"{d.message_id} @ {d.scheduled_for.isoformat()}  |  {d.rationale}")

    # 2) Compute and print the inter-send gaps (seconds)
    print("\nInter-send gaps (seconds):")
    times = [d.scheduled_for for d in plan]
    gaps = []
    for i in range(1, len(times)):
        gap = (times[i] - times[i-1]).total_seconds()
        gaps.append(gap)
        print(f"gap[{i}] = {gap:.2f}s")

    # 3) Tiny “robot-ness” check: are recent gaps almost equal?
    if len(gaps) >= 3:
        g1, g2, g3 = gaps[-3], gaps[-2], gaps[-1]
        near_equal = (abs(g1 - g2) < 15) and (abs(g2 - g3) < 15)
        print(f"\nEqual-gap pattern in last three? {near_equal}")
