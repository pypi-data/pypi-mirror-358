import importlib
import subprocess
import sys
import os
import glob
import shutil

def cleanup_init_files():
    """Remove all __init__.py files from the app/ directory."""
    print("🧹 Cleaning up __init__.py files...")
    
    # Get the app directory (assuming this script is in app/utils/)
    app_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    
    # Find all __init__.py files in app/ and subdirectories
    init_files = glob.glob(os.path.join(app_dir, "**", "__init__.py"), recursive=True)
    
    if not init_files:
        print("✓ No __init__.py files found to clean up")
        return
    
    deleted_count = 0
    for init_file in init_files:
        try:
            os.remove(init_file)
            print(f"🗑️  Deleted: {os.path.relpath(init_file, app_dir)}")
            deleted_count += 1
        except OSError as e:
            print(f"⚠️  Could not delete {init_file}: {e}")
    
    print(f"✅ Cleaned up {deleted_count} __init__.py files")

def cleanup_pycache():
    """Remove all __pycache__ directories and .pyc files from the app/ directory."""
    print("🧹 Cleaning up __pycache__ directories and .pyc files...")
    
    # Get the app directory (assuming this script is in app/utils/)
    app_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    
    # Find all __pycache__ directories
    pycache_dirs = glob.glob(os.path.join(app_dir, "**", "__pycache__"), recursive=True)
    
    # Find all .pyc files
    pyc_files = glob.glob(os.path.join(app_dir, "**", "*.pyc"), recursive=True)
    
    # Find all .pyo files (optimized bytecode)
    pyo_files = glob.glob(os.path.join(app_dir, "**", "*.pyo"), recursive=True)
    
    deleted_dirs = 0
    deleted_files = 0
    
    # Delete __pycache__ directories
    for pycache_dir in pycache_dirs:
        try:
            shutil.rmtree(pycache_dir)
            print(f"🗑️  Deleted directory: {os.path.relpath(pycache_dir, app_dir)}")
            deleted_dirs += 1
        except OSError as e:
            print(f"⚠️  Could not delete {pycache_dir}: {e}")
    
    # Delete .pyc files
    for pyc_file in pyc_files:
        try:
            os.remove(pyc_file)
            print(f"🗑️  Deleted: {os.path.relpath(pyc_file, app_dir)}")
            deleted_files += 1
        except OSError as e:
            print(f"⚠️  Could not delete {pyc_file}: {e}")
    
    # Delete .pyo files
    for pyo_file in pyo_files:
        try:
            os.remove(pyo_file)
            print(f"🗑️  Deleted: {os.path.relpath(pyo_file, app_dir)}")
            deleted_files += 1
        except OSError as e:
            print(f"⚠️  Could not delete {pyo_file}: {e}")
    
    if deleted_dirs == 0 and deleted_files == 0:
        print("✓ No __pycache__ directories or .pyc files found to clean up")
    else:
        print(f"✅ Cleaned up {deleted_dirs} __pycache__ directories and {deleted_files} .pyc/.pyo files")

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

def setup_environment():
    """Set up the environment by cleaning up and ensuring dependencies."""
    cleanup_init_files()
    cleanup_pycache()
    ensure_embedding_dependencies()

if __name__ == "__main__":
    setup_environment()