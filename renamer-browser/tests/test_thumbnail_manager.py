import sys
import tempfile
import time
import unittest
from pathlib import Path

from PIL import Image  # type: ignore[import-untyped]

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from models.thumbnail_manager import ThumbnailManager  # noqa: E402


class ThumbnailManagerTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.assets_dir = Path(self.temp_dir.name) / "assets"
        self.assets_dir.mkdir()
        self.manager = ThumbnailManager(cache_root=self.temp_dir.name, size=120, max_workers=2)

    def tearDown(self) -> None:
        self.manager.shutdown()
        self.temp_dir.cleanup()

    def _create_image(self, name: str, color: tuple[int, int, int] = (10, 20, 30)) -> Path:
        path = self.assets_dir / name
        img = Image.new("RGB", (400, 200), color=color)
        img.save(path, format="JPEG")
        img.close()
        return path

    def test_generate_thumbnail_creates_cache_file(self) -> None:
        source = self._create_image("sample.jpg")
        thumb_path = Path(self.manager.get_thumbnail(source))
        self.assertTrue(thumb_path.exists())
        with Image.open(thumb_path) as thumb:
            self.assertLessEqual(max(thumb.size), 120)

    def test_cache_refreshes_when_source_changes(self) -> None:
        source = self._create_image("refresh.jpg")
        first_thumb = Path(self.manager.get_thumbnail(source))
        first_mtime = first_thumb.stat().st_mtime

        time.sleep(1.1)
        self._create_image("refresh.jpg", color=(200, 10, 10))  # overwrite same path
        refreshed_thumb = Path(self.manager.get_thumbnail(source))
        self.assertEqual(first_thumb, refreshed_thumb)
        self.assertGreater(refreshed_thumb.stat().st_mtime, first_mtime)

    def test_corrupted_image_creates_error_thumbnail(self) -> None:
        bad_file = self.assets_dir / "broken.jpg"
        bad_file.write_text("not an image", encoding="utf-8")
        thumb_path = Path(self.manager.get_thumbnail(bad_file))
        self.assertTrue(thumb_path.exists())
        self.assertIn(thumb_path, self.manager._failed_paths)

    def test_queue_thumbnail_runs_async(self) -> None:
        source = self._create_image("async.jpg")
        future = self.manager.queue_thumbnail(source)
        thumb_path = Path(future.result(timeout=5))
        self.assertTrue(thumb_path.exists())


if __name__ == "__main__":
    unittest.main()
