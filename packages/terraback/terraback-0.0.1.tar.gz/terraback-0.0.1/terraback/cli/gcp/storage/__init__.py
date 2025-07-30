# terraback/cli/gcp/storage/__init__.py
import typer
from pathlib import Path
from typing import Optional

from . import buckets
from .buckets import scan_gcp_buckets
from terraback.utils.cross_scan_registry import register_scan_function, cross_scan_registry

app = typer.Typer(
    name="storage",
    help="Work with GCP Storage resources.",
    no_args_is_help=True
)

def register():
    """Register storage resources with cross-scan registry."""
    # Buckets
    register_scan_function("gcp_bucket", scan_gcp_buckets)
    
    # Bucket Dependencies (if any)
    # GCP buckets are fairly standalone, but could have IAM dependencies

# Add sub-commands
app.add_typer(buckets.app, name="bucket")

@app.command("scan-all")
def scan_all_storage(
    output_dir: Path = typer.Option("generated", "-o", "--output-dir", help="Directory for generated Terraform files."),
    project_id: Optional[str] = typer.Option(None, "--project-id", "-p", help="GCP Project ID.", envvar="GOOGLE_CLOUD_PROJECT"),
    with_deps: bool = typer.Option(False, "--with-deps", help="Recursively scan dependencies")
):
    """Scan all GCP storage resources."""
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
            "gcp_bucket",
            output_dir=output_dir,
            project_id=project_id
        )
    else:
        # Scan buckets
        buckets.scan_buckets(
            output_dir=output_dir,
            project_id=project_id,
            with_deps=False
        )