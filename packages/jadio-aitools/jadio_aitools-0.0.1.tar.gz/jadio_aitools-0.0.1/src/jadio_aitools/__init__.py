# src/jadio_aitools/__init__.py
__version__ = "0.0.1"

def install_hook(project_path):
    """Copies all tools into user project's jadio_aitools/ folder."""
    from pathlib import Path
    import shutil

    src = Path(__file__).parent / "tools"
    dest = Path(project_path) / "jadio_aitools"
    dest.mkdir(exist_ok=True)

    for file in src.glob("*.py"):
        shutil.copy2(file, dest / file.name)

def uninstall_hook(project_path):
    """Removes jadio_aitools folder from user project on uninstall."""
    from pathlib import Path
    import shutil
    dest = Path(project_path) / "jadio_aitools"
    if dest.exists():
        shutil.rmtree(dest)
