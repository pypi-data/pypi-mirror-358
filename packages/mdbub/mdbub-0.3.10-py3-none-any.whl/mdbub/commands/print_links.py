import re

from rich.console import Console
from rich.table import Table


def main(filename: str) -> None:
    console = Console()
    anchor_pattern = re.compile(r"\[id:([^]]+)\]")
    rows = []
    with open(filename, "r", encoding="utf-8") as f:
        for lineno, line in enumerate(f, 1):
            m = anchor_pattern.search(line)
            if m:
                anchor = m.group(1)
                label = line.strip().split("[id:", 1)[0].strip()
                rows.append((lineno, label, anchor))
    table = Table(title=f"[id:...] anchors in {filename}")
    table.add_column("Line", justify="right")
    table.add_column("Node Label")
    table.add_column("Anchor")
    for row in rows:
        table.add_row(str(row[0]), row[1], row[2])
    console.print(table)
