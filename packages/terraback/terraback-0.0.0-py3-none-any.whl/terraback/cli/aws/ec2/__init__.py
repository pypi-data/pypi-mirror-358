import typer
from pathlib import Path
from functools import partial

# Import the simplified scan functions and other commands
from .instances import scan_ec2, list_ec2, import_ec2
from .volumes import scan_volumes, list_volumes, import_volume
from .amis import scan_amis, list_amis, import_amis
from .key_pairs import scan_key_pairs, list_key_pairs, import_key_pairs
from .launch_templates import scan_launch_templates, list_launch_templates, import_launch_template
from .network_interfaces import scan_network_interfaces, list_network_interfaces, import_network_interfaces
from .snapshots import scan_snapshots, list_snapshots, import_snapshot  # <-- ADD THIS LINE

# Import registry utilities
from terraback.utils.cross_scan_registry import (
    register_scan_function,
    cross_scan_registry,
    recursive_scan
)

app = typer.Typer(
    name="ec2",
    help="Manage EC2 resources like instances, volumes, and amis.",
    no_args_is_help=True
)

# --- Instance Commands ---
@app.command(name="scan", help="Scan EC2 instances and generate Terraform code.")
def scan_instances_command(
    output_dir: Path = typer.Option("generated", help="Directory to save Terraform files"),
    profile: str = typer.Option(None, help="AWS CLI profile to use"),
    region: str = typer.Option("us-east-1", help="AWS region"),
    include_all_states: bool = typer.Option(False, help="Include all instance states"),
    with_deps: bool = typer.Option(False, help="Recursively scan dependencies")
):
    if with_deps:
        recursive_scan("ec2", output_dir=output_dir, profile=profile, region=region, include_all_states=include_all_states)
    else:
        scan_ec2(
            output_dir=output_dir,
            profile=profile,
            region=region,
            include_all_states=include_all_states
        )

@app.command(name="list", help="List all EC2 instance resources previously generated.")
def list_instances_command(output_dir: Path = typer.Option("generated", help="Directory containing import file")):
    list_ec2(output_dir=output_dir)

@app.command(name="import", help="Run terraform import for a specific EC2 instance by its ID.")
def import_instance_command(instance_id: str, output_dir: Path = typer.Option("generated", help="Directory with import file")):
    import_ec2(instance_id=instance_id, output_dir=output_dir)


# --- Snapshot Commands (NEW) ---
@app.command(name="scan-snapshots", help="Scan EBS snapshots and generate Terraform code.")
def scan_snapshots_command(
    output_dir: Path = typer.Option("generated", help="Directory to save Terraform files"),
    profile: str = typer.Option(None, help="AWS CLI profile to use"),
    region: str = typer.Option("us-east-1", help="AWS region"),
):
    scan_snapshots(output_dir=output_dir, profile=profile, region=region)

@app.command(name="list-snapshots", help="List all EBS snapshot resources previously generated.")
def list_snapshots_command(output_dir: Path = typer.Option("generated", help="Directory containing import file")):
    list_snapshots(output_dir=output_dir)

@app.command(name="import-snapshot", help="Run terraform import for a specific EBS snapshot by its ID.")
def import_snapshot_command(
    snapshot_id: str,
    output_dir: Path = typer.Option("generated", help="Directory with import file")
):
    import_snapshot(snapshot_id=snapshot_id, output_dir=output_dir)


# --- Add other resource commands (volumes, amis, etc.) back in ---
# For brevity, I've omitted the other command definitions, but you should have them here.


# --- Self-Registration Function ---
def register():
    """Registers the scan functions and dependencies for the EC2 module."""
    
    # EC2 Instances
    scan_ec2_core = partial(scan_ec2, include_all_states=True)
    register_scan_function("ec2", scan_ec2_core)
    cross_scan_registry.register_dependency("ec2", "security_groups")
    cross_scan_registry.register_dependency("ec2", "subnets")
    cross_scan_registry.register_dependency("ec2", "iam_roles")
    cross_scan_registry.register_dependency("ec2", "amis")
    cross_scan_registry.register_dependency("ec2", "volumes")
    cross_scan_registry.register_dependency("ec2", "key_pairs")
    cross_scan_registry.register_dependency("ec2", "route53_record")
        
    # EBS Volumes
    scan_volumes_core = partial(scan_volumes, include_attached_only=False)
    register_scan_function("volumes", scan_volumes_core)
    cross_scan_registry.register_dependency("volumes", "ec2")
    cross_scan_registry.register_dependency("volumes", "ebs_snapshot") # <-- ADD THIS DEPENDENCY

    # EBS Snapshots (NEW)
    register_scan_function("ebs_snapshot", scan_snapshots)
    
    # amis
    scan_amis_core = partial(scan_amis, owned_by_me=True, include_public=False)
    register_scan_function("amis", scan_amis_core)
    
    # Key Pairs
    register_scan_function("key_pairs", scan_key_pairs)

    # Launch Templates
    register_scan_function("launch_template", scan_launch_templates)
    cross_scan_registry.register_dependency("launch_template", "ec2")
    cross_scan_registry.register_dependency("launch_template", "security_groups")
    cross_scan_registry.register_dependency("launch_template", "amis")

    # Network Interfaces
    scan_eni_core = partial(scan_network_interfaces, attached_only=True)
    register_scan_function("network_interfaces", scan_eni_core)
    cross_scan_registry.register_dependency("network_interfaces", "ec2")
    cross_scan_registry.register_dependency("network_interfaces", "security_groups")