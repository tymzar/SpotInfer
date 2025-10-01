"""
Datacrunch API Adapter.

Thin wrapper around the Datacrunch SDK providing a clean interface
for offers, pricing, instance/volume lifecycle, and SSH/SFTP utilities.
"""

import os
from typing import List, Optional

from datacrunch import DataCrunchClient
from datacrunch.instance_types.instance_types import InstanceType
from dotenv import load_dotenv

from ..utils.gpu import get_available_gpu_types_from_instances

# Load environment variables from .env file
load_dotenv()


class DatacrunchAdapter:
    """Adapter for Datacrunch API operations."""

    def __init__(self, client_id: Optional[str] = None, client_secret: Optional[str] = None):
        """Initialize the Datacrunch client."""
        self.client_id = client_id or os.getenv("DATACRUNCH_CLIENT_ID")
        self.client_secret = client_secret or os.getenv("DATACRUNCH_CLIENT_SECRET")

        if not self.client_id or not self.client_secret:
            raise ValueError(
                "Datacrunch credentials not found. Please set DATACRUNCH_CLIENT_ID and "
                "DATACRUNCH_CLIENT_SECRET environment variables or pass them directly."
            )

        self.client = DataCrunchClient(self.client_id, self.client_secret)

    def get_instance_types(self) -> List[InstanceType]:
        """Get all available instance types."""
        return self.client.instance_types.get()

    def get_spot_instance_types(self) -> List[InstanceType]:
        """Get instance types with spot pricing."""
        instance_types = self.get_instance_types()
        return [it for it in instance_types if it.spot_price_per_hour > 0]

    def filter_by_gpu_type(self, gpu_type: str) -> List[InstanceType]:
        """Filter instance types by GPU type (case-insensitive)."""
        instance_types = self.get_instance_types()
        gpu_type_upper = gpu_type.upper()
        filtered = []

        for itype in instance_types:
            gpu_description = itype.gpu.get("description", "").upper()
            if gpu_type_upper in gpu_description:
                filtered.append(itype)

        filtered.sort(key=lambda x: x.price_per_hour)
        return filtered

    def get_cheapest_offer(self, gpu_type: Optional[str] = None, spot: bool = False) -> Optional[InstanceType]:
        """Get the cheapest offer, optionally filtered by GPU type and spot preference."""
        if gpu_type:
            offers = self.filter_by_gpu_type(gpu_type)
        elif spot:
            offers = self.get_spot_instance_types()
        else:
            offers = self.get_instance_types()

        if not offers:
            return None

        # Sort by spot price if spot is preferred, otherwise on-demand price
        if spot:
            offers.sort(key=lambda x: x.spot_price_per_hour)
        else:
            offers.sort(key=lambda x: x.price_per_hour)

        return offers[0]

    def get_available_gpu_types(self) -> List[str]:
        """Get list of available GPU types from instance descriptions."""
        instance_types = self.get_instance_types()
        return get_available_gpu_types_from_instances(instance_types)
