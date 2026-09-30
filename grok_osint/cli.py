"""GrokOSINT CLI - Beautiful terminal interface"""

import asyncio
from pathlib import Path
from typing import Optional

import typer
import yaml
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn

from . import __version__
from .core.reporter import Reporter
from .core.utils import show_disclaimer, print_info, print_success, print_error
from .modules.email_osint import EmailOSINT
from .modules.phone_osint import PhoneOSINT

app = typer.Typer(
    name="grokosint",
    help="GrokOSINT - Advanced Ethical OSINT for Email + Phone (Public data only)",
    add_completion=False,
    rich_markup_mode="rich",
)
console = Console()


def load_config(config_path: Optional[Path] = None) -> dict:
    paths = [
        config_path,
        Path("config.yaml"),
        Path.home() / ".config" / "grokosint" / "config.yaml",
    ]
    for p in paths:
        if p and p.exists():
            with open(p) as f:
                return yaml.safe_load(f) or {}
    return {}


@app.callback()
def main(
    ctx: typer.Context,
    version: bool = typer.Option(False, "--version", "-v", help="Show version"),
):
    if version:
        console.print(f"[bold]GrokOSINT[/bold] v{__version__}")
        raise typer.Exit()


@app.command("email")
def email_cmd(
    email: str = typer.Argument(..., help="Email address to investigate"),
    config: Optional[Path] = typer.Option(None, "--config", "-c", help="Config file path"),
    export: bool = typer.Option(True, "--export/--no-export", help="Export JSON + Markdown"),
    yes: bool = typer.Option(False, "--yes", "-y", help="Skip ethical confirmation"),
):
    """Investigate an email address (Gmail etc.)"""
    if not yes and not show_disclaimer():
        raise typer.Exit(1)

    cfg = load_config(config)
    api_keys = cfg.get("api_keys", {})
    export_dir = cfg.get("settings", {}).get("export_dir", "reports")

    osint = EmailOSINT(api_keys=api_keys)

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
        transient=True,
    ) as progress:
        progress.add_task(description="Running Email OSINT...", total=None)
        result = asyncio.run(osint.run_async(email))

    osint.display(result)

    if export:
        reporter = Reporter(export_dir)
        reporter.export_all(email_result=result, prefix="email")


@app.command("phone")
def phone_cmd(
    phone: str = typer.Argument(..., help="Phone number (with country code preferred)"),
    region: str = typer.Option("BD", "--region", "-r", help="Default region (BD, IN, US...)"),
    config: Optional[Path] = typer.Option(None, "--config", "-c"),
    export: bool = typer.Option(True, "--export/--no-export"),
    yes: bool = typer.Option(False, "--yes", "-y"),
):
    """Investigate a phone number"""
    if not yes and not show_disclaimer():
        raise typer.Exit(1)

    cfg = load_config(config)
    api_keys = cfg.get("api_keys", {})
    export_dir = cfg.get("settings", {}).get("export_dir", "reports")

    osint = PhoneOSINT(default_region=region, api_keys=api_keys)

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
        transient=True,
    ) as progress:
        progress.add_task(description="Running Phone OSINT...", total=None)
        result = asyncio.run(osint.run_async(phone, region=region))

    osint.display(result)

    if export:
        reporter = Reporter(export_dir)
        reporter.export_all(phone_result=result, prefix="phone")


@app.command("full")
def full_cmd(
    email: Optional[str] = typer.Option(None, "--email", "-e", help="Email address"),
    phone: Optional[str] = typer.Option(None, "--phone", "-p", help="Phone number"),
    region: str = typer.Option("BD", "--region", "-r"),
    config: Optional[Path] = typer.Option(None, "--config", "-c"),
    export: bool = typer.Option(True, "--export/--no-export"),
    yes: bool = typer.Option(False, "--yes", "-y"),
):
    """Run both Email + Phone OSINT together"""
    if not email and not phone:
        console.print("[red]Provide at least --email or --phone[/red]")
        raise typer.Exit(1)

    if not yes and not show_disclaimer():
        raise typer.Exit(1)

    cfg = load_config(config)
    api_keys = cfg.get("api_keys", {})
    export_dir = cfg.get("settings", {}).get("export_dir", "reports")

    email_result = None
    phone_result = None

    if email:
        print_info("=== EMAIL MODULE ===")
        eosint = EmailOSINT(api_keys=api_keys)
        email_result = asyncio.run(eosint.run_async(email))
        eosint.display(email_result)
        console.print()

    if phone:
        print_info("=== PHONE MODULE ===")
        posint = PhoneOSINT(default_region=region, api_keys=api_keys)
        phone_result = asyncio.run(posint.run_async(phone, region=region))
        posint.display(phone_result)

    if export:
        reporter = Reporter(export_dir)
        reporter.export_all(email_result=email_result, phone_result=phone_result, prefix="full")


@app.command("about")
def about():
    """About GrokOSINT"""
    console.print(Panel.fit(
        f"""[bold]GrokOSINT v{__version__}[/bold]
Advanced Ethical OSINT Tool for Email + Phone

• Publicly available data only
• Beautiful terminal UI (Rich)
• JSON + Markdown export
• Optional API keys for deeper checks
• Account existence + Paste search
• Username guesses + Possible apps
• Built for authorized research

GitHub: https://github.com/sayan9168/GrokOSINT
Author: Sayan the researcher

[red]Use ethically. Unauthorized investigation is illegal.[/red]
""",
        title="About",
        border_style="cyan",
    ))


if __name__ == "__main__":
    app()
