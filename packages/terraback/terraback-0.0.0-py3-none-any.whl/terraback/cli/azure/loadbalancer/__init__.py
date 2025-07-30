import typer
from . import load_balancers

app = typer.Typer(
    name="lb",
    help="Work with Azure Load Balancers.",
    no_args_is_help=True
)

def register():
    """Registers the load balancer resources with the cross-scan registry."""
    pass

app.add_typer(load_balancers.app, name="standard")