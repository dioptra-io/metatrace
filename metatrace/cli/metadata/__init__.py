import typer

from metatrace.cli.metadata import asn, ixp

app = typer.Typer()
app.add_typer(asn.app, name="asn")
app.add_typer(ixp.app, name="ixp")
