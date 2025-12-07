"""
Image Processing Module for Anubis Intelligence Platform
Handles EXIF stripping, optimization, and image processing
"""

import hashlib
import shutil
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

from PIL import Image
from PIL.ExifTags import TAGS

from config import ASSETS_DIR, config
from src.utils.validators import logger


@dataclass
class ImageMetadata:
    """Container for image metadata"""

    filename: str
    original_size_bytes: int
    processed_size_bytes: int
    width: int
    height: int
    format: str
    has_exif: bool
    exif_data_stripped: bool
    file_hash: str
    processed_at: str


class ExifProcessor:
    """Handles EXIF data extraction and removal"""

    SENSITIVE_TAGS = {
        "GPSInfo",
        "DateTime",
        "DateTimeOriginal",
        "DateTimeDigitized",
        "Make",
        "Model",
        "Software",
        "Orientation",
    }

    @staticmethod
    def has_exif(image_path: Path) -> bool:
        try:
            image = Image.open(image_path)
            exif_data = image._getexif()
            return exif_data is not None and len(exif_data) > 0
        except Exception as e:
            logger.warning(f"Could not check EXIF data: {e}")
            return False

    @staticmethod
    def extract_exif(image_path: Path) -> Dict[str, Any]:
        exif_data = {}
        try:
            image = Image.open(image_path)
            exif_raw = image._getexif()

            if exif_raw:
                for tag_id, value in exif_raw.items():
                    tag_name = TAGS.get(tag_id, tag_id)
                    exif_data[tag_name] = str(value)

                logger.debug(
                    f"Extracted {len(exif_data)} EXIF tags from {image_path.name}"
                )
        except Exception as e:
            logger.warning(f"Failed to extract EXIF data: {e}")

        return exif_data

    @staticmethod
    def strip_exif(image_path: Path, output_path: Path) -> bool:
        try:
            image = Image.open(image_path)
            data = list(image.getdata())
            image_without_exif = Image.new(image.mode, image.size)
            image_without_exif.putdata(data)
            image_without_exif.save(output_path, quality=95, optimize=True)
            logger.info(f"EXIF data stripped from {image_path.name}")
            return True
        except Exception as e:
            logger.error(f"Failed to strip EXIF data: {e}")
            return False

    @staticmethod
    def get_sensitive_exif(image_path: Path) -> Dict[str, str]:
        exif_data = ExifProcessor.extract_exif(image_path)
        return {
            k: v for k, v in exif_data.items() if k in ExifProcessor.SENSITIVE_TAGS
        }


class ImageOptimizer:
    """Handles image compression and optimization"""

    MAX_WIDTH = 2000
    MAX_HEIGHT = 2000
    QUALITY = 85
    TARGET_SIZE_MB = 5

    @staticmethod
    def calculate_file_hash(image_path: Path) -> str:
        hash_sha256 = hashlib.sha256()
        try:
            with open(image_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_sha256.update(chunk)
            return hash_sha256.hexdigest()
        except Exception as e:
            logger.error(f"Failed to calculate file hash: {e}")
            return ""

    @staticmethod
    def optimize_image(
        input_path: Path, output_path: Path, max_width: int = MAX_WIDTH
    ) -> bool:
        try:
            image = Image.open(input_path)

            if image.mode in ("RGBA", "LA", "P"):
                background = Image.new("RGB", image.size, (255, 255, 255))
                background.paste(
                    image, mask=image.split()[-1] if image.mode == "RGBA" else None
                )
                image = background

            image.thumbnail((max_width, max_width), Image.Resampling.LANCZOS)
            image.save(
                output_path, "JPEG", quality=ImageOptimizer.QUALITY, optimize=True
            )

            original_size = input_path.stat().st_size / (1024 * 1024)
            optimized_size = output_path.stat().st_size / (1024 * 1024)

            logger.info(
                f"Image optimized: {original_size:.2f}MB -> {optimized_size:.2f}MB"
            )
            return True

        except Exception as e:
            logger.error(f"Image optimization failed: {e}")
            return False

    @staticmethod
    def get_image_dimensions(image_path: Path) -> Tuple[int, int]:
        try:
            with Image.open(image_path) as img:
                return img.size
        except Exception as e:
            logger.error(f"Failed to get image dimensions: {e}")
            return (0, 0)

    @staticmethod
    def apply_grayscale_filter(input_path: Path, output_path: Path) -> bool:
        try:
            image = Image.open(input_path)
            grayscale = image.convert("L")
            grayscale.save(output_path, quality=95)
            logger.info(f"Grayscale filter applied to {input_path.name}")
            return True
        except Exception as e:
            logger.error(f"Failed to apply grayscale filter: {e}")
            return False


class ImageProcessor:
    """Main image processor combining optimization and EXIF handling"""

    def __init__(self):
        self.exif_processor = ExifProcessor()
        self.optimizer = ImageOptimizer()

    def process_image(
        self,
        input_path: Path,
        strip_exif: bool = True,
        optimize: bool = True,
        apply_grayscale: bool = True,
        output_dir: Optional[Path] = None,
    ) -> Tuple[bool, Optional[ImageMetadata]]:
        """Process image: strip EXIF, optimize, apply filters"""
        input_path = Path(input_path)

        if not input_path.exists():
            logger.error(f"Image file not found: {input_path}")
            return False, None

        if output_dir is None:
            output_dir = ASSETS_DIR

        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_filename = f"{input_path.stem}_processed_{timestamp}.jpg"
        output_path = output_dir / output_filename

        original_size = input_path.stat().st_size
        file_hash = self.optimizer.calculate_file_hash(input_path)

        try:
            has_exif = self.exif_processor.has_exif(input_path)
            exif_stripped = False

            if has_exif and strip_exif and config.security.enable_exif_stripping:
                logger.info(f"Stripping EXIF data from {input_path.name}")
                temp_path = output_dir / f"{input_path.stem}_temp.jpg"
                exif_stripped = self.exif_processor.strip_exif(input_path, temp_path)

                if exif_stripped:
                    input_path = temp_path
                else:
                    logger.warning("EXIF stripping failed, continuing without it")

            if optimize:
                logger.info(f"Optimizing image: {input_path.name}")
                if not self.optimizer.optimize_image(input_path, output_path):
                    return False, None
            else:
                shutil.copy2(input_path, output_path)

            if apply_grayscale:
                logger.info(f"Applying grayscale filter to {output_path.name}")
                temp_gray = output_dir / f"{output_path.stem}_gray.jpg"
                if self.optimizer.apply_grayscale_filter(output_path, temp_gray):
                    shutil.move(temp_gray, output_path)

            width, height = self.optimizer.get_image_dimensions(output_path)
            processed_size = output_path.stat().st_size

            metadata = ImageMetadata(
                filename=output_filename,
                original_size_bytes=original_size,
                processed_size_bytes=processed_size,
                width=width,
                height=height,
                format="JPEG",
                has_exif=has_exif,
                exif_data_stripped=exif_stripped,
                file_hash=file_hash,
                processed_at=datetime.now().isoformat(),
            )

            logger.info(
                f"Image processing completed: {output_filename} "
                f"({original_size / 1024:.1f}KB -> {processed_size / 1024:.1f}KB)"
            )

            return True, metadata

        except Exception as e:
            logger.error(f"Image processing error: {e}")
            return False, None

    def process_batch(
        self, image_paths: list, output_dir: Optional[Path] = None, **processing_options
    ) -> Dict[str, Any]:
        """Process multiple images"""
        results = {
            "total": len(image_paths),
            "successful": 0,
            "failed": 0,
            "processed_images": [],
            "errors": [],
        }

        for idx, image_path in enumerate(image_paths, 1):
            logger.info(f"Processing image {idx}/{len(image_paths)}: {image_path}")

            success, metadata = self.process_image(
                image_path, output_dir=output_dir, **processing_options
            )

            if success and metadata:
                results["successful"] += 1
                results["processed_images"].append(metadata.__dict__)
            else:
                results["failed"] += 1
                results["errors"].append(str(image_path))

        logger.info(
            f"Batch processing complete: {results['successful']}/{results['total']} successful"
        )
        return results

    def get_image_info(self, image_path: Path) -> Dict[str, Any]:
        """Get comprehensive image information"""
        image_path = Path(image_path)

        if not image_path.exists():
            return {"error": "File not found"}

        try:
            image = Image.open(image_path)
            width, height = image.size
            file_size = image_path.stat().st_size

            exif_data = self.exif_processor.extract_exif(image_path)
            sensitive_exif = self.exif_processor.get_sensitive_exif(image_path)

            return {
                "filename": image_path.name,
                "size_bytes": file_size,
                "size_mb": file_size / (1024 * 1024),
                "width": width,
                "height": height,
                "aspect_ratio": f"{width}:{height}",
                "format": image.format,
                "mode": image.mode,
                "has_exif": len(exif_data) > 0,
                "exif_tags_count": len(exif_data),
                "sensitive_exif": sensitive_exif,
                "file_hash": self.optimizer.calculate_file_hash(image_path),
                "created": datetime.fromtimestamp(
                    image_path.stat().st_ctime
                ).isoformat(),
            }

        except Exception as e:
            logger.error(f"Failed to get image info: {e}")
            return {"error": str(e)}
