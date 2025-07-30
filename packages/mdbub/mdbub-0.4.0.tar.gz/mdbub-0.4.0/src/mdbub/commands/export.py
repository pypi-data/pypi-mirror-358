import typer

app = typer.Typer()


@app.command()  # type: ignore
def main(filename: str, out: str = "-") -> None:
    """Export mindmap to various formats (stub)."""
    typer.echo(f"[export] Would export {filename} as {out} (stub)")
