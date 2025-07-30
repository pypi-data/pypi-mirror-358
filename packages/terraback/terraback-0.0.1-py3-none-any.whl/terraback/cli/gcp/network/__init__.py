# terraback/cli/gcp/network/__init__.py
import typer
from pathlib import Path
from typing import Optional

from . import networks, subnets, firewalls
from .networks import scan_gcp_networks
from .subnets import scan_gcp_subnets
from .firewalls import scan_gcp_firewalls
from terraback.utils.cross_scan_registry import register_scan_function, cross_scan_registry

app = typer.Typer(
    name="network",
    help="Work with GCP networking resources like VPCs, subnets, and firewall rules.",
    no_args_is_help=True
)

def register():
    """Registers the network resources with the cross-scan registry."""
    # Networks
    register_scan_function("gcp_network", scan_gcp_networks)
    
    # Subnets
    register_scan_function("gcp_subnet", scan_gcp_subnets)
    
    # Firewall Rules
    register_scan_function("gcp_firewall", scan_gcp_firewalls)
    
    # Network Dependencies
    cross_scan_registry.register_dependency("gcp_subnet", "gcp_network")
    cross_scan_registry.register_dependency("gcp_firewall", "gcp_network")
    cross_scan_registry.register_dependency("gcp_instance", "gcp_subnet")
    cross_scan_registry.register_dependency("gcp_instance", "gcp_firewall")

# Add sub-commands
app.add_typer(networks.app, name="vpc")
app.add_typer(subnets.app, name="subnet")
app.add_typer(firewalls.app, name="firewall")

# Add convenience command for scanning all network resources
@app.command("scan-all")
def scan_all_network(
    output_dir: Path = typer.Option("generated", "-o", "--output-dir", help="Directory for generated Terraform files."),
    project_id: Optional[str] = typer.Option(None, "--project-id", "-p", help="GCP Project ID.", envvar="GOOGLE_CLOUD_PROJECT"),
    region: Optional[str] = typer.Option(None, "--region", "-r", help="Filter by GCP region."),
    with_deps: bool = typer.Option(False, "--with-deps", help="Recursively scan dependencies")
):
    """Scan all GCP network resources."""
    from terraback.cli.gcp.session import get_default_project_id
    
    # Get default project if not provided
    if not project_id:
        project_id = get_default_project_id()
        if not project_id:
            typer.echo("Error: No GCP project found. Please run 'gcloud config set project' or set GOOGLE_CLOUD_PROJECT", err=True)
            raise typer.Exit(code=1)
    
    if with_deps:
        from terraback.utils.cross_scan_registry import recursive_scan
        recursive_scan(
            "gcp_network",
            output_dir=output_dir,
            project_id=project_id,
            region=region
        )
    else:
        # Scan networks
        networks.scan_networks(
            output_dir=output_dir,
            project_id=project_id,
            with_deps=False
        )
        
        # Scan subnets
        subnets.scan_subnets(
            output_dir=output_dir,
            project_id=project_id,
            region=region,
            with_deps=False
        )
        
        # Scan firewall rules
        firewalls.scan_firewalls(
            output_dir=output_dir,
            project_id=project_id,
            with_deps=False
        )