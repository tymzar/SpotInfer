"""
Test configuration and fixtures for SpotInfer tests.
"""

from unittest.mock import Mock

import pytest
from datacrunch.instance_types.instance_types import InstanceType


@pytest.fixture
def mock_instance_type():
    """Create a mock InstanceType object."""
    instance = Mock(spec=InstanceType)
    instance.instance_type = "1A100.40S.22V"
    instance.price_per_hour = 0.72
    instance.spot_price_per_hour = 0.26
    instance.gpu = {"description": "1x A100 SXM4 40GB", "number_of_gpus": 1}
    instance.cpu = {"number_of_cores": 22}
    instance.memory = {"size_in_gigabytes": 120}
    instance.gpu_memory = {"size_in_gigabytes": 40}
    return instance


@pytest.fixture
def mock_instance_types():
    """Create a list of mock InstanceType objects."""
    instances = []

    # A100 instances
    a100_40gb = Mock(spec=InstanceType)
    a100_40gb.instance_type = "1A100.40S.22V"
    a100_40gb.price_per_hour = 0.72
    a100_40gb.spot_price_per_hour = 0.26
    a100_40gb.gpu = {"description": "1x A100 SXM4 40GB", "number_of_gpus": 1}
    a100_40gb.cpu = {"number_of_cores": 22}
    a100_40gb.memory = {"size_in_gigabytes": 120}
    a100_40gb.gpu_memory = {"size_in_gigabytes": 40}
    instances.append(a100_40gb)

    a100_80gb = Mock(spec=InstanceType)
    a100_80gb.instance_type = "1A100.22V"
    a100_80gb.price_per_hour = 1.16
    a100_80gb.spot_price_per_hour = 0.63
    a100_80gb.gpu = {"description": "1x A100 SXM4 80GB", "number_of_gpus": 1}
    a100_80gb.cpu = {"number_of_cores": 22}
    a100_80gb.memory = {"size_in_gigabytes": 120}
    a100_80gb.gpu_memory = {"size_in_gigabytes": 80}
    instances.append(a100_80gb)

    # H100 instance
    h100 = Mock(spec=InstanceType)
    h100.instance_type = "1H100.80S.30V"
    h100.price_per_hour = 1.99
    h100.spot_price_per_hour = 0.98
    h100.gpu = {"description": "1x H100 SXM5 80GB", "number_of_gpus": 1}
    h100.cpu = {"number_of_cores": 30}
    h100.memory = {"size_in_gigabytes": 120}
    h100.gpu_memory = {"size_in_gigabytes": 80}
    instances.append(h100)

    # RTX A6000 instance
    rtx_a6000 = Mock(spec=InstanceType)
    rtx_a6000.instance_type = "1A6000.10V"
    rtx_a6000.price_per_hour = 0.47
    rtx_a6000.spot_price_per_hour = 0.13
    rtx_a6000.gpu = {"description": "1x RTX A6000 48GB", "number_of_gpus": 1}
    rtx_a6000.cpu = {"number_of_cores": 10}
    rtx_a6000.memory = {"size_in_gigabytes": 60}
    rtx_a6000.gpu_memory = {"size_in_gigabytes": 48}
    instances.append(rtx_a6000)

    # CPU-only instance
    cpu_only = Mock(spec=InstanceType)
    cpu_only.instance_type = "CPU.4V.16G"
    cpu_only.price_per_hour = 0.03
    cpu_only.spot_price_per_hour = 0.01
    cpu_only.gpu = {"description": "", "number_of_gpus": 0}
    cpu_only.cpu = {"number_of_cores": 4}
    cpu_only.memory = {"size_in_gigabytes": 16}
    cpu_only.gpu_memory = {"size_in_gigabytes": 0}
    instances.append(cpu_only)

    return instances


@pytest.fixture
def mock_datacrunch_client():
    """Create a mock Datacrunch client."""
    client = Mock()
    client.instance_types = Mock()
    client.instance_types.get.return_value = []
    return client


@pytest.fixture
def mock_console():
    """Create a mock Rich console."""
    console = Mock()
    console.print = Mock()
    return console
