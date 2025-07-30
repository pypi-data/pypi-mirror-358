import importlib
import subprocess
import sys
import os
import glob

def ensure_package(pkg_name, pip_name=None):
    """Ensure a package is installed, install it if missing."""
    try:
        importlib.import_module(pkg_name)
        print(f"✓ Package '{pkg_name}' is already installed")
    except ImportError:
        print(f"📦 Package '{pkg_name}' not found. Installing...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", pip_name or pkg_name])
            print(f"✓ Successfully installed '{pkg_name}'")
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install '{pkg_name}': {e}")
            raise

def ensure_embedding_dependencies():
    """Ensure all required embedding packages are installed."""
    print("🔍 Checking embedding dependencies...")
    
    # Core embedding packages
    ensure_package("transformers")
    ensure_package("sentence_transformers", "sentence-transformers")
    ensure_package("tokenizers")
    ensure_package("torch")
    
    print("✅ All embedding dependencies are ready!")

def ensure_api_dependencies():
    """Ensure all required API packages are installed."""
    print("🔍 Checking API dependencies...")
    
    # API packages
    ensure_package("fastapi")
    ensure_package("uvicorn")
    ensure_package("python_dotenv", "python-dotenv")
    ensure_package("pydantic")
    ensure_package("openai-agents")
    
    print("✅ All API dependencies are ready!")

def setup_environment():
    """Set up the environment by cleaning up and ensuring dependencies."""
    ensure_embedding_dependencies()
    ensure_api_dependencies()

if __name__ == "__main__":
    setup_environment()