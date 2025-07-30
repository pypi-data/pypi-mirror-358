# terraback/cli/azure/__init__.py
import typer
from pathlib import Path
from typing import Optional

app = typer.Typer(
    name="azure",
    help="Work with Microsoft Azure resources.",
    no_args_is_help=True
)

# Import service-level Typer apps
from . import compute, network, storage, loadbalancer

# Registration flag to avoid multiple registrations
_registered = False

def register():
    """Register all Azure resources with cross-scan registry."""
    global _registered
    if _registered:
        return
    _registered = True
    
    compute.register()
    network.register()
    storage.register()
    loadbalancer.register()

# Add service subcommands
app.add_typer(compute.app, name="compute", help="VMs, disks, and compute resources")
app.add_typer(network.app, name="network", help="VNets, subnets, and network security")
app.add_typer(storage.app, name="storage", help="Storage accounts and related resources")
app.add_typer(loadbalancer.app, name="lb", help="Load balancers")

@app.command("scan-all")
def scan_all_azure(
    output_dir: Path = typer.Option("generated", "-o", "--output-dir", help="Directory for generated Terraform files"),
    subscription_id: Optional[str] = typer.Option(None, "--subscription-id", "-s", help="Azure Subscription ID", envvar="AZURE_SUBSCRIPTION_ID"),
    location: Optional[str] = typer.Option(None, "--location", "-l", help="Filter by Azure location", envvar="AZURE_LOCATION"),
    resource_group_name: Optional[str] = typer.Option(None, "--resource-group", "-g", help="Filter by a specific resource group"),
    with_deps: bool = typer.Option(False, "--with-deps", help="Recursively scan dependencies")
):
    """Scan all Azure resources across all services."""
    # Ensure resources are registered
    register()
    
    from terraback.cli.azure.session import get_default_subscription_id
    from terraback.core.license import check_feature_access, Tier
    
    # Get default subscription if not provided
    if not subscription_id:
        subscription_id = get_default_subscription_id()
        if not subscription_id:
            typer.echo("Error: No Azure subscription found. Please run 'az login' or set AZURE_SUBSCRIPTION_ID", err=True)
            raise typer.Exit(code=1)
    
    typer.echo(f"Scanning all Azure resources in subscription '{subscription_id}'...")
    if location:
        typer.echo(f"Filtering by location: {location}")
    if resource_group_name:
        typer.echo(f"Filtering by resource group: {resource_group_name}")
    
    if with_deps:
        if check_feature_access(Tier.PROFESSIONAL):
            # Start with VMs as they have the most dependencies
            from terraback.utils.cross_scan_registry import recursive_scan
            
            typer.echo("\nScanning with dependency resolution (Professional feature)...")
            recursive_scan(
                "azure_virtual_machine",
                output_dir=output_dir,
                subscription_id=subscription_id,
                resource_group_name=resource_group_name,
                location=location
            )
            
            # Then scan networking resources
            recursive_scan(
                "azure_virtual_network",
                output_dir=output_dir,
                subscription_id=subscription_id,
                resource_group_name=resource_group_name,
                location=location
            )
        else:
            typer.echo("\nDependency scanning (--with-deps) requires a Professional license")
            with_deps = False
    
    if not with_deps:
        # Scan each service independently
        typer.echo("\nScanning compute resources...")
        compute.scan_all_compute(
            output_dir=output_dir,
            subscription_id=subscription_id,
            location=location,
            resource_group_name=resource_group_name,
            with_deps=False
        )
        
        typer.echo("\nScanning network resources...")
        network.scan_all_network(
            output_dir=output_dir,
            subscription_id=subscription_id,
            location=location,
            resource_group_name=resource_group_name,
            with_deps=False
        )
        
        typer.echo("\nScanning storage resources...")
        storage.scan_all(
            output_dir=output_dir,
            subscription_id=subscription_id,
            location=location,
            resource_group_name=resource_group_name,
            with_deps=False
        )

@app.command("list-resources")
def list_azure_resources(
    output_dir: Path = typer.Option("generated", "-o", "--output-dir", help="Directory containing import files")
):
    """List all Azure resources previously scanned."""
    from terraback.utils.importer import ImportManager
    
    resource_types = [
        "azure_virtual_machine",
        "azure_managed_disk",
        "azure_virtual_network",
        "azure_subnet",
        "azure_network_security_group",
        "azure_network_interface",
        "azure_storage_account",
        "azure_lb",
        "azure_resource_group",
    ]
    
    for resource_type in resource_types:
        import_file = output_dir / f"{resource_type}_import.json"
        if import_file.exists():
            typer.echo(f"\n=== {resource_type} ===")
            ImportManager(output_dir, resource_type).list_all()

@app.command("clean")
def clean_azure_files(
    output_dir: Path = typer.Option("generated", "-o", "--output-dir", help="Directory to clean"),
    yes: bool = typer.Option(False, "--yes", "-y", help="Skip confirmation")
):
    """Clean all Azure-related generated files."""
    from terraback.utils.cleanup import clean_generated_files
    
    if not yes:
        confirm = typer.confirm(f"This will delete all Azure .tf and _import.json files in {output_dir}. Continue?")
        if not confirm:
            raise typer.Abort()
    
    azure_prefixes = [
        "azure_virtual_machine",
        "azure_managed_disk", 
        "azure_virtual_network",
        "azure_subnet",
        "azure_network_security_group",
        "azure_network_interface",
        "azure_storage_account",
        "azure_lb",
        "azure_resource_group",
    ]
    
    for prefix in azure_prefixes:
        clean_generated_files(output_dir, prefix)
    
    typer.echo("Azure generated files cleaned successfully!")