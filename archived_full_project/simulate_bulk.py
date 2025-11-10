# simulate_bulk.py
from datetime import datetime
from jitter_core import schedule_messages
import random, csv, sys
from typing import List, Tuple

def make_msgs(n: int) -> List[Tuple[str, str]]:
    # toy messages with varied lengths
    base = [
        "Ping",
        "Quick update on Q4 metrics—deck coming soon.",
        "Following up on the vendor invoice—did AP receive it?",
        "Heads up: deploying the patch around 3pm ET.",
        "Can you share last week’s numbers when you get a chance?",
        "Thanks! Also, lunch tomorrow?",
    ]
    msgs = []
    for i in range(n):
        body = " ".join(random.choices(base, k=random.randint(1, 2)))
        msgs.append((f"m{i+1}", body))
    return msgs

if __name__ == "__main__":
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 50
    now = datetime.utcnow()
    plan = schedule_messages(make_msgs(n), now_ts=now, history=[], seed=7)

    times = [d.scheduled_for for d in plan]
    gaps = [(times[i] - times[i-1]).total_seconds() for i in range(1, len(times))]

    print(f"Generated {n} messages. Mean gap={sum(gaps)/len(gaps):.2f}s, min={min(gaps):.2f}s, max={max(gaps):.2f}s")

    # Write CSV for inspection
    with open("schedule.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["id", "scheduled_for", "why"])
        for d in plan:
            w.writerow([d.message_id, d.scheduled_for.isoformat(), d.rationale])

    # Quick histogram with matplotlib (no specific colors/styles)
    try:
        import matplotlib.pyplot as plt
        plt.figure()
        plt.hist(gaps, bins=20)
        plt.title("Inter-send gap distribution (seconds)")
        plt.xlabel("Gap (s)")
        plt.ylabel("Count")
        plt.tight_layout()
        plt.savefig("gaps_hist.png")
        print("Wrote schedule.csv and gaps_hist.png")
    except Exception as e:
        print("matplotlib not installed; skipping chart. Run: pip install matplotlib")
