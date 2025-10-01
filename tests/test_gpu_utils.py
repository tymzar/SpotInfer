"""
Tests for the GPU utility module.
"""

from unittest.mock import Mock

from spotinfer.utils.gpu import extract_gpu_type, format_gpu_display, get_available_gpu_types_from_instances


class TestExtractGpuType:
    """Test cases for extract_gpu_type function."""

    def test_extract_b300(self):
        """Test extracting B300 GPU type."""
        description = "1x B300 SXM6 262GB"
        result = extract_gpu_type(description)
        assert result == "B300"

    def test_extract_b200(self):
        """Test extracting B200 GPU type."""
        description = "1x B200 SXM6 180GB"
        result = extract_gpu_type(description)
        assert result == "B200"

    def test_extract_h200(self):
        """Test extracting H200 GPU type."""
        description = "1x H200 SXM5 141GB"
        result = extract_gpu_type(description)
        assert result == "H200"

    def test_extract_h100(self):
        """Test extracting H100 GPU type."""
        description = "1x H100 SXM5 80GB"
        result = extract_gpu_type(description)
        assert result == "H100"

    def test_extract_a100(self):
        """Test extracting A100 GPU type."""
        description = "1x A100 SXM4 40GB"
        result = extract_gpu_type(description)
        assert result == "A100"

    def test_extract_rtx_pro(self):
        """Test extracting RTX PRO GPU type."""
        description = "1x RTX PRO 6000 96GB"
        result = extract_gpu_type(description)
        assert result == "RTX PRO"

    def test_extract_rtx_6000_ada(self):
        """Test extracting RTX 6000 Ada GPU type."""
        description = "1x RTX 6000 Ada 48GB"
        result = extract_gpu_type(description)
        assert result == "RTX 6000"

    def test_extract_rtx_a6000(self):
        """Test extracting RTX A6000 GPU type."""
        description = "1x RTX A6000 48GB"
        result = extract_gpu_type(description)
        assert result == "RTX A6000"

    def test_extract_tesla_v100(self):
        """Test extracting Tesla V100 GPU type."""
        description = "1x Tesla V100 16GB"
        result = extract_gpu_type(description)
        assert result == "Tesla V100"

    def test_extract_l40s(self):
        """Test extracting L40S GPU type."""
        description = "1x L40S 48GB"
        result = extract_gpu_type(description)
        assert result == "L40S"

    def test_extract_unknown_gpu(self):
        """Test extracting unknown GPU type returns None."""
        description = "1x Unknown GPU 16GB"
        result = extract_gpu_type(description)
        assert result is None

    def test_extract_empty_description(self):
        """Test extracting from empty description returns None."""
        result = extract_gpu_type("")
        assert result is None

    def test_extract_none_description(self):
        """Test extracting from None description returns None."""
        result = extract_gpu_type(None)
        assert result is None


class TestFormatGpuDisplay:
    """Test cases for format_gpu_display function."""

    def test_format_single_gpu(self):
        """Test formatting single GPU display."""
        description = "1x B300 SXM6 262GB"
        count = 1
        result = format_gpu_display(description, count)
        assert result == "B300"

    def test_format_multiple_gpus(self):
        """Test formatting multiple GPU display."""
        description = "2x H100 SXM5 80GB"
        count = 2
        result = format_gpu_display(description, count)
        assert result == "2xH100"

    def test_format_cpu_only(self):
        """Test formatting CPU-only display."""
        description = ""
        count = 0
        result = format_gpu_display(description, count)
        assert result == "CPU Only"

    def test_format_unknown_gpu(self):
        """Test formatting unknown GPU display."""
        description = "1x Unknown GPU 16GB"
        count = 1
        result = format_gpu_display(description, count)
        assert result == "Unknown"

    def test_format_empty_description_with_gpu_count(self):
        """Test formatting empty description with GPU count."""
        description = ""
        count = 1
        result = format_gpu_display(description, count)
        assert result == "CPU Only"


class TestGetAvailableGpuTypesFromInstances:
    """Test cases for get_available_gpu_types_from_instances function."""

    def test_get_gpu_types_from_instances(self):
        """Test getting GPU types from instance list."""
        # Create mock instances
        instances = []

        # B300 instance
        b300 = Mock()
        b300.gpu = {"description": "1x B300 SXM6 262GB", "number_of_gpus": 1}
        instances.append(b300)

        # H100 instance
        h100 = Mock()
        h100.gpu = {"description": "1x H100 SXM5 80GB", "number_of_gpus": 1}
        instances.append(h100)

        # A100 instance
        a100 = Mock()
        a100.gpu = {"description": "1x A100 SXM4 40GB", "number_of_gpus": 1}
        instances.append(a100)

        # CPU-only instance (should be ignored)
        cpu_only = Mock()
        cpu_only.gpu = {"description": "", "number_of_gpus": 0}
        instances.append(cpu_only)

        result = get_available_gpu_types_from_instances(instances)

        expected_types = ["A100", "B300", "H100"]
        assert set(result) == set(expected_types)
        assert result == sorted(result)  # Should be sorted

    def test_get_gpu_types_no_gpus(self):
        """Test getting GPU types when no GPUs available."""
        instances = []

        # CPU-only instance
        cpu_only = Mock()
        cpu_only.gpu = {"description": "", "number_of_gpus": 0}
        instances.append(cpu_only)

        result = get_available_gpu_types_from_instances(instances)
        assert result == []

    def test_get_gpu_types_empty_list(self):
        """Test getting GPU types from empty instance list."""
        result = get_available_gpu_types_from_instances([])
        assert result == []

    def test_get_gpu_types_duplicate_types(self):
        """Test getting GPU types with duplicate types (should be unique)."""
        instances = []

        # Two A100 instances
        a100_1 = Mock()
        a100_1.gpu = {"description": "1x A100 SXM4 40GB", "number_of_gpus": 1}
        instances.append(a100_1)

        a100_2 = Mock()
        a100_2.gpu = {"description": "2x A100 SXM4 40GB", "number_of_gpus": 2}
        instances.append(a100_2)

        result = get_available_gpu_types_from_instances(instances)
        assert result == ["A100"]  # Should be unique and sorted
