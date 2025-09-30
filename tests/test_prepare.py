"""
Tests for the prepare module (InstanceSelectionService).
"""

from unittest.mock import patch

from spotinfer.prepare.offers import InstanceSelectionService, list_offers


class TestInstanceSelectionService:
    """Test cases for InstanceSelectionService class."""

    def test_init(self):
        """Test service initialization."""
        with patch("spotinfer.prepare.offers.DatacrunchAdapter") as mock_adapter:
            service = InstanceSelectionService("test_id", "test_secret")
            mock_adapter.assert_called_once_with("test_id", "test_secret")
            assert service.adapter == mock_adapter.return_value

    def test_list_all_offers(self, mock_instance_types):
        """Test listing all offers."""
        with patch("spotinfer.prepare.offers.DatacrunchAdapter") as mock_adapter:
            mock_adapter.return_value.get_instance_types.return_value = (
                mock_instance_types
            )

            service = InstanceSelectionService()
            result = service.list_all_offers()

            assert result == mock_instance_types
            mock_adapter.return_value.get_instance_types.assert_called_once()

    def test_list_spot_offers(self, mock_instance_types):
        """Test listing spot offers."""
        with patch("spotinfer.prepare.offers.DatacrunchAdapter") as mock_adapter:
            mock_adapter.return_value.get_spot_instance_types.return_value = (
                mock_instance_types
            )

            service = InstanceSelectionService()
            result = service.list_spot_offers()

            assert result == mock_instance_types
            mock_adapter.return_value.get_spot_instance_types.assert_called_once()

    def test_filter_by_gpu_type(self, mock_instance_types):
        """Test filtering by GPU type."""
        with patch("spotinfer.prepare.offers.DatacrunchAdapter") as mock_adapter:
            a100_instances = [
                inst
                for inst in mock_instance_types
                if "A100" in inst.gpu["description"]
            ]
            mock_adapter.return_value.filter_by_gpu_type.return_value = a100_instances

            service = InstanceSelectionService()
            result = service.filter_by_gpu_type("A100")

            assert result == a100_instances
            mock_adapter.return_value.filter_by_gpu_type.assert_called_once_with("A100")

    def test_get_cheapest_offer(self, mock_instance_types):
        """Test getting cheapest offer."""
        with patch("spotinfer.prepare.offers.DatacrunchAdapter") as mock_adapter:
            cheapest = min(mock_instance_types, key=lambda x: x.price_per_hour)
            mock_adapter.return_value.get_cheapest_offer.return_value = cheapest

            service = InstanceSelectionService()
            result = service.get_cheapest_offer()

            assert result == cheapest
            mock_adapter.return_value.get_cheapest_offer.assert_called_once_with(
                None, False
            )

    def test_get_cheapest_offer_with_params(self, mock_instance_types):
        """Test getting cheapest offer with parameters."""
        with patch("spotinfer.prepare.offers.DatacrunchAdapter") as mock_adapter:
            cheapest = min(mock_instance_types, key=lambda x: x.price_per_hour)
            mock_adapter.return_value.get_cheapest_offer.return_value = cheapest

            service = InstanceSelectionService()
            result = service.get_cheapest_offer(gpu_type="A100", spot=True)

            assert result == cheapest
            mock_adapter.return_value.get_cheapest_offer.assert_called_once_with(
                "A100", True
            )

    def test_get_available_gpu_types(self):
        """Test getting available GPU types."""
        with patch("spotinfer.prepare.offers.DatacrunchAdapter") as mock_adapter:
            gpu_types = ["A100", "H100", "RTX A6000"]
            mock_adapter.return_value.get_available_gpu_types.return_value = gpu_types

            service = InstanceSelectionService()
            result = service.get_available_gpu_types()

            assert result == gpu_types
            mock_adapter.return_value.get_available_gpu_types.assert_called_once()


class TestListOffersFunction:
    """Test cases for the list_offers convenience function."""

    def test_list_offers_all(self, mock_instance_types):
        """Test listing all offers."""
        with patch("spotinfer.prepare.offers.InstanceSelectionService") as mock_service:
            mock_service.return_value.list_all_offers.return_value = mock_instance_types

            result = list_offers()

            assert result == mock_instance_types
            mock_service.assert_called_once_with(client_id=None, client_secret=None)
            mock_service.return_value.list_all_offers.assert_called_once()

    def test_list_offers_with_gpu_type(self, mock_instance_types):
        """Test listing offers with GPU type filter."""
        with patch("spotinfer.prepare.offers.InstanceSelectionService") as mock_service:
            a100_instances = [
                inst
                for inst in mock_instance_types
                if "A100" in inst.gpu["description"]
            ]
            mock_service.return_value.filter_by_gpu_type.return_value = a100_instances

            result = list_offers(gpu_type="A100")

            assert result == a100_instances
            mock_service.assert_called_once_with(client_id=None, client_secret=None)
            mock_service.return_value.filter_by_gpu_type.assert_called_once_with("A100")

    def test_list_offers_spot_only(self, mock_instance_types):
        """Test listing spot offers only."""
        with patch("spotinfer.prepare.offers.InstanceSelectionService") as mock_service:
            mock_service.return_value.list_spot_offers.return_value = (
                mock_instance_types
            )

            result = list_offers(spot_only=True)

            assert result == mock_instance_types
            mock_service.assert_called_once_with(client_id=None, client_secret=None)
            mock_service.return_value.list_spot_offers.assert_called_once()

    def test_list_offers_cheapest_only(self, mock_instance_types):
        """Test listing cheapest offer only."""
        with patch("spotinfer.prepare.offers.InstanceSelectionService") as mock_service:
            cheapest = min(mock_instance_types, key=lambda x: x.price_per_hour)
            mock_service.return_value.get_cheapest_offer.return_value = cheapest

            result = list_offers(cheapest_only=True)

            assert result == [cheapest]
            mock_service.assert_called_once_with(client_id=None, client_secret=None)
            mock_service.return_value.get_cheapest_offer.assert_called_once_with(
                gpu_type=None, spot=False
            )

    def test_list_offers_cheapest_only_with_gpu_type(self, mock_instance_types):
        """Test listing cheapest offer with GPU type filter."""
        with patch("spotinfer.prepare.offers.InstanceSelectionService") as mock_service:
            cheapest = min(mock_instance_types, key=lambda x: x.price_per_hour)
            mock_service.return_value.get_cheapest_offer.return_value = cheapest

            result = list_offers(gpu_type="A100", cheapest_only=True, spot_only=True)

            assert result == [cheapest]
            mock_service.assert_called_once_with(client_id=None, client_secret=None)
            mock_service.return_value.get_cheapest_offer.assert_called_once_with(
                gpu_type="A100", spot=True
            )

    def test_list_offers_cheapest_only_no_offer(self):
        """Test listing cheapest offer when no offer available."""
        with patch("spotinfer.prepare.offers.InstanceSelectionService") as mock_service:
            mock_service.return_value.get_cheapest_offer.return_value = None

            result = list_offers(cheapest_only=True)

            assert result == []
            mock_service.assert_called_once_with(client_id=None, client_secret=None)
            mock_service.return_value.get_cheapest_offer.assert_called_once_with(
                gpu_type=None, spot=False
            )

    def test_list_offers_with_credentials(self, mock_instance_types):
        """Test listing offers with custom credentials."""
        with patch("spotinfer.prepare.offers.InstanceSelectionService") as mock_service:
            mock_service.return_value.list_all_offers.return_value = mock_instance_types

            result = list_offers(client_id="custom_id", client_secret="custom_secret")

            assert result == mock_instance_types
            mock_service.assert_called_once_with(
                client_id="custom_id", client_secret="custom_secret"
            )
            mock_service.return_value.list_all_offers.assert_called_once()


class TestOffersServiceAlias:
    """Test backward compatibility alias."""

    def test_offers_service_alias(self):
        """Test that OffersService is an alias for InstanceSelectionService."""
        from spotinfer.prepare.offers import OffersService

        with patch("spotinfer.prepare.offers.DatacrunchAdapter") as mock_adapter:
            service = OffersService("test_id", "test_secret")
            mock_adapter.assert_called_once_with("test_id", "test_secret")
            assert service.adapter == mock_adapter.return_value
