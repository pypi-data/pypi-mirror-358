# terraback/cli/gcp/compute/__init__.py
import typer
from pathlib import Path
from typing import Optional

# Don't import submodules here to avoid circular imports
app = typer.Typer(
    name="compute",
    help="Work with GCP Compute Engine resources.",
    no_args_is_help=True
)

def register():
    """Register compute resources with cross-scan registry."""
    # Import here to avoid circular imports
    from terraback.utils.cross_scan_registry import register_scan_function, cross_scan_registry
    from .instances import scan_gcp_instances
    from .disks import scan_gcp_disks
    
    # Register scan functions
    register_scan_function("gcp_instance", scan_gcp_instances)
    register_scan_function("gcp_disk", scan_gcp_disks)
    
    # Register dependencies
    cross_scan_registry.register_dependency("gcp_instance", "gcp_network")
    cross_scan_registry.register_dependency("gcp_instance", "gcp_subnet")
    cross_scan_registry.register_dependency("gcp_instance", "gcp_disk")
    cross_scan_registry.register_dependency("gcp_instance", "gcp_firewall")

# Add sub-commands using lazy imports
@app.command("instance")
def instance_cmd():
    """Work with GCP instances."""
    from . import instances
    return instances.app

@app.command("disk") 
def disk_cmd():
    """Work with GCP disks."""
    from . import disks
    return disks.app