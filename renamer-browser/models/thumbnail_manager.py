"""Thumbnail generation and caching utilities."""
from __future__ import annotations

import hashlib
import logging
import os
import threading
from concurrent.futures import Future, ThreadPoolExecutor
from pathlib import Path
from typing import Dict, Optional, Set, Union

from PIL import Image, ImageDraw, ImageFont, ImageOps  # type: ignore[import-untyped]

logger = logging.getLogger(__name__)

SUPPORTED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".jp2"}
DEFAULT_SIZE = 150


class ThumbnailManager:
    """Generate and cache thumbnails on disk for faster gallery rendering."""

    def __init__(
        self,
        cache_root: Optional[Union[str, Path]] = None,
        size: int = DEFAULT_SIZE,
        max_workers: int = 4,
    ) -> None:
        base_dir = Path(cache_root or Path.home() / ".image-tagger-renamer")
        self.cache_dir = (base_dir / "cache" / "thumbnails").expanduser().resolve()
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.size = size
        self._executor = ThreadPoolExecutor(max_workers=max_workers)
        self._lock = threading.Lock()
        self._inflight: Dict[Path, Future[str]] = {}
        self._failed_paths: Set[Path] = set()
        self._shutdown = False

    # ----------------------------------------------------------------------------------
    # Public API
    # ----------------------------------------------------------------------------------
    def get_thumbnail(self, image_path: Union[str, Path]) -> str:
        """Return path to thumbnail, generating and caching as needed."""
        image_path = Path(image_path).expanduser().resolve()
        cache_path = self._cache_path_for(image_path)

        if self._is_cache_valid(image_path, cache_path):
            return str(cache_path)

        return self._generate_thumbnail(image_path, cache_path)

    def queue_thumbnail(self, image_path: Union[str, Path]) -> Future[str]:
        """Queue thumbnail generation in thread pool and return the future."""
        image_path = Path(image_path).expanduser().resolve()
        cache_path = self._cache_path_for(image_path)

        if self._is_cache_valid(image_path, cache_path):
            future: Future[str] = Future()
            future.set_result(str(cache_path))
            return future

        with self._lock:
            existing = self._inflight.get(image_path)
            if existing and not existing.done():
                return existing

            future: Future[str] = self._executor.submit(
                self._generate_thumbnail, image_path, cache_path
            )
            self._inflight[image_path] = future
            future.add_done_callback(lambda _: self._inflight.pop(image_path, None))
            return future

    def clear_cache(self) -> None:
        """Delete every cached thumbnail."""
        for file in self.cache_dir.glob("*.jpg"):
            try:
                file.unlink()
            except OSError:
                logger.warning("Failed to delete cached thumbnail %s", file)

    def shutdown(self) -> None:
        """Cleanly shut down executor (for tests)."""
        if self._shutdown:
            return
        self._executor.shutdown(wait=True)
        self._shutdown = True

    # ----------------------------------------------------------------------------------
    # Internal helpers
    # ----------------------------------------------------------------------------------
    def _is_cache_valid(self, image_path: Path, cache_path: Path) -> bool:
        if not cache_path.exists():
            return False
        try:
            image_mtime = image_path.stat().st_mtime
            cache_mtime = cache_path.stat().st_mtime
            return cache_mtime >= image_mtime
        except OSError:
            return False

    def _cache_path_for(self, image_path: Path) -> Path:
        hash_input = str(image_path)
        digest = hashlib.md5(hash_input.encode(), usedforsecurity=False).hexdigest()
        return self.cache_dir / f"{digest}.jpg"

    def _generate_thumbnail(self, image_path: Path, cache_path: Path) -> str:
        if image_path.suffix.lower() not in SUPPORTED_EXTENSIONS:
            logger.warning("Unsupported format %s", image_path.suffix)
            return self._create_error_thumbnail(cache_path, "unsupported")

        try:
            with Image.open(image_path) as img:
                img = ImageOps.exif_transpose(img)
                img.thumbnail((self.size, self.size))

                if img.mode not in ("RGB", "L"):
                    img = img.convert("RGB")

                img.save(cache_path, "JPEG", quality=90)
                return str(cache_path)
        except Exception as exc:  # Pillow raises many custom errors; catch-all is acceptable
            logger.error("Failed to create thumbnail for %s: %s", image_path, exc)
            return self._create_error_thumbnail(cache_path, str(exc))

    def _create_error_thumbnail(self, cache_path: Path, reason: str) -> str:
        cache_path.parent.mkdir(parents=True, exist_ok=True)
        img = Image.new("RGB", (self.size, self.size), color=(230, 230, 230))
        draw = ImageDraw.Draw(img)
        text = "ERR"
        try:
            font = ImageFont.load_default()
        except OSError:
            font = None

        try:
            left, top, right, bottom = draw.textbbox((0, 0), text, font=font)
            text_width = right - left
            text_height = bottom - top
        except AttributeError:  # Pillow < 8 compatibility
            text_width, text_height = draw.textsize(text, font=font)
        draw.text(
            ((self.size - text_width) / 2, (self.size - text_height) / 2),
            text,
            fill=(200, 0, 0),
            font=font,
        )

        img.save(cache_path, "JPEG", quality=70)
        img.close()
        with self._lock:
            self._failed_paths.add(cache_path)
        return str(cache_path)
