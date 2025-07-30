"""Quick mode for mdbub - A lightning-fast, keyboard-driven mindmap editor."""

import fcntl
import logging
import os
import select
import signal
import sys
import termios
import threading
import time
import tty
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, TextIO, Tuple

from rich.console import Console
from rich.text import Text

# UI Config
from mdbub.commands.quickmode_config import (
    load_quickmode_config,
    load_session,
    save_session,
)
from mdbub.core.mindmap import MindMapNode as Node
from mdbub.core.mindmap import mindmap_to_markdown, parse_markdown_to_mindmap

CONFIG: Dict[str, Any] = load_quickmode_config()

# Load all color constants directly from _FG/_BG keys (no legacy support)
COLOR_PRINTS_ACCENT_FG = CONFIG["COLOR_PRINTS_ACCENT_FG"]
COLOR_PRINTS_ACCENT_BG = CONFIG["COLOR_PRINTS_ACCENT_BG"]
COLOR_PRINTS_HIGHLIGHT_FG = CONFIG["COLOR_PRINTS_HIGHLIGHT_FG"]
COLOR_PRINTS_HIGHLIGHT_BG = CONFIG["COLOR_PRINTS_HIGHLIGHT_BG"]
COLOR_PRINTS_TEXT_FG = CONFIG["COLOR_PRINTS_TEXT_FG"]
COLOR_PRINTS_TEXT_BG = CONFIG["COLOR_PRINTS_TEXT_BG"]
COLOR_PRINTS_DIM_FG = CONFIG["COLOR_PRINTS_DIM_FG"]
COLOR_PRINTS_DIM_BG = CONFIG["COLOR_PRINTS_DIM_BG"]
COLOR_PRINTS_WARNING_FG = CONFIG["COLOR_PRINTS_WARNING_FG"]
COLOR_PRINTS_WARNING_BG = CONFIG["COLOR_PRINTS_WARNING_BG"]
COLOR_PRINTS_SUCCESS_FG = CONFIG["COLOR_PRINTS_SUCCESS_FG"]
COLOR_PRINTS_SUCCESS_BG = CONFIG["COLOR_PRINTS_SUCCESS_BG"]
COLOR_PRINTS_ERROR_FG = CONFIG["COLOR_PRINTS_ERROR_FG"]
COLOR_PRINTS_ERROR_BG = CONFIG["COLOR_PRINTS_ERROR_BG"]
COLOR_PRINTS_STATUS_BAR_FG = CONFIG["COLOR_PRINTS_STATUS_BAR_FG"]
COLOR_PRINTS_STATUS_BAR_BG = CONFIG["COLOR_PRINTS_STATUS_BAR_BG"]
COLOR_PRINTS_BREADCRUMB_BAR_FG = CONFIG["COLOR_PRINTS_BREADCRUMB_BAR_FG"]
COLOR_PRINTS_BREADCRUMB_BAR_BG = CONFIG["COLOR_PRINTS_BREADCRUMB_BAR_BG"]
COLOR_PRINTS_CHILD_HIGHLIGHT_FG = CONFIG["COLOR_PRINTS_CHILD_HIGHLIGHT_FG"]
COLOR_PRINTS_CHILD_HIGHLIGHT_BG = CONFIG["COLOR_PRINTS_CHILD_HIGHLIGHT_BG"]
COLOR_PRINTS_CLEAR = CONFIG["COLOR_PRINTS_CLEAR"]  # Clear screen
COLOR_PRINTS_RESET = CONFIG["COLOR_PRINTS_RESET"]  # Reset
COLOR_PRINTS_BLINK = CONFIG["COLOR_PRINTS_BLINK"]  # Rich blink style (not ANSI)
STATUS_MESSAGE_TIMEOUT_SHORT = float(CONFIG["STATUS_MESSAGE_TIMEOUT_SHORT"])
STATUS_MESSAGE_TIMEOUT = float(CONFIG["STATUS_MESSAGE_TIMEOUT"])
STATUS_MESSAGE_TIMEOUT_LONG = float(CONFIG["STATUS_MESSAGE_TIMEOUT_LONG"])
MAX_VISIBLE_CHILDREN = int(CONFIG["MAX_VISIBLE_CHILDREN"])
MAX_NODE_LABEL_VIZ_LENGTH = int(CONFIG["MAX_NODE_LABEL_VIZ_LENGTH"])
MAX_BREADCRUMB_NODE_VIZ_LENGTH = int(CONFIG["MAX_BREADCRUMB_NODE_VIZ_LENGTH"])
MAX_CHILDNODE_VIZ_LENGTH = int(CONFIG["MAX_CHILDNODE_VIZ_LENGTH"])
COLOR_BREADCRUMBS = str(CONFIG["COLOR_BREADCRUMBS"])
COLOR_BREADCRUMBS_ROOT = str(CONFIG["COLOR_BREADCRUMBS_ROOT"])
COLOR_BREADCRUMBS_CURRENT = str(CONFIG["COLOR_BREADCRUMBS_CURRENT"])
COLOR_CURRENT_NODE = str(CONFIG["COLOR_CURRENT_NODE"])
COLOR_SELECTED_CHILD = str(CONFIG["COLOR_SELECTED_CHILD"])
COLOR_CHILD = str(CONFIG["COLOR_CHILD"])
COLOR_PAGINATION = str(CONFIG["COLOR_PAGINATION"])
COLOR_POSITION = str(CONFIG["COLOR_POSITION"])
COLOR_STATUS = str(CONFIG["COLOR_STATUS"])
COLOR_HOTKEYS = str(CONFIG["COLOR_HOTKEYS"])
COLOR_ERROR = str(CONFIG["COLOR_ERROR"])
COLOR_SUCCESS = str(CONFIG["COLOR_SUCCESS"])
SYMBOL_BULLET = str(CONFIG["SYMBOL_BULLET"])
SYMBOL_BRANCH = str(CONFIG["SYMBOL_BRANCH"])
SYMBOL_ROOT = str(CONFIG["SYMBOL_ROOT"])
SYMBOL_MORE_LEFT = str(CONFIG["SYMBOL_MORE_LEFT"])
SYMBOL_MORE_RIGHT = str(CONFIG["SYMBOL_MORE_RIGHT"])
SYMBOL_CHILDNODE_OPENWRAP = str(CONFIG["SYMBOL_CHILDNODE_OPENWRAP"])
SYMBOL_CHILDNODE_CLOSEWRAP = str(CONFIG["SYMBOL_CHILDNODE_CLOSEWRAP"])
SYMBOL_BREADCRUMBNODE_OPENWRAP = str(CONFIG["SYMBOL_BREADCRUMBNODE_OPENWRAP"])
SYMBOL_BREADCRUMBNODE_CLOSEWRAP = str(CONFIG["SYMBOL_BREADCRUMBNODE_CLOSEWRAP"])

# UI states
STATE_READY = "Ready"
STATE_EDITING = "Editing"
STATE_SAVING = "Saving..."
STATE_SAVED = "Saved"
STATE_SEARCHING = "Searching"
STATE_DELETE = "Confirm Delete"


class QuickModeUI:
    """Handles rendering of the Quick Mode interface."""

    def __init__(self, state: "QuickModeState"):
        self.state = state
        self.console = Console()
        self.term_size = self.console.size
        self.live = None

    def get_term_size(self) -> Tuple[int, int]:
        """Get current terminal dimensions."""
        # Cast to Tuple[int, int] for mypy
        return tuple(self.console.size)  # type: ignore

    def render_breadcrumbs(self) -> Text:
        """Render the breadcrumb navigation showing the path to current node."""
        result = Text("")

        # At the root node, just show the root symbol
        if not self.state.path:
            result.append(SYMBOL_ROOT, style=COLOR_BREADCRUMBS_ROOT)
            return result

        # Build the full path including the root node
        node = self.state.mindmap
        path_segments = [node.label]  # Start with root node label

        # Follow the path to collect node labels
        for i, idx in enumerate(self.state.path):
            if idx < len(node.children):
                node = node.children[idx]
                path_segments.append(node.label)

        # Helper function to truncate long node names
        def truncate_node_name(name: str) -> str:
            if len(name) > MAX_BREADCRUMB_NODE_VIZ_LENGTH:
                return name[: MAX_BREADCRUMB_NODE_VIZ_LENGTH - 3] + "..."
            return name

        # Start the breadcrumb with the root node label (truncated if needed)
        root_name = truncate_node_name(path_segments[0])
        result.append(
            f"{SYMBOL_BREADCRUMBNODE_OPENWRAP}{root_name}{SYMBOL_BREADCRUMBNODE_CLOSEWRAP}",
            style=COLOR_BREADCRUMBS_ROOT,
        )  # Root node label

        # Handle the path display
        if len(path_segments) > 3:  # Root + at least 2 levels deep
            # Handle truncation for long paths
            result.append(" > ", style=COLOR_BREADCRUMBS)
            # Truncate first level node name if needed
            first_level_name = truncate_node_name(path_segments[1])
            result.append(
                f"{SYMBOL_BREADCRUMBNODE_OPENWRAP}{first_level_name}{SYMBOL_BREADCRUMBNODE_CLOSEWRAP}",
                style=COLOR_BREADCRUMBS,
            )  # First level

            if len(path_segments) > 4:  # More than 3 levels deep
                # Add '... >' for each hidden level
                hidden_levels = (
                    len(path_segments) - 4
                )  # -4 because we show root, first, parent and current
                result.append(" >", style=COLOR_BREADCRUMBS)

                # Add '... >' for each hidden level
                for _ in range(hidden_levels):
                    result.append("... >", style=COLOR_BREADCRUMBS)
                    result.append(" ", style=COLOR_BREADCRUMBS)

                # Remove extra space at the end (already added inside the loop)
                if hidden_levels > 0:
                    result.pop()
            else:
                result.append(" > ", style=COLOR_BREADCRUMBS)

            # Truncate parent node name if needed
            parent_name = truncate_node_name(path_segments[-2])
            result.append(
                f"{SYMBOL_BREADCRUMBNODE_OPENWRAP}{parent_name}{SYMBOL_BREADCRUMBNODE_CLOSEWRAP}",
                style=COLOR_BREADCRUMBS_CURRENT,
            )  # Parent of current
        elif len(path_segments) > 2:  # Root + 1 level deep
            # Show path directly
            for i, segment in enumerate(path_segments[:-1]):  # Exclude current node
                if i > 0:  # Skip root node label (already added)
                    result.append(" > ", style=COLOR_BREADCRUMBS)
                    # Truncate segment name if needed
                    segment_name = truncate_node_name(segment)
                    result.append(
                        f"{SYMBOL_BREADCRUMBNODE_OPENWRAP}{segment_name}{SYMBOL_BREADCRUMBNODE_CLOSEWRAP}",
                        style=COLOR_BREADCRUMBS,
                    )

        return result

    def render_current_node(self) -> Text:
        """Render the current node with bullet and edit cursor if needed."""
        text = Text()

        if self.state.editing:
            # Show input buffer with cursor
            text.append(self.state.input_buffer, style=COLOR_CURRENT_NODE)
            text.append("|", style="blink")  # Cursor
        else:
            # Show node label
            text.append(self.state.current_node.label, style=COLOR_CURRENT_NODE)

        return text

    def render_children(self) -> Text:
        """Render the children of the current node in a horizontal layout."""
        text = Text()
        current_node = self.state.current_node

        if not current_node.children:
            text.append("No children", style=COLOR_CHILD)
            return text

        # Calculate pagination
        total_children = len(current_node.children)
        selected_idx = self.state.selected_index

        # Calculate window start and end
        window_size = min(MAX_VISIBLE_CHILDREN, total_children)
        window_half = window_size // 2

        # Ensure selected item is in the middle when possible
        window_start = max(
            0, min(selected_idx - window_half, total_children - window_size)
        )
        window_end = min(window_start + window_size, total_children)

        # Add left pagination indicator if needed
        if window_start > 0:
            text.append("< ", style=COLOR_PAGINATION)

        # Helper function to truncate long node names
        def truncate_child_name(name: str) -> str:
            if len(name) > MAX_CHILDNODE_VIZ_LENGTH:
                return name[: MAX_CHILDNODE_VIZ_LENGTH - 3] + "..."
            return name

        # Add children
        for i in range(window_start, window_end):
            child = current_node.children[i]
            # Truncate child name if needed
            child_name = truncate_child_name(child.label)
            style = COLOR_SELECTED_CHILD if i == selected_idx else COLOR_CHILD
            text.append(
                f"{SYMBOL_CHILDNODE_OPENWRAP}{child_name}{SYMBOL_CHILDNODE_CLOSEWRAP} ",
                style=style,
            )

        # Add right pagination indicator if needed
        if window_end < total_children:
            text.append("> ", style=COLOR_PAGINATION)

        # Add position indicator if there are multiple pages
        if total_children > window_size:
            text.append(f"({selected_idx + 1}/{total_children})", style=COLOR_POSITION)

        return text

    def render_status_bar(self) -> Text:
        """Render the status bar with state and hotkeys."""
        text = Text()

        # Show all status messages
        if self.state.message[0]:
            status_text = self.state.message[0]
            status_color = self.state.message[1]
            text.append(f"{status_text} ", style=status_color)
        elif self.state.editing:
            text.append("Editing ", style="yellow")
            text.append("↵:save esc:cancel", style=COLOR_HOTKEYS)
            return text

        # Mini status hotkeys
        # TODO: Replace with hotkey map
        if not self.state.editing:
            text.append(
                "^c/^d:quit ↑↓←→:nav tab:add-child enter:add-sibling del:delete",
                style=COLOR_HOTKEYS,
            )

        return text

    def render(self) -> Text:
        """Render the complete UI."""
        # Check for expired temporary messages before rendering
        self.state.check_expired_message()

        content = Text()

        # Add breadcrumbs and current node on the same line
        breadcrumbs = self.render_breadcrumbs()
        content.append(breadcrumbs)
        content.append(" ")
        content.append(self.render_current_node())

        # Add children on the next line
        content.append("\n")
        content.append(self.render_children())

        # Add status bar on the next line only if there's something to show
        status = self.render_status_bar()
        if status.plain:
            content.append("\n")
            content.append(status)

        return content


@dataclass
class QuickModeState:
    """Manages the state of the quick mode interface."""

    mindmap: Node
    path: List[int] = field(default_factory=list)  # Path to current node
    selected_index: int = 0
    editing: bool = False
    input_buffer: str = ""
    dirty: bool = False
    should_quit: bool = False
    message: Tuple[str, str] = field(
        default_factory=lambda: ("", "")
    )  # (message, color)
    message_timestamp: float = 0.0  # When the message was set
    message_temporary: bool = False  # Whether the message should auto-expire
    message_timeout: float = 0.0  # Timeout in seconds for temporary messages
    version: str = ""
    build_info: str = ""
    search_mode: bool = False
    search_term: str = ""
    search_results: List[Tuple[List[int], int]] = field(
        default_factory=list
    )  # List of (path, child_index) tuples for each match
    search_result_index: int = 0  # Current position in search results
    search_result_mode: bool = (
        False  # True when we've executed search and are browsing results
    )
    pre_search_path: List[int] = field(
        default_factory=list
    )  # Path before search was started
    pre_search_index: int = 0  # Selected index before search was started
    delete_confirm: bool = False

    @property
    def current_node(self) -> Node:
        """Get the currently selected node."""
        node = self.mindmap
        for idx in self.path:
            if 0 <= idx < len(node.children):
                node = node.children[idx]
            else:
                # Reset to root if path becomes invalid
                self.path = []
                return self.mindmap
        return node

    @property
    def parent_node(self) -> Optional[Node]:
        """Get the parent of the current node."""
        if not self.path:
            return None
        return self.get_node_at_path(self.path[:-1])

    def get_node_at_path(self, path: List[int]) -> Node:
        """Get node at the given path."""
        node = self.mindmap
        for idx in path:
            if 0 <= idx < len(node.children):
                node = node.children[idx]
            else:
                raise IndexError("Invalid path")
        return node

    def set_message(
        self,
        text: str,
        color: str = "",
        temporary: bool = False,
        timeout: float = STATUS_MESSAGE_TIMEOUT,
    ) -> None:
        """Set a status message to display to the user.

        Args:
            text: The message text
            color: Color for the message
            temporary: If True, message will auto-expire after timeout seconds
            timeout: Number of seconds before the message expires (only used if temporary=True)
        """
        self.message = (text, color or "default")
        self.message_timestamp = time.time()
        self.message_temporary = temporary
        self.message_timeout = timeout if temporary else 0.0

    def clear_message(self) -> None:
        """Clear any status message."""
        self.message = ("", "")
        self.message_temporary = False
        self.message_timeout = 0.0

    def check_expired_message(self) -> None:
        """Check if a temporary message has expired and clear it if needed."""
        if self.message_temporary and self.message[0]:
            current_time = time.time()
            elapsed = current_time - self.message_timestamp
            # Print debug info to console about message timing
            # print(f"DEBUG: Message '{self.message[0]}' age: {elapsed:.1f}s vs timeout {self.message_timeout}s", file=sys.stderr)
            if elapsed >= self.message_timeout:
                # print(f"DEBUG: Clearing message '{self.message[0]}'", file=sys.stderr)
                self.clear_message()

    def navigate_prev_sibling(self) -> None:
        """Move selection to previous sibling (left)."""
        # print(f"\nDEBUG: navigate_prev_sibling called, current selected_index={self.selected_index}")
        if self.selected_index > 0:
            self.selected_index -= 1
            self.clear_message()
            # print(f"DEBUG: selected_index now {self.selected_index}")
        # else:
        # print("DEBUG: Can't navigate to previous sibling (already at first sibling)")

    def navigate_next_sibling(self) -> None:
        """Move selection to next sibling (right)."""
        # print(f"\nDEBUG: navigate_next_sibling called, current selected_index={self.selected_index}")
        # print(f"DEBUG: current node has {len(self.current_node.children)} children")
        if self.selected_index < len(self.current_node.children) - 1:
            self.selected_index += 1
            self.clear_message()
            # print(f"DEBUG: selected_index now {self.selected_index}")
        # else:
        # print("DEBUG: Can't navigate to next sibling (already at last sibling)")

    def navigate_to_parent(self) -> None:
        """Move to parent node (up the tree)."""
        # print(f"\nDEBUG: navigate_to_parent called, current path={self.path}")
        if self.path:
            index_to_remember = self.path[-1]  # Remember which child we came from
            self.path.pop()
            self.selected_index = (
                index_to_remember  # Position cursor on the child we came from
            )
            self.clear_message()
            # print(f"DEBUG: Moved to parent, new path={self.path}, selected_index={self.selected_index}")
        # else:
        # print("DEBUG: Can't navigate to parent (already at root)")

    def navigate_to_child(self) -> None:
        """Move to selected child node (down the tree)."""
        # print(f"\nDEBUG: navigate_to_child called")
        if self.current_node.children:
            self.path.append(self.selected_index)
            self.selected_index = 0
            self.clear_message()
            # print(f"DEBUG: Moved into child, new path={self.path}")
        # else:
        # print("DEBUG: Can't navigate to child (no children)")

    def start_editing(self) -> None:
        """Start editing the current node."""
        self.editing = True
        self.input_buffer = self.current_node.label

    def start_inserting(self) -> None:
        self.editing = True
        self.input_buffer = self.current_node.label

    def save_edit(self) -> None:
        """Save the current edit."""
        from mdbub.core.mindmap import _parse_node_metadata

        if self.input_buffer != self.current_node.label:
            # Re-parse label for tags/metadata
            label, metadata = _parse_node_metadata(self.input_buffer)
            truncated = False
            if len(label) > MAX_NODE_LABEL_VIZ_LENGTH:
                label = label[:MAX_NODE_LABEL_VIZ_LENGTH] + "... [truncated]"
                truncated = True
            self.current_node.label = label
            # Only update tags in metadata (preserve other keys)
            if "tags" in metadata:
                self.current_node.metadata["tags"] = metadata["tags"]
            elif "tags" in self.current_node.metadata:
                del self.current_node.metadata["tags"]
            # Optionally handle other metadata keys here
            self.dirty = True
            if truncated:
                self.set_message(
                    f"Node label was too long and truncated to {MAX_NODE_LABEL_VIZ_LENGTH} chars.",
                    "yellow",
                    temporary=True,
                    timeout=STATUS_MESSAGE_TIMEOUT_LONG,
                )
            else:
                self.set_message(
                    "Updated node with changes",
                    "green",
                    temporary=True,
                    timeout=STATUS_MESSAGE_TIMEOUT_SHORT,
                )
        self.editing = False
        self.input_buffer = ""

    def cancel_edit(self) -> None:
        """Cancel the current edit."""
        self.set_message(
            "Cancelling node changes",
            "yellow",
            temporary=True,
            timeout=STATUS_MESSAGE_TIMEOUT_SHORT,
        )
        self.editing = False
        self.input_buffer = ""

    def add_child(self) -> None:
        """Add a new child node and navigate to it."""
        new_node = Node("")
        self.current_node.children.append(new_node)
        # Store the index of the new child
        child_index = len(self.current_node.children) - 1
        # Navigate into the new child node
        self.path.append(child_index)
        self.selected_index = 0  # Reset selection to first position in the new level
        self.dirty = True
        self.start_editing()

    def add_sibling(self) -> None:
        """Add a new sibling node."""
        if not self.path:
            self.set_message("Cannot add sibling to root", "yellow", temporary=True)
            return

        parent = self.parent_node
        if not parent:
            self.set_message(
                "Cannot add a sibling when there is no parent", "yellow", temporary=True
            )
            return

        new_node = Node("")
        insert_pos = self.path[-1] + 1
        parent.children.insert(insert_pos, new_node)
        self.path[-1] = insert_pos
        self.dirty = True
        self.start_editing()

    def delete_node(self) -> None:
        """Delete the selected child node."""
        # If there are no children, there's nothing to delete
        if not self.current_node.children:
            self.set_message("No children to delete", "yellow", temporary=True)
            return

        # Get the selected child index and node
        selected_idx = self.selected_index
        if selected_idx >= len(self.current_node.children):
            return

        selected_node = self.current_node.children[selected_idx]

        # Confirm deletion if not already confirming
        if not self.delete_confirm:
            self.delete_confirm = True
            # Use the same wrapper style and truncation for the node name in the confirmation message
            node_label = selected_node.label
            if len(node_label) > MAX_CHILDNODE_VIZ_LENGTH:
                node_label = node_label[: MAX_CHILDNODE_VIZ_LENGTH - 3] + "..."
            wrapped_node = (
                f"{SYMBOL_CHILDNODE_OPENWRAP}{node_label}{SYMBOL_CHILDNODE_CLOSEWRAP}"
            )
            self.set_message(f"Delete {wrapped_node}? (y/n)", "yellow")
            return

        # Delete the selected child
        del self.current_node.children[selected_idx]

        # Adjust selected index if we deleted the last child
        if (
            self.selected_index >= len(self.current_node.children)
            and self.current_node.children
        ):
            self.selected_index = len(self.current_node.children) - 1

        self.dirty = True
        self.delete_confirm = False
        self.set_message("Child node deleted", "green", temporary=True)

    def cancel_delete(self) -> None:
        """Cancel the current delete operation."""
        self.delete_confirm = False
        self.set_message("Delete canceled", "yellow", temporary=True)

    def navigate_to_first_child(self) -> None:
        """Jump to the first child."""
        if self.current_node.children:
            self.selected_index = 0
            self.clear_message()

    def navigate_to_last_child(self) -> None:
        """Jump to the last child."""
        if self.current_node.children:
            self.selected_index = len(self.current_node.children) - 1
            self.clear_message()

    def navigate_to_root(self) -> None:
        """Jump back to the root node."""
        self.path = []
        self.selected_index = 0
        self.clear_message()

    def start_search(self) -> None:
        """Enter search mode."""
        # Save current position so we can return to it if user cancels
        # Create a deep copy to ensure we don't have reference issues
        self.pre_search_path = self.path.copy() if self.path else []
        self.pre_search_index = self.selected_index

        # Log the saved position for debugging
        logging.debug(
            f"Saved pre-search position: path={self.pre_search_path}, index={self.pre_search_index}"
        )

        self.search_mode = True
        self.search_result_mode = False
        self.search_term = ""
        self.search_results = []
        self.search_result_index = 0
        # This message hides where the term is being typed, commenting out for now
        # self.set_message("Enter search term", "yellow", temporary=True)

    def cancel_search(self) -> None:
        """Exit search mode."""
        self.search_mode = False
        self.search_result_mode = False
        self.search_term = ""

        # Save current position for logging
        current_path = self.path.copy()
        current_index = self.selected_index

        # On first launch, just return to root
        if not self.pre_search_path and current_path:
            # If we have no pre-search path but we're not at root, go to root
            logging.debug("First search after launch, returning to root")
            self.path = []
            self.selected_index = 0
            self.set_message(
                "Returned to root",
                "green",
                temporary=True,
                timeout=STATUS_MESSAGE_TIMEOUT_SHORT,
            )
        # Otherwise use pre-search position if we've moved
        elif self.pre_search_path:
            # Check if we've moved from pre-search position
            if (
                current_path != self.pre_search_path
                or current_index != self.pre_search_index
            ):
                logging.debug(
                    f"Restoring position from {current_path} to {self.pre_search_path}"
                )
                self.path = self.pre_search_path.copy()
                self.selected_index = self.pre_search_index
                self.set_message(
                    "Returned to pre-search position",
                    "green",
                    temporary=True,
                    timeout=STATUS_MESSAGE_TIMEOUT_SHORT,
                )

        # Clear search-related data
        self.search_results = []
        self.search_result_index = 0
        self.pre_search_path = []
        self.pre_search_index = 0

    def _fuzzy_match(self, text: str, pattern: str) -> bool:
        """Perform a case-insensitive substring match.

        Args:
            text: The text to search in
            pattern: The pattern to search for

        Returns:
            True if the pattern matches, False otherwise
        """
        if not pattern:
            return False

        # Convert to lowercase for case-insensitive matching
        text_lower = text.lower()
        pattern_lower = pattern.lower()

        # Simple substring match - more precise than the previous fuzzy match
        return pattern_lower in text_lower

    def perform_search(self) -> None:
        """Search the mindmap for the current search term."""
        if not self.search_term:
            return

        # Reset search results
        self.search_results = []
        self.search_result_index = 0

        # Recursively search through the mindmap
        self._search_node(self.mindmap, [], 0)

        # If we found matches, navigate to the first match
        if self.search_results:
            # Enter result browsing mode where we can't modify the search term
            self.search_result_mode = True
            self.navigate_to_search_result()
            # result_count = len(self.search_results)  # Removed unused variable
            # This message hides the seach status bar, commenting out for now
            # self.set_message(f"Found {result_count} match{'es' if result_count != 1 else ''}. Press right/left to navigate.", "green", temporary=True, timeout=STATUS_MESSAGE_TIMEOUT_LONG)
        else:
            self.set_message(
                f"Pattern not found: '{self.search_term}'",
                "yellow",
                temporary=True,
                timeout=STATUS_MESSAGE_TIMEOUT_LONG,
            )

    def _search_node(self, node: Node, current_path: List[int], depth: int) -> None:
        """Recursively search a node and its children for the search term.

        Args:
            node: The node to search
            current_path: The path to this node
            depth: Current recursion depth (to prevent stack overflow)
        """
        # Limit search depth to prevent stack overflow
        if depth > 100:
            return

        # Check this node's label
        if self._fuzzy_match(node.label, self.search_term):
            # For the root node, we save [0] as the child index since we can't navigate to the root itself
            if not current_path:
                self.search_results.append(([], 0))

        # Search all children
        for i, child in enumerate(node.children):
            # Check if this child matches
            if self._fuzzy_match(child.label, self.search_term):
                # Save the path to the parent and the child's index
                self.search_results.append((current_path.copy(), i))

            # Recursively search this child's children
            new_path = current_path.copy()
            new_path.append(i)
            self._search_node(child, new_path, depth + 1)

    def navigate_to_search_result(self) -> None:
        """Navigate to the current search result."""
        if not self.search_results:
            return

        # Get the current result
        result_path, child_index = self.search_results[self.search_result_index]

        # Navigate to the parent node of the match
        self.path = result_path.copy()

        # Select the matching child
        self.selected_index = child_index

    def next_search_result(self) -> None:
        """Navigate to the next search result."""
        if not self.search_results:
            return

        # Move to the next result
        self.search_result_index = (self.search_result_index + 1) % len(
            self.search_results
        )
        self.navigate_to_search_result()
        # This message hides the seach status bar, commenting out for now
        # self.set_message(f"Match {self.search_result_index + 1}/{len(self.search_results)}", "green", temporary=True)

    def prev_search_result(self) -> None:
        """Navigate to the previous search result."""
        if not self.search_results:
            return

        # Move to the previous result
        self.search_result_index = (self.search_result_index - 1) % len(
            self.search_results
        )
        self.navigate_to_search_result()
        # This message hides the seach status bar, commenting out for now
        # self.set_message(f"Match {self.search_result_index + 1}/{len(self.search_results)}", "green", temporary=True)

    def select_search_result(self) -> None:
        """Select the current search result and make it the focus node."""
        if not self.search_results:
            return

        # Get the current result path and child index
        result_path, child_index = self.search_results[self.search_result_index]

        # Navigate to the child node itself (it should become the current node)
        self.navigate_to_child()

        # Clear search mode and results
        self.search_mode = False
        self.search_result_mode = False
        self.search_results = []
        self.search_result_index = 0
        self.pre_search_path = []
        self.pre_search_index = 0

        # Confirm the selection with a message
        self.set_message(
            f"Selected match: '{self.current_node.label}'",
            "green",
            temporary=True,
            timeout=STATUS_MESSAGE_TIMEOUT,
        )

    def confirm_delete(self, confirm: bool) -> None:
        """Confirm or cancel node deletion."""
        if confirm:
            # Actually delete the node
            parent = self.parent_node
            if not parent:
                return

            del parent.children[self.path[-1]]

            # Adjust path if we deleted the last child
            if self.path[-1] >= len(parent.children) and parent.children:
                self.path[-1] = len(parent.children) - 1

            self.dirty = True
            self.set_message("Node deleted", "green", temporary=True)
        else:
            self.set_message("Delete canceled", "yellow", temporary=True)

        self.delete_confirm = False


# Key constants for clearer code
KEY_UP = "\x1b[A"
KEY_DOWN = "\x1b[B"
KEY_RIGHT = "\x1b[C"
KEY_LEFT = "\x1b[D"
KEY_ENTER = "\r"
KEY_ESC = "\x1b"
KEY_TAB = "\t"
KEY_BACKSPACE = "\x7f"
KEY_INSERT = "\x1b[2~"
KEY_CTRL_C = "\x03"
KEY_CTRL_D = "\x04"
KEY_SLASH = "/"
KEY_CTRL_F = "\x06"
KEY_CTRL_E = "\x05"
KEY_CTRL_I = "\x09"

# TODO not sure this is used - Vibe programming :shrug: need to see if it should be used
# Commenting out for now - JTD 2025-06-21
# def handle_key(state: QuickModeState, key: str) -> bool:
#     """Process a keypress and update state accordingly.

#     Args:
#         state: The current state object
#         key: The key that was pressed

#     Returns:
#         bool: True if the application should continue, False if it should exit
#     """

#     # Handle delete confirmation state
#     if state.delete_confirm:
#         if key.lower() == "y":
#             state.confirm_delete(True)
#         elif key.lower() == "n" or key == "\x1b":  # n or Escape
#             state.confirm_delete(False)
#         return True

#     # Handle search mode
#     if state.search_mode:
#         if key == KEY_ESC:  # Escape
#             state.cancel_search()
#         elif key == KEY_ENTER:  # Enter
#             if state.search_result_mode:
#                 # We're browsing results, so select the current one
#                 state.select_search_result()
#             elif state.search_term:
#                 # We're typing a search, so execute it
#                 state.perform_search()
#             else:
#                 # Empty search, just cancel
#                 state.cancel_search()
#         elif (
#             key == KEY_BACKSPACE and not state.search_result_mode
#         ):  # Backspace - only in input mode
#             if state.search_term:
#                 state.search_term = state.search_term[:-1]
#         elif key == KEY_LEFT:  # Left arrow - previous result
#             if state.search_results:
#                 state.prev_search_result()
#         elif key == KEY_RIGHT:  # Right arrow - next result
#             if state.search_results:
#                 state.next_search_result()
#         elif (
#             len(key) == 1 and key.isprintable() and not state.search_result_mode
#         ):  # Only add chars in input mode
#             state.search_term += key
#         return True

#     # Handle editing mode
#     if state.editing:
#         if key == KEY_ESC:  # Escape
#             state.cancel_edit()
#         elif key == KEY_ENTER:  # Enter
#             state.save_edit()
#         elif key == "e":
#             state.start_edit()
#         elif key == KEY_BACKSPACE:  # Backspace
#             if state.input_buffer:
#                 state.input_buffer = state.input_buffer[:-1]
#         elif len(key) == 1 and key.isprintable():
#             state.input_buffer += key
#         return True

#     # Navigation mode
#     if key == KEY_SLASH:  # Slash - start search
#         state.start_search()
#         return True
#     elif key == KEY_CTRL_C:  # Ctrl+C
#         return False
#     elif key == KEY_CTRL_D:  # Ctrl+D
#         return False
#     elif key == KEY_UP:  # Up arrow
#         state.navigate_up()
#     elif key == KEY_DOWN:  # Down arrow
#         state.navigate_down()
#     elif key == KEY_LEFT:  # Left arrow
#         state.navigate_left()
#     elif key == KEY_RIGHT:  # Right arrow
#         state.navigate_right()
#     elif key == "\x1b[1;3A":  # Alt+Up
#         state.navigate_to_root()
#     elif key == "\x1b[1;3D":  # Alt+Left
#         state.navigate_to_first_child()
#     elif key == "\x1b[1;3C":  # Alt+Right
#         state.navigate_to_last_child()
#     elif key == KEY_ENTER:  # Enter
#         state.add_sibling()
#     elif key == KEY_TAB:  # Tab
#         state.add_child()
#     elif key == KEY_BACKSPACE:  # Delete or Backspace
#         state.delete_node()
#     elif key == KEY_SLASH:  # Slash for search
#         state.start_search()
#     elif len(key) == 1 and key.isprintable():
#         # Any other printable character starts editing
#         state.start_editing()
#         state.input_buffer = key

#     return True


def get_key(timeout: float = 1.0) -> str:
    """Get a single keypress from terminal, handling special keys like arrows.

    Args:
        timeout: Maximum time to wait for a key press in seconds.
               If no key is pressed within this time, returns empty string.

    Returns:
        The key pressed, or empty string if timeout occurred.
    """
    # Dictionary of escape sequences
    ARROW_KEY_SEQUENCES = {
        "\x1b[A": KEY_UP,  # Up arrow
        "\x1b[B": KEY_DOWN,  # Down arrow
        "\x1b[C": KEY_RIGHT,  # Right arrow
        "\x1b[D": KEY_LEFT,  # Left arrow
        "\x1bOA": KEY_UP,  # Up arrow (alternate)
        "\x1bOB": KEY_DOWN,  # Down arrow (alternate)
        "\x1bOC": KEY_RIGHT,  # Right arrow (alternate)
        "\x1bOD": KEY_LEFT,  # Left arrow (alternate)
    }

    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    key = ""
    try:
        tty.setraw(fd)

        # Set stdin to non-blocking mode
        fcntl.fcntl(fd, fcntl.F_SETFL, os.O_NONBLOCK)

        # Wait for input with timeout using select
        ready, _, _ = select.select([sys.stdin], [], [], timeout)
        if ready:
            key = sys.stdin.read(1)
        else:
            # Timeout occurred, no key pressed
            return ""
        if key == KEY_ESC:  # Escape sequence
            # Set stdin to non-blocking mode
            fcntl.fcntl(fd, fcntl.F_SETFL, os.O_NONBLOCK)

            # Try to read the escape sequence
            seq = key
            try:
                while True:
                    ch = sys.stdin.read(1)
                    if not ch:  # No more characters
                        break
                    seq += ch
                    # Check if we have a known sequence
                    if seq in ARROW_KEY_SEQUENCES:
                        return ARROW_KEY_SEQUENCES[seq]
                    # Avoid reading too many characters
                    if len(seq) >= 6:
                        break
            except Exception:
                # If anything goes wrong, just return what we have
                pass
            finally:
                # Reset stdin to blocking mode
                fcntl.fcntl(fd, fcntl.F_SETFL, 0)

            return seq
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

    return key


def auto_save(state: QuickModeState, file: TextIO) -> None:
    """Auto-save function to periodically save changes."""
    while not state.should_quit:
        if state.dirty:
            try:
                # Only show the message if we're not in the middle of another operation
                show_message = not (state.editing or state.delete_confirm)

                # Save changes
                file.seek(0)
                file.truncate()
                file.write(mindmap_to_markdown(state.mindmap))
                file.flush()
                state.dirty = False

                # Only show 'Saved' message if we're not in the middle of another operation
                if show_message:
                    state.set_message("Autosave complete", "green", temporary=True)
            except Exception as e:
                state.set_message(f"Error autosaving: {str(e)}", "red")
        # Check every 2 seconds
        time.sleep(2)


def main(
    file: TextIO, version: str, build_info: str, deep_link_path: Optional[str] = None
) -> int:
    """Main entry point for quick mode with session restore support."""
    import os

    session_used = False
    session = None
    if file is None:
        session = load_session()
        if session and session.get("last_file"):
            try:
                file = open(session["last_file"], "r+")
                session_used = True
            except Exception as e:
                print(f"[mdbub] Failed to open last session file: {e}", file=sys.stderr)
                file = None
    if file is None:
        print("No file provided and no session to restore. Exiting.", file=sys.stderr)
        return 1
    try:
        # Read the file content
        content = file.read()

        # Parse the markdown content into a mindmap
        create_new_mindmap = False
        try:
            mindmap = parse_markdown_to_mindmap(content)
            if not mindmap or not mindmap.label:  # If parsing failed or empty file
                create_new_mindmap = True
        except Exception as e:
            print(f"Error parsing mindmap: {e}", file=sys.stderr)
            create_new_mindmap = True

        # Create a new mindmap if needed
        if create_new_mindmap:
            # Create an empty mindmap with the filename as the root node
            filename = os.path.basename(file.name)
            root_name = os.path.splitext(filename)[0] if "." in filename else filename
            mindmap = Node(root_name)

        # Initialize state
        state = QuickModeState(mindmap)
        if create_new_mindmap:
            state.dirty = True  # Ensure we save the new mindmap
        state.version = version
        state.build_info = build_info

        # Restore last node path if session was used
        if session_used and session and session.get("last_node_path"):
            try:
                path = session["last_node_path"]
                node = mindmap
                for i, idx in enumerate(path):
                    if 0 <= idx < len(node.children):
                        node = node.children[idx]
                    else:
                        raise IndexError
                state.path = path
                state.selected_index = path[-1] if path else 0
            except Exception:
                state.path = []
                state.selected_index = 0

        # Anchor-style deep link: search for label containing [id:path/to/me]
        def find_node_with_anchor(root: Node, anchor: str) -> Optional[List[int]]:
            stack: List[Any] = [(root, [])]  # Start with root node and empty path
            anchor_str = f"[id:{anchor}]"
            while stack:
                node, path = stack.pop()
                if anchor_str in node.label:
                    if isinstance(path, list) and all(isinstance(i, int) for i in path):
                        return path
                    else:
                        return None
                for idx, child in enumerate(node.children):
                    stack.append((child, path + [idx]))
            return None

        if deep_link_path:
            anchor_path = deep_link_path
            result_path = find_node_with_anchor(mindmap, anchor_path)
            if result_path is not None:
                state.path = result_path
                state.selected_index = 0 if not result_path else result_path[-1]
            else:
                # Show temp warning if anchor not found
                anchor_str = "/".join(anchor_path)
                state.set_message(
                    f"Link id /{anchor_str} not found",
                    "yellow",
                    temporary=True,
                    timeout=3.0,
                )
                # Remain at root

        # Initialize pre-search position to the root
        # This ensures ESC after search will return to root even on first launch
        state.pre_search_path = []
        state.pre_search_index = 0

        # Initialize UI
        # ui = QuickModeUI(state)  # Removed unused variable

        # Set up autosave thread
        autosave_thread = threading.Thread(
            target=auto_save, args=(state, file), daemon=True
        )
        autosave_thread.start()

        # Set up signal handler for clean exit
        def handle_sigint(sig: int, frame: Any) -> None:
            state.should_quit = True
            return

        signal.signal(signal.SIGINT, handle_sigint)

        # Main UI loop - minimal UI approach
        should_quit = False
        key = ""  # Initialize key variable
        while not should_quit and not state.should_quit:
            try:
                # Save session state on every navigation loop
                save_session(file.name, state.path)
                # Check for expired temporary messages
                state.check_expired_message()

                # Clear screen and display current state
                print(COLOR_PRINTS_CLEAR, end="")  # ANSI escape to clear screen

                # Print only minimal info - no debugging clutter
                # Intentionally left blank to make UI super minimal

                # Display breadcrumbs
                if not state.path:
                    # When at the root, show just the root symbol
                    print("\033[36m<no parents>\033[0m")
                else:
                    # Build the path starting with the root node's label
                    current_path = [state.mindmap.label]  # Start with root node's label
                    node = state.mindmap
                    for i, idx in enumerate(state.path):
                        if idx < len(node.children):
                            node = node.children[idx]
                            current_path.append(node.label)

                    # Format the breadcrumb path with the root node's text
                    # Remove the current node from the breadcrumb (last element)

                    # Truncate long node names
                    def truncate_node_name(name: str) -> str:
                        if len(name) > MAX_BREADCRUMB_NODE_VIZ_LENGTH:
                            return name[: MAX_BREADCRUMB_NODE_VIZ_LENGTH - 3] + "..."
                        return name

                    # Truncate root node name if needed
                    root_name = truncate_node_name(current_path[0])
                    breadcrumb_path = f"{SYMBOL_BREADCRUMBNODE_OPENWRAP}{root_name}{SYMBOL_BREADCRUMBNODE_CLOSEWRAP}"  # Root node's label

                    if len(current_path) > 3:  # Root + more than 2 levels deep
                        # Truncate the first level node name if needed
                        first_level_name = truncate_node_name(current_path[1])
                        breadcrumb_path += f" > {SYMBOL_BREADCRUMBNODE_OPENWRAP}{first_level_name}{SYMBOL_BREADCRUMBNODE_CLOSEWRAP}"
                        if len(current_path) > 4:  # Root + more than 3 levels deep
                            # Add '... >' for each hidden level
                            hidden_levels = (
                                len(current_path) - 4
                            )  # -4 because we show root, first, parent and current

                            # Truncate long node names
                            def truncate_node_name(name: str) -> str:
                                if len(name) > MAX_BREADCRUMB_NODE_VIZ_LENGTH:
                                    return (
                                        name[: MAX_BREADCRUMB_NODE_VIZ_LENGTH - 3]
                                        + "..."
                                    )
                                return name

                            # First add the > after the first visible node
                            breadcrumb_path += " >"

                            ellipsis_arrows = ""
                            for _ in range(hidden_levels):
                                ellipsis_arrows += " ... >"

                            # Truncate the parent node name if needed
                            parent_name = truncate_node_name(current_path[-2])
                            breadcrumb_path += f"{ellipsis_arrows} {SYMBOL_BREADCRUMBNODE_OPENWRAP}{parent_name}{SYMBOL_BREADCRUMBNODE_CLOSEWRAP}"
                        else:
                            # Truncate parent node name if needed
                            parent_name = truncate_node_name(current_path[-2])
                            breadcrumb_path += f" > {SYMBOL_BREADCRUMBNODE_OPENWRAP}{parent_name}{SYMBOL_BREADCRUMBNODE_CLOSEWRAP}"
                    elif len(current_path) > 2:  # Root + 1 child level
                        # Truncate the first level node name if needed
                        first_level_name = truncate_node_name(current_path[1])
                        breadcrumb_path += f" > {SYMBOL_BREADCRUMBNODE_OPENWRAP}{first_level_name}{SYMBOL_BREADCRUMBNODE_CLOSEWRAP}"

                    print(
                        f"{COLOR_PRINTS_BREADCRUMB_BAR_BG}{COLOR_PRINTS_BREADCRUMB_BAR_FG}{breadcrumb_path}{COLOR_PRINTS_RESET}"
                    )  # Breadcrumb bar color

                # Display current node
                if state.editing:
                    # Use the same bullet regardless of position when editing
                    print(
                        f"● {COLOR_PRINTS_TEXT_BG}{COLOR_PRINTS_TEXT_FG}{state.input_buffer}|{COLOR_PRINTS_RESET}"
                    )  # Main text with cursor
                else:
                    # Use root symbol when at root, regular bullet otherwise
                    bullet = SYMBOL_ROOT if not state.path else SYMBOL_BULLET
                    print(
                        f"{bullet} {COLOR_PRINTS_TEXT_BG}{COLOR_PRINTS_TEXT_FG}{state.current_node.label}{COLOR_PRINTS_RESET}"
                    )  # Main text

                # Display children if any
                children = state.current_node.children
                if children:
                    child_text = "└─ "
                    total_children = len(children)
                    selected_idx = state.selected_index

                    # Show pagination if needed
                    window_size = min(MAX_VISIBLE_CHILDREN, total_children)
                    window_half = window_size // 2
                    window_start = max(
                        0, min(selected_idx - window_half, total_children - window_size)
                    )
                    window_end = min(window_start + window_size, total_children)

                    if window_start > 0:
                        child_text += "< "

                    # Helper function to truncate long child names
                    def truncate_child_name(name: str) -> str:
                        if len(name) > MAX_CHILDNODE_VIZ_LENGTH:
                            return name[: MAX_CHILDNODE_VIZ_LENGTH - 3] + "..."
                        return name

                    for i in range(window_start, window_end):
                        # Truncate child name if needed
                        child_name = truncate_child_name(children[i].label)
                        if i == selected_idx:
                            # Selected child: use highlight FG/BG
                            child_text += f"{COLOR_PRINTS_CHILD_HIGHLIGHT_BG}{COLOR_PRINTS_CHILD_HIGHLIGHT_FG}{SYMBOL_CHILDNODE_OPENWRAP}{child_name}{SYMBOL_CHILDNODE_CLOSEWRAP}{COLOR_PRINTS_RESET} "
                        else:
                            child_text += f"{SYMBOL_CHILDNODE_OPENWRAP}{child_name}{SYMBOL_CHILDNODE_CLOSEWRAP} "

                    if window_end < total_children:
                        child_text += "> "

                    if total_children > window_size:
                        child_text += f"({selected_idx + 1}/{total_children})"

                    print(child_text)
                else:
                    print("└─ No children (press Tab to add one)")

                # Display status bar
                status_text = ""

                # Always prioritize displaying message from state if available, regardless of mode
                if state.message[0]:
                    # Use the message color if provided, otherwise use default
                    color_code = f"{COLOR_PRINTS_STATUS_BAR_BG}{COLOR_PRINTS_STATUS_BAR_FG}"  # Default to warning/yellow
                    if state.message[1] == "green":
                        color_code = (
                            f"{COLOR_PRINTS_SUCCESS_BG}{COLOR_PRINTS_SUCCESS_FG}"
                        )
                    elif state.message[1] == "red":
                        color_code = f"{COLOR_PRINTS_ERROR_BG}{COLOR_PRINTS_ERROR_FG}"

                    status_text = f"{color_code}{state.message[0]}{COLOR_PRINTS_RESET}"
                # If no message, show appropriate status based on mode
                elif state.delete_confirm:
                    status_text = f"{COLOR_PRINTS_WARNING_BG}{COLOR_PRINTS_WARNING_FG}Delete? (y/n){COLOR_PRINTS_RESET}"
                elif state.editing:
                    # Use more verbose format that's easier to understand
                    status_text = f"{COLOR_PRINTS_SUCCESS_BG}{COLOR_PRINTS_SUCCESS_FG}Editing: Enter to save, Esc to cancel{COLOR_PRINTS_RESET}"
                elif state.search_mode:
                    # Display search info with match count if we have results
                    if state.search_results:
                        current_pos = state.search_result_index + 1
                        total = len(state.search_results)
                        status_text = f"{COLOR_PRINTS_ACCENT_BG}{COLOR_PRINTS_ACCENT_FG}Search: {state.search_term}| ({current_pos}/{total}) \u2190\u2192:navigate Enter:select ESC:exit{COLOR_PRINTS_RESET}"
                    else:
                        status_text = f"{COLOR_PRINTS_ACCENT_BG}{COLOR_PRINTS_ACCENT_FG}Search: {state.search_term}| Enter:search ESC:cancel{COLOR_PRINTS_RESET}"
                else:
                    status_text = f"{COLOR_PRINTS_STATUS_BAR_BG}{COLOR_PRINTS_STATUS_BAR_FG}^C/^D:quit ↑↓←→:nav tab:add-child enter:add-sibling del:delete /=search{COLOR_PRINTS_RESET}"
                print("\n" + status_text)

                # Get key with timeout to allow message expiration
                key = get_key(timeout=0.5)  # Shorter timeout for more responsive UI

                # If no key was pressed (timeout), check for expired messages and continue the loop
                if key == "":
                    state.check_expired_message()
                    continue

                # Debug disabled
                # if key in [KEY_UP, KEY_DOWN, KEY_LEFT, KEY_RIGHT]:
                #     print(f"\nDEBUG: Arrow key pressed: {repr(key)}")
                #     time.sleep(0.2)  # Less delay for better responsiveness

                # Process input based on current state
                if key in (KEY_CTRL_C, KEY_CTRL_D):  # Ctrl+C or Ctrl+D
                    should_quit = True
                    state.should_quit = True
                elif state.delete_confirm:
                    # Delete confirmation mode
                    if key.lower() == "y":
                        state.delete_node()
                        state.delete_confirm = False
                    elif key.lower() == "n" or key == KEY_ESC:  # n or Escape
                        state.delete_confirm = False
                elif state.editing:
                    # Editing mode
                    if key == KEY_ENTER:  # Enter
                        state.save_edit()
                    elif key == KEY_ESC:  # Escape
                        state.cancel_edit()
                    elif key == KEY_BACKSPACE:  # Backspace
                        state.input_buffer = state.input_buffer[:-1]
                    else:
                        # Add character to input buffer if printable
                        if len(key) == 1 and key.isprintable():
                            state.input_buffer += key
                elif state.search_mode:
                    # Search mode
                    if key == KEY_ENTER:  # Enter - execute search or select result
                        if state.search_result_mode:
                            # We're browsing results, so select the current one
                            state.select_search_result()
                        elif state.search_term:
                            # We're typing a search, so execute it
                            state.perform_search()
                        else:
                            # Empty search, just cancel
                            state.cancel_search()
                    elif key == KEY_ESC:  # Escape - cancel search
                        state.cancel_search()
                    elif (
                        key == KEY_BACKSPACE and not state.search_result_mode
                    ):  # Backspace - delete last character (only if not in result mode)
                        if state.search_term:
                            state.search_term = state.search_term[:-1]
                    elif key == KEY_LEFT:  # Left arrow - previous result
                        if state.search_results:
                            state.prev_search_result()
                    elif key == KEY_RIGHT:  # Right arrow - next result
                        if state.search_results:
                            state.next_search_result()
                    elif (
                        len(key) == 1
                        and key.isprintable()
                        and not state.search_result_mode
                    ):  # Only add characters if not in result mode
                        # Add character to search term if printable
                        state.search_term += key
                else:
                    # Navigation mode with correctly named methods
                    if key in (KEY_SLASH, KEY_CTRL_F):  # Slash or Ctrl+F - start search
                        state.start_search()
                    elif key == KEY_UP:  # Up arrow - navigate up to parent
                        state.navigate_to_parent()  # Move up the tree
                    elif key == KEY_DOWN:  # Down arrow - navigate down to child
                        state.navigate_to_child()  # Move down the tree
                    elif key == KEY_LEFT:  # Left arrow - previous sibling
                        state.navigate_prev_sibling()  # Move left horizontally
                    elif key == KEY_RIGHT:  # Right arrow - next sibling
                        state.navigate_next_sibling()  # Move right horizontally
                    elif key == KEY_TAB:  # Tab
                        state.add_child()
                    elif key == KEY_ENTER:  # Enter
                        if state.path:  # Not at root
                            state.start_editing()
                            state.input_buffer = ""
                            state.add_sibling()
                    elif key == KEY_BACKSPACE:  # Delete
                        state.delete_node()
                    elif key == KEY_SLASH:  # Search
                        state.search_mode = True
                        state.search_term = ""
                    elif key in (
                        KEY_CTRL_I,
                        KEY_INSERT,
                        KEY_CTRL_E,
                    ):  # Insert key - edit current label in-place
                        state.start_inserting()  # input_buffer is set to current label by start_editing
                    elif len(key) == 1 and key.isprintable():
                        # Start editing and add the pressed key
                        state.start_editing()
                        state.input_buffer = key
            except Exception as e:
                print(f"\n\033[31mError: {e}\033[0m")
                print("Press any key to continue or Ctrl+C to quit...")
                try:
                    err_key = get_key()
                    if err_key in (KEY_CTRL_C, KEY_CTRL_D):  # Ctrl+C or Ctrl+D
                        should_quit = True
                        state.should_quit = True
                except Exception:
                    should_quit = True
                    state.should_quit = True

        # Final save if needed
        if state.dirty:
            file.seek(0)
            file.truncate()
            file.write(mindmap_to_markdown(state.mindmap))
        # Always save session on quit
        save_session(file.name, state.path)
        return 0
    except Exception as e:
        print(f"Error in quick mode: {e}", file=sys.stderr)
        import traceback

        traceback.print_exc()
        return 1
