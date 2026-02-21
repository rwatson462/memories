"""Confidence decay computation for memories.

Pure function — no classes, no state, no I/O.  The only logic here
is the linear-decay formula applied differently per decay policy.
"""

from datetime import datetime, timezone


def compute_confidence(
    decay_policy: str,
    created_at: datetime,
    last_reinforced_at: datetime | None,
    half_life_hours: float,
) -> float:
    """Calculate current confidence for a memory based on its decay policy.

    Returns a float in [0.0, 1.0] rounded to 4 decimal places.

    Policies:
      - stable: always 1.0, ignoring age entirely.
      - contextual: linear decay from created_at to zero over half_life_hours.
      - reinforceable: same linear decay, but age is measured from
        last_reinforced_at (falls back to created_at if never reinforced).
    """
    if decay_policy == "stable":
        return 1.0

    now = datetime.now(timezone.utc)

    if decay_policy == "reinforceable" and last_reinforced_at is not None:
        # Reinforceable memories reset their age on reinforcement.
        age_hours = (now - last_reinforced_at).total_seconds() / 3600
    else:
        # Contextual — or reinforceable that was never reinforced.
        age_hours = (now - created_at).total_seconds() / 3600

    confidence = max(0.0, 1.0 - (age_hours / half_life_hours))
    return round(confidence, 4)
