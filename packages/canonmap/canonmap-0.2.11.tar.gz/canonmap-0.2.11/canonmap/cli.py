import os
import sys
from pathlib import Path

def create_api():
    base_path = Path.cwd() / "app"
    structure = {
        "context/context_helpers": ["__init__.py", "get_canonmap_helper.py"],
        "context": ["__init__.py", "context.py"],
        "utils": ["__init__.py", "_ensure_embedding_deps.py", "logger.py"],
        "": ["__init__.py", "main.py"],
    }

    for folder, files in structure.items():
        full_dir = base_path / folder
        full_dir.mkdir(parents=True, exist_ok=True)
        for file in files:
            file_path = full_dir / file
            if not file_path.exists():
                file_path.touch()
                print(f"✅ Created {file_path}")

def main():
    if len(sys.argv) > 1 and sys.argv[1] == "create-api":
        create_api()
    else:
        print("Usage: cm create-api")
