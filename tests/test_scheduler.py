from datetime import datetime
# from jitter_core import schedule_messages, AntiPattern
from ghosteye.jitter_core import schedule_messages, AntiPattern


def test_min_gap_enforced():
    now = datetime(2025, 1, 1, 10, 0, 0)
    msgs = [(f"m{i}", "short msg") for i in range(6)]
    plan = schedule_messages(msgs, now_ts=now, history=[], seed=1)
    times = [d.scheduled_for for d in plan]
    gaps = [(times[i] - times[i-1]).total_seconds() for i in range(1, len(times))]
    assert min(gaps) >= 17.9  # ~18s with float slack

def test_quiet_hours_pushes_to_morning():
    # Start during quiet hours; first message should land around 07:00 local window
    now = datetime(2025, 1, 1, 23, 55, 0)
    msgs = [("m1", "hello"), ("m2", "world")]
    plan = schedule_messages(msgs, now_ts=now, history=[], seed=2)
    first = plan[0].scheduled_for
    assert 7 <= first.hour < 8  # 07:00–07:59

def test_equal_gap_nudge_can_trigger():
    # Craft a history with two near-equal gaps, then see a nudge on the third
    now = datetime(2025, 1, 1, 12, 0, 0)
    # Fake history: 12:00:00, 12:00:30, 12:01:00  (two 30s gaps)
    hist = [now, now.replace(second=30), now.replace(minute=1, second=0)]
    msgs = [("m1", "hi there")]  # next candidate would tend to be ~30s again
    plan = schedule_messages(msgs, now_ts=now.replace(minute=1, second=0), history=hist, seed=3)
    # Third gap should be nudged away from ~30s; allow wide band but not ~30±5
    new_gap = (plan[0].scheduled_for - hist[-1]).total_seconds()
    assert not (25 <= new_gap <= 35)
