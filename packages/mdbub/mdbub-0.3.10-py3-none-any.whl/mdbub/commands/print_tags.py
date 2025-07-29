import re
from collections import defaultdict
from typing import Dict, Tuple

from rich.console import Console
from rich.table import Table


def extract_tags_from_file(
    filename: str,
) -> Tuple[Dict[str, int], Dict[str, list[int]]]:
    tag_pattern = re.compile(r"#(\w+)")
    tag_counts: Dict[str, int] = defaultdict(int)
    tag_lines = defaultdict(list)
    with open(filename, "r", encoding="utf-8") as f:
        for lineno, line in enumerate(f, 1):
            for match in tag_pattern.finditer(line):
                tag = match.group(1)
                tag_counts[tag] += 1
                tag_lines[tag].append(lineno)
    return tag_counts, tag_lines


def main(filename: str) -> None:
    console = Console()
    tag_counts, tag_lines = extract_tags_from_file(filename)
    if not tag_counts:
        console.print(
            f"[bold red]No tags found in:[/bold red] [italic]{filename}[/italic]"
        )
        return
    table = Table(title=f"Tags in {filename}", show_lines=True)
    table.add_column("Tag", style="cyan", no_wrap=True)
    table.add_column("Count", style="magenta", justify="right")
    table.add_column("Lines", style="dim")
    for tag in sorted(tag_counts):
        unique_lines = sorted(set(tag_lines[tag]))
        lines = ", ".join(str(n) for n in unique_lines)
        table.add_row(f"#{tag}", str(tag_counts[tag]), lines)
    console.print(table)
