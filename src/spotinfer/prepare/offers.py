"""
SpotInfer - Instance Selection and Offers.

This module provides functionality for instance selection, offers listing,
and filtering based on GPU type, pricing, and availability.
"""

from typing import List, Optional

from ..adapter import DatacrunchAdapter


class InstanceSelectionService:
    """Service for instance selection and offers management."""

    def __init__(
        self, client_id: Optional[str] = None, client_secret: Optional[str] = None
    ):
        """Initialize the Datacrunch adapter."""
        self.adapter = DatacrunchAdapter(client_id, client_secret)

    def list_all_offers(self) -> List:
        """List all available instance types with pricing."""
        return self.adapter.get_instance_types()

    def list_spot_offers(self) -> List:
        """List all available instance types sorted by spot pricing."""
        return self.adapter.get_spot_instance_types()

    def filter_by_gpu_type(self, gpu_type: str) -> List:
        """Filter instance types by GPU type (case-insensitive)."""
        return self.adapter.filter_by_gpu_type(gpu_type)

    def get_cheapest_offer(self, gpu_type: Optional[str] = None, spot: bool = False):
        """Get the cheapest available offer."""
        return self.adapter.get_cheapest_offer(gpu_type, spot)

    def get_available_gpu_types(self) -> List[str]:
        """Get list of available GPU types."""
        return self.adapter.get_available_gpu_types()


# Backward compatibility alias
OffersService = InstanceSelectionService


def list_offers(
    gpu_type: Optional[str] = None,
    spot_only: bool = False,
    cheapest_only: bool = False,
    client_id: Optional[str] = None,
    client_secret: Optional[str] = None,
):
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
    service = InstanceSelectionService(client_id=client_id, client_secret=client_secret)

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
