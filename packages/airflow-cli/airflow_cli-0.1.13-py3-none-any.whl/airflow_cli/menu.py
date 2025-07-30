import logging
from simple_term_menu import TerminalMenu
from .docker_utils import docker_up, docker_down, run_dag, fix_python_code

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
