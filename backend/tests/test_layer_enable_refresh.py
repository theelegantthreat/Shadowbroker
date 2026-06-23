"""Tests for on-enable layer refresh (Phase 2 UX guardrail)."""
from __future__ import annotations

from unittest.mock import patch

from services.fetchers._store import active_layers, bump_active_layers_version
from services.layer_enable_refresh import refresh_newly_enabled_layers, snapshot_active_layers


def test_refresh_firms_on_enable_only():
    before = snapshot_active_layers()
    active_layers["firms"] = True
    bump_active_layers_version()

    with (
        patch("services.fetchers.earth_observation.fetch_firms_fires") as firms,
        patch("services.fetchers.earth_observation.fetch_firms_country_fires") as country,
        patch("services.fetchers._store.bump_data_version") as bump,
    ):
        refresh_newly_enabled_layers({**before, "firms": False})

    firms.assert_called_once()
    country.assert_called_once()
    bump.assert_called_once()

    active_layers["firms"] = before.get("firms", False)


def test_refresh_skips_when_layer_stays_off():
    before = {**snapshot_active_layers(), "cctv": False}
    active_layers["cctv"] = False

    with patch("services.fetchers.infrastructure.fetch_cctv") as fetch_cctv:
        refresh_newly_enabled_layers(before)

    fetch_cctv.assert_not_called()
