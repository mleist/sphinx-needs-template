"""Domain helpers backing the gardening user stories.

Each public function maps to one or more functional requirements that are
declared in ``docs/public/reqs/functional.md``. The pytest suite then ties
those requirements to actual tests via ``@pytest.mark.satisfies(...)``.
"""

from __future__ import annotations

import datetime as _dt


def is_mowing_weather(temperature_c: float, rain_mm: float) -> bool:
    """Return True if conditions are suitable for mowing the lawn.

    Verifies FR_MOW_WEATHER:

    - Temperature must be at or above 8 °C (cold grass tears).
    - No rain in the last reading window (wet clippings clog the mower).
    """
    return temperature_c >= 8.0 and rain_mm <= 0.0


def days_until_harvest(planted: _dt.date, today: _dt.date,
                       maturity_days: int = 70) -> int:
    """Return remaining days until a vegetable can be harvested.

    Verifies FR_HARVEST_ESTIMATE:

    - Returns 0 if the produce is ready or overdue.
    - Otherwise returns ``maturity_days - elapsed`` (≥ 1).
    """
    if today < planted:
        raise ValueError("today is before planting date")
    elapsed = (today - planted).days
    remaining = maturity_days - elapsed
    return max(0, remaining)


def party_capacity(patio_area_m2: float, sqm_per_guest: float = 1.5) -> int:
    """Return how many guests fit comfortably on the patio.

    Verifies FR_PARTY_CAPACITY:

    - Floor-divides the available area by per-guest space.
    - Returns at least 0 for non-positive areas.
    """
    if patio_area_m2 <= 0:
        return 0
    return int(patio_area_m2 // sqm_per_guest)
