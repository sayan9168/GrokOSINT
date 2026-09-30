"""Utility functions for GrokOSINT"""

import hashlib
import re
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

from rich.console import Console
from rich.panel import Panel
from rich.text import Text

console = Console()

DISCLAIMER = """
[bold red]⚠️  ETHICAL USE ONLY / শুধুমাত্র নৈতিক ব্যবহার[/bold red]

This tool collects ONLY publicly available information.
এই টুল শুধুমাত্র publicly available তথ্য সংগ্রহ করে।

• Use only on accounts/numbers you own or have explicit written authorization for.
• Stalking, doxxing, harassment, or unauthorized investigation is ILLEGAL.
• The author and contributors accept no liability for misuse.
• Always respect privacy laws (GDPR, CCPA, local laws in Bangladesh/India etc.).

By continuing you confirm you will use this tool ethically and legally.
"""


def show_disclaimer(force: bool = True) -> bool:
    """Display ethical disclaimer and optionally require confirmation."""
    console.print(Panel(DISCLAIMER, title="[bold yellow]GrokOSINT Disclaimer[/bold yellow]", border_style="red"))
    if force:
        try:
            answer = console.input("\n[bold]Do you agree to use this tool ethically? (yes/no): [/bold]").strip().lower()
            if answer not in ("yes", "y", "হ্যাঁ", "ha"):
                console.print("[red]Aborted. Ethical confirmation required.[/red]")
                return False
        except (KeyboardInterrupt, EOFError):
            console.print("\n[red]Aborted.[/red]")
            return False
    return True


def md5_hash(text: str) -> str:
    return hashlib.md5(text.strip().lower().encode()).hexdigest()


def is_valid_email(email: str) -> bool:
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return bool(re.match(pattern, email))


def normalize_phone(phone: str) -> str:
    """Remove spaces, dashes etc."""
    return re.sub(r"[^\d+]", "", phone)


def timestamp() -> str:
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def ensure_dir(path: str | Path) -> Path:
    p = Path(path)
    p.mkdir(parents=True, exist_ok=True)
    return p


def safe_get(data: dict, *keys, default=None) -> Any:
    for key in keys:
        if isinstance(data, dict):
            data = data.get(key, default)
        else:
            return default
    return data


def rate_limit(seconds: float = 1.0):
    """Simple rate limiter decorator helper."""
    def decorator(func):
        last_called = [0.0]
        def wrapper(*args, **kwargs):
            elapsed = time.time() - last_called[0]
            if elapsed < seconds:
                time.sleep(seconds - elapsed)
            result = func(*args, **kwargs)
            last_called[0] = time.time()
            return result
        return wrapper
    return decorator


def print_success(msg: str):
    console.print(f"[green]✓[/green] {msg}")


def print_error(msg: str):
    console.print(f"[red]✗[/red] {msg}")


def print_info(msg: str):
    console.print(f"[cyan]ℹ[/cyan] {msg}")


def print_warning(msg: str):
    console.print(f"[yellow]⚠[/yellow] {msg}")
