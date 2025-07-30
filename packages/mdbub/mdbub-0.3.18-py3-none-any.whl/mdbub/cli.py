import typer

from mdbub import BUILD_INFO
from mdbub import __version__ as VERSION
from mdbub.commands import about, version
from mdbub.commands.quick import main as quick_main

app = typer.Typer(
    help="""
    mdbub: Interactive mindmap CLI tool.

    Usage examples:
      poetry run mdbub FILE.md
      poetry run mdbub --print-tags FILE.md
      poetry run mdbub --version
      poetry run mdbub --about

    [bold yellow]Note:[/bold yellow] Options like --print-tags must come before the filename.
    If you do not provide a filename, the last session will be restored (if available).
    """,
    add_completion=False,
    invoke_without_command=True,
)


@app.callback(invoke_without_command=True)  # type: ignore
def main(
    ctx: typer.Context,
    file: str = typer.Argument(
        None,
        help="""
        Markdown mindmap file to open or create (append #path to open to a node with [id:path]).
        [bold yellow]Options like --print-tags must come before the filename.[/bold yellow]
        """,
    ),
    print_tags: bool = typer.Option(
        False, "--print-tags", help="Print all #tags in the [FILE] as a table and exit."
    ),
    print_kv: bool = typer.Option(
        False,
        "--print-kv",
        help="Print all @key:value metadata in the [FILE] as a table and exit.",
    ),
    print_links: bool = typer.Option(
        False,
        "--print-links",
        help="Print all [id:...] anchors in the [FILE] as a table and exit.",
    ),
    version_flag: bool = typer.Option(
        False, "--version", help="Show version, build info, and config path."
    ),
    about_flag: bool = typer.Option(False, "--about", help="Show about info."),
) -> None:
    """
    Quick mode: mini interactive shell (default).
    Use --version for version info, --config for config management.
    """
    if version_flag:
        version.main()
        raise typer.Exit()
    if about_flag:
        about.main()
        raise typer.Exit()
    if print_links:
        from mdbub.commands.print_links import main as print_links_main

        print_links_main(file)
        raise typer.Exit()

    if print_tags:
        from mdbub.commands.print_tags import main as print_tags_main

        print_tags_main(file)
        raise typer.Exit()

    if print_kv:
        from mdbub.commands.print_kv import main as print_kv_main

        print_kv_main(file)
        raise typer.Exit()

    if ctx.invoked_subcommand is None:
        try:
            # Support deep links: filename.md#path/to/node
            if file is not None and "#" in file:
                filename, deep_link = file.split("#", 1)
                deep_link_path = deep_link.strip("/") if deep_link.strip("/") else None
                file = filename
            else:
                deep_link_path = None
            if file is not None:
                file_obj = open(file, "r+")
            else:
                file_obj = None
            if print_tags:
                from mdbub.commands.print_tags import main as print_tags_main

                print_tags_main(file)
                raise typer.Exit()
            if print_kv:
                from mdbub.commands.print_kv import main as print_kv_main

                print_kv_main(file)
                raise typer.Exit()
            if print_links:
                from mdbub.commands.links import main as links_main

                links_main(file)
                raise typer.Exit()
            quick_main(
                file_obj,
                VERSION,
                BUILD_INFO,
                deep_link_path=deep_link_path,
            )
        except Exception as e:
            typer.echo(f"Error: {e}")
            raise typer.Exit(1)


if __name__ == "__main__":
    app()
