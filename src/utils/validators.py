"""
Consolidated Utilities Module for Anubis Intelligence Platform
Includes logging, validation, and database management
"""

import json
import logging
import logging.handlers
import re
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from pythonjsonlogger import jsonlogger

from config import LOGS_DIR, config


# ============================================================================
# LOGGING
# ============================================================================


class RavenFormatter(logging.Formatter):
    """Custom formatter for Raven logs"""

    def format(self, record: logging.LogRecord) -> str:
        if not hasattr(record, "user_id"):
            record.user_id = "SYSTEM"
        if not hasattr(record, "session_id"):
            record.session_id = "UNKNOWN"
        return super().format(record)


class RavenLogger:
    """Main logger singleton for Anubis Intelligence Platform"""

    _instance: Optional["RavenLogger"] = None

    def __new__(cls) -> "RavenLogger":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self.logger = logging.getLogger("raven")
        self._setup_handlers()
        self._initialized = True

    def _setup_handlers(self) -> None:
        LOGS_DIR.mkdir(parents=True, exist_ok=True)
        log_level = getattr(logging, config.logging.log_level.upper(), logging.INFO)
        self.logger.setLevel(log_level)
        self.logger.handlers.clear()

        # File handler
        log_file = Path(config.logging.log_file)
        log_file.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=config.logging.max_log_size_mb * 1024 * 1024,
            backupCount=config.logging.backup_count,
        )

        file_formatter = (
            jsonlogger.JsonFormatter("%(timestamp)s %(level)s %(name)s %(message)s")
            if config.logging.json_logging
            else RavenFormatter(config.logging.format)
        )
        file_handler.setFormatter(file_formatter)
        self.logger.addHandler(file_handler)

        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_formatter = logging.Formatter(
            "[%(levelname)s] %(asctime)s - %(name)s - %(message)s"
        )
        console_handler.setFormatter(console_formatter)
        self.logger.addHandler(console_handler)

    def debug(self, message: str, **kwargs) -> None:
        self.logger.debug(message, **kwargs)

    def info(self, message: str, **kwargs) -> None:
        self.logger.info(message, **kwargs)

    def warning(self, message: str, **kwargs) -> None:
        self.logger.warning(message, **kwargs)

    def error(self, message: str, **kwargs) -> None:
        self.logger.error(message, **kwargs)

    def critical(self, message: str, **kwargs) -> None:
        self.logger.critical(message, **kwargs)

    def exception(self, message: str, **kwargs) -> None:
        self.logger.exception(message, **kwargs)


logger = RavenLogger()


# ============================================================================
# VALIDATION
# ============================================================================


@dataclass
class ValidationResult:
    """Result of a validation operation"""

    is_valid: bool
    errors: List[str] = None
    warnings: List[str] = None
    sanitized_data: Dict[str, Any] = None

    def __post_init__(self):
        if self.errors is None:
            self.errors = []
        if self.warnings is None:
            self.warnings = []
        if self.sanitized_data is None:
            self.sanitized_data = {}

    def add_error(self, error: str) -> None:
        self.errors.append(error)
        self.is_valid = False

    def add_warning(self, warning: str) -> None:
        self.warnings.append(warning)


class StringValidator:
    """Validates and sanitizes string inputs"""

    MAX_NAME_LENGTH = 200
    MAX_TEXT_LENGTH = 10000
    MAX_SHORT_TEXT = 500
    MIN_NAME_LENGTH = 2

    NAME_PATTERN = re.compile(r"^[a-zA-Z\s\-\'\.]+$")
    EMAIL_PATTERN = re.compile(
        r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    )
    PHONE_PATTERN = re.compile(r"^\+?1?\d{9,15}$")
    IP_PATTERN = re.compile(
        r"^(\d{1,3}\.){3}\d{1,3}$|^(?:[0-9a-fA-F]{0,4}:){2,7}[0-9a-fA-F]{0,4}$"
    )
    URL_PATTERN = re.compile(
        r"^https?://(?:www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b(?:[-a-zA-Z0-9()@:%_\+.~#?&//=]*)$"
    )
    ADMIRALTY_CODE_PATTERN = re.compile(r"^[A-F][1-4]$")

    @staticmethod
    def sanitize_input(text: str, max_length: int = MAX_TEXT_LENGTH) -> str:
        if not isinstance(text, str):
            return str(text)
        text = text.replace("\x00", "")
        text = " ".join(text.split())
        if len(text) > max_length:
            text = text[:max_length]
        return text

    @classmethod
    def validate_name(cls, name: str) -> ValidationResult:
        result = ValidationResult(is_valid=True)
        if not isinstance(name, str):
            result.add_error("Name must be a string")
            return result
        name = cls.sanitize_input(name, cls.MAX_NAME_LENGTH)
        if not name or len(name) < cls.MIN_NAME_LENGTH:
            result.add_error(f"Name must be at least {cls.MIN_NAME_LENGTH} characters")
        if len(name) > cls.MAX_NAME_LENGTH:
            result.add_error(f"Name must not exceed {cls.MAX_NAME_LENGTH} characters")
        result.sanitized_data["name"] = name
        return result

    @classmethod
    def validate_email(cls, email: str) -> ValidationResult:
        result = ValidationResult(is_valid=True)
        if not isinstance(email, str):
            result.add_error("Email must be a string")
            return result
        email = cls.sanitize_input(email, cls.MAX_SHORT_TEXT).lower()
        if not cls.EMAIL_PATTERN.match(email):
            result.add_error("Invalid email format")
        if len(email) > 254:
            result.add_error("Email exceeds maximum length")
        result.sanitized_data["email"] = email
        return result

    @classmethod
    def validate_phone(cls, phone: str) -> ValidationResult:
        result = ValidationResult(is_valid=True)
        if not isinstance(phone, str):
            result.add_error("Phone must be a string")
            return result
        phone_clean = re.sub(r"[\s\-\(\)\.]+", "", phone)
        if not cls.PHONE_PATTERN.match(phone_clean):
            result.add_error("Invalid phone number format")
        result.sanitized_data["phone"] = phone_clean
        return result

    @classmethod
    def validate_ip_address(cls, ip: str) -> ValidationResult:
        result = ValidationResult(is_valid=True)
        if not isinstance(ip, str):
            result.add_error("IP address must be a string")
            return result
        ip = cls.sanitize_input(ip, 50)
        if not cls.IP_PATTERN.match(ip):
            result.add_error("Invalid IP address format")
        result.sanitized_data["ip"] = ip
        return result

    @classmethod
    def validate_url(cls, url: str) -> ValidationResult:
        result = ValidationResult(is_valid=True)
        if not isinstance(url, str):
            result.add_error("URL must be a string")
            return result
        url = cls.sanitize_input(url, 2048)
        if not cls.URL_PATTERN.match(url):
            result.add_error("Invalid URL format")
        result.sanitized_data["url"] = url
        return result

    @classmethod
    def validate_admiralty_code(cls, code: str) -> ValidationResult:
        result = ValidationResult(is_valid=True)
        if not isinstance(code, str):
            result.add_error("Admiralty Code must be a string")
            return result
        code = cls.sanitize_input(code, 10).upper()
        if not cls.ADMIRALTY_CODE_PATTERN.match(code):
            result.add_error("Invalid Admiralty Code format. Use format like A1, B2, C3.")
        result.sanitized_data["code"] = code
        return result


class DateValidator:
    """Validates and parses date inputs"""

    SUPPORTED_FORMATS = [
        "%Y-%m-%d",
        "%d-%m-%Y",
        "%d/%m/%Y",
        "%Y/%m/%d",
        "%d.%m.%Y",
        "%Y.%m.%d",
    ]

    @classmethod
    def validate_date(cls, date_str: str) -> ValidationResult:
        result = ValidationResult(is_valid=True)
        if not isinstance(date_str, str):
            result.add_error("Date must be a string")
            return result

        date_str = date_str.strip()
        parsed_date = None

        for fmt in cls.SUPPORTED_FORMATS:
            try:
                parsed_date = datetime.strptime(date_str, fmt)
                break
            except ValueError:
                continue

        if parsed_date is None:
            result.add_error(
                f"Invalid date format. Supported: {', '.join(cls.SUPPORTED_FORMATS)}"
            )
            return result

        if parsed_date > datetime.now():
            result.add_warning("Date appears to be in the future")

        result.sanitized_data["date"] = parsed_date.strftime("%Y-%m-%d")
        return result

    @classmethod
    def validate_date_range(cls, start_date: str, end_date: str) -> ValidationResult:
        result = ValidationResult(is_valid=True)
        start_result = cls.validate_date(start_date)
        end_result = cls.validate_date(end_date)

        if not start_result.is_valid:
            result.errors.extend(["Start date: " + e for e in start_result.errors])
        if not end_result.is_valid:
            result.errors.extend(["End date: " + e for e in end_result.errors])

        if result.is_valid:
            start = datetime.strptime(start_result.sanitized_data["date"], "%Y-%m-%d")
            end = datetime.strptime(end_result.sanitized_data["date"], "%Y-%m-%d")
            if start > end:
                result.add_error("Start date must be before end date")

        return result


class ImageValidator:
    """Validates image files"""

    ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png", "webp", "gif"}
    MAX_FILE_SIZE_MB = 50
    MIN_WIDTH = 100
    MIN_HEIGHT = 100
    MAX_WIDTH = 4000
    MAX_HEIGHT = 4000

    @classmethod
    def validate_image_file(cls, file_path: Path) -> ValidationResult:
        result = ValidationResult(is_valid=True)
        if not isinstance(file_path, (str, Path)):
            result.add_error("File path must be a string or Path object")
            return result

        file_path = Path(file_path)
        if not file_path.exists():
            result.add_error(f"File does not exist: {file_path}")
            return result

        ext = file_path.suffix.lstrip(".").lower()
        if ext not in cls.ALLOWED_EXTENSIONS:
            result.add_error(
                f"Invalid image format. Allowed: {', '.join(cls.ALLOWED_EXTENSIONS)}"
            )

        file_size_mb = file_path.stat().st_size / (1024 * 1024)
        if file_size_mb > cls.MAX_FILE_SIZE_MB:
            result.add_error(
                f"File size ({file_size_mb:.2f}MB) exceeds maximum ({cls.MAX_FILE_SIZE_MB}MB)"
            )

        return result

    @classmethod
    def validate_image_dimensions(cls, width: int, height: int) -> ValidationResult:
        result = ValidationResult(is_valid=True)
        if not isinstance(width, int) or not isinstance(height, int):
            result.add_error("Width and height must be integers")
            return result
        if width < cls.MIN_WIDTH or height < cls.MIN_HEIGHT:
            result.add_error(
                f"Image dimensions too small. Minimum: {cls.MIN_WIDTH}x{cls.MIN_HEIGHT}"
            )
        if width > cls.MAX_WIDTH or height > cls.MAX_HEIGHT:
            result.add_error(
                f"Image dimensions too large. Maximum: {cls.MAX_WIDTH}x{cls.MAX_HEIGHT}"
            )
        return result


class DocumentValidator:
    """Validates complete document structures"""

    @classmethod
    def validate_metadata(cls, metadata: Dict[str, Any]) -> ValidationResult:
        result = ValidationResult(is_valid=True)
        required_fields = [
            "classification",
            "report_id",
            "author",
            "tlp",
        ]

        for field in required_fields:
            if field not in metadata:
                result.add_error(f"Missing required field: {field}")

        # Accept either "date" or "date_created"
        date_value = metadata.get("date") or metadata.get("date_created")
        if not date_value:
            result.add_error("Missing required field: date or date_created")

        # org_name is optional now
        if result.is_valid:
            if isinstance(metadata.get("author"), str):
                author_result = StringValidator.validate_name(metadata["author"])
                if not author_result.is_valid:
                    result.errors.extend(
                        ["Author: " + e for e in author_result.errors]
                    )

            if date_value and isinstance(date_value, str):
                date_result = DateValidator.validate_date(date_value)
                if not date_result.is_valid:
                    result.errors.extend(["Date: " + e for e in date_result.errors])

        return result

    @classmethod
    def validate_target_data(cls, target: Dict[str, Any]) -> ValidationResult:
        result = ValidationResult(is_valid=True)
        required_fields = ["name", "status", "dob", "nationality"]

        for field in required_fields:
            if field not in target or not target[field]:
                result.add_error(f"Missing required field: {field}")

        # "alias" is now optional
        if result.is_valid:
            name_result = StringValidator.validate_name(target.get("name", ""))
            if not name_result.is_valid:
                result.errors.extend(["Name: " + e for e in name_result.errors])

            dob_result = DateValidator.validate_date(target.get("dob", ""))
            if not dob_result.is_valid:
                result.errors.extend(["DOB: " + e for e in dob_result.errors])

        return result

    @classmethod
    def validate_digital_footprint(
        cls, footprint_list: List[Dict[str, Any]]
    ) -> ValidationResult:
        result = ValidationResult(is_valid=True)
        if not isinstance(footprint_list, list):
            result.add_error("Digital footprint must be a list")
            return result

        for idx, entry in enumerate(footprint_list):
            if not isinstance(entry, dict):
                result.add_error(f"Entry {idx} must be a dictionary")
                continue

            # Accept both "Platform" and "platform"
            platform = entry.get("Platform") or entry.get("platform")
            if not platform:
                result.add_error(f"Entry {idx}: Missing Platform")

            # Accept both "Admiralty Code" and "admiralty_code"
            admiralty_code = entry.get("Admiralty Code") or entry.get("admiralty_code")
            if admiralty_code:
                code_result = StringValidator.validate_admiralty_code(admiralty_code)
                if not code_result.is_valid:
                    result.errors.extend(
                        [f"Entry {idx}: " + e for e in code_result.errors]
                    )

        return result

    @classmethod
    def validate_timeline(cls, timeline_list: List[Dict[str, Any]]) -> ValidationResult:
        result = ValidationResult(is_valid=True)
        if not isinstance(timeline_list, list):
            result.add_error("Timeline must be a list")
            return result

        for idx, entry in enumerate(timeline_list):
            if not isinstance(entry, dict):
                result.add_error(f"Entry {idx} must be a dictionary")
                continue

            # Accept both "Date" and "date"
            date_value = entry.get("Date") or entry.get("date")
            if not date_value:
                result.add_error(f"Entry {idx}: Missing Date")
            else:
                date_result = DateValidator.validate_date(date_value)
                if not date_result.is_valid:
                    result.errors.extend(
                        [f"Entry {idx} Date: " + e for e in date_result.errors]
                    )

            # Accept both "Event Description" and "event"
            event_desc = entry.get("Event Description") or entry.get("event")
            if not event_desc:
                result.add_warning(f"Entry {idx}: Empty Event Description")

        return result


class RedactionValidator:
    """Validates redaction patterns"""

    REDACTION_PATTERN = re.compile(r"\|\|(.*?)\|\|")
    MAX_REDACTIONS = 1000

    @classmethod
    def validate_redactions(cls, text: str) -> ValidationResult:
        result = ValidationResult(is_valid=True)
        if not isinstance(text, str):
            return result

        redactions = cls.REDACTION_PATTERN.findall(text)
        if len(redactions) > cls.MAX_REDACTIONS:
            result.add_error(f"Too many redactions. Maximum: {cls.MAX_REDACTIONS}")

        for idx, redaction in enumerate(redactions):
            if not redaction.strip():
                result.add_warning(f"Redaction {idx} is empty")
            if len(redaction) > 1000:
                result.add_warning(
                    f"Redaction {idx} is very long ({len(redaction)} chars)"
                )

        return result

    @classmethod
    def count_redactions(cls, text: str) -> int:
        if not isinstance(text, str):
            return 0
        return len(cls.REDACTION_PATTERN.findall(text))
