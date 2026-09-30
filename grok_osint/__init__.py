"""
GrokOSINT - Advanced Ethical OSINT Tool for Email + Phone Intelligence
Publicly available data only. Authorized use only.
"""

__version__ = "1.0.0"
__author__ = "Sayan the researcher"
__license__ = "MIT"

from .core.validator import EmailValidator, PhoneValidator
from .modules.email_osint import EmailOSINT
from .modules.phone_osint import PhoneOSINT

__all__ = [
    "EmailValidator",
    "PhoneValidator",
    "EmailOSINT",
    "PhoneOSINT",
]
