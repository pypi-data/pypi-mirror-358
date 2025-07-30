# Conventions

A CLI tool to search for conference talks.

## Installation

```bash
# Install from PyPI
pip install conventions

# Or install from source
git clone https://github.com/hwranderson/conventions.git
cd conventions
pip install -e .
```

## Usage

Search for talks by keyword:

```bash
# Search for SLAM talks in ICRA 2025 (default)
python -m conventions search slam

# Search in a specific conference
python -m conventions search navigation --conference ICRA25

# Limit results
python -m conventions search robotics --max-results 10
```

List available conferences:

```bash
python -m conventions list
```

Get information about a specific conference:

```bash
python -m conventions info ICRA25
```

Clear the cache:

```bash
# Clear cache for a specific conference
python -m conventions clear-cache ICRA25

# Clear all cached data
python -m conventions clear-cache --all
```

## Supported Conferences

- ICRA25 (IEEE International Conference on Robotics and Automation 2025)

## Development

```bash
# Clone the repository
git clone https://github.com/hwranderson/conventions.git
cd conventions

# Install in development mode
pip install -e .

# Run the CLI
python -m conventions search slam
```
