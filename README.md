# SpotInfer

A Python package for running local notebooks and scripts on remote Datacrunch GPU instances with minimal friction and strong reliability.

## Overview

SpotInfer provides a simple CLI and Python API to discover, provision, and manage Datacrunch GPU instances for machine learning workloads. It handles the complexity of instance selection, pricing optimization, and execution orchestration while providing a clean interface for developers.

## Features

- **Instance Discovery**: Find available GPU instances with real-time pricing
- **Smart Selection**: Filter by GPU type, spot/on-demand pricing, and cost constraints
- **Interactive Mode**: Guided setup for instance selection and configuration
- **Cost Optimization**: Prefer spot instances with automatic fallback to on-demand
- **Rich CLI**: Beautiful terminal output with tables and progress indicators

## Quick Start

### 1. Set up credentials

```bash
export DATACRUNCH_CLIENT_ID="your_client_id"
export DATACRUNCH_CLIENT_SECRET="your_client_secret"
```

### 2. List available offers

```bash
# Show all available instances
spotinfer offers list

# Filter by GPU type
spotinfer offers list --gpu-type A100

# Show only spot pricing
spotinfer offers list --spot

# Show cheapest option
spotinfer offers list --cheapest
```

### 3. Interactive mode

```bash
# Guided instance selection
spotinfer interactive run
```

### 4. Python API

```python
from spotinfer import list_offers

# Get all offers
offers = list_offers()

# Filter by GPU type
a100_offers = list_offers(gpu_type="A100")

# Get cheapest spot instance
cheapest = list_offers(spot_only=True, cheapest_only=True)
```

## CLI Commands

### Offers

```bash
# List all available instances
spotinfer offers list

# Filter options
spotinfer offers list --gpu-type H100 --spot --limit 5

# Show available GPU types
spotinfer offers gpu-types
```

### Interactive

```bash
# Run interactive guided setup
spotinfer interactive run

# Options
spotinfer interactive run --client-id ID --client-secret SECRET
```

## Configuration

### Environment Variables

- `DATACRUNCH_CLIENT_ID`: Your Datacrunch client ID
- `DATACRUNCH_CLIENT_SECRET`: Your Datacrunch client secret

### CLI Options

- `--gpu-type`: Filter by GPU type (case-insensitive)
- `--spot`: Show spot pricing only
- `--cheapest`: Show only the cheapest offer
- `--limit`: Limit number of results
- `--client-id`: Override client ID
- `--client-secret`: Override client secret

## Development

### Setup

```bash
# Clone repository
git clone https://github.com/your-username/spotinfer.git
cd spotinfer

# Install dependencies
poetry install

# Install pre-commit hooks
pre-commit install
```

### Testing

```bash
# Run tests
pytest

# Run with coverage
pytest --cov=spotinfer

# Run specific test file
pytest tests/test_adapter.py
```

### Project Structure

```
spotinfer/
├── src/spotinfer/
│   ├── adapter/          # Datacrunch API adapter
│   ├── cli/              # CLI commands
│   ├── prepare/          # Instance selection logic
│   └── main.py           # Main CLI entry point
├── tests/                # Test suite
├── docs/                 # Documentation
└── pyproject.toml        # Project configuration
```

## Architecture

SpotInfer follows a modular architecture:

- **Adapter Layer**: Handles Datacrunch API interactions
- **Service Layer**: Business logic for instance selection and filtering
- **CLI Layer**: User interface and command handling
- **Core Logic**: Focused on instance discovery, pricing, and selection

## Testing Strategy

The project maintains a focused test suite covering core business logic:

- **Unit Tests**: Adapter and service layer logic
- **Mock-based Testing**: Isolated testing without external API calls
- **Logic-focused**: Tests concentrate on business rules rather than CLI/API integration

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Run the test suite
6. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Roadmap

- [ ] Instance provisioning and execution
- [ ] Volume management and persistence
- [ ] Artifact collection and download

## Support

For questions, issues, or contributions, please:

1. Check the [documentation](docs/)
2. Search existing [issues](https://github.com/your-username/spotinfer/issues)
3. Create a new issue if needed
