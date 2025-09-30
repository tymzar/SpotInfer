"""
SpotInfer - Datacrunch API Adapter.

This module provides a thin wrapper around the Datacrunch SDK for offers,
pricing, instance/volume lifecycle, and SSH/SFTP utilities.
"""

from .datacrunch_adapter import DatacrunchAdapter

__all__ = ["DatacrunchAdapter"]
