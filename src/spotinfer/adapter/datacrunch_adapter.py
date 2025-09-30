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

# Load environment variables from .env file
load_dotenv()


class DatacrunchAdapter:
    """Adapter for Datacrunch API operations."""

    def __init__(
        self, client_id: Optional[str] = None, client_secret: Optional[str] = None
    ):
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

    def get_cheapest_offer(
        self, gpu_type: Optional[str] = None, spot: bool = False
    ) -> Optional[InstanceType]:
        """Get the cheapest offer, optionally filtered by GPU type and spot preference."""  # noqa: E501
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
        gpu_types = set()

        for itype in instance_types:
            gpu_description = itype.gpu.get("description", "")
            if gpu_description and itype.gpu.get("number_of_gpus", 0) > 0:
                # Extract GPU type from description using regex patterns
                import re

                patterns = [
                    r"(B300)\s+SXM6",  # e.g., "B300 SXM6"
                    r"(B200)\s+SXM6",  # e.g., "B200 SXM6"
                    r"(H200)\s+SXM5",  # e.g., "H200 SXM5"
                    r"(H100)\s+SXM5",  # e.g., "H100 SXM5"
                    r"(A100)\s+SXM4",  # e.g., "A100 SXM4"
                    r"(RTX\s+PRO)\s+6000",  # e.g., "RTX PRO 6000"
                    r"(RTX\s+6000)\s+Ada",  # e.g., "RTX 6000 Ada"
                    r"(RTX\s+A6000)",  # e.g., "RTX A6000"
                    r"(Tesla\s+V100)",  # e.g., "Tesla V100"
                    r"(L40S)",  # e.g., "L40S"
                ]

                for pattern in patterns:
                    match = re.search(pattern, gpu_description)
                    if match:
                        gpu_type = match.group(1)
                        gpu_types.add(gpu_type)
                        break

        return sorted(list(gpu_types))
