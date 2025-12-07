"""
Anubis Intelligence Platform Configuration Module
Centralized configuration management for the entire platform
"""

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List

from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Project Root Directory
PROJECT_ROOT = Path(__file__).parent.parent.absolute()
ASSETS_DIR = PROJECT_ROOT / "assets"
DATA_DIR = PROJECT_ROOT / "data"
TEMPLATES_DIR = PROJECT_ROOT / "templates"
OUTPUT_DIR = PROJECT_ROOT / "output"
LOGS_DIR = PROJECT_ROOT / "logs"
DATABASE_DIR = PROJECT_ROOT / "database"


@dataclass
class SecurityConfig:
    """Security-related configuration"""

    enable_pdf_encryption: bool = True
    enable_exif_stripping: bool = True
    enable_audit_logging: bool = True
    pdf_password_default: str = "CLASSIFIED"
    max_file_upload_size_mb: int = 50
    allowed_image_formats: List[str] = None

    def __post_init__(self):
        if self.allowed_image_formats is None:
            self.allowed_image_formats = ["jpg", "jpeg", "png", "webp"]


@dataclass
class PDFConfig:
    """PDF generation configuration"""

    page_size: str = "A4"
    margin_top_cm: float = 1.5
    margin_bottom_cm: float = 1.5
    margin_left_cm: float = 1.5
    margin_right_cm: float = 1.5
    dpi: int = 300
    compress_images: bool = True
    embed_fonts: bool = True
    enable_watermark: bool = True
    watermark_opacity: float = 0.15


@dataclass
class DatabaseConfig:
    """Database configuration"""

    db_type: str = "sqlite"
    sqlite_path: str = str(DATABASE_DIR / "anubis_intel.db")
    echo_sql: bool = False
    auto_migrate: bool = True
    backup_enabled: bool = True
    backup_dir: str = str(DATABASE_DIR / "backups")


@dataclass
class LoggingConfig:
    """Logging configuration"""

    log_level: str = "INFO"
    log_file: str = str(LOGS_DIR / "anubis_intel.log")
    max_log_size_mb: int = 10
    backup_count: int = 5
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    json_logging: bool = True


@dataclass
class ClassificationLevels:
    """Intelligence classification levels"""

    levels: Dict[str, Dict[str, Any]] = None

    def __post_init__(self):
        if self.levels is None:
            self.levels = {
                "TOP SECRET // NOFORN": {
                    "color": "#FF0000",
                    "level": 5,
                    "description": "Top Secret - No Foreign Distribution",
                },
                "TOP SECRET": {
                    "color": "#FF3300",
                    "level": 4,
                    "description": "Top Secret",
                },
                "SECRET": {"color": "#FFCC00", "level": 3, "description": "Secret"},
                "CONFIDENTIAL": {
                    "color": "#0066FF",
                    "level": 2,
                    "description": "Confidential",
                },
                "UNCLASSIFIED": {
                    "color": "#00AA00",
                    "level": 1,
                    "description": "Unclassified",
                },
            }


@dataclass
class TLPLevels:
    """Traffic Light Protocol levels"""

    levels: Dict[str, Dict[str, Any]] = None

    def __post_init__(self):
        if self.levels is None:
            self.levels = {
                "RED": {
                    "color": "#FF0000",
                    "description": "Not for distribution. Information should not be shared.",
                    "level": 4,
                },
                "AMBER": {
                    "color": "#FFAA00",
                    "description": "Limited sharing. Information may be shared within organizations.",
                    "level": 3,
                },
                "GREEN": {
                    "color": "#00AA00",
                    "description": "Community willing to share. Information may be shared with communities.",
                    "level": 2,
                },
                "WHITE": {
                    "color": "#FFFFFF",
                    "description": "Unrestricted sharing. Information is not sensitive.",
                    "level": 1,
                },
            }


@dataclass
class AdmiraltyCodeRatings:
    """Admiralty Code source reliability ratings"""

    ratings: Dict[str, Dict[str, str]] = None

    def __post_init__(self):
        if self.ratings is None:
            self.ratings = {
                "A1": {"source": "Completely Reliable", "info": "Confirmed by Other Sources"},
                "A2": {"source": "Completely Reliable", "info": "Probably True"},
                "A3": {"source": "Completely Reliable", "info": "Possibly True"},
                "A4": {"source": "Completely Reliable", "info": "Doubtful"},
                "B1": {"source": "Usually Reliable", "info": "Confirmed by Other Sources"},
                "B2": {"source": "Usually Reliable", "info": "Probably True"},
                "B3": {"source": "Usually Reliable", "info": "Possibly True"},
                "B4": {"source": "Usually Reliable", "info": "Doubtful"},
                "C1": {"source": "Fairly Reliable", "info": "Confirmed by Other Sources"},
                "C2": {"source": "Fairly Reliable", "info": "Probably True"},
                "C3": {"source": "Fairly Reliable", "info": "Possibly True"},
                "C4": {"source": "Fairly Reliable", "info": "Doubtful"},
                "D1": {"source": "Unreliable", "info": "Confirmed by Other Sources"},
                "D2": {"source": "Unreliable", "info": "Probably True"},
                "D3": {"source": "Unreliable", "info": "Possibly True"},
                "D4": {"source": "Unreliable", "info": "Doubtful"},
                "E1": {"source": "Reliability Cannot Be Judged", "info": "Confirmed by Other Sources"},
                "E2": {"source": "Reliability Cannot Be Judged", "info": "Probably True"},
                "E3": {"source": "Reliability Cannot Be Judged", "info": "Possibly True"},
                "E4": {"source": "Reliability Cannot Be Judged", "info": "Doubtful"},
                "F1": {"source": "Reporting Agency Cannot Be Judged", "info": "Confirmed by Other Sources"},
            }


@dataclass
class TemplateConfig:
    """Template configuration"""

    default_template: str = "anubis_dossier"
    available_templates: List[str] = None

    def __post_init__(self):
        if self.available_templates is None:
            self.available_templates = [
                "anubis_dossier",
                "sacred_scroll",
            ]


class AnubisConfig:
    """Main configuration class that aggregates all settings"""

    def __init__(self):
        self.security = SecurityConfig()
        self.pdf = PDFConfig()
        self.database = DatabaseConfig()
        self.logging = LoggingConfig()
        self.classifications = ClassificationLevels()
        self.tlp = TLPLevels()
        self.admiralty_codes = AdmiraltyCodeRatings()
        self.templates = TemplateConfig()

        # Create necessary directories
        self._create_directories()

        # Environment overrides
        self._load_env_overrides()

    def _create_directories(self) -> None:
        """Create all necessary directories if they don't exist"""
        for directory in [
            ASSETS_DIR,
            DATA_DIR,
            TEMPLATES_DIR,
            OUTPUT_DIR,
            LOGS_DIR,
            DATABASE_DIR,
        ]:
            directory.mkdir(parents=True, exist_ok=True)

    def _load_env_overrides(self) -> None:
        """Load configuration overrides from environment variables"""
        if env_log_level := os.getenv("ANUBIS_LOG_LEVEL"):
            self.logging.log_level = env_log_level

        if env_db_path := os.getenv("ANUBIS_DB_PATH"):
            self.database.sqlite_path = env_db_path

        if env_pdf_encrypt := os.getenv("ANUBIS_PDF_ENCRYPT"):
            self.security.enable_pdf_encryption = env_pdf_encrypt.lower() == "true"

        if env_template := os.getenv("ANUBIS_DEFAULT_TEMPLATE"):
            self.templates.default_template = env_template

    def get_classification_color(self, classification: str) -> str:
        """Get color for a classification level"""
        return self.classifications.levels.get(classification, {"color": "#000000"})[
            "color"
        ]

    def get_tlp_color(self, tlp_level: str) -> str:
        """Get color for a TLP level"""
        return self.tlp.levels.get(tlp_level, {"color": "#000000"})["color"]

    def is_classification_valid(self, classification: str) -> bool:
        """Check if a classification level is valid"""
        return classification in self.classifications.levels

    def is_tlp_valid(self, tlp_level: str) -> bool:
        """Check if a TLP level is valid"""
        return tlp_level in self.tlp.levels

    def is_admiralty_code_valid(self, code: str) -> bool:
        """Check if an Admiralty Code is valid"""
        return code in self.admiralty_codes.ratings

    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary"""
        return {
            "security": self.security.__dict__,
            "pdf": self.pdf.__dict__,
            "database": self.database.__dict__,
            "logging": self.logging.__dict__,
            "classifications": self.classifications.levels,
            "tlp": self.tlp.levels,
            "admiralty_codes": self.admiralty_codes.ratings,
            "templates": self.templates.__dict__,
        }


# Global configuration instance
config = AnubisConfig()
