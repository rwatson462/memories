"""Unit tests for confidence decay computation.

Tests all three decay policies (stable, contextual, reinforceable)
with boundary conditions.  Uses the ``now`` parameter on
``compute_confidence`` for deterministic results — no mocking needed.
"""

from datetime import datetime, timedelta, timezone

from memories.services.decay import compute_confidence

# Default half-life used throughout tests (matches Settings default).
HALF_LIFE = 720  # hours (30 days)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _utc_now():
    """Return a fixed 'now' for deterministic tests."""
    return datetime(2025, 6, 1, 12, 0, 0, tzinfo=timezone.utc)


def _hours_ago(hours: float, now: datetime | None = None):
    """Return a datetime *hours* before *now*."""
    now = now or _utc_now()
    return now - timedelta(hours=hours)


# ---------------------------------------------------------------------------
# Stable policy — always 1.0 regardless of age
# ---------------------------------------------------------------------------

class TestStablePolicy:
    """Stable memories never decay."""

    def test_age_zero(self):
        assert compute_confidence("stable", _utc_now(), None, HALF_LIFE) == 1.0

    def test_age_360_hours(self):
        assert compute_confidence("stable", _hours_ago(360), None, HALF_LIFE) == 1.0

    def test_age_720_hours(self):
        assert compute_confidence("stable", _hours_ago(720), None, HALF_LIFE) == 1.0

    def test_age_10000_hours(self):
        assert compute_confidence("stable", _hours_ago(10000), None, HALF_LIFE) == 1.0


# ---------------------------------------------------------------------------
# Contextual policy — linear decay over half_life_hours
# ---------------------------------------------------------------------------

class TestContextualPolicy:
    """Contextual memories decay linearly to zero at the half-life."""

    def test_age_zero(self):
        now = _utc_now()
        result = compute_confidence("contextual", now, None, HALF_LIFE, now=now)
        assert result == 1.0

    def test_half_of_half_life(self):
        """At 360 hours (half the half-life), confidence should be 0.5."""
        now = _utc_now()
        created = _hours_ago(360, now)
        result = compute_confidence("contextual", created, None, HALF_LIFE, now=now)
        assert result == 0.5

    def test_full_half_life(self):
        """At 720 hours (the full half-life), confidence should be 0.0."""
        now = _utc_now()
        created = _hours_ago(720, now)
        result = compute_confidence("contextual", created, None, HALF_LIFE, now=now)
        assert result == 0.0

    def test_beyond_half_life(self):
        """Past the half-life, confidence is clamped to 0.0."""
        now = _utc_now()
        created = _hours_ago(1000, now)
        result = compute_confidence("contextual", created, None, HALF_LIFE, now=now)
        assert result == 0.0


# ---------------------------------------------------------------------------
# Reinforceable policy — decays from last_reinforced_at
# ---------------------------------------------------------------------------

class TestReinforceablePolicy:
    """Reinforceable memories decay from the last reinforcement time."""

    def test_decay_from_last_reinforced(self):
        """Age is measured from last_reinforced_at, not created_at."""
        now = _utc_now()
        created = _hours_ago(1000, now)  # Very old
        reinforced = _hours_ago(360, now)  # Reinforced 360h ago
        result = compute_confidence(
            "reinforceable", created, reinforced, HALF_LIFE, now=now,
        )
        assert result == 0.5

    def test_fallback_to_created_when_never_reinforced(self):
        """Without reinforcement, reinforceable decays like contextual."""
        now = _utc_now()
        created = _hours_ago(360, now)
        result = compute_confidence(
            "reinforceable", created, None, HALF_LIFE, now=now,
        )
        assert result == 0.5


# ---------------------------------------------------------------------------
# Rounding
# ---------------------------------------------------------------------------

class TestRounding:
    """Confidence values are rounded to 4 decimal places."""

    def test_non_round_age(self):
        """An age that produces a non-round confidence gets rounded."""
        now = _utc_now()
        # 100 hours → 1 - 100/720 = 0.86111... → rounds to 0.8611
        created = _hours_ago(100, now)
        result = compute_confidence("contextual", created, None, HALF_LIFE, now=now)
        assert result == 0.8611
