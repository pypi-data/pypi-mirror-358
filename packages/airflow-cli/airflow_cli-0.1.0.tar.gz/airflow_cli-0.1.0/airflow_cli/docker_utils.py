import subprocess
import logging
from glob import glob
import yaml

log = logging.getLogger(__name__)

def docker_up():
    log.info("🐳 Starting Docker environment...")
    subprocess.run(["docker", "compose", "up", "-d"], check=True)
    log.info("✅ Docker environment is ready.")

def docker_down():
    log.info("🐳 Stopping Docker environment...")
    subprocess.run(["docker", "compose", "down"], check=False)

def run_dag():
    log.info("🚀 Running DAG in Docker...")
    try:
        config = glob("dags/*/config.yml").pop()
        with open(config, "r") as file:
            config_data = yaml.safe_load(file)
            dag_id = config_data['args']["id"]

        subprocess.run([
            "docker", "exec", "-it", "airflow-worker-container",
            "airflow", "dags", "test", dag_id
        ], check=True)
        log.info(f"✅ DAG '{dag_id}' executed successfully.")
    except Exception as e:
        log.error(f"❌ Error running DAG: {e}")

def fix_python_code():
    log.info("🔧 Running flake8 on 'dags' folder...")
    try:
        subprocess.run(["flake8", "dags"], check=True)
        log.info("✅ Code checked with flake8.")
    except subprocess.CalledProcessError as e:
        log.error(f"❌ flake8 found issues: {e}")
