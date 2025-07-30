import subprocess
import logging
from glob import glob
import yaml
import os

log = logging.getLogger(__name__)

def docker_up():
    log.info("🐳 Starting Docker environment...")
    env = os.environ.copy()
    env["AIRFLOW_UID"] = "50000"
    
    compose_file = os.path.join(os.path.dirname(__file__), "docker-compose.yml")
    subprocess.run(["docker", "compose", "-f", compose_file, "up", "-d"], env=env, check=True)
    log.info("✅ Docker environment is ready: http://localhost:8080")

def docker_down():
    log.info("🐳 Stopping Docker environment...")
    compose_file = os.path.join(os.path.dirname(__file__), "docker-compose.yml")
    subprocess.run(["docker", "compose", "-f", compose_file, "down"], check=False)

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
