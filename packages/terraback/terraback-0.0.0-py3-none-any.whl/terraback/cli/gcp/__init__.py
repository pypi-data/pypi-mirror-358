# terraback/cli/gcp/__init__.py
import typer
from pathlib import Path
from typing import Optional

app = typer.Typer(
    name="gcp",
    help="Work with Google Cloud Platform resources.",
    no_args_is_help=True
)

def register():
    """Register GCP resources with cross-scan registry."""
    from terraback.utils.cross_scan_registry import register_scan_function, cross_scan_registry

    # --- FIX START ---
    # Corrected the function names being imported to match the actual function names
    # in the resource modules (e.g., scan_instances instead of scan_gcp_instances).
    # This resolves the "Failed to register" warnings.
    try:
        from terraback.cli.gcp.compute.instances import scan_instances
        register_scan_function("gcp_instance", scan_instances)
    except ImportError as e:
        typer.echo(f"Warning: Failed to register GCP instances: {e}", err=True)

    try:
        from terraback.cli.gcp.compute.disks import scan_disks
        register_scan_function("gcp_disk", scan_disks)
    except ImportError as e:
        typer.echo(f"Warning: Failed to register GCP disks: {e}", err=True)

    try:
        from terraback.cli.gcp.network.networks import scan_networks
        register_scan_function("gcp_network", scan_networks)
    except ImportError as e:
        typer.echo(f"Warning: Failed to register GCP networks: {e}", err=True)

    try:
        from terraback.cli.gcp.network.subnets import scan_subnets
        register_scan_function("gcp_subnet", scan_subnets)
    except ImportError as e:
        typer.echo(f"Warning: Failed to register GCP subnets: {e}", err=True)

    try:
        from terraback.cli.gcp.network.firewalls import scan_firewalls
        register_scan_function("gcp_firewall", scan_firewalls)
    except ImportError as e:
        typer.echo(f"Warning: Failed to register GCP firewalls: {e}", err=True)

    try:
        from terraback.cli.gcp.storage.buckets import scan_buckets
        register_scan_function("gcp_bucket", scan_buckets)
    except ImportError as e:
        typer.echo(f"Warning: Failed to register GCP buckets: {e}", err=True)
    # --- FIX END ---
    
    # Register dependencies
    cross_scan_registry.register_dependency("gcp_instance", "gcp_network")
    cross_scan_registry.register_dependency("gcp_instance", "gcp_subnet")
    cross_scan_registry.register_dependency("gcp_instance", "gcp_disk")
    cross_scan_registry.register_dependency("gcp_instance", "gcp_firewall")
    cross_scan_registry.register_dependency("gcp_subnet", "gcp_network")
    cross_scan_registry.register_dependency("gcp_firewall", "gcp_network")

# Add top-level commands for each resource type

@app.command("scan-all")
def scan_all_gcp(
    output_dir: Path = typer.Option("generated", "-o", "--output-dir"),
    project_id: Optional[str] = typer.Option(None, "--project-id", "-p"),
    region: Optional[str] = typer.Option(None, "--region", "-r"),
    zone: Optional[str] = typer.Option(None, "--zone", "-z"),
    with_deps: bool = typer.Option(False, "--with-deps")
):
    """Scan all GCP resources across all services."""
    from terraback.cli.gcp.session import get_default_project_id
    
    if not project_id:
        project_id = get_default_project_id()
        if not project_id:
            typer.echo("Error: No GCP project found. Please run 'gcloud config set project' or set GOOGLE_CLOUD_PROJECT", err=True)
            raise typer.Exit(code=1)
    
    typer.echo(f"Scanning all GCP resources in project '{project_id}'...")
    
    if with_deps:
        from terraback.utils.cross_scan_registry import recursive_scan
        recursive_scan(
            "gcp_instance",
            output_dir=output_dir,
            project_id=project_id,
            region=region,
            zone=zone
        )
    else:
        # Scan instances
        instance_scan(output_dir, project_id, region, zone, False)
        
        # Scan disks
        disk_scan(output_dir, project_id, zone, False)
        
        # Scan networks
        network_scan(output_dir, project_id, False)
        
        # Scan subnets
        subnet_scan(output_dir, project_id, region, False)
        
        # Scan firewalls
        firewall_scan(output_dir, project_id, False)
        
        # Scan buckets
        bucket_scan(output_dir, project_id, False)

# Instance commands
@app.command("instance")
def instance_group():
    """Work with GCP Compute Engine instances."""
    typer.echo("Use 'terraback gcp instance scan/list/import' commands")

@app.command("instance-scan")
def instance_scan(
    output_dir: Path = typer.Option("generated", "-o", "--output-dir"),
    project_id: Optional[str] = typer.Option(None, "--project-id", "-p", help="GCP project ID (uses default if not specified)"),
    region: Optional[str] = typer.Option(None, "--region", "-r", help="GCP region"),
    zone: Optional[str] = typer.Option(None, "--zone", "-z", help="GCP zone (e.g., us-central1-a)"),
    with_deps: bool = typer.Option(False, "--with-deps", help="Scan with dependencies")
):
    """Scan GCP Compute Engine instances."""
    from terraback.cli.gcp.session import get_default_project_id
    from terraback.cli.gcp.compute.instances import scan_instances

    if not project_id:
        project_id = get_default_project_id()
        if not project_id:
            typer.echo("Error: No GCP project found. Set project with 'gcloud config set project' or use --project-id", err=True)
            raise typer.Exit(code=1)
    
    typer.echo(f"Scanning GCP instances in project '{project_id}'...")
    if zone:
        typer.echo(f"Zone: {zone}")
    else:
        typer.echo("Zone: all zones")
    
    if with_deps:
        from terraback.utils.cross_scan_registry import recursive_scan
        recursive_scan(
            "gcp_instance",
            output_dir=output_dir,
            project_id=project_id,
            zone=zone
        )
    else:
        try:
            scan_instances(output_dir, project_id, zone, with_deps)
        except Exception as e:
            typer.echo(f"Error scanning instances: {e}", err=True)
            raise typer.Exit(code=1)

@app.command("instance-list")
def instance_list(
    output_dir: Path = typer.Option("generated", "-o", "--output-dir")
):
    """List previously scanned GCP instances."""
    from terraback.cli.gcp.compute.instances import list_instances
    list_instances(output_dir)

@app.command("instance-import")
def instance_import(
    instance_id: str = typer.Argument(..., help="GCP instance ID (project/zone/name)"),
    output_dir: Path = typer.Option("generated", "-o", "--output-dir")
):
    """Import a specific GCP instance."""
    from terraback.cli.gcp.compute.instances import import_instance
    import_instance(instance_id, output_dir)

# Disk commands
@app.command("disk-scan")
def disk_scan(
    output_dir: Path = typer.Option("generated", "-o", "--output-dir"),
    project_id: Optional[str] = typer.Option(None, "--project-id", "-p", help="GCP project ID (uses default if not specified)"),
    zone: Optional[str] = typer.Option(None, "--zone", "-z", help="GCP zone (scans all zones if not specified)"),
    with_deps: bool = typer.Option(False, "--with-deps", help="Scan with dependencies")
):
    """Scan GCP persistent disks."""
    from terraback.cli.gcp.compute.disks import scan_disks
    from terraback.cli.gcp.session import get_default_project_id
    
    if not project_id:
        project_id = get_default_project_id()
        if not project_id:
            typer.echo("Error: No GCP project found. Set project with 'gcloud config set project' or use --project-id", err=True)
            raise typer.Exit(code=1)
    
    typer.echo(f"Scanning GCP disks in project '{project_id}'...")
    if zone:
        typer.echo(f"Zone: {zone}")
    else:
        typer.echo("Zone: all zones")
    
    scan_disks(output_dir, project_id, zone, with_deps)

@app.command("disk-list")
def disk_list(
    output_dir: Path = typer.Option("generated", "-o", "--output-dir")
):
    """List previously scanned GCP disks."""
    from terraback.cli.gcp.compute.disks import list_disks
    list_disks(output_dir)

@app.command("disk-import")
def disk_import(
    disk_id: str = typer.Argument(..., help="GCP disk ID (project/zone/name)"),
    output_dir: Path = typer.Option("generated", "-o", "--output-dir")
):
    """Import a specific GCP disk."""
    from terraback.cli.gcp.compute.disks import import_disk
    import_disk(disk_id, output_dir)

# Network commands
@app.command("network-scan")
def network_scan(
    output_dir: Path = typer.Option("generated", "-o", "--output-dir"),
    project_id: Optional[str] = typer.Option(None, "--project-id", "-p", help="GCP project ID (uses default if not specified)"),
    with_deps: bool = typer.Option(False, "--with-deps", help="Scan with dependencies")
):
    """Scan GCP VPC networks."""
    from terraback.cli.gcp.session import get_default_project_id
    from terraback.cli.gcp.network.networks import scan_networks

    if not project_id:
        project_id = get_default_project_id()
        if not project_id:
            typer.echo("Error: No GCP project found. Set project with 'gcloud config set project' or use --project-id", err=True)
            raise typer.Exit(code=1)
    
    typer.echo(f"Scanning GCP networks in project '{project_id}'...")
    scan_networks(output_dir, project_id, with_deps)

@app.command("network-list")
def network_list(
    output_dir: Path = typer.Option("generated", "-o", "--output-dir")
):
    """List previously scanned GCP networks."""
    from terraback.cli.gcp.network.networks import list_networks
    list_networks(output_dir)

@app.command("network-import")
def network_import(
    network_id: str = typer.Argument(..., help="GCP network ID (project/name)"),
    output_dir: Path = typer.Option("generated", "-o", "--output-dir")
):
    """Import a specific GCP network."""
    from terraback.cli.gcp.network.networks import import_network
    import_network(network_id, output_dir)

# Subnet commands
@app.command("subnet-scan")
def subnet_scan(
    output_dir: Path = typer.Option("generated", "-o", "--output-dir"),
    project_id: Optional[str] = typer.Option(None, "--project-id", "-p", help="GCP project ID (uses default if not specified)"),
    region: Optional[str] = typer.Option(None, "--region", "-r", help="GCP region (scans all regions if not specified)"),
    with_deps: bool = typer.Option(False, "--with-deps", help="Scan with dependencies")
):
    """Scan GCP subnets."""
    from terraback.cli.gcp.session import get_default_project_id
    from terraback.cli.gcp.network.subnets import scan_subnets

    if not project_id:
        project_id = get_default_project_id()
        if not project_id:
            typer.echo("Error: No GCP project found. Set project with 'gcloud config set project' or use --project-id", err=True)
            raise typer.Exit(code=1)
    
    typer.echo(f"Scanning GCP subnets in project '{project_id}'...")
    if region:
        typer.echo(f"Region: {region}")
    else:
        typer.echo("Region: all regions")
    
    scan_subnets(output_dir, project_id, region, with_deps)

@app.command("subnet-list")
def subnet_list(
    output_dir: Path = typer.Option("generated", "-o", "--output-dir")
):
    """List previously scanned GCP subnets."""
    from terraback.cli.gcp.network.subnets import list_subnets
    list_subnets(output_dir)

@app.command("subnet-import")
def subnet_import(
    subnet_id: str = typer.Argument(..., help="GCP subnet ID (project/region/name)"),
    output_dir: Path = typer.Option("generated", "-o", "--output-dir")
):
    """Import a specific GCP subnet."""
    from terraback.cli.gcp.network.subnets import import_subnet
    import_subnet(subnet_id, output_dir)

# Firewall commands
@app.command("firewall-scan")
def firewall_scan(
    output_dir: Path = typer.Option("generated", "-o", "--output-dir"),
    project_id: Optional[str] = typer.Option(None, "--project-id", "-p", help="GCP project ID (uses default if not specified)"),
    with_deps: bool = typer.Option(False, "--with-deps", help="Scan with dependencies")
):
    """Scan GCP firewall rules."""
    from terraback.cli.gcp.session import get_default_project_id
    from terraback.cli.gcp.network.firewalls import scan_firewalls

    if not project_id:
        project_id = get_default_project_id()
        if not project_id:
            typer.echo("Error: No GCP project found. Set project with 'gcloud config set project' or use --project-id", err=True)
            raise typer.Exit(code=1)
    
    typer.echo(f"Scanning GCP firewall rules in project '{project_id}'...")
    scan_firewalls(output_dir, project_id, with_deps)

@app.command("firewall-list")
def firewall_list(
    output_dir: Path = typer.Option("generated", "-o", "--output-dir")
):
    """List previously scanned GCP firewall rules."""
    from terraback.cli.gcp.network.firewalls import list_firewalls
    list_firewalls(output_dir)

@app.command("firewall-import")
def firewall_import(
    firewall_id: str = typer.Argument(..., help="GCP firewall ID (project/name)"),
    output_dir: Path = typer.Option("generated", "-o", "--output-dir")
):
    """Import a specific GCP firewall rule."""
    from terraback.cli.gcp.network.firewalls import import_firewall
    import_firewall(firewall_id, output_dir)

# Storage bucket commands
@app.command("bucket-scan")
def bucket_scan(
    output_dir: Path = typer.Option("generated", "-o", "--output-dir"),
    project_id: Optional[str] = typer.Option(None, "--project-id", "-p", help="GCP project ID (uses default if not specified)"),
    with_deps: bool = typer.Option(False, "--with-deps", help="Scan with dependencies")
):
    """Scan GCP Storage buckets."""
    from terraback.cli.gcp.session import get_default_project_id
    from terraback.cli.gcp.storage.buckets import scan_buckets

    if not project_id:
        project_id = get_default_project_id()
        if not project_id:
            typer.echo("Error: No GCP project found. Set project with 'gcloud config set project' or use --project-id", err=True)
            raise typer.Exit(code=1)
    
    typer.echo(f"Scanning GCP buckets in project '{project_id}'...")
    scan_buckets(output_dir, project_id, with_deps)

@app.command("bucket-list")
def bucket_list(
    output_dir: Path = typer.Option("generated", "-o", "--output-dir")
):
    """List previously scanned GCP buckets."""
    from terraback.cli.gcp.storage.buckets import list_buckets
    list_buckets(output_dir)

@app.command("bucket-import")
def bucket_import(
    bucket_name: str = typer.Argument(..., help="GCP bucket name"),
    output_dir: Path = typer.Option("generated", "-o", "--output-dir")
):
    """Import a specific GCP bucket."""
    from terraback.cli.gcp.storage.buckets import import_bucket
    import_bucket(bucket_name, output_dir)
