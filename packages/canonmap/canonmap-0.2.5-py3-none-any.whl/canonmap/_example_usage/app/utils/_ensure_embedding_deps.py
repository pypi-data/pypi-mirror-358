import importlib
import subprocess
import sys

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

if __name__ == "__main__":
    ensure_embedding_dependencies()