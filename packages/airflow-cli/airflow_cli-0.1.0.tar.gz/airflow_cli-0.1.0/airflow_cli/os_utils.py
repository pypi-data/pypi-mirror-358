import platform
import logging
import subprocess
import os
import shutil
import pkg_resources

log = logging.getLogger(__name__)

def check_os():
    system = platform.system()
    if system == "Linux":
        try:
            with open("/proc/version", "r") as f:
                if "microsoft" in f.read().lower():
                    log.info("✅ Running on WSL (Linux under Windows).")
                else:
                    log.info("✅ Running on native Linux.")
        except FileNotFoundError:
            log.info("✅ Running on Linux.")
    elif system == "Darwin":
        log.info("✅ Running on MacOS.")
    else:
        log.error(f"❌ Unsupported OS: {system}")

def check_docker():
    try:
        subprocess.check_output(["docker", "--version"])
        subprocess.check_output(["docker", "info"])
        log.info("✅ Docker is installed and running.")
        return True
    except Exception as e:
        log.error(f"❌ Docker check failed: {e}")
        return False

def update_docker_compose():
    """Copy docker-compose.yml from package to current directory if it doesn't exist"""
    if not os.path.exists("docker-compose.yml"):
        try:
            # Get the docker-compose.yml from the package
            source = pkg_resources.resource_filename('airflow_docker', 'docker-compose.yml')
            shutil.copy2(source, "docker-compose.yml")
            log.info("✅ docker-compose.yml copied to current directory.")
        except Exception as e:
            log.error(f"❌ Failed to copy docker-compose.yml: {e}")
    else:
        log.info("✅ docker-compose.yml already exists.")
