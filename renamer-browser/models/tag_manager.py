"""Tag persistence and validation utilities for Image Tagger & Renamer."""
from __future__ import annotations

import json
import os
import re
import threading
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple, Union

try:  # fcntl is unavailable on Windows but present on macOS/Linux
    import fcntl  # type: ignore
except ImportError:  # pragma: no cover
    fcntl = None  # type: ignore

TagValidationResult = Tuple[bool, str]


class TagManager:
    """Manage the persistent tag catalog stored in the user config directory."""

    VERSION = "1.0.0"
    DEFAULT_TAGS = [
        "comics",
        "nancy",
        "sluggo",
        "popart",
        "warhol",
        "fineart",
        "advertising",
        "logos",
        "food",
        "horror",
        "western",
    ]
    VALID_TAG_PATTERN = re.compile(r"^[\w-]+$")

    def __init__(
        self,
        config_dir: Optional[Union[str, Path]] = None,
        default_tags: Optional[Iterable[str]] = None,
    ) -> None:
        base_dir = Path(config_dir or Path.home() / ".image-tagger-renamer")
        self.config_dir = base_dir.expanduser().resolve()
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self.tags_file = self.config_dir / "tags.json"
        self._lock = threading.Lock()
        self.default_tags: List[str] = list(default_tags or self.DEFAULT_TAGS)
        self._tag_data: Dict[str, Any] = {}
        self._load_tag_data()

    # --------------------------------------------------------------------------------------
    # Public API
    # --------------------------------------------------------------------------------------
    def get_all_tags(self) -> List[str]:
        """Return a copy of the current tag list."""
        return list(self._tag_data.get("tags", []))

    def get_metadata(self) -> Dict[str, Any]:
        """Expose metadata (created, last_modified, version) for UI display/testing."""
        return {
            "created": self._tag_data.get("created"),
            "last_modified": self._tag_data.get("last_modified"),
            "version": self._tag_data.get("version", self.VERSION),
        }

    def validate_tag(self, tag: str) -> TagValidationResult:
        """Validate a prospective tag before mutating state."""
        candidate = tag.strip()
        if not candidate:
            return False, "Tag cannot be empty"

        if not self.VALID_TAG_PATTERN.match(candidate):
            return False, "Tags may only contain letters, numbers, underscores, or hyphens"

        existing = {t.lower() for t in self.get_all_tags()}
        if candidate.lower() in existing:
            return False, "Tag already exists"

        return True, "OK"

    def add_tag(self, tag: str) -> TagValidationResult:
        """Add a new tag if it passes validation."""
        is_valid, message = self.validate_tag(tag)
        if not is_valid:
            return False, message

        normalized = tag.strip()
        with self._lock:
            self._tag_data.setdefault("tags", []).append(normalized)
            self._touch_last_modified()
            self._persist()
        return True, "Tag added successfully"

    def add_tags(self, tags: Iterable[str]) -> Dict[str, TagValidationResult]:
        """Bulk add helper used by future UI flows."""
        results: Dict[str, TagValidationResult] = {}
        for tag in tags:
            results[tag] = self.add_tag(tag)
        return results

    def remove_tag(self, tag: str) -> TagValidationResult:
        """Remove a tag, ignoring case."""
        candidate = tag.strip()
        if not candidate:
            return False, "Tag cannot be empty"

        with self._lock:
            tags = self._tag_data.get("tags", [])
            lower_map = {t.lower(): idx for idx, t in enumerate(tags)}
            idx = lower_map.get(candidate.lower())
            if idx is None:
                return False, "Tag not found"

            tags.pop(idx)
            self._touch_last_modified()
            self._persist()
            return True, "Tag removed"

    def reload(self) -> None:
        """Force a reload from disk (useful after external edits)."""
        with self._lock:
            self._load_tag_data()

    def reset_to_defaults(self) -> None:
        """Reset the catalog back to the shipped defaults."""
        with self._lock:
            self._tag_data = self._build_default_payload()
            self._persist()

    # --------------------------------------------------------------------------------------
    # Internal helpers
    # --------------------------------------------------------------------------------------
    def _load_tag_data(self) -> None:
        if not self.tags_file.exists():
            self._tag_data = self._build_default_payload()
            self._persist()
            return

        try:
            with open(self.tags_file, "r", encoding="utf-8") as fh:
                data = json.load(fh)
        except (json.JSONDecodeError, OSError):
            self._tag_data = self._build_default_payload()
            self._persist()
            return

        tags = data.get("tags") if isinstance(data, dict) else None
        if not isinstance(tags, list) or not all(isinstance(t, str) for t in tags):
            tags = list(self.default_tags)

        self._tag_data = {
            "tags": tags,
            "created": data.get("created") or self._utc_iso(),
            "last_modified": data.get("last_modified") or self._utc_iso(),
            "version": data.get("version") or self.VERSION,
        }
        # Ensure defaults always include at least one tag to avoid empty options
        if not self._tag_data["tags"]:
            self._tag_data["tags"] = list(self.default_tags)

    def _build_default_payload(self) -> Dict[str, Any]:
        now = self._utc_iso()
        return {
            "tags": list(self.default_tags),
            "created": now,
            "last_modified": now,
            "version": self.VERSION,
        }

    def _touch_last_modified(self) -> None:
        self._tag_data["last_modified"] = self._utc_iso()

    def _persist(self) -> None:
        payload = {
            "tags": list(self._tag_data.get("tags", [])),
            "created": self._tag_data.get("created") or self._utc_iso(),
            "last_modified": self._tag_data.get("last_modified") or self._utc_iso(),
            "version": self.VERSION,
        }
        self._save_tag_data(payload)

    def _save_tag_data(self, tag_data: Dict[str, Any]) -> None:
        temp_file = self.tags_file.with_suffix(".tmp")
        try:
            with open(temp_file, "w", encoding="utf-8") as fh:
                if fcntl is not None:
                    fcntl.flock(fh, fcntl.LOCK_EX)
                json.dump(tag_data, fh, indent=2)
                fh.write("\n")
                fh.flush()
                os.fsync(fh.fileno())
            temp_file.replace(self.tags_file)
            self._tag_data = tag_data
        finally:
            if temp_file.exists():
                try:
                    temp_file.unlink()
                except FileNotFoundError:
                    pass

    @staticmethod
    def _utc_iso() -> str:
        """Return a timezone-aware ISO-8601 timestamp."""
        return datetime.now(UTC).isoformat()
