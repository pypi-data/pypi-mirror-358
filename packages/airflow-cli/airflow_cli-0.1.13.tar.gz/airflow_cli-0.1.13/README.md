# Airflow Docker Helper

A command-line tool to facilitate the setup of Apache Airflow using Docker and enable local DAG development and testing.

## Features

- 🚀 Quick Airflow setup with Docker Compose
- 🔧 Local DAG development and testing
- 📦 Pre-configured Docker environment
- 🛠️ CLI interface for common Airflow operations
- 🧪 Testing utilities for DAG validation

## Prerequisites

- Python 3.7+
- Docker and Docker Compose
- Git

## Installation

### From PyPI (Recommended)

```bash
pip install airflow-cli
```


## Quick Start

### 1. Start Airflow Environment

```bash
airflow-cli up
```

This command will:
- Check Docker installation and environment
- Download the latest docker-compose.yml from LEMA UFPB repository
- Start Airflow services with Docker Compose

### 2. Access Airflow UI

Open your browser and navigate to http://localhost:8080

Default credentials:
- Username: `airflow`
- Password: `airflow`

### 3. Stop Airflow Environment

```bash
airflow-cli down
```

## Usage

### Available Commands

```bash
# Start Docker environment
airflow-cli up

# Stop Docker environment  
airflow-cli down

# Run Airflow DAG inside Docker
airflow-cli run-dag

# Run flake8 linter on DAGs
airflow-cli fix-code

# Show help
airflow-cli --help
```

### DAG Development

1. Place your DAG files in the `dags/` directory
2. The directory is automatically mounted to the Airflow container
3. Changes are reflected immediately (no restart required)

Expected DAG structure for `run-dag` command:
```
project/
├── dags/
│   └── my_dag/
│       ├── config.yml
│       └── dag.py

```

Example `config.yml`:
```yaml
args:
  id: "my_dag_id"
```

### Testing DAGs

#### Run a DAG inside Docker
```bash
airflow-cli run-dag
```

This command will:
- Look for DAG configuration files in `dags/*/config.yml`
- Execute the DAG inside the running Airflow container

#### Validate DAG syntax with flake8
```bash
airflow-cli fix-code
```

This will run flake8 linter on the `dags/` folder to check for Python syntax issues.

### Building from Source

```bash
# Build wheel
python -m build

# Install built package
pip install dist/airflow_cli-*.whl
```

## Publishing to PyPI
```bash
# Build wheel
python -m build
# Publish to PyPI
twine upload dist/*
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.


---

Made with ❤️ by the LEMA UFPB team
