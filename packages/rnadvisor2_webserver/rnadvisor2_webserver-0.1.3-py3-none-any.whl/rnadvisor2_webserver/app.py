import subprocess
import os
import sys

def run():
    base_dir = os.path.dirname(__file__)
    app_path = os.path.join(base_dir, "Home.py")

    command = [
        sys.executable, "-m", "streamlit", "run", app_path,
        "--server.port=8501",
        "--server.address=0.0.0.0",
        "--server.baseUrlPath=/RNAdvisor",
    ]

    subprocess.run(command)