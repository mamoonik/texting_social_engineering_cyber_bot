# # jitter_core.py
# from __future__ import annotations
# import math, random
# from dataclasses import dataclass
# from datetime import datetime, timedelta
# from typing import List, Tuple, Optional

# @dataclass
# class PersonProfile:
#     # We treat human typing speeds as log-normal: WPM ~ logN(mu, sigma)
#     wpm_mu: float = math.log(45.0)  # log-mean of ~45 words/min
#     wpm_sigma: float = 0.35         # log-std

#     # Thinking / distraction pauses during compose ~ Gamma(k, theta)
#     pause_shape: float = 2.0        # k
#     pause_scale: float = 1.2        # theta (seconds)
#     pause_prob: float = 0.35        # chance to add another pause

# @dataclass
# class AntiPattern:
#     equal_gap_tol_s: float = 15.0   # treat near-equal gaps as “robotic”
#     min_gap_s: float = 18.0         # never send back-to-back faster than this
#     max_hourly_rate: int = 16       # soft cap per rolling hour

# @dataclass
# class ScheduleDecision:
#     message_id: str
#     scheduled_for: datetime
#     rationale: str

# # --- tiny helpers
# from datetime import time as dtime, timedelta

# def _in_quiet_hours(ts, start=22, end=7) -> bool:
#     # Quiet if between 22:00–24:00 or 00:00–07:00
#     h = ts.hour
#     return (h >= start) or (h < end)

# def _snap_near_boundary(ts, prob=0.35, window=(180, 420)):
#     # With prob, snap toward :00 or :30 ± 3–7 minutes
#     import random, math
#     if random.random() > prob:
#         return ts
#     minute = ts.minute
#     target_min = 0 if abs(minute - 0) < abs(minute - 30) else 30
#     base = ts.replace(minute=target_min, second=0, microsecond=0)
#     lo, hi = window
#     jitter = random.randint(-hi, hi)
#     if abs(jitter) < lo:
#         jitter = (lo if jitter >= 0 else -lo)
#     return base + timedelta(seconds=jitter)



# def _lognormal(mu: float, sigma: float) -> float:
#     """Sample a log-normal value: exp(N(mu, sigma^2))."""
#     return math.exp(random.gauss(mu, sigma))

# def _gamma(shape: float, scale: float) -> float:
#     """Quick gamma sampler (k>0)."""
#     # Using Python's built-in random.gammavariate for simplicity (k=alpha, theta=beta)
#     return random.gammavariate(shape, scale)

# def _estimate_words(text: str) -> int:
#     return max(1, len([t for t in text.split() if t.strip()]))

# def _equal_gap_like(history: List[datetime], candidate: datetime, tol_s: float) -> bool:
#     if len(history) < 3:
#         return False
#     gaps = [(history[i]-history[i-1]).total_seconds() for i in range(1, len(history))]
#     last_gap = (candidate - history[-1]).total_seconds()
#     return abs(gaps[-1] - gaps[-2]) < tol_s and abs(last_gap - gaps[-1]) < tol_s

# def _enforce_limits(candidate: datetime, history: List[datetime], min_gap_s: float, max_hourly_rate: int) -> datetime:
#     # Enforce a minimum gap vs last message
#     if history:
#         candidate = max(candidate, history[-1] + timedelta(seconds=min_gap_s))
#     # Soft per-hour cap: if already hit, push later slightly
#     recent = [t for t in history if (candidate - t).total_seconds() <= 3600]
#     if len(recent) >= max_hourly_rate:
#         bump = 60 + random.randint(20, 180)  # 1–4 extra minutes
#         candidate = candidate + timedelta(seconds=bump)
#     return candidate

# # --- main API

# def schedule_messages(
#     messages: List[Tuple[str, str]],
#     now_ts: datetime,
#     history: List[datetime] | None = None,
#     profile: PersonProfile = PersonProfile(),
#     ap: AntiPattern = AntiPattern(),
#     seed: Optional[int] = 7,
# ) -> List[ScheduleDecision]:
#     if seed is not None:
#         random.seed(seed)

#     history = list(history or [])
#     out: List[ScheduleDecision] = []

#     for mid, text in messages:
#         # 1) Words in message
#         words = _estimate_words(text)

#         # 2) Sample a human typing speed (words/min) from a log-normal
#         wpm = _lognormal(profile.wpm_mu, profile.wpm_sigma)

#         # 3) Base compose time = words / (wpm/60) seconds
#         base_compose_s = words / (wpm / 60.0)

#         # 4) Add “thinking/distraction” pauses: sum of a few Gamma(k, theta) draws
#         pauses_s = 0.0
#         while random.random() < profile.pause_prob:
#             pauses_s += _gamma(profile.pause_shape, profile.pause_scale)

#         compose_s = max(1.0, base_compose_s + pauses_s)

#         # 5) Candidate send time
#         candidate = now_ts + timedelta(seconds=compose_s)

#         # 6) Anti-pattern guard: if spacing starts looking “too equal”, nudge
#         if _equal_gap_like(history, candidate, ap.equal_gap_tol_s):
#             candidate += timedelta(seconds=random.randint(7, 97))

#         # 7) Rate limits (min inter-send gap + hourly softness)
#         candidate = _enforce_limits(candidate, history, ap.min_gap_s, ap.max_hourly_rate)

#         # 8) Last-mile “finger press” jitter: tiny human delay
#         candidate += timedelta(milliseconds=random.randint(80, 650))

#         # snap near :00/:30 sometimes
#         candidate = _snap_near_boundary(candidate, prob=0.35, window=(180, 420))

#         # softly move out of quiet hours
#         if _in_quiet_hours(candidate, start=22, end=7):
#             # push into the next active window with a small random delay
#             candidate = candidate.replace(second=0, microsecond=0) + timedelta(minutes=8)

#         why = (f"{words} words @~{wpm:.1f} wpm → base {base_compose_s:.1f}s + pauses {pauses_s:.1f}s; "
#                f"equal-gap-nudge={_equal_gap_like(history, candidate, ap.equal_gap_tol_s)}; "
#                f"history={len(history)}")

#         out.append(ScheduleDecision(mid, candidate, why))
#         history.append(candidate)
#         now_ts = max(now_ts, candidate)  # serialize on one device/number

#     return out


# jitter_core.py
from __future__ import annotations
import math, random
from dataclasses import dataclass
from datetime import datetime, timedelta, time
from typing import List, Tuple, Optional

@dataclass
class PersonProfile:
    # Human typing speeds ~ LogNormal(mu, sigma) in log-space
    wpm_mu: float = math.log(45.0)   # log-mean of ~45 wpm
    wpm_sigma: float = 0.35          # log-std
    # Thinking/distraction pauses during compose ~ Gamma(k, theta)
    pause_shape: float = 2.0         # k
    pause_scale: float = 1.2         # theta (seconds)
    pause_prob: float = 0.35         # chance to add another pause

@dataclass
class AntiPattern:
    equal_gap_tol_s: float = 15.0    # treat near-equal gaps as “robotic”
    min_gap_s: float = 18.0          # never send back-to-back faster than this
    max_hourly_rate: int = 16        # soft cap per rolling hour

@dataclass
class ScheduleDecision:
    message_id: str
    scheduled_for: datetime
    rationale: str

# ---------- helpers

def _lognormal(mu: float, sigma: float) -> float:
    """exp(N(mu, sigma^2))"""
    return math.exp(random.gauss(mu, sigma))

def _gamma(shape: float, scale: float) -> float:
    """Gamma(k=shape, theta=scale)"""
    return random.gammavariate(shape, scale)

def _estimate_words(text: str) -> int:
    return max(1, len([t for t in text.split() if t.strip()]))

def _equal_gap_like(history: List[datetime], candidate: datetime, tol_s: float) -> bool:
    if len(history) < 3:
        return False
    gaps = [(history[i] - history[i-1]).total_seconds() for i in range(1, len(history))]
    last_gap = (candidate - history[-1]).total_seconds()
    return (abs(gaps[-1] - gaps[-2]) < tol_s) and (abs(last_gap - gaps[-1]) < tol_s)

def _enforce_limits(candidate: datetime, history: List[datetime],
                    min_gap_s: float, max_hourly_rate: int) -> datetime:
    # min inter-send gap
    if history:
        candidate = max(candidate, history[-1] + timedelta(seconds=min_gap_s))
    # rolling-hour softness
    recent = [t for t in history if (candidate - t).total_seconds() <= 3600]
    if len(recent) >= max_hourly_rate:
        candidate += timedelta(seconds=60 + random.randint(20, 180))  # +1–4 min
    return candidate

def _in_quiet_hours(ts: datetime, start_h: int = 22, end_h: int = 7) -> bool:
    # Quiet if in [start_h, 24) U [0, end_h)
    return (ts.hour >= start_h) or (ts.hour < end_h)

def _push_out_of_quiet(ts: datetime, start_h: int = 22, end_h: int = 7) -> datetime:
    """
    Move to the next active-window start (end_h:00 local), with small jitter.
    If ts is after start_h (night), jump to next day end_h:00.
    If ts is before end_h (early morning), jump to today end_h:00.
    """
    if ts.hour >= start_h:
        # next day at end_h:00
        base = ts.replace(hour=end_h, minute=0, second=0, microsecond=0) + timedelta(days=1)
    else:
        # today at end_h:00
        base = ts.replace(hour=end_h, minute=0, second=0, microsecond=0)
    return base + timedelta(minutes=random.randint(5, 19))  # soft human jitter

def _snap_near_boundary(ts: datetime, prob: float = 0.35,
                        window: Tuple[int, int] = (180, 420)) -> datetime:
    """
    With probability, snap toward :00 or :30 ± 3–7 minutes (human meeting edges).
    """
    if random.random() > prob:
        return ts
    target_min = 0 if abs(ts.minute - 0) <= abs(ts.minute - 30) else 30
    base = ts.replace(minute=target_min, second=0, microsecond=0)
    lo, hi = window
    jitter = random.randint(-hi, hi)
    if abs(jitter) < lo:
        jitter = (lo if jitter >= 0 else -lo)
    return base + timedelta(seconds=jitter)

# ---------- main API

def schedule_messages(
    messages: List[Tuple[str, str]],
    now_ts: datetime,
    history: List[datetime] | None = None,
    profile: PersonProfile = PersonProfile(),
    ap: AntiPattern = AntiPattern(),
    seed: Optional[int] = 7,
) -> List[ScheduleDecision]:
    if seed is not None:
        random.seed(seed)

    history = list(history or [])
    out: List[ScheduleDecision] = []

    for mid, text in messages:
        # (1) Words and WPM
        words = _estimate_words(text)
        wpm = _lognormal(profile.wpm_mu, profile.wpm_sigma)

        # (2) Base compose time (seconds)
        base_compose_s = words / (wpm / 60.0)

        # (3) Thinking/distraction pauses (Gamma)
        pauses_s = 0.0
        while random.random() < profile.pause_prob:
            pauses_s += _gamma(profile.pause_shape, profile.pause_scale)

        compose_s = max(1.0, base_compose_s + pauses_s)

        # (4) Candidate time
        candidate = now_ts + timedelta(seconds=compose_s)

        # (5) Snap near natural boundaries
        candidate = _snap_near_boundary(candidate, prob=0.35, window=(180, 420))

        # (6) Quiet-hours push (to next active window)
        if _in_quiet_hours(candidate, start_h=22, end_h=7):
            candidate = _push_out_of_quiet(candidate, start_h=22, end_h=7)

        # (7) Anti-pattern nudge
        if _equal_gap_like(history, candidate, ap.equal_gap_tol_s):
            candidate += timedelta(seconds=random.randint(7, 97))

        # (8) Rate limits
        candidate = _enforce_limits(candidate, history, ap.min_gap_s, ap.max_hourly_rate)

        # (9) Last-mile human “press” jitter
        candidate += timedelta(milliseconds=random.randint(80, 650))

        why = (
            f"{words} words @~{wpm:.1f} wpm → base {base_compose_s:.1f}s + pauses {pauses_s:.1f}s; "
            f"equal-gap-nudge={_equal_gap_like(history, candidate, ap.equal_gap_tol_s)}; "
            f"history={len(history)}"
        )

        out.append(ScheduleDecision(mid, candidate, why))
        history.append(candidate)
        now_ts = max(now_ts, candidate)

    return out
