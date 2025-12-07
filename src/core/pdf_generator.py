"""
PDF Generation Engine for Anubis Intelligence Platform
Implements encryption, watermarks, templates, and professional features
"""

import re
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML

from config import OUTPUT_DIR, TEMPLATES_DIR, config
from src.utils.validators import logger
from src.core.intelligence_formatter import IntelligenceFormatter
from src.core.intelligence_enricher import IntelligenceEnricher


class WatermarkGenerator:
    """Generates watermarks for documents"""

    @staticmethod
    def create_watermark_css(text: str, opacity: float = 0.15, angle: int = -45) -> str:
        return f"""
        body::before {{
            content: "{text}";
            position: fixed;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%) rotate({angle}deg);
            font-size: 60px;
            font-weight: bold;
            color: #000;
            opacity: {opacity};
            z-index: -1;
            pointer-events: none;
            white-space: nowrap;
            font-family: Arial, sans-serif;
        }}
        """


class RedactionEngine:
    """Advanced redaction system with analytics"""

    REDACTION_PATTERN = re.compile(r"\|\|(.*?)\|\|")

    @staticmethod
    def apply_redaction(text: str) -> str:
        if not isinstance(text, str):
            return str(text)

        def replace_redaction(match):
            redacted_text = match.group(1)
            return f'<span class="redacted" data-redaction-length="{len(redacted_text)}">{redacted_text}</span>'

        return RedactionEngine.REDACTION_PATTERN.sub(replace_redaction, text)

    @staticmethod
    def count_redactions(text: str) -> int:
        if not isinstance(text, str):
            return 0
        return len(RedactionEngine.REDACTION_PATTERN.findall(text))

    @staticmethod
    def get_redaction_stats(data: Dict[str, Any]) -> Dict[str, Any]:
        stats = {
            "total_redactions": 0,
            "fields_with_redactions": [],
            "redaction_breakdown": {},
        }

        def count_in_field(field_data, field_name):
            if isinstance(field_data, str):
                count = RedactionEngine.count_redactions(field_data)
                if count > 0:
                    stats["total_redactions"] += count
                    stats["fields_with_redactions"].append(field_name)
                    stats["redaction_breakdown"][field_name] = count
            elif isinstance(field_data, dict):
                for key, value in field_data.items():
                    count_in_field(value, f"{field_name}.{key}")
            elif isinstance(field_data, list):
                for idx, item in enumerate(field_data):
                    count_in_field(item, f"{field_name}[{idx}]")

        count_in_field(data, "data")
        return stats


class TemplateManager:
    """Manages multiple document templates"""

    def __init__(self):
        self.env = Environment(loader=FileSystemLoader(TEMPLATES_DIR))
        self.available_templates = self._discover_templates()

    def _discover_templates(self) -> Dict[str, Path]:
        templates = {}
        template_files = TEMPLATES_DIR.glob("*.html")

        for template_file in template_files:
            template_name = template_file.stem
            templates[template_name] = template_file

        logger.info(f"Discovered {len(templates)} templates: {list(templates.keys())}")
        return templates

    def get_template(self, template_name: str = None):
        if template_name is None:
            template_name = config.templates.default_template

        if template_name not in self.available_templates:
            logger.warning(f"Template '{template_name}' not found, using default")
            template_name = config.templates.default_template

        try:
            return self.env.get_template(f"{template_name}.html")
        except Exception as e:
            logger.error(f"Failed to load template '{template_name}': {e}")
            return None

    def render_template(
        self, template_name: str, data: Dict[str, Any], filters: Dict[str, Any] = None
    ) -> Optional[str]:
        if filters is None:
            filters = {}

        # Register filters FIRST before loading template
        filters.setdefault("redact", RedactionEngine.apply_redaction)
        filters.setdefault("upper", lambda x: str(x).upper() if x else "")
        filters.setdefault("lower", lambda x: str(x).lower() if x else "")
        filters.setdefault(
            "truncate",
            lambda x, length=50: str(x)[:length] + "..."
            if len(str(x)) > length
            else str(x),
        )

        for filter_name, filter_func in filters.items():
            self.env.filters[filter_name] = filter_func

        template = self.get_template(template_name)

        if template is None:
            return None

        try:
            return template.render(data)
        except Exception as e:
            logger.error(f"Template rendering error: {e}")
            return None


class PDFGenerator:
    """Main PDF generation engine with intelligence formatting"""

    def __init__(self):
        self.template_manager = TemplateManager()
        self.redaction_engine = RedactionEngine()
        self.formatter = IntelligenceFormatter()
        self.enricher = IntelligenceEnricher()

    def generate_pdf(
        self,
        data: Dict[str, Any],
        output_filename: str = "report.pdf",
        template_name: str = None,
        encrypt: bool = True,
        password: str = None,
        watermark_text: str = None,
        enrich_intelligence: bool = True,
    ) -> Optional[Path]:
        """Generate PDF from data and template with professional intelligence formatting"""
        try:
            OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

            # Enrich data with professional intelligence formatting
            if enrich_intelligence:
                data = self._enrich_report_data(data)
            
            html_content = self.template_manager.render_template(
                template_name or config.templates.default_template, data
            )

            if html_content is None:
                logger.error("Template rendering failed")
                return None

            if watermark_text and config.pdf.enable_watermark:
                watermark_css = WatermarkGenerator.create_watermark_css(
                    watermark_text, opacity=config.pdf.watermark_opacity
                )
                html_content = f"<style>{watermark_css}</style>" + html_content

            output_path = OUTPUT_DIR / output_filename

            logger.info(f"Generating professional intelligence report: {output_path}")

            html_obj = HTML(string=html_content, base_url=str(Path(__file__).parent))
            html_obj.write_pdf(output_path, dpi=config.pdf.dpi)

            logger.info(f"Intelligence report generated successfully: {output_path}")

            if encrypt and config.security.enable_pdf_encryption:
                if password is None:
                    password = config.security.pdf_password_default

                success = self._encrypt_pdf(output_path, password)
                if not success:
                    logger.warning("PDF encryption failed")

            redaction_stats = self.redaction_engine.get_redaction_stats(data)
            logger.info(f"Redaction stats: {redaction_stats}")

            return output_path

        except Exception as e:
            logger.error(f"PDF generation failed: {e}")
            return None
    
    def _enrich_report_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Enrich report data with professional intelligence formatting"""
        # Apply intelligence formatter
        enriched_data = self.formatter.enrich_report_data(data)
        
        # Enrich individual sections
        if "target" in enriched_data:
            enriched_data["target"] = self.enricher.enrich_target_profile(enriched_data["target"])
        
        if "biometrics" in enriched_data:
            enriched_data["biometrics"] = self.enricher.enrich_biometrics(enriched_data["biometrics"])
        
        if "osint" in enriched_data:
            enriched_data["osint"] = self.enricher.enrich_osint(enriched_data["osint"])
        
        if "sigint" in enriched_data:
            enriched_data["sigint"] = self.enricher.enrich_sigint(enriched_data["sigint"])
        
        if "humint" in enriched_data:
            enriched_data["humint"] = self.enricher.enrich_humint(enriched_data["humint"])
        
        if "financial_intelligence" in enriched_data:
            enriched_data["financial_intelligence"] = self.enricher.enrich_financial(
                enriched_data["financial_intelligence"]
            )
        
        if "timeline" in enriched_data and isinstance(enriched_data["timeline"], list):
            enriched_data["timeline"] = self.enricher.enrich_timeline(enriched_data["timeline"])
        
        if "incidents" in enriched_data and isinstance(enriched_data["incidents"], list):
            enriched_data["incidents"] = self.enricher.enrich_incidents(enriched_data["incidents"])
        
        if "connections" in enriched_data and isinstance(enriched_data["connections"], list):
            enriched_data["connections"] = self.enricher.enrich_connections(enriched_data["connections"])
        
        # Add recommendations
        enriched_data["intelligence_recommendations"] = self.enricher.add_intelligence_recommendations(
            enriched_data
        )
        
        logger.info("Report data enriched with professional intelligence formatting")
        return enriched_data

    def _encrypt_pdf(self, pdf_path: Path, password: str) -> bool:
        """Encrypt PDF with password"""
        try:
            from pypdf import PdfReader, PdfWriter

            pdf_reader = PdfReader(pdf_path)
            pdf_writer = PdfWriter()

            # Copy all pages from reader to writer
            for page in pdf_reader.pages:
                pdf_writer.add_page(page)

            # Encrypt with password
            pdf_writer.encrypt(password)

            with open(pdf_path, "wb") as f:
                pdf_writer.write(f)

            logger.info(f"PDF encrypted: {pdf_path.name}")
            return True

        except Exception as e:
            logger.error(f"PDF encryption failed: {e}")
            return False

    def generate_batch(
        self, batch_data: list, output_dir: Optional[Path] = None, **kwargs
    ) -> Dict[str, Any]:
        """Generate multiple PDFs in batch"""
        results = {
            "total": len(batch_data),
            "successful": 0,
            "failed": 0,
            "generated_files": [],
            "errors": [],
        }

        for idx, (data, filename) in enumerate(batch_data, 1):
            logger.info(f"Generating batch PDF {idx}/{len(batch_data)}")

            try:
                pdf_path = self.generate_pdf(data, filename, **kwargs)

                if pdf_path:
                    results["successful"] += 1
                    results["generated_files"].append(str(pdf_path))
                else:
                    results["failed"] += 1
                    results["errors"].append(
                        f"{filename}: PDF generation returned None"
                    )

            except Exception as e:
                results["failed"] += 1
                results["errors"].append(f"{filename}: {str(e)}")

        logger.info(
            f"Batch generation complete: {results['successful']}/{results['total']} successful"
        )

        return results

    def get_pdf_info(self, pdf_path: Path) -> Dict[str, Any]:
        """Get information about a generated PDF"""
        pdf_path = Path(pdf_path)

        if not pdf_path.exists():
            return {"error": "File not found"}

        try:
            from pypdf import PdfReader

            with open(pdf_path, "rb") as f:
                pdf_reader = PdfReader(f)

            return {
                "filename": pdf_path.name,
                "size_bytes": pdf_path.stat().st_size,
                "size_mb": pdf_path.stat().st_size / (1024 * 1024),
                "pages": len(pdf_reader.pages),
                "is_encrypted": pdf_reader.is_encrypted,
                "created": datetime.fromtimestamp(pdf_path.stat().st_ctime).isoformat(),
                "modified": datetime.fromtimestamp(
                    pdf_path.stat().st_mtime
                ).isoformat(),
            }

        except Exception as e:
            logger.error(f"Failed to get PDF info: {e}")
            return {"error": str(e)}


class ReportBuilder:
    """Helper class for building report data structures"""

    @staticmethod
    def create_base_report(
        classification: str,
        report_id: str,
        author: str,
        org_name: str = "INTELLIGENCE AGENCY",
        tlp: str = "RED",
    ) -> Dict[str, Any]:
        return {
            "meta": {
                "classification": classification,
                "report_id": report_id,
                "date": datetime.now().strftime("%Y-%m-%d"),
                "author": author,
                "tlp": tlp,
                "org_name": org_name,
            },
            "target": {},
            "biometrics": {},
            "intelligence_summary": "",
            "digital_footprint": [],
            "timeline": [],
            "images": {"profile": None, "logo": None},
        }

    @staticmethod
    def add_target_info(
        report: Dict[str, Any],
        name: str,
        alias: str,
        dob: str,
        nationality: str,
        status: str = "UNKNOWN",
        location: str = "",
    ) -> Dict[str, Any]:
        report["target"].update(
            {
                "name": name,
                "alias": alias,
                "dob": dob,
                "nationality": nationality,
                "status": status,
                "location": location,
            }
        )
        return report

    @staticmethod
    def add_digital_footprint(
        report: Dict[str, Any], platform: str, identity: str, admiralty_code: str = "E1"
    ) -> Dict[str, Any]:
        report["digital_footprint"].append(
            {
                "Platform": platform,
                "Username/IP": identity,
                "Admiralty Code": admiralty_code,
            }
        )
        return report

    @staticmethod
    def add_timeline_event(
        report: Dict[str, Any], date: str, time: str, event: str
    ) -> Dict[str, Any]:
        report["timeline"].append(
            {
                "Date": date,
                "Time": time,
                "Event Description": event,
            }
        )
        return report


pdf_generator = PDFGenerator()
report_builder = ReportBuilder()
