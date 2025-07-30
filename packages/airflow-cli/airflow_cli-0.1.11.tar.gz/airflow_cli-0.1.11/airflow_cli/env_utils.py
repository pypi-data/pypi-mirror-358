import os
import subprocess
import sys
import importlib.util
import logging

log = logging.getLogger(__name__)

venv_dir = ".venv"

def is_in_venv():
    return os.path.abspath(sys.prefix).endswith(os.path.abspath(venv_dir))

def ensure_venv():
    if not os.path.exists(venv_dir):
        log.info(f"🔄 Creating Python virtual environment at {venv_dir}...")
        try:
            subprocess.check_call([sys.executable, "-m", "venv", venv_dir])
            log.info("✅ Virtual environment created.")
        except subprocess.CalledProcessError as e:
            log.error(f"❌ Error creating venv: {e}")
            return False
    return True

def install_package_if_missing(packages):
    for package in packages:
        if importlib.util.find_spec(package) is None:
            log.info(f"📦 Installing missing package '{package}'...")
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install", package])
            except subprocess.CalledProcessError as e:
                log.error(f"❌ Failed to install '{package}': {e}")
                sys.exit(1)
