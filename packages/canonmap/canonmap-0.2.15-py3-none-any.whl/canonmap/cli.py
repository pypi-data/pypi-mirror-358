import shutil
from pathlib import Path
import sys

from canonmap._example_usage.setup_api_environment import setup_environment

def create_api():
    # Find the installed _example_usage/app path
    source = Path(__file__).parent / "_example_usage" / "app"
    target = Path.cwd() / "app"

    if not source.exists():
        print(f"❌ Template not found at {source}")
        return

    for src_path in source.rglob("*"):
        rel_path = src_path.relative_to(source)
        dst_path = target / rel_path

        if src_path.is_dir():
            dst_path.mkdir(parents=True, exist_ok=True)
        else:
            dst_path.parent.mkdir(parents=True, exist_ok=True)
            if not dst_path.exists():
                shutil.copy2(src_path, dst_path)
                print(f"✅ Copied {dst_path}")
            else:
                print(f"⚠️ Skipped existing file: {dst_path}")

    print("🧩 Running setup environment tasks...")
    setup_environment()

def main():
    if len(sys.argv) > 1 and sys.argv[1] == "create-api":
        create_api()
    else:
        print("Usage: cm create-api")