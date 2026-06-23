"""Immediate data refresh when the operator enables a map layer.

Runs synchronously inside POST /api/layers so the frontend's post-toggle
live-data refetch sees populated payloads (T_toggle_visible guardrail).
"""
from __future__ import annotations

import logging

logger = logging.getLogger(__name__)


def snapshot_active_layers() -> dict[str, bool]:
    from services.fetchers._store import active_layers

    return dict(active_layers)


def refresh_newly_enabled_layers(before: dict[str, bool]) -> None:
    """Fetch any layers that transitioned off → on."""
    from services.fetchers._store import active_layers, bump_data_version

    refreshed = False

    def _enabled(key: str) -> bool:
        return bool(active_layers.get(key, False))

    def _was_off_now_on(key: str) -> bool:
        return not bool(before.get(key, False)) and _enabled(key)

    if _was_off_now_on("cctv"):
        from services.fetchers.infrastructure import fetch_cctv

        fetch_cctv()
        refreshed = True
        logger.info("CCTV loaded (layer enabled)")

    if _was_off_now_on("firms"):
        from services.fetchers.earth_observation import (
            fetch_firms_country_fires,
            fetch_firms_fires,
        )

        fetch_firms_fires()
        fetch_firms_country_fires()
        refreshed = True
        logger.info("FIRMS fires loaded (layer enabled)")

    if _was_off_now_on("power_plants"):
        from services.fetchers.infrastructure import fetch_power_plants

        fetch_power_plants()
        refreshed = True
        logger.info("Power plants loaded (layer enabled)")

    if _was_off_now_on("psk_reporter"):
        from services.fetchers.infrastructure import fetch_psk_reporter

        fetch_psk_reporter()
        refreshed = True
        logger.info("PSK Reporter loaded (layer enabled)")

    if _was_off_now_on("datacenters"):
        from services.fetchers.infrastructure import fetch_datacenters

        fetch_datacenters()
        refreshed = True
        logger.info("Datacenters loaded (layer enabled)")

    if _was_off_now_on("fishing_activity"):
        from services.fetchers.geo import fetch_fishing_activity

        fetch_fishing_activity()
        refreshed = True
        logger.info("Fishing activity loaded (layer enabled)")

    if refreshed:
        bump_data_version()
