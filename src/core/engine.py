"""
Main Intelligence Report Engine for Anubis Intelligence Platform v4.0
Complete report generation with validation, image processing, PDF encryption, and database persistence
"""

import hashlib
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from config import OUTPUT_DIR, config
from src.core.image_processor import ImageProcessor
from src.core.pdf_generator import PDFGenerator, RedactionEngine, report_builder
from src.utils import (
    DateValidator,
    DocumentValidator,
    ImageValidator,
    RedactionValidator,
    StringValidator,
    db,
    logger,
)


class IntelligenceReportEngine:
    """Main engine for generating intelligence reports with advanced features"""

    def __init__(self):
        """Initialize the intelligence report engine"""
        self.pdf_generator = PDFGenerator()
        self.image_processor = ImageProcessor()
        self.redaction_engine = RedactionEngine()
        logger.info("Intelligence Report Engine initialized")

    def validate_report_data(self, data: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """Comprehensive validation of all report data. Returns (is_valid, errors_list)"""
        errors = []

        # Validate metadata
        if "meta" in data:
            meta_result = DocumentValidator.validate_metadata(data["meta"])
            if not meta_result.is_valid:
                errors.extend(meta_result.errors)

        # Validate target data
        if "target" in data:
            target_result = DocumentValidator.validate_target_data(data["target"])
            if not target_result.is_valid:
                errors.extend(target_result.errors)

        # Validate digital footprint
        if "digital_footprint" in data:
            footprint_result = DocumentValidator.validate_digital_footprint(
                data["digital_footprint"]
            )
            if not footprint_result.is_valid:
                errors.extend(footprint_result.errors)

        # Validate timeline
        if "timeline" in data:
            timeline_result = DocumentValidator.validate_timeline(data["timeline"])
            if not timeline_result.is_valid:
                errors.extend(timeline_result.errors)

        # Validate redactions
        for key, value in data.items():
            if isinstance(value, str):
                redaction_result = RedactionValidator.validate_redactions(value)
                if not redaction_result.is_valid:
                    errors.extend([f"{key}: {e}" for e in redaction_result.errors])

        is_valid = len(errors) == 0

        if is_valid:
            logger.info("Report data validation successful")
        else:
            logger.warning(f"Report data validation failed: {len(errors)} errors")
            for error in errors:
                logger.error(f"  - {error}")

        return is_valid, errors

    def process_images(
        self,
        image_paths: Dict[str, str],
        strip_exif: bool = True,
        apply_grayscale: bool = True,
    ) -> Tuple[bool, Dict[str, str], List[str]]:
        """Process all images in the report. Returns (success, processed_paths, errors)"""
        processed_paths = {}
        errors = []

        for image_type, image_path in image_paths.items():
            if not image_path:
                continue

            try:
                # Validate image file
                image_val = ImageValidator.validate_image_file(Path(image_path))
                if not image_val.is_valid:
                    errors.extend(image_val.errors)
                    continue

                # Process image
                success, metadata = self.image_processor.process_image(
                    Path(image_path),
                    strip_exif=strip_exif,
                    optimize=True,
                    apply_grayscale=apply_grayscale,
                )

                if success and metadata:
                    processed_path = "file://" + str(
                        OUTPUT_DIR.parent / "assets" / metadata.filename
                    )
                    processed_paths[image_type] = processed_path

                    logger.info(f"Image processed: {image_type} -> {metadata.filename}")
                else:
                    errors.append(f"Failed to process {image_type} image")

            except Exception as e:
                error_msg = f"Error processing {image_type} image: {str(e)}"
                errors.append(error_msg)
                logger.error(error_msg)

        success = len(errors) == 0
        return success, processed_paths, errors

    def generate_pdf_from_data(
        self,
        data: Dict[str, Any],
        filename: str = "report.pdf",
        template_name: Optional[str] = None,
        encrypt: bool = True,
        password: Optional[str] = None,
        persist_to_db: bool = True,
        create_version: bool = True,
    ) -> Optional[Path]:
        """Generate PDF from report data with full feature set"""
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

        try:
            logger.info("Step 1: Validating report data...")
            is_valid, validation_errors = self.validate_report_data(data)

            if not is_valid:
                logger.error("Report data validation failed")
                return None

            logger.info("Step 2: Processing images...")
            if "images" in data and data["images"]:
                image_success, processed_paths, image_errors = self.process_images(
                    data["images"],
                    strip_exif=config.security.enable_exif_stripping,
                    apply_grayscale=True,
                )

                if image_errors:
                    for error in image_errors:
                        logger.warning(error)

                data["images"].update(processed_paths)

            logger.info("Step 3: Computing redaction statistics...")
            redaction_stats = self.redaction_engine.get_redaction_stats(data)
            redaction_count = redaction_stats["total_redactions"]

            logger.info("Step 4: Generating PDF...")
            watermark_text = data.get("meta", {}).get("classification", "UNCLASSIFIED")

            pdf_path = self.pdf_generator.generate_pdf(
                data=data,
                output_filename=filename,
                template_name=template_name or config.templates.default_template,
                encrypt=encrypt,
                password=password or config.security.pdf_password_default,
                watermark_text=watermark_text if config.pdf.enable_watermark else None,
            )

            if pdf_path is None:
                logger.error("PDF generation failed")
                return None

            if persist_to_db:
                logger.info("Step 5: Persisting report to database...")
                report_id = data.get("meta", {}).get("report_id", "UNKNOWN")
                file_hash = self._calculate_file_hash(pdf_path)

                db_report = db.create_report(
                    report_id=report_id,
                    classification=data.get("meta", {}).get(
                        "classification", "UNCLASSIFIED"
                    ),
                    tlp_level=data.get("meta", {}).get("tlp", "WHITE"),
                    title=f"Dossier: {data.get('target', {}).get('name', 'UNKNOWN')}",
                    author=data.get("meta", {}).get("author", "UNKNOWN"),
                    organization=data.get("meta", {}).get("org_name", "AGENCY"),
                    target_name=data.get("target", {}).get("name"),
                    target_alias=data.get("target", {}).get("alias"),
                    status=data.get("target", {}).get("status"),
                    summary=data.get("intelligence_summary", "")[:500],
                    data=data,
                    redaction_count=redaction_count,
                    page_count=1,
                    file_path=str(pdf_path),
                    file_hash=file_hash,
                    is_encrypted=encrypt,
                    custom_metadata=redaction_stats,
                )

                if db_report:
                    logger.info(f"Report persisted to database: ID={report_id}")

                    if create_version:
                        db.create_version(
                            report_id=report_id,
                            version=1,
                            data=data,
                            change_summary="Initial version",
                            modified_by=data.get("meta", {}).get("author", "SYSTEM"),
                        )

                    db.log_audit_event(
                        event_type="REPORT_GENERATION",
                        action="PDF_CREATED",
                        user=data.get("meta", {}).get("author", "UNKNOWN"),
                        report_id=report_id,
                        details={
                            "filename": filename,
                            "encrypted": encrypt,
                            "redactions": redaction_count,
                            "template": template_name,
                        },
                    )

            logger.info(f"Report generation complete: {pdf_path}")
            return pdf_path

        except Exception as e:
            logger.error(f"Report generation failed: {e}")
            return None

    def generate_batch_reports(
        self,
        batch_data: List[Tuple[Dict[str, Any], str]],
        encrypt: bool = True,
        persist_to_db: bool = True,
    ) -> Dict[str, Any]:
        """Generate multiple reports in batch"""
        results = {
            "total": len(batch_data),
            "successful": 0,
            "failed": 0,
            "generated_files": [],
            "errors": [],
            "start_time": datetime.now().isoformat(),
        }

        for idx, (data, filename) in enumerate(batch_data, 1):
            logger.info(f"Generating batch report {idx}/{len(batch_data)}: {filename}")

            try:
                pdf_path = self.generate_pdf_from_data(
                    data,
                    filename=filename,
                    encrypt=encrypt,
                    persist_to_db=persist_to_db,
                )

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

        results["end_time"] = datetime.now().isoformat()
        logger.info(
            f"Batch generation complete: {results['successful']}/{results['total']} successful"
        )

        return results

    def get_report_from_database(self, report_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve report metadata from database"""
        report = db.get_report(report_id)
        if report:
            return report.to_dict()
        return None

    def search_reports(self, query: str) -> List[Dict[str, Any]]:
        """Search reports in database"""
        reports = db.search_reports(query)
        return [r.to_dict() for r in reports]

    def list_reports(
        self,
        classification: Optional[str] = None,
        author: Optional[str] = None,
        limit: int = 100,
    ) -> List[Dict[str, Any]]:
        """List reports from database"""
        reports = db.list_reports(
            classification=classification, author=author, limit=limit
        )
        return [r.to_dict() for r in reports]

    def _calculate_file_hash(self, file_path: Path) -> str:
        """Calculate SHA256 hash of file"""
        hash_sha256 = hashlib.sha256()
        try:
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_sha256.update(chunk)
            return hash_sha256.hexdigest()
        except Exception as e:
            logger.error(f"Failed to calculate file hash: {e}")
            return ""


# Global engine instance
intelligence_engine = IntelligenceReportEngine()


def generate_pdf_from_data(
    data: Dict[str, Any], filename: str = "report.pdf"
) -> Optional[Path]:
    """Legacy function for backward compatibility"""
    return intelligence_engine.generate_pdf_from_data(
        data, filename=filename, encrypt=True, persist_to_db=True
    )


if __name__ == "__main__":
    import yaml

    data_path = Path(__file__).parent.parent / "data" / "mission_alpha.yaml"

    try:
        with open(data_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)

        logger.info(f"Loading sample data from {data_path}")

        pdf_path = intelligence_engine.generate_pdf_from_data(
            data, filename="TopSecret_Report.pdf"
        )

        if pdf_path:
            logger.info("=" * 60)
            logger.info(f"SUCCESS: Report generated at {pdf_path}")
            logger.info("=" * 60)

            stats = db.get_statistics()
            logger.info(f"Database statistics: {stats}")
        else:
            logger.error("Report generation failed")

    except FileNotFoundError:
        logger.error(f"Data file not found: {data_path}")
    except Exception as e:
        logger.error(f"Error: {e}")
