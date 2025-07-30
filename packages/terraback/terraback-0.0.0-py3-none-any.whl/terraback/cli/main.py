# terraback/cli/main.py
import typer
from pathlib import Path
from typing import Optional

# Clean provider imports
from terraback.cli import aws, azure

# Import command modules
from terraback.cli.commands.clean import app as clean_app
from terraback.cli.commands.list import app as list_app
from terraback.cli.commands.analyse import app as analyse_app

# Import licensing
from terraback.core.license import (
    activate_license, get_active_license, get_active_tier, get_license_status,
    require_professional, require_enterprise, check_feature_access, Tier
)

app = typer.Typer(
    name="terraback",
    help="Terraback: A tool to generate Terraform from existing cloud infrastructure.",
    no_args_is_help=True
)

# License Command Group
license_app = typer.Typer(help="Manage your Terraback license.")

@license_app.command("status")
def license_status():
    """Check the current license status and tier."""
    status = get_license_status()
    
    typer.echo(f"Active Feature Tier: {typer.style(status['active_tier'].capitalize(), bold=True)}")
    
    if status['has_license']:
        typer.secho("\nLicense Details:", fg=typer.colors.GREEN)
        typer.echo(f"  - Email: {status.get('email', 'N/A')}")
        typer.echo(f"  - Tier: {status.get('tier', 'N/A').capitalize()}")
        typer.echo(f"  - Expires: {status.get('expires', 'N/A')}")
        if status.get('order_id'):
            typer.echo(f"  - Order ID: {status.get('order_id')}")
    else:
        typer.secho("\nNo active license key found.", fg=typer.colors.YELLOW)
        typer.echo("Running in Community mode.")
        typer.echo("\nCommunity Edition includes:")
        typer.echo("  Unlimited core resources (EC2, VPC, S3, VMs, VNets, Storage)")
        typer.echo("  Basic dependency mapping")
        typer.echo("  Multi-cloud support (AWS, Azure, GCP)")
        typer.echo("  Community support via GitHub")
        typer.echo("\nTo unlock advanced services (RDS, Lambda, EKS, etc.):")
        typer.echo("  Get Migration Pass: https://terraback.io/pricing")
        typer.echo("  Activate license: terraback license activate <key>")

@license_app.command("activate")
def license_activate(key: str = typer.Argument(..., help="Your license key.")):
    """Activate a new license key."""
    if activate_license(key):
        typer.secho("License activated successfully!", fg=typer.colors.GREEN, bold=True)
        typer.echo()
        license_status()
    else:
        typer.secho("License activation failed.", fg=typer.colors.RED, bold=True)
        typer.echo("Please check that:")
        typer.echo("  - The license key is copied correctly")
        typer.echo("  - The license hasn't expired")
        typer.echo("  - You have write permissions to ~/.terraback/")
        typer.echo("\nIf you continue to have issues, contact support@terraback.io")
        raise typer.Exit(code=1)

@license_app.command("validate")
def license_validate():
    """Validate the current license and show detailed information."""
    license_data = get_active_license()
    
    if license_data:
        typer.secho("License is valid and active", fg=typer.colors.GREEN, bold=True)
        typer.echo(f"\nLicense Information:")
        typer.echo(f"  Email: {license_data.get('email', 'N/A')}")
        typer.echo(f"  Tier: {license_data.get('tier', 'N/A').capitalize()}")
        typer.echo(f"  Issued: {license_data.get('iat', 'N/A')}")
        typer.echo(f"  Expires: {license_data.get('expiry', 'N/A')}")
        
        tier = license_data.get('tier', Tier.COMMUNITY)
        if tier == Tier.PROFESSIONAL:
            typer.echo(f"\nProfessional Features Unlocked:")
            typer.echo(f"  - Advanced AWS services (RDS, Lambda, EKS, etc.)")
            typer.echo(f"  - Dependency scanning with --with-deps")
            typer.echo(f"  - Multi-account support")
            typer.echo(f"  - Priority email support")
        elif tier == Tier.ENTERPRISE:
            typer.echo(f"\nEnterprise Features Unlocked:")
            typer.echo(f"  - All Professional features")
            typer.echo(f"  - Custom scanners and integrations")
            typer.echo(f"  - SSO integration")
            typer.echo(f"  - Dedicated support")
    else:
        typer.secho("No valid license found", fg=typer.colors.RED, bold=True)
        typer.echo("\nRunning in Community mode with core features only.")
        raise typer.Exit(code=1)

# Cache Command Group
cache_app = typer.Typer(help="Manage terraback cache")

@cache_app.command("stats")
def cache_stats():
    """Show cache statistics."""
    from terraback.utils.scan_cache import get_scan_cache
    
    cache = get_scan_cache()
    stats = cache.get_stats()
    
    typer.echo("\nCache Statistics:")
    typer.echo(f"  Hit Rate: {stats['hit_rate']}")
    typer.echo(f"  Total Hits: {stats['hits']}")
    typer.echo(f"  Total Misses: {stats['misses']}")
    typer.echo(f"  Cache Size: {stats['total_size_kb']} KB")
    typer.echo(f"  Memory Cache Items: {stats['memory_cache_size']}")
    typer.echo(f"  TTL: {stats['ttl_minutes']:.0f} minutes")

@cache_app.command("clear")
def cache_clear(
    confirm: bool = typer.Option(False, "--yes", "-y", help="Skip confirmation")
):
    """Clear all cached data."""
    from terraback.utils.scan_cache import get_scan_cache
    
    if not confirm:
        confirm = typer.confirm("Are you sure you want to clear all cached data?")
    
    if confirm:
        cache = get_scan_cache()
        cache.clear()
        typer.echo("Cache cleared successfully!")
    else:
        typer.echo("Cache clear cancelled.")

@cache_app.command("invalidate")
def cache_invalidate(
    service: Optional[str] = typer.Option(None, help="Cloud service name (e.g., ec2, s3)"),
    operation: Optional[str] = typer.Option(None, help="Operation name (e.g., describe_instances)")
):
    """Invalidate specific cache entries."""
    from terraback.utils.scan_cache import get_scan_cache
    
    cache = get_scan_cache()
    count = cache.invalidate_pattern(service, operation)
    
    if service and operation:
        typer.echo(f"Invalidated {count} cache entries for {service}:{operation}")
    elif service:
        typer.echo(f"Invalidated {count} cache entries for service: {service}")
    elif operation:
        typer.echo(f"Invalidated {count} cache entries for operation: {operation}")
    else:
        typer.echo(f"Invalidated {count} cache entries")

# Add command groups to main app
app.add_typer(aws.app, name="aws", help="Amazon Web Services resources")
app.add_typer(azure.app, name="azure", help="Microsoft Azure resources")
app.add_typer(clean_app, name="clean", help="Clean generated files")
app.add_typer(list_app, name="list", help="List scanned resources")
app.add_typer(analyse_app, name="analyse", help="Analyse Terraform state")
app.add_typer(license_app, name="license", help="License management")
app.add_typer(cache_app, name="cache", help="Cache management")

@app.callback()
def main_callback():
    """Initialize providers on first command."""
    # Providers handle their own initialization
    pass

@app.command("scan-all")
def scan_all(
    provider: str = typer.Argument(..., help="Cloud provider: 'aws', 'azure', or 'gcp'"),
    output_dir: Path = typer.Option("generated", "-o", "--output-dir", help="Directory to save Terraform files"),
    profile: Optional[str] = typer.Option(None, "--profile", "-p", help="AWS profile name"),
    region: Optional[str] = typer.Option(None, "--region", "-r", help="AWS region or Azure location"),
    subscription_id: Optional[str] = typer.Option(None, "--subscription-id", "-s", help="Azure subscription ID"),
    resource_group: Optional[str] = typer.Option(None, "--resource-group", "-g", help="Azure resource group"),
    with_deps: bool = typer.Option(False, "--with-deps", help="Recursively scan dependencies (Professional feature)")
):
    """Scan all resources for a specific cloud provider."""
    provider = provider.lower()
    
    if provider == "aws":
        # Delegate to AWS scan-all
        from terraback.cli.aws import scan_all_aws
        scan_all_aws(
            output_dir=output_dir,
            profile=profile,
            region=region,
            with_deps=with_deps
        )
    elif provider == "azure":
        # Delegate to Azure scan-all
        from terraback.cli.azure import scan_all_azure
        scan_all_azure(
            output_dir=output_dir,
            subscription_id=subscription_id,
            location=region,  # region is used as location for Azure
            resource_group_name=resource_group,
            with_deps=with_deps
        )
    elif provider == "gcp":
        typer.echo("GCP support is coming soon!")
        raise typer.Exit(code=1)
    else:
        typer.echo(f"Error: Unknown provider '{provider}'. Use 'aws', 'azure', or 'gcp'.", err=True)
        raise typer.Exit(code=1)

@app.command("scan-recursive")
@require_professional
def scan_recursive(
    resource_type: str = typer.Argument(..., help="Initial resource type to scan"),
    output_dir: Path = typer.Option("generated", "-o", "--output-dir"),
    profile: Optional[str] = typer.Option(None, "--profile", "-p"),
    region: Optional[str] = typer.Option(None, "--region", "-r"),
    subscription_id: Optional[str] = typer.Option(None, "--subscription-id", "-s"),
    use_cache: bool = typer.Option(True, "--cache/--no-cache")
):
    """(Professional Feature) Recursively scan cloud resources with smart dependency resolution."""
    from datetime import timedelta
    from terraback.utils.scan_cache import get_scan_cache
    from terraback.utils.cross_scan_registry import recursive_scan as base_recursive_scan

    # Normalize resource type
    resource_type_map = {
        'vm': 'azure_virtual_machine',
        'vms': 'azure_virtual_machine',
        'disk': 'azure_managed_disk',
        'disks': 'azure_managed_disk',
        'vnet': 'azure_virtual_network',
        'vnets': 'azure_virtual_network',
        'subnet': 'azure_subnet',
        'subnets': 'azure_subnet',
        'nsg': 'azure_network_security_group',
        'nsgs': 'azure_network_security_group',
        'instance': 'ec2',
        'instances': 'ec2',
        'bucket': 's3_bucket',
        'buckets': 's3_bucket',
    }
    
    normalized_type = resource_type_map.get(resource_type.lower(), resource_type.lower())
    typer.echo(f"Starting Professional recursive scan for '{normalized_type}'...")

    is_azure = normalized_type.startswith('azure_')
    
    kwargs = {
        'resource_type': normalized_type,
        'output_dir': output_dir
    }
    
    if is_azure:
        from terraback.cli.azure.session import get_default_subscription_id
        if not subscription_id:
            subscription_id = get_default_subscription_id()
            if not subscription_id:
                typer.echo("Error: No Azure subscription found. Please run 'az login'", err=True)
                raise typer.Exit(code=1)
        kwargs['subscription_id'] = subscription_id
        kwargs['location'] = region
    else:
        # AWS
        from terraback.cli.common.defaults import get_aws_defaults
        defaults = get_aws_defaults()
        kwargs['profile'] = profile or defaults['profile']
        kwargs['region'] = region or defaults['region']
    
    if use_cache:
        cache = get_scan_cache(
            cache_dir=output_dir / ".terraback" / "cache",
            ttl=timedelta(minutes=60)
        )
        typer.echo("Caching enabled (TTL: 60 minutes)")
    
    base_recursive_scan(**kwargs)
    
    if use_cache:
        stats = cache.get_stats()
        typer.echo(f"\nCache Statistics:")
        typer.echo(f"  Hit Rate: {stats['hit_rate']}")
        typer.echo(f"  Cache Size: {stats['total_size_kb']} KB")

@app.command("auth-check")
def check_auth():
    """Check authentication status for all cloud providers."""
    typer.echo("Checking cloud authentication status...\n")
    
    # Check AWS
    try:
        from terraback.cli.aws.session import get_boto_session
        session = get_boto_session()
        sts = session.client('sts')
        identity = sts.get_caller_identity()
        typer.echo("AWS: Authenticated")
        typer.echo(f"  Account: {identity['Account']}")
        typer.echo(f"  User/Role: {identity['Arn'].split('/')[-1]}")
        typer.echo(f"  Region: {session.region_name}")
    except Exception:
        typer.echo("AWS: Not authenticated (run: aws configure)")
    
    # Check Azure
    try:
        from terraback.cli.azure.session import get_default_subscription_id
        sub_id = get_default_subscription_id()
        if sub_id:
            typer.echo("\nAzure: Authenticated")
            typer.echo(f"  Subscription: {sub_id}")
        else:
            typer.echo("\nAzure: Not authenticated (run: az login)")
    except Exception:
        typer.echo("\nAzure: Not authenticated (run: az login)")

@app.command("upgrade")
def upgrade_info():
    """Show information about upgrading to Professional features."""
    current_tier = get_active_tier()
    
    if current_tier == Tier.COMMUNITY:
        typer.echo("Upgrade to Professional for Advanced Features\n")
        
        typer.echo("Your Current Plan: Community Edition (Free)")
        typer.echo("  - Unlimited core resources (EC2, VPC, S3, VMs, VNets, Storage)")
        typer.echo("  - Multi-cloud support (AWS, Azure, GCP)")
        typer.echo("  - Basic dependency mapping\n")
        
        typer.echo("Unlock with Migration Pass ($299 for 3 months):")
        typer.echo("  - Advanced AWS services (RDS, Lambda, EKS, ALB, Route53, etc.)")
        typer.echo("  - Recursive dependency scanning (--with-deps)")
        typer.echo("  - Multi-account/subscription support")
        typer.echo("  - Priority email support")
        typer.echo("  - Advanced caching and performance features\n")
        
        typer.echo("Get Migration Pass: https://terraback.io/pricing")
        typer.echo("Enterprise needs: sales@terraback.io")
    elif current_tier == Tier.PROFESSIONAL:
        typer.secho("You have Professional access!", fg=typer.colors.GREEN, bold=True)
        typer.echo("All advanced features are unlocked.")
    elif current_tier == Tier.ENTERPRISE:
        typer.secho("You have Enterprise access!", fg=typer.colors.GREEN, bold=True)
        typer.echo("All features including enterprise support are available.")

if __name__ == "__main__":
    app()