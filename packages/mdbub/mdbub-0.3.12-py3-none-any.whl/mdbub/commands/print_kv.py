import re
from collections import defaultdict
from typing import Dict, Tuple

from rich.console import Console
from rich.table import Table


def extract_kv_metadata_from_file(
    filename: str,
) -> Tuple[list[dict[str, object]], set[str], Dict[str, Dict[str, int]]]:
    kv_pattern = re.compile(r"@(\w+):([^\s]+)")
    node_kvs = []  # List of dicts: {line, label, kvs: {k:v}}
    all_keys = set()
    value_counts: Dict[str, Dict[str, int]] = defaultdict(
        lambda: defaultdict(int)
    )  # key -> value -> count
    with open(filename, "r", encoding="utf-8") as f:
        for lineno, line in enumerate(f, 1):
            kvs = {}
            for match in kv_pattern.finditer(line):
                key = match.group(1)
                value = match.group(2)
                kvs[key] = value
                all_keys.add(key)
                value_counts[key][value] += 1
            if kvs:
                label = line.strip().split("@", 1)[0].strip()
                node_kvs.append({"line": lineno, "label": label, "kvs": kvs})
    return node_kvs, set(all_keys), value_counts


def main(filename: str) -> None:
    console = Console()
    node_kvs, all_keys, value_counts = extract_kv_metadata_from_file(filename)
    if not node_kvs:
        console.print(
            f"[yellow]No @key:value metadata found in:[/yellow] [italic]{filename}[/italic]"
        )
        return
    table = Table(title=f"@key:value metadata in {filename}", show_lines=True)
    table.add_column("Line", style="dim", justify="right")
    table.add_column("Node Label", style="cyan")
    for key in all_keys:
        table.add_column(f"@{key}", style="magenta")
    for node in node_kvs:
        row = [str(node["line"]), node["label"]]
        for key in all_keys:
            row.append(node["kvs"].get(key, "") if hasattr(node["kvs"], "get") else "")
        table.add_row(*row)
    console.print(table)
    # Print summary
    console.print("\n[bold yellow]Summary of value counts per key:[/bold yellow]")
    for key in all_keys:
        vc = value_counts[key]
        summary = ", ".join(
            f"{v} ({c})" for v, c in sorted(vc.items(), key=lambda x: (-x[1], x[0]))
        )
        console.print(f"  [cyan]@{key}[/cyan]: {summary}")
