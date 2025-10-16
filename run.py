#!/usr/bin/env python
"""
Unified launcher for CodeRed: Engagement & Retention Intelligence Layer
Handles dependency checking, installation, and server startup
Works on freshly cloned repos
"""

import subprocess
import sys
import os
import time
import threading
import webbrowser
from pathlib import Path

# ANSI color codes for pretty output
GREEN = '\033[92m'
YELLOW = '\033[93m'
RED = '\033[91m'
BLUE = '\033[94m'
RESET = '\033[0m'

# Required packages (versions removed for Python 3.13 compatibility)
REQUIRED_PACKAGES = {
    # Core Backend Dependencies
    'fastapi': None,
    'uvicorn': None,
    'pydantic': None,

    # Machine Learning Dependencies
    'scikit-learn': None,
    'pandas': None,
    'numpy': None,
    'joblib': None,
    'matplotlib': None,
    'seaborn': None,

    # Dashboard Dependencies
    'streamlit': None,
    'plotly': None,
    'altair': None,

    # Data Generation
    'faker': None,

    # HTTP Client
    'httpx': None,
    'requests': None,

    # Date/Time Utilities
    'python-dateutil': None
}

def print_banner():
    """Print application banner"""
    banner = """
    ==============================================================

         CodeRed: Engagement & Retention Intelligence

         ML-Powered Platform for Dropout Prediction
         and Learner Engagement

    ==============================================================
    """
    print(f"{BLUE}{banner}{RESET}")

def check_python_version():
    """Ensure Python 3.8+ is being used"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print(f"{RED}X Python 3.8+ required. Current version: {sys.version}{RESET}")
        sys.exit(1)
    print(f"{GREEN}OK Python version: {sys.version.split()[0]}{RESET}")

def check_package(package_name):
    """Check if a package is installed"""
    try:
        # Special handling for scikit-learn
        if package_name == 'scikit-learn':
            __import__('sklearn')
        else:
            __import__(package_name.replace('-', '_'))
        return True
    except ImportError:
        return False

def install_packages():
    """Check and install required packages"""
    print(f"\n{YELLOW}[Packages] Checking dependencies...{RESET}")

    missing_packages = []
    for package in REQUIRED_PACKAGES.keys():
        if not check_package(package):
            missing_packages.append(package)

    if missing_packages:
        print(f"{YELLOW}Installing missing packages: {', '.join(missing_packages)}{RESET}")

        # Install using pip - skip version for packages that might have compatibility issues
        packages_to_install = []
        for pkg in missing_packages:
            ver = REQUIRED_PACKAGES[pkg]
            if ver and pkg != 'scikit-learn':  # Don't force version for scikit-learn on Python 3.13
                packages_to_install.append(f"{pkg}=={ver}")
            else:
                packages_to_install.append(pkg)

        # Install using pip
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "--quiet"] + packages_to_install)
            print(f"{GREEN}OK All dependencies installed successfully{RESET}")
        except subprocess.CalledProcessError as e:
            print(f"{RED}X Failed to install some packages{RESET}")
            print(f"{YELLOW}This might be due to Python 3.13 compatibility issues.{RESET}")
            print(f"{YELLOW}Trying to continue anyway...{RESET}")
            # Don't exit, try to continue
    else:
        print(f"{GREEN}OK All dependencies are already installed{RESET}")

def check_data_exists():
    """Check if training data exists"""
    data_path = Path("data/sample_learners.csv")
    return data_path.exists()

def generate_data():
    """Generate synthetic training data if needed"""
    if not check_data_exists():
        print(f"\n{YELLOW}[Data] Generating synthetic training data...{RESET}")
        try:
            # Ensure data directory exists
            Path("data").mkdir(exist_ok=True)

            # Run data generation script
            result = subprocess.run([sys.executable, "data/generate_data.py"],
                                  capture_output=True, text=True)

            if result.returncode == 0:
                print(f"{GREEN}OK Training data generated successfully{RESET}")
            else:
                print(f"{RED}X Failed to generate data: {result.stderr}{RESET}")
                # Continue anyway - dashboard can work without data
        except FileNotFoundError:
            print(f"{YELLOW}Warning: Data generation script not found, continuing...{RESET}")
        except Exception as e:
            print(f"{YELLOW}Warning: Could not generate data: {e}{RESET}")
    else:
        print(f"{GREEN}OK Training data already exists{RESET}")

def check_models_exist():
    """Check if ML models are trained"""
    model_path = Path("models/random_forest_model.pkl")
    return model_path.exists()

def train_models():
    """Train ML models if needed"""
    if not check_models_exist():
        print(f"\n{YELLOW}[ML] Training ML models...{RESET}")
        try:
            # Ensure models directory exists
            Path("models").mkdir(exist_ok=True)

            # Check if train script exists
            if Path("train_model.py").exists():
                result = subprocess.run([sys.executable, "train_model.py"],
                                      capture_output=True, text=True)

                if result.returncode == 0:
                    print(f"{GREEN}OK Models trained successfully{RESET}")
                    # Parse and display metrics if available
                    if "Accuracy" in result.stdout:
                        for line in result.stdout.split('\n'):
                            if "Accuracy" in line or "Recall" in line:
                                print(f"  {line.strip()}")
                else:
                    print(f"{YELLOW}Warning: Model training had issues, continuing...{RESET}")
            else:
                print(f"{YELLOW}Warning: Training script not found, using simulated predictions{RESET}")
        except Exception as e:
            print(f"{YELLOW}Warning: Could not train models: {e}{RESET}")
    else:
        print(f"{GREEN}OK Trained models already exist{RESET}")

def create_streamlit_config():
    """Create Streamlit configuration to avoid prompts"""
    config_dir = Path.home() / ".streamlit"
    config_dir.mkdir(exist_ok=True)

    config_file = config_dir / "config.toml"
    if not config_file.exists():
        config_content = """[browser]
gatherUsageStats = false

[server]
headless = true
port = 8501
"""
        config_file.write_text(config_content)
        print(f"{GREEN}OK Streamlit config created{RESET}")

def check_command_available(command):
    """Check if a command is available in PATH"""
    import shutil
    return shutil.which(command) is not None

def run_backend():
    """Run FastAPI backend server"""
    print(f"\n{BLUE}Starting FastAPI backend on port 8000...{RESET}")

    # Run in backend directory without changing the process directory
    backend_dir = Path("backend")

    # Check if uvicorn is directly available
    if check_command_available("uvicorn"):
        print(f"{GREEN}Using direct uvicorn command{RESET}")
        subprocess.run(["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"],
                      cwd=backend_dir)
    else:
        print(f"{YELLOW}Using python -m uvicorn{RESET}")
        subprocess.run([sys.executable, "-m", "uvicorn",
                       "app:app", "--host", "0.0.0.0", "--port", "8000"],
                      cwd=backend_dir)

def run_frontend():
    """Run Streamlit frontend"""
    print(f"\n{BLUE}Starting Streamlit dashboard on port 8501...{RESET}")

    # Check if streamlit is directly available
    if check_command_available("streamlit"):
        print(f"{GREEN}Using direct streamlit command{RESET}")
        subprocess.run(["streamlit", "run", "dashboard/app.py",
                       "--server.headless", "true", "--server.port", "8501"])
    else:
        print(f"{YELLOW}Using python -m streamlit{RESET}")
        subprocess.run([sys.executable, "-m", "streamlit", "run",
                       "dashboard/app.py", "--server.headless", "true",
                       "--server.port", "8501"])

def check_port_available(port):
    """Check if a port is available"""
    import socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.bind(('', port))
            return True
        except:
            return False

def check_path_setup():
    """Check if Python Scripts are in PATH and provide guidance"""
    import shutil

    streamlit_available = shutil.which("streamlit") is not None
    uvicorn_available = shutil.which("uvicorn") is not None

    if not streamlit_available or not uvicorn_available:
        print(f"\n{YELLOW}[PATH Info] Commands not directly available in PATH{RESET}")
        print(f"{YELLOW}Currently using 'python -m' to run commands.{RESET}")
        print(f"{YELLOW}To use commands directly, run: python setup_path.py{RESET}\n")
    else:
        print(f"{GREEN}[PATH OK] Commands available directly in PATH{RESET}")

def main():
    """Main execution function"""
    print_banner()

    # Step 1: Check Python version
    check_python_version()

    # Step 2: Check PATH setup (informational)
    check_path_setup()

    # Step 3: Install dependencies if needed
    install_packages()

    # Step 4: Generate data if needed
    generate_data()

    # Step 5: Train models if needed (optional)
    train_models()

    # Step 6: Create Streamlit config
    create_streamlit_config()

    # Step 7: Check port availability
    print(f"\n{YELLOW}[Check] Checking port availability...{RESET}")

    if not check_port_available(8000):
        print(f"{YELLOW}Warning: Port 8000 is already in use (FastAPI){RESET}")
    else:
        print(f"{GREEN}OK Port 8000 is available{RESET}")

    if not check_port_available(8501):
        print(f"{YELLOW}Warning: Port 8501 is already in use (Streamlit){RESET}")
    else:
        print(f"{GREEN}OK Port 8501 is available{RESET}")

    # Step 8: Start servers
    print(f"\n{GREEN}{'='*60}{RESET}")
    print(f"{GREEN}[Launch] Starting servers...{RESET}")
    print(f"{GREEN}{'='*60}{RESET}")

    print(f"""
{YELLOW}The application will be available at:{RESET}

  [Data] Dashboard (Streamlit):  {BLUE}http://localhost:8501{RESET}
  [API] API Documentation:      {BLUE}http://localhost:8000/docs{RESET}

{YELLOW}Press Ctrl+C to stop all servers{RESET}
    """)

    # Create threads for both servers
    backend_thread = threading.Thread(target=run_backend, daemon=True)
    frontend_thread = threading.Thread(target=run_frontend, daemon=True)

    # Start backend first
    backend_thread.start()
    time.sleep(3)  # Give backend time to start

    # Start frontend
    frontend_thread.start()
    time.sleep(5)  # Give frontend time to start

    # Open browser automatically
    try:
        print(f"\n{GREEN}[Browser] Opening dashboard in browser...{RESET}")
        webbrowser.open('http://localhost:8501')
    except:
        print(f"{YELLOW}Please open your browser to http://localhost:8501{RESET}")

    # Keep main thread alive
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print(f"\n{RED}[Stop] Shutting down servers...{RESET}")
        print(f"{GREEN}OK Application stopped successfully{RESET}")
        sys.exit(0)

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"{RED}X An error occurred: {e}{RESET}")
        sys.exit(1)