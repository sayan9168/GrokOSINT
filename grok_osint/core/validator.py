"""Input validation for email and phone numbers"""

import re
from dataclasses import dataclass
from typing import Optional

import phonenumbers
from phonenumbers import NumberParseException, PhoneNumberFormat, carrier, geocoder, timezone
from phonenumbers.phonenumberutil import number_type, PhoneNumberType

from .utils import is_valid_email, normalize_phone


@dataclass
class EmailValidationResult:
    is_valid: bool
    email: str
    local_part: str
    domain: str
    is_gmail: bool
    is_disposable: bool
    reason: Optional[str] = None


@dataclass
class PhoneValidationResult:
    is_valid: bool
    original: str
    e164: Optional[str]
    national: Optional[str]
    international: Optional[str]
    country_code: Optional[int]
    country_name: Optional[str]
    region: Optional[str]
    carrier_name: Optional[str]
    number_type: Optional[str]
    timezones: list[str]
    is_possible: bool
    reason: Optional[str] = None


# Common disposable email domains (partial list for offline check)
DISPOSABLE_DOMAINS = {
    "mailinator.com", "guerrillamail.com", "tempmail.com", "10minutemail.com",
    "throwaway.email", "yopmail.com", "maildrop.cc", "temp-mail.org",
    "fakeinbox.com", "sharklasers.com", "guerrillamailblock.com", "trashmail.com",
    "getnada.com", "tempail.com", "dispostable.com", "mailnesia.com",
}


class EmailValidator:
    def __init__(self):
        self.disposable = DISPOSABLE_DOMAINS

    def validate(self, email: str) -> EmailValidationResult:
        email = email.strip().lower()
        if not is_valid_email(email):
            return EmailValidationResult(
                is_valid=False,
                email=email,
                local_part="",
                domain="",
                is_gmail=False,
                is_disposable=False,
                reason="Invalid email format"
            )

        local, domain = email.rsplit("@", 1)
        is_gmail = domain in ("gmail.com", "googlemail.com")
        is_disposable = domain in self.disposable

        return EmailValidationResult(
            is_valid=True,
            email=email,
            local_part=local,
            domain=domain,
            is_gmail=is_gmail,
            is_disposable=is_disposable,
            reason=None
        )


class PhoneValidator:
    def __init__(self, default_region: str = "BD"):
        """default_region = BD for Bangladesh, IN for India, etc."""
        self.default_region = default_region

    def validate(self, phone: str, region: Optional[str] = None) -> PhoneValidationResult:
        phone = normalize_phone(phone)
        region = region or self.default_region

        try:
            parsed = phonenumbers.parse(phone, region)
        except NumberParseException as e:
            return PhoneValidationResult(
                is_valid=False,
                original=phone,
                e164=None,
                national=None,
                international=None,
                country_code=None,
                country_name=None,
                region=None,
                carrier_name=None,
                number_type=None,
                timezones=[],
                is_possible=False,
                reason=str(e)
            )

        is_valid = phonenumbers.is_valid_number(parsed)
        is_possible = phonenumbers.is_possible_number(parsed)

        e164 = phonenumbers.format_number(parsed, PhoneNumberFormat.E164) if is_valid or is_possible else None
        national = phonenumbers.format_number(parsed, PhoneNumberFormat.NATIONAL) if is_valid or is_possible else None
        international = phonenumbers.format_number(parsed, PhoneNumberFormat.INTERNATIONAL) if is_valid or is_possible else None

        country_code = parsed.country_code
        country_name = geocoder.country_name_for_number(parsed, "en")
        region_desc = geocoder.description_for_number(parsed, "en")
        carrier_name = carrier.name_for_number(parsed, "en") or None

        ntype = number_type(parsed)
        type_map = {
            PhoneNumberType.MOBILE: "Mobile",
            PhoneNumberType.FIXED_LINE: "Fixed Line",
            PhoneNumberType.FIXED_LINE_OR_MOBILE: "Fixed or Mobile",
            PhoneNumberType.TOLL_FREE: "Toll Free",
            PhoneNumberType.PREMIUM_RATE: "Premium Rate",
            PhoneNumberType.SHARED_COST: "Shared Cost",
            PhoneNumberType.VOIP: "VoIP",
            PhoneNumberType.PERSONAL_NUMBER: "Personal",
            PhoneNumberType.PAGER: "Pager",
            PhoneNumberType.UAN: "UAN",
            PhoneNumberType.VOICEMAIL: "Voicemail",
            PhoneNumberType.UNKNOWN: "Unknown",
        }
        number_type_str = type_map.get(ntype, "Unknown")

        tzs = list(timezone.time_zones_for_number(parsed))

        return PhoneValidationResult(
            is_valid=is_valid,
            original=phone,
            e164=e164,
            national=national,
            international=international,
            country_code=country_code,
            country_name=country_name or None,
            region=region_desc or None,
            carrier_name=carrier_name,
            number_type=number_type_str,
            timezones=tzs,
            is_possible=is_possible,
            reason=None if is_valid else "Number is possible but not confirmed valid"
        )
