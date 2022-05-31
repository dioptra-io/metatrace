import typer

from metatrace.cli.metadata import ixp

app = typer.Typer()
app.add_typer(ixp.app, name="ixp")
