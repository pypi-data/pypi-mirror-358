"""
quickmode_config.py - Loads and manages Quick Mode UI configuration (colors, symbols, caps, etc.)
"""

import json
import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

import toml

# Default UI constants
QUICKMODE_DEFAULTS = {
    # Semantic ANSI color and highlight codes for terminal prints
    # Semantic color roles (legacy single-value keys for backward compatibility)
    "COLOR_PRINTS_CLEAR": "\033[H\033[J",  # Clear screen
    "COLOR_PRINTS_RESET": "\033[0m",  # Reset
    "COLOR_PRINTS_BLINK": "blink",  # Rich blink style (not ANSI)
    # Foreground/background split for all roles (preferred)
    "COLOR_PRINTS_ACCENT_FG": "\033[36m",
    "COLOR_PRINTS_ACCENT_BG": "",
    "COLOR_PRINTS_HIGHLIGHT_FG": "",
    "COLOR_PRINTS_HIGHLIGHT_BG": "\033[44m",
    "COLOR_PRINTS_TEXT_FG": "\033[97m",
    "COLOR_PRINTS_TEXT_BG": "",
    "COLOR_PRINTS_DIM_FG": "\033[90m",
    "COLOR_PRINTS_DIM_BG": "",
    "COLOR_PRINTS_WARNING_FG": "\033[33m",
    "COLOR_PRINTS_WARNING_BG": "",
    "COLOR_PRINTS_SUCCESS_FG": "\033[32m",
    "COLOR_PRINTS_SUCCESS_BG": "",
    "COLOR_PRINTS_ERROR_FG": "\033[31m",
    "COLOR_PRINTS_ERROR_BG": "",
    "COLOR_PRINTS_STATUS_BAR_FG": "\u001b[93m",
    "COLOR_PRINTS_STATUS_BAR_BG": "",
    "COLOR_PRINTS_BREADCRUMB_BAR_FG": "\u001b[36m",
    "COLOR_PRINTS_BREADCRUMB_BAR_BG": "",
    "COLOR_PRINTS_CHILD_HIGHLIGHT_FG": "\u001b[90m",
    "COLOR_PRINTS_CHILD_HIGHLIGHT_BG": "",  # Child highlight (default: dim gray, no bg)
    # UI timings
    "STATUS_MESSAGE_TIMEOUT_SHORT": 1.0,
    "STATUS_MESSAGE_TIMEOUT": 2.0,
    "STATUS_MESSAGE_TIMEOUT_LONG": 4.0,
    # Layout
    "MAX_VISIBLE_CHILDREN": 4,
    # Length caps
    "MAX_NODE_LABEL_VIZ_LENGTH": 2048,
    "MAX_BREADCRUMB_NODE_VIZ_LENGTH": 15,
    "MAX_CHILDNODE_VIZ_LENGTH": 20,
    # Colors
    "COLOR_BREADCRUMBS": "dim white",
    "COLOR_BREADCRUMBS_ROOT": "bold cyan",
    "COLOR_BREADCRUMBS_CURRENT": "bold white",
    "COLOR_CURRENT_NODE": "bold white",
    "COLOR_SELECTED_CHILD": "grey23 on dim cyan",
    "COLOR_CHILD": "dim cyan",
    "COLOR_PAGINATION": "yellow",
    "COLOR_POSITION": "dim white",
    "COLOR_STATUS": "green",
    "COLOR_HOTKEYS": "cyan",
    "COLOR_ERROR": "red",
    "COLOR_WARNING": "yellow",
    "COLOR_SUCCESS": "green",
    # Symbols
    "SYMBOL_BULLET": "●",
    "SYMBOL_BRANCH": "└─",
    "SYMBOL_ROOT": "◉",
    "SYMBOL_MORE_LEFT": "◀ more",
    "SYMBOL_MORE_RIGHT": "more ▶",
    "SYMBOL_CHILDNODE_OPENWRAP": "⦇",
    "SYMBOL_CHILDNODE_CLOSEWRAP": "⦈",
    "SYMBOL_BREADCRUMBNODE_OPENWRAP": "【",
    "SYMBOL_BREADCRUMBNODE_CLOSEWRAP": "】",
}

CONFIG_FILENAME = "mdbub.toml"
SESSION_FILENAME = "session.json"

APPNAME = "mdbub"


def get_session_path() -> Path:
    return get_xdg_config_path() / SESSION_FILENAME


def save_session(last_file: str, last_node_path: List[int]) -> None:
    """Persist the last opened file and selected node path to the session file."""
    session_path = get_session_path()
    session_path.parent.mkdir(parents=True, exist_ok=True)
    session = {
        "last_file": last_file,
        "last_node_path": last_node_path,
    }
    try:
        with open(session_path, "w", encoding="utf-8") as f:
            json.dump(session, f)
    except Exception as e:
        print(
            f"[mdbub] Failed to save session: {e}",
            file=sys.stderr,
        )


def load_session() -> Optional[Dict[str, Any]]:
    """Load the last session from the session file, if it exists."""
    session_path = get_session_path()
    if session_path.exists():
        try:
            with open(session_path, "r", encoding="utf-8") as f:
                session: Dict[str, Any] = json.load(f)
                return session
        except Exception as e:
            print(
                f"[mdbub] Failed to load session: {e}",
                file=sys.stderr,
            )
    return None


def get_xdg_config_path() -> Path:
    # XDG_CONFIG_HOME or ~/.config/mdbub/
    base = os.environ.get("XDG_CONFIG_HOME")
    if base:
        return Path(base) / APPNAME
    return Path.home() / ".config" / APPNAME


def load_quickmode_config() -> Dict[str, Any]:
    config_dir = get_xdg_config_path()
    config_path = config_dir / CONFIG_FILENAME
    config: Dict[str, Any] = QUICKMODE_DEFAULTS.copy()
    if config_path.exists():
        try:
            user_cfg: Dict[str, Any] = toml.load(config_path)
            for k, v in user_cfg.items():
                if k in config:
                    config[k] = v
        except Exception as e:
            print(f"[mdbub] Failed to load quickmode config: {e}", file=sys.stderr)
    return config  # Always return a dict, never None
