"""GrokOSINT v3 — Extreme Kali-style Ethical OSINT Arsenal"""

__version__ = "3.0.0"
__author__ = "Sayan the researcher"
__license__ = "MIT"

from .core.validator import EmailValidator, PhoneValidator
from .modules.email_osint import EmailOSINT
from .modules.phone_osint import PhoneOSINT
from .modules.username_osint import UsernameOSINT
from .modules.domain_osint import DomainOSINT
from .modules.ip_osint import IPOSINT
from .modules.archive_osint import ArchiveOSINT

__all__ = [
    "EmailValidator", "PhoneValidator",
    "EmailOSINT", "PhoneOSINT", "UsernameOSINT",
    "DomainOSINT", "IPOSINT", "ArchiveOSINT",
]
