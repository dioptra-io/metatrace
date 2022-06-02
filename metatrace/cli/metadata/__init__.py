import typer

from metatrace.cli.metadata.asn import ASNMetadataCLI
from metatrace.cli.metadata.geo import GeolocationMetadataCLI
from metatrace.cli.metadata.ixp import IXPMetadataCLI

app = typer.Typer()
app.add_typer(ASNMetadataCLI.to_typer(), name="asn")
app.add_typer(GeolocationMetadataCLI.to_typer(), name="geo")
app.add_typer(IXPMetadataCLI.to_typer(), name="ixp")
