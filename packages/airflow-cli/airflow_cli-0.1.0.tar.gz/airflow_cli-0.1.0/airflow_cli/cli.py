import argparse
import logging
import sys

from .env_utils import ensure_venv, is_in_venv
from .os_utils import check_docker, check_os, update_docker_compose
from .docker_utils import docker_up, docker_down, run_dag, fix_python_code

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
log = logging.getLogger(__name__)

def main():
    parser = argparse.ArgumentParser(description="Airflow Docker Helper CLI")
    subparsers = parser.add_subparsers(dest="command")

    # Subcommand: up
    subparsers.add_parser("up", help="Start Docker environment")

    # Subcommand: down
    subparsers.add_parser("down", help="Stop Docker environment")

    # Subcommand: run-dag
    subparsers.add_parser("run-dag", help="Run Airflow DAG inside Docker")

    # Subcommand: fix-code
    subparsers.add_parser("fix-code", help="Run flake8 linter")

    args = parser.parse_args()

    # Pré-checks antes de qualquer comando
    ensure_venv()
    if not is_in_venv():
        log.warning("⚠️ Not running inside virtual environment. Interpreter: %s", sys.executable)



    if not check_docker():
        log.error("❌ Docker not ready.")
        sys.exit(1)

    check_os()
    update_docker_compose()

    # Execução dos comandos
    if args.command == "up":
        docker_up()
    elif args.command == "down":
        docker_down()
    elif args.command == "run-dag":
        run_dag()
    elif args.command == "fix-code":
        fix_python_code()
    else:
        parser.print_help()

