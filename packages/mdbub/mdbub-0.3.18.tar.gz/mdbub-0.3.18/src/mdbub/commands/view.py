import typer

app = typer.Typer()


@app.command()  # type: ignore[misc]
def main(filename: str) -> None:
    """Render mindmap as ASCII/Unicode tree (stub)."""
    typer.echo(f"[view] Would render {filename} (stub)")
