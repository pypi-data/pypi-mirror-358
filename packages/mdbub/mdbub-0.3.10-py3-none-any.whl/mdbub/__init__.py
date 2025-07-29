"""
mdbub - Terminal-first interactive mindmap CLI tool with extended markdown support
"""

import os
import subprocess
from datetime import datetime
from importlib.metadata import PackageNotFoundError, version

__version__ = "0.3.0"


def get_version() -> str:
    try:
        __version__ = version("mdbub")
    except PackageNotFoundError:
        __version__ = "unknown"
    return __version__


def _get_build_info() -> str:
    """Get comprehensive build information."""
    info_parts = []

    # Git commit hash
    try:
        commit = (
            subprocess.check_output(
                ["git", "rev-parse", "--short", "HEAD"], stderr=subprocess.DEVNULL
            )
            .decode("ascii")
            .strip()
        )
        info_parts.append(f"git:{commit}")
    except Exception:
        info_parts.append("git:unknown")

    # Build date (from environment variable if available, otherwise current time)
    build_date = os.environ.get("BUILD_DATE")
    if not build_date:
        try:
            # Try to get git commit date
            build_date = (
                subprocess.check_output(
                    ["git", "log", "-1", "--format=%ci"], stderr=subprocess.DEVNULL
                )
                .decode("ascii")
                .strip()
                .split()[0]  # Just the date part
            )
        except Exception:
            build_date = datetime.now().strftime("%Y-%m-%d")

    info_parts.append(f"date:{build_date}")

    # Build environment
    build_env = os.environ.get("BUILD_ENV", "dev")
    info_parts.append(f"env:{build_env}")

    return " ".join(info_parts)


BUILD_INFO = _get_build_info()
