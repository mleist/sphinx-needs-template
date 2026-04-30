"""Tests for garden_helper, each linked to a functional requirement."""
import datetime as _dt

import pytest

from garden_helper import is_mowing_weather, days_until_harvest, party_capacity


# ----------------------------------------------------------------- FR_MOW_WEATHER
@pytest.mark.satisfies("FR_MOW_WEATHER")
def test_mowing_warm_and_dry_is_ok():
    assert is_mowing_weather(temperature_c=18.0, rain_mm=0.0) is True


@pytest.mark.satisfies("FR_MOW_WEATHER")
def test_mowing_after_rain_is_blocked():
    assert is_mowing_weather(temperature_c=18.0, rain_mm=2.5) is False


# ----------------------------------------------------------------- FR_HARVEST_ESTIMATE
@pytest.mark.satisfies("FR_HARVEST_ESTIMATE")
def test_harvest_returns_zero_when_overdue():
    planted = _dt.date(2026, 5, 1)
    today = _dt.date(2026, 9, 1)  # > 70 days later
    assert days_until_harvest(planted, today, maturity_days=70) == 0


@pytest.mark.satisfies("FR_HARVEST_ESTIMATE")
def test_harvest_remaining_days_correct():
    planted = _dt.date(2026, 5, 1)
    today = _dt.date(2026, 5, 21)  # 20 days in
    assert days_until_harvest(planted, today, maturity_days=70) == 50


# ----------------------------------------------------------------- FR_PARTY_CAPACITY
@pytest.mark.satisfies("FR_PARTY_CAPACITY")
def test_party_capacity_floor_division():
    # 30 m² / 1.5 m² per guest = 20 guests
    assert party_capacity(30.0) == 20


@pytest.mark.satisfies("FR_PARTY_CAPACITY")
def test_party_capacity_zero_for_no_space():
    assert party_capacity(0.0) == 0
    assert party_capacity(-5.0) == 0
