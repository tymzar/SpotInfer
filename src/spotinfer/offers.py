"""
Offers listing functionality using Datacrunch SDK.

Simple module for listing available instance types and pricing.
"""

import os
from typing import List, Optional

from datacrunch import DataCrunchClient
from datacrunch.instance_types.instance_types import InstanceType
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class OffersService:
    """Service for listing Datacrunch instance offers and pricing."""

    def __init__(
        self,
        client_id: Optional[str] = None,
        client_secret: Optional[str] = None,
    ):
        """
        Initialize Datacrunch client.

        Args:
            client_id: Datacrunch client ID (defaults to env DATACRUNCH_CLIENT_ID)
            client_secret: Datacrunch client secret (defaults to env)
        """
        self.client = DataCrunchClient(
            client_id=client_id or os.getenv("DATACRUNCH_CLIENT_ID"),
            client_secret=client_secret or os.getenv("DATACRUNCH_CLIENT_SECRET"),
        )

    def list_all_offers(self) -> List[InstanceType]:
        """
        List all available instance types with pricing.

        Returns:
            List of InstanceType objects sorted by on-demand price
        """
        instance_types = self.client.instance_types.get()

        # Sort by on-demand price (ascending)
        instance_types.sort(key=lambda x: x.price_per_hour)

        return instance_types

    def list_spot_offers(self) -> List[InstanceType]:
        """
        List all available instance types sorted by spot pricing.

        Returns:
            List of InstanceType objects sorted by spot price
        """
        instance_types = self.client.instance_types.get()

        # Sort by spot price (ascending)
        instance_types.sort(key=lambda x: x.spot_price_per_hour)

        return instance_types

    def filter_by_gpu_type(self, gpu_type: str) -> List[InstanceType]:
        """
        Filter instance types by GPU type.

        Args:
            gpu_type: GPU type to filter by (e.g., 'V100', 'RTX4090', 'A100')

        Returns:
            List of InstanceType objects matching the GPU type
        """
        instance_types = self.client.instance_types.get()

        # Normalize GPU type to uppercase for case-insensitive matching
        gpu_type_upper = gpu_type.upper()

        # Filter by GPU type (case-insensitive) using description field
        filtered = []
        for itype in instance_types:
            gpu_description = itype.gpu.get("description", "").upper()
            if gpu_type_upper in gpu_description:
                filtered.append(itype)

        # Sort by on-demand price
        filtered.sort(key=lambda x: x.price_per_hour)

        return filtered

    def get_cheapest_offer(
        self, gpu_type: Optional[str] = None, spot: bool = False
    ) -> Optional[InstanceType]:
        """
        Get the cheapest available offer.

        Args:
            gpu_type: Optional GPU type filter
            spot: Whether to use spot pricing (default: False for on-demand)

        Returns:
            Cheapest InstanceType or None if no offers
        """
        if gpu_type:
            offers = self.filter_by_gpu_type(gpu_type)
        else:
            offers = self.list_all_offers()

        if not offers:
            return None

        if spot:
            # Sort by spot price and return cheapest
            offers.sort(key=lambda x: x.spot_price_per_hour)
            return offers[0]
        else:
            # Already sorted by on-demand price
            return offers[0]

    def get_available_gpu_types(self) -> List[str]:
        """
        Get list of available GPU types.

        Returns:
            List of unique GPU types
        """
        instance_types = self.client.instance_types.get()
        gpu_types = set()

        for itype in instance_types:
            gpu_description = itype.gpu.get("description", "")
            if gpu_description and itype.gpu.get("number_of_gpus", 0) > 0:
                # Extract GPU type from description
                # Try to find common GPU patterns
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


def list_offers(
    gpu_type: Optional[str] = None,
    spot_only: bool = False,
    cheapest_only: bool = False,
    client_id: Optional[str] = None,
    client_secret: Optional[str] = None,
) -> List[InstanceType]:
    """
    Convenience function to list offers.

    Args:
        gpu_type: Optional GPU type filter
        spot_only: Whether to show only spot pricing
        cheapest_only: Whether to return only the cheapest offer
        client_id: Optional Datacrunch client ID
        client_secret: Optional Datacrunch client secret

    Returns:
        List of InstanceType objects
    """
    service = OffersService(client_id=client_id, client_secret=client_secret)

    if cheapest_only:
        offer = service.get_cheapest_offer(gpu_type=gpu_type, spot=spot_only)
        return [offer] if offer else []

    if gpu_type:
        offers = service.filter_by_gpu_type(gpu_type)
    elif spot_only:
        offers = service.list_spot_offers()
    else:
        offers = service.list_all_offers()

    return offers
