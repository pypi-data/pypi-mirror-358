import os
import platform
import sys
from pathlib import Path

import typer

from mdbub import BUILD_INFO, get_version
from mdbub.commands.quickmode_config import CONFIG_FILENAME, get_xdg_config_path


def main() -> None:
    """Print version, build info, and config path."""
    version = get_version()
    build_info = BUILD_INFO

    # Rich output with more details
    typer.echo("🧠 mdbub - Terminal mindmap tool")
    typer.echo("Warning: Pre-release version - data may be lost, expect bugs!")
    typer.echo(f"Version: {version}")
    typer.echo(f"Build: {build_info}")
    typer.echo(f"Python: {sys.version.split()[0]} ({platform.python_implementation()})")
    typer.echo(
        f"Platform: {platform.system()} {platform.release()} ({platform.machine()})"
    )
    typer.echo("")
    # Installation info
    try:
        import mdbub

        install_path = Path(mdbub.__file__).parent.parent.parent
        typer.echo(f"📦 Installed at: {install_path}")
    except Exception:
        typer.echo("📦 Installed at: unknown")

    # check if config for mdbub exists and print path other print "using defaults"
    config_dir = get_xdg_config_path()
    config_path = config_dir / CONFIG_FILENAME
    if config_path.exists():
        typer.echo(f"🔧 Config: {config_path}")
    else:
        typer.echo(f"🔧 Config: {config_path}, Not found (using defaults)")

    # Session info
    import json

    from mdbub.commands.quickmode_config import SESSION_FILENAME

    session_path = config_dir / SESSION_FILENAME
    if session_path.exists():
        try:
            with open(session_path, "r") as f:
                session_data = json.load(f)
            last_file = session_data.get("last_file", "-")
            typer.echo(f"📝 Session: {session_path}")
            if last_file != "-" and not (
                Path(last_file).is_file() and os.access(last_file, os.R_OK)
            ):
                typer.echo(f"    Last file: {last_file} (missing or unreadable)")
            else:
                typer.echo(f"    Last file: {last_file}")
            # typer.echo(f"    Last node path: {last_node_path}")
        except Exception as e:
            typer.echo(f"📝 Session: {session_path} (error reading: {e})")
    else:
        typer.echo(f"📝 Session: {session_path}, Not found")
    typer.echo("")
