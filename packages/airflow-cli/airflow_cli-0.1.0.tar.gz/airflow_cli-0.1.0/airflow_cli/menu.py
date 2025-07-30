import logging
import sys
from simple_term_menu import TerminalMenu
from .docker_utils import docker_up, docker_down, run_dag, fix_python_code
from .env_utils import ensure_venv, is_in_venv
from .os_utils import check_os, update_docker_compose, check_docker

log = logging.getLogger(__name__)

def show_menu():
    options = [
        "🐳 Docker Environment Up",
        "🚀 Run DAG on Terminal",
        "🐳 Docker Environment Down",
        "🔧 Fix Python Code",
        "🚪 Exit"
    ]
    menu = TerminalMenu(options, title="🎛️ Choose an option:")
    choice = menu.show()
    return options[choice] if choice is not None else None



def run():
    ensure_venv()
    if not is_in_venv():
        log.warning("⚠️ Not running inside the virtual environment.")
        log.warning(f"Interpreter: {sys.executable}")



    if not check_docker():
        log.error("❌ Docker is not ready.")
        return

    check_os()
    update_docker_compose()

    while True:
        option = show_menu()
        if option == "🐳 Docker Environment Up":
            docker_up()
        elif option == "🚀 Run DAG on Terminal":
            run_dag()
        elif option == "🐳 Docker Environment Down":
            docker_down()
        elif option == "🔧 Fix Python Code":
            fix_python_code()
        elif option == "🚪 Exit" or option is None:
            log.info("👋 Exiting...")
            break
