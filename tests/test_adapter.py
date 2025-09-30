"""
Tests for the DatacrunchAdapter module.
"""

from unittest.mock import Mock, patch

import pytest

from spotinfer.adapter.datacrunch_adapter import DatacrunchAdapter


class TestDatacrunchAdapter:
    """Test cases for DatacrunchAdapter class."""

    def test_init_with_credentials(self):
        """Test adapter initialization with explicit credentials."""
        with patch(
            "spotinfer.adapter.datacrunch_adapter.DataCrunchClient"
        ) as mock_client:
            adapter = DatacrunchAdapter("test_id", "test_secret")
            mock_client.assert_called_once_with("test_id", "test_secret")
            assert adapter.client_id == "test_id"
            assert adapter.client_secret == "test_secret"

    def test_init_with_env_vars(self, monkeypatch):
        """Test adapter initialization with environment variables."""
        monkeypatch.setenv("DATACRUNCH_CLIENT_ID", "env_id")
        monkeypatch.setenv("DATACRUNCH_CLIENT_SECRET", "env_secret")

        with patch(
            "spotinfer.adapter.datacrunch_adapter.DataCrunchClient"
        ) as mock_client:
            adapter = DatacrunchAdapter()
            mock_client.assert_called_once_with("env_id", "env_secret")
            assert adapter.client_id == "env_id"
            assert adapter.client_secret == "env_secret"

    def test_init_without_credentials(self, monkeypatch):
        """Test adapter initialization without credentials raises error."""
        monkeypatch.delenv("DATACRUNCH_CLIENT_ID", raising=False)
        monkeypatch.delenv("DATACRUNCH_CLIENT_SECRET", raising=False)

        with pytest.raises(ValueError, match="Datacrunch credentials not found"):
            DatacrunchAdapter()

    def test_get_instance_types(self, mock_datacrunch_client, mock_instance_types):
        """Test getting all instance types."""
        mock_datacrunch_client.instance_types.get.return_value = mock_instance_types

        with patch(
            "spotinfer.adapter.datacrunch_adapter.DataCrunchClient",
            return_value=mock_datacrunch_client,
        ):
            adapter = DatacrunchAdapter("test_id", "test_secret")
            result = adapter.get_instance_types()

            assert result == mock_instance_types
            mock_datacrunch_client.instance_types.get.assert_called_once()

    def test_get_spot_instance_types(self, mock_datacrunch_client, mock_instance_types):
        """Test getting spot instance types."""
        mock_datacrunch_client.instance_types.get.return_value = mock_instance_types

        with patch(
            "spotinfer.adapter.datacrunch_adapter.DataCrunchClient",
            return_value=mock_datacrunch_client,
        ):
            adapter = DatacrunchAdapter("test_id", "test_secret")
            result = adapter.get_spot_instance_types()

            # Should return all instances since they all have spot pricing > 0
            assert len(result) == len(mock_instance_types)
            assert all(instance.spot_price_per_hour > 0 for instance in result)

    def test_filter_by_gpu_type(self, mock_datacrunch_client, mock_instance_types):
        """Test filtering instance types by GPU type."""
        mock_datacrunch_client.instance_types.get.return_value = mock_instance_types

        with patch(
            "spotinfer.adapter.datacrunch_adapter.DataCrunchClient",
            return_value=mock_datacrunch_client,
        ):
            adapter = DatacrunchAdapter("test_id", "test_secret")
            result = adapter.filter_by_gpu_type("A100")

            # Should return A100 instances
            assert len(result) == 2
            assert all("A100" in instance.gpu["description"] for instance in result)
            # Should be sorted by price
            assert result[0].price_per_hour <= result[1].price_per_hour

    def test_filter_by_gpu_type_case_insensitive(
        self, mock_datacrunch_client, mock_instance_types
    ):
        """Test filtering by GPU type is case insensitive."""
        mock_datacrunch_client.instance_types.get.return_value = mock_instance_types

        with patch(
            "spotinfer.adapter.datacrunch_adapter.DataCrunchClient",
            return_value=mock_datacrunch_client,
        ):
            adapter = DatacrunchAdapter("test_id", "test_secret")
            result = adapter.filter_by_gpu_type("a100")  # lowercase

            # Should return A100 instances
            assert len(result) == 2
            assert all("A100" in instance.gpu["description"] for instance in result)

    def test_filter_by_gpu_type_no_matches(
        self, mock_datacrunch_client, mock_instance_types
    ):
        """Test filtering by GPU type with no matches."""
        mock_datacrunch_client.instance_types.get.return_value = mock_instance_types

        with patch(
            "spotinfer.adapter.datacrunch_adapter.DataCrunchClient",
            return_value=mock_datacrunch_client,
        ):
            adapter = DatacrunchAdapter("test_id", "test_secret")
            result = adapter.filter_by_gpu_type("RTX4090")

            assert len(result) == 0

    def test_get_cheapest_offer_with_gpu_type(
        self, mock_datacrunch_client, mock_instance_types
    ):
        """Test getting cheapest offer filtered by GPU type."""
        mock_datacrunch_client.instance_types.get.return_value = mock_instance_types

        with patch(
            "spotinfer.adapter.datacrunch_adapter.DataCrunchClient",
            return_value=mock_datacrunch_client,
        ):
            adapter = DatacrunchAdapter("test_id", "test_secret")
            result = adapter.get_cheapest_offer(gpu_type="A100")

            assert result is not None
            assert "A100" in result.gpu["description"]
            assert result.price_per_hour == 0.72  # Cheapest A100

    def test_get_cheapest_offer_spot_pricing(
        self, mock_datacrunch_client, mock_instance_types
    ):
        """Test getting cheapest offer with spot pricing."""
        mock_datacrunch_client.instance_types.get.return_value = mock_instance_types

        with patch(
            "spotinfer.adapter.datacrunch_adapter.DataCrunchClient",
            return_value=mock_datacrunch_client,
        ):
            adapter = DatacrunchAdapter("test_id", "test_secret")
            result = adapter.get_cheapest_offer(spot=True)

            assert result is not None
            # Should be sorted by spot price
            assert result.spot_price_per_hour == 0.01  # Cheapest spot price

    def test_get_cheapest_offer_no_offers(self, mock_datacrunch_client):
        """Test getting cheapest offer when no offers available."""
        mock_datacrunch_client.instance_types.get.return_value = []

        with patch(
            "spotinfer.adapter.datacrunch_adapter.DataCrunchClient",
            return_value=mock_datacrunch_client,
        ):
            adapter = DatacrunchAdapter("test_id", "test_secret")
            result = adapter.get_cheapest_offer()

            assert result is None

    def test_get_available_gpu_types(self, mock_datacrunch_client, mock_instance_types):
        """Test getting available GPU types."""
        mock_datacrunch_client.instance_types.get.return_value = mock_instance_types

        with patch(
            "spotinfer.adapter.datacrunch_adapter.DataCrunchClient",
            return_value=mock_datacrunch_client,
        ):
            adapter = DatacrunchAdapter("test_id", "test_secret")
            result = adapter.get_available_gpu_types()

            expected_types = ["A100", "H100", "RTX A6000"]
            assert set(result) == set(expected_types)
            assert result == sorted(result)  # Should be sorted

    def test_get_available_gpu_types_no_gpus(self, mock_datacrunch_client):
        """Test getting available GPU types when no GPUs available."""
        cpu_only_instance = Mock()
        cpu_only_instance.gpu = {"description": "", "number_of_gpus": 0}
        mock_datacrunch_client.instance_types.get.return_value = [cpu_only_instance]

        with patch(
            "spotinfer.adapter.datacrunch_adapter.DataCrunchClient",
            return_value=mock_datacrunch_client,
        ):
            adapter = DatacrunchAdapter("test_id", "test_secret")
            result = adapter.get_available_gpu_types()

            assert result == []

    def test_get_available_gpu_types_regex_patterns(self, mock_datacrunch_client):
        """Test GPU type extraction with various regex patterns."""
        # Create instances with different GPU descriptions
        instances = []

        # B300 SXM6
        b300 = Mock()
        b300.gpu = {"description": "1x B300 SXM6 262GB", "number_of_gpus": 1}
        instances.append(b300)

        # B200 SXM6
        b200 = Mock()
        b200.gpu = {"description": "1x B200 SXM6 180GB", "number_of_gpus": 1}
        instances.append(b200)

        # H200 SXM5
        h200 = Mock()
        h200.gpu = {"description": "1x H200 SXM5 141GB", "number_of_gpus": 1}
        instances.append(h200)

        # H100 SXM5
        h100 = Mock()
        h100.gpu = {"description": "1x H100 SXM5 80GB", "number_of_gpus": 1}
        instances.append(h100)

        # RTX PRO 6000
        rtx_pro = Mock()
        rtx_pro.gpu = {"description": "1x RTX PRO 6000 96GB", "number_of_gpus": 1}
        instances.append(rtx_pro)

        # RTX 6000 Ada
        rtx_6000 = Mock()
        rtx_6000.gpu = {"description": "1x RTX 6000 Ada 48GB", "number_of_gpus": 1}
        instances.append(rtx_6000)

        # Tesla V100
        v100 = Mock()
        v100.gpu = {"description": "1x Tesla V100 16GB", "number_of_gpus": 1}
        instances.append(v100)

        # L40S
        l40s = Mock()
        l40s.gpu = {"description": "1x L40S 48GB", "number_of_gpus": 1}
        instances.append(l40s)

        mock_datacrunch_client.instance_types.get.return_value = instances

        with patch(
            "spotinfer.adapter.datacrunch_adapter.DataCrunchClient",
            return_value=mock_datacrunch_client,
        ):
            adapter = DatacrunchAdapter("test_id", "test_secret")
            result = adapter.get_available_gpu_types()

            expected_types = [
                "B200",
                "B300",
                "H100",
                "H200",
                "L40S",
                "RTX 6000",
                "RTX PRO",
                "Tesla V100",
            ]
            assert set(result) == set(expected_types)
            assert result == sorted(result)  # Should be sorted
