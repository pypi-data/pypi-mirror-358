"""
SSL certificate management commands for CodeGuard.

Provides CLI commands for managing CodeGuard's SSL certificates,
including CA export and certificate status.
"""

import logging
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.table import Table

from ...core.infrastructure.ssl_service import SSLServiceError, get_ssl_service
from ...core.runtime import get_default_console

logger = logging.getLogger(__name__)
console = get_default_console()

ssl_app = typer.Typer(name="ssl", help="SSL certificate management for CodeGuard services")


@ssl_app.command("export-ca")
def export_ca(
    output_path: Optional[Path] = typer.Option(
        None,
        "--output",
        "-o",
        help="Output path for CA certificate (default: show current location)",
    )
):
    """
    Export CodeGuard CA certificate for installation.

    This certificate must be installed in your system's trust store
    to use HTTPS-enabled CodeGuard services like the proxy server.
    """
    try:
        ssl_service = get_ssl_service()
        ca_path = ssl_service.export_ca_certificate()

        if output_path:
            # Copy to specified location
            import shutil

            output_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(ca_path, output_path)
            console.print(f"📋 CA certificate copied to: [bold cyan]{output_path}[/bold cyan]")
            ca_display_path = output_path
        else:
            ca_display_path = ca_path
            console.print(f"📋 CodeGuard CA Certificate: [bold cyan]{ca_display_path}[/bold cyan]")

        console.print("\n🔧 [bold yellow]Installation Instructions:[/bold yellow]")
        console.print(
            "┌─────────────────────────────────────────────────────────────────────────────┐"
        )
        console.print(
            "│ [bold]macOS Option 1 (GUI):[/bold]                                                     │"
        )
        console.print(
            f'│   1. Run: [cyan]open "{ca_display_path}"[/cyan]                              │'
        )
        console.print(
            "│   2. In Keychain Access → Add to 'System' keychain                        │"
        )
        console.print(
            "│   3. Double-click the certificate → Trust → SSL: Always Trust             │"
        )
        console.print(
            "│   4. Close window and enter your password when prompted                    │"
        )
        console.print(
            "│                                                                             │"
        )
        console.print(
            "│ [bold]macOS Option 2 (Command Line):[/bold]                                            │"
        )
        console.print(
            f"│   [cyan]sudo security add-trusted-cert -d -r trustRoot \\[/cyan]                      │"
        )
        console.print(
            f'│   [cyan]  -k /Library/Keychains/System.keychain "{ca_display_path}"[/cyan]          │'
        )
        console.print(
            "│                                                                             │"
        )
        console.print(
            "│ [bold]Linux:[/bold]                                                                     │"
        )
        console.print(
            f'│   [cyan]sudo cp "{ca_display_path}" /usr/local/share/ca-certificates/[/cyan]        │'
        )
        console.print(
            "│   [cyan]sudo update-ca-certificates[/cyan]                                             │"
        )
        console.print(
            "│                                                                             │"
        )
        console.print(
            "│ [bold]Windows:[/bold]                                                                   │"
        )
        console.print(
            "│   1. Right-click the .crt file → Install Certificate                      │"
        )
        console.print(
            "│   2. Choose 'Local Machine' → Next                                         │"
        )
        console.print(
            "│   3. Choose 'Place all certificates in the following store'               │"
        )
        console.print(
            "│   4. Browse → Trusted Root Certification Authorities → OK                 │"
        )
        console.print(
            "└─────────────────────────────────────────────────────────────────────────────┘"
        )

        console.print(
            "\n✅ [bold green]After installation, all CodeGuard HTTPS services will be trusted![/bold green]"
        )

    except SSLServiceError as e:
        console.print(f"❌ [bold red]SSL Error:[/bold red] {e}")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"❌ [bold red]Unexpected error:[/bold red] {e}")
        logger.exception("Failed to export CA certificate")
        raise typer.Exit(1)


@ssl_app.command("status")
def ssl_status():
    """
    Show SSL certificate status and information.

    Displays information about the CodeGuard CA certificate
    and any generated service certificates.
    """
    try:
        ssl_service = get_ssl_service()
        ca_info = ssl_service.get_ca_info()

        # Create status table
        table = Table(title="CodeGuard SSL Certificate Status", show_header=True)
        table.add_column("Property", style="cyan", width=20)
        table.add_column("Value", style="white")

        if ca_info["status"] == "exists":
            table.add_row("CA Status", "✅ Created")
            table.add_row("CA Path", ca_info["path"])
            table.add_row("Subject", ca_info["subject"])
            table.add_row("Valid From", ca_info["not_valid_before"][:10])  # Date only
            table.add_row("Valid Until", ca_info["not_valid_after"][:10])  # Date only
            table.add_row("Serial Number", ca_info["serial_number"])

            # Check if CA is close to expiration
            from datetime import datetime

            valid_until = datetime.fromisoformat(ca_info["not_valid_after"].replace("Z", "+00:00"))
            days_until_expiry = (valid_until - datetime.now(valid_until.tzinfo)).days

            if days_until_expiry < 30:
                table.add_row("⚠️  Warning", f"CA expires in {days_until_expiry} days")
            elif days_until_expiry < 365:
                table.add_row("Notice", f"CA expires in {days_until_expiry} days")

        elif ca_info["status"] == "not_created":
            table.add_row("CA Status", "❌ Not Created")
            table.add_row("CA Path", ca_info["path"])
            table.add_row("Note", "Run 'codeguard ssl export-ca' to create")

        else:  # error
            table.add_row("CA Status", "❌ Error")
            table.add_row("Error", ca_info.get("error", "Unknown error"))
            table.add_row("CA Path", ca_info["path"])

        console.print(table)

        # Show service certificates if CA exists
        if ca_info["status"] == "exists":
            console.print("\n📁 [bold]Service Certificates:[/bold]")
            cert_dir = Path(ca_info["path"]).parent

            service_certs = []
            for cert_file in cert_dir.glob("*.crt"):
                if cert_file.name != "codeguard-ca.crt":
                    service_name = cert_file.stem
                    key_file = cert_dir / f"{service_name}.key"

                    if key_file.exists():
                        service_certs.append(service_name)

            if service_certs:
                for service in service_certs:
                    console.print(f"  • {service}")
            else:
                console.print("  [dim]No service certificates generated yet[/dim]")

        # Show installation status
        console.print("\n🔧 [bold]Installation Status:[/bold]")
        if ca_info["status"] == "exists":
            console.print("  CA certificate is ready for installation")
            console.print(
                "  Run [cyan]codeguard ssl export-ca[/cyan] for installation instructions"
            )
        else:
            console.print("  CA certificate needs to be created first")

    except SSLServiceError as e:
        console.print(f"❌ [bold red]SSL Error:[/bold red] {e}")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"❌ [bold red]Unexpected error:[/bold red] {e}")
        logger.exception("Failed to get SSL status")
        raise typer.Exit(1)


@ssl_app.command("regenerate")
def regenerate_ca(
    force: bool = typer.Option(
        False, "--force", "-f", help="Force regeneration even if CA already exists"
    )
):
    """
    Regenerate the CodeGuard CA certificate.

    This will create a new CA certificate and invalidate all existing
    service certificates. Use with caution as it will require reinstalling
    the CA certificate in all systems.
    """
    try:
        ssl_service = get_ssl_service()
        ca_info = ssl_service.get_ca_info()

        if ca_info["status"] == "exists" and not force:
            console.print("⚠️  [bold yellow]CA certificate already exists![/bold yellow]")
            console.print("This will invalidate all existing service certificates.")
            console.print("Run with --force to proceed anyway.")
            raise typer.Exit(1)

        # Remove existing certificates
        cert_dir = Path(ssl_service.cert_dir)
        for cert_file in cert_dir.glob("*.crt"):
            cert_file.unlink()
            console.print(f"Removed: {cert_file.name}")

        for key_file in cert_dir.glob("*.key"):
            key_file.unlink()
            console.print(f"Removed: {key_file.name}")

        # Regenerate CA
        ssl_service.ensure_ca_exists()
        ca_path = ssl_service.export_ca_certificate()

        console.print(f"✅ [bold green]New CA certificate generated:[/bold green] {ca_path}")
        console.print("\n⚠️  [bold yellow]Important:[/bold yellow]")
        console.print("1. You must reinstall the CA certificate in all systems")
        console.print("2. Restart any running CodeGuard services")
        console.print("3. Run [cyan]codeguard ssl export-ca[/cyan] for installation instructions")

    except SSLServiceError as e:
        console.print(f"❌ [bold red]SSL Error:[/bold red] {e}")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"❌ [bold red]Unexpected error:[/bold red] {e}")
        logger.exception("Failed to regenerate CA certificate")
        raise typer.Exit(1)
