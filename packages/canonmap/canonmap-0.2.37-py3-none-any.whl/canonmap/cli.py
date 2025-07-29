from codename.codename import codename
import shutil
from pathlib import Path
import sys
import re

from canonmap._example_usage.setup_api_environment import setup_environment

def create_api():
    # Determine name from --name flag or codename fallback
    cli_args = sys.argv[2:]  # Skip "create-api"
    app_name = None
    if "--name" in cli_args:
        try:
            app_name = cli_args[cli_args.index("--name") + 1]
        except IndexError:
            print("❌ You must provide a name after --name")
            sys.exit(1)

    app_name = app_name or f"{codename(separator='_')}_api"
    target = Path.cwd() / app_name

    # Find the installed _example_usage/app path
    source = Path(__file__).parent / "_example_usage" / "cm_api"
    print(f"📁 Creating new API project at: {target}")

    if not source.exists():
        print(f"❌ Template not found at {source}")
        return

    for src_path in source.rglob("*"):
        rel_path = src_path.relative_to(source)
        dst_path = target / rel_path

        # Skip __pycache__ directories and __init__.py files
        if "__pycache__" in src_path.parts or src_path.name == "__init__.py":
            continue

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

    print("🎉 API project created successfully!")
    print("🚀 Run one of the following commands to start the API:")
    print(f"    \033[1;36muvicorn {target.name}.main:app\033[0m")
    print("    \033[1;33mor\033[0m")
    print(f"    \033[1;36muvicorn {target.name}.main:app --reload\033[0m\n")

    # Update imports throughout copied files
    print("🛠️  Updating local imports to use generated name...")
    for file in target.rglob("*.py"):
        content = file.read_text()
        # Replace outdated import paths with the new target module
        updated = re.sub(
            r"(from|import) canonmap\\._example_usage\\.cm_api(\\.|(?=\\s))",
            rf"\1 {target.name}\2",
            content
        )
        updated = updated.replace("from cm_api.", f"from {target.name}.").replace("import cm_api.", f"import {target.name}.")
        file.write_text(updated)

def main():
    if len(sys.argv) > 1 and sys.argv[1] == "create-api":
        create_api()
    else:
        print("Usage: cm create-api [--name my_api_name]")