import sys
import tempfile
import unittest
from pathlib import Path
from typing import cast

from PIL import Image  # type: ignore[import-untyped]

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app import create_app  # noqa: E402
from config import ConfigManager  # noqa: E402
from models.tag_manager import TagManager  # noqa: E402
from models.thumbnail_manager import ThumbnailManager  # noqa: E402


class DummyConfigManager:
    def __init__(self, base_dir: Path):
        self.config_dir = Path(base_dir)
        self.cache_dir = self.config_dir / "cache" / "thumbnails"
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.config = {
            'thumbnail_size': 64,
            'log_level': 'ERROR',
            'last_directory': None,
        }

    def initialize_tags(self) -> None:
        # Tests stub this out to avoid touching user config files
        pass

    def set(self, key, value) -> None:
        self.config[key] = value

    def get(self, key, default=None):
        return self.config.get(key, default)


class ThumbnailRoutesTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.image_dir = Path(self.temp_dir.name) / "images"
        self.image_dir.mkdir()
        self.sample_image = self._create_image(self.image_dir / "sample.jpg")

        self.config_manager = DummyConfigManager(Path(self.temp_dir.name))
        self.thumbnail_manager = ThumbnailManager(cache_root=self.temp_dir.name, size=80, max_workers=2)
        self.tag_manager = TagManager(config_dir=self.temp_dir.name)
        self.app = create_app(
            config_manager=cast(ConfigManager, self.config_manager),
            thumbnail_manager=self.thumbnail_manager,
            tag_manager=self.tag_manager,
        )
        self.client = self.app.test_client()

    def tearDown(self) -> None:
        self.thumbnail_manager.shutdown()
        self.temp_dir.cleanup()

    def _create_image(self, path: Path) -> Path:
        img = Image.new('RGB', (320, 180), color=(123, 45, 67))
        img.save(path, format='JPEG')
        img.close()
        return path

    def test_fetch_thumbnail_returns_image_content(self) -> None:
        response = self.client.get('/api/thumbnails', query_string={'path': str(self.sample_image)})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.mimetype, 'image/jpeg')
        self.assertGreater(len(response.data), 0)
        response.close()

    def test_fetch_thumbnail_with_queue_mode_returns_ack(self) -> None:
        response = self.client.get(
            '/api/thumbnails',
            query_string={'path': str(self.sample_image), 'mode': 'queue'}
        )
        self.assertEqual(response.status_code, 200)
        payload = response.get_json()
        self.assertEqual(payload['status'], 'queued')
        response.close()

    def test_queue_endpoint_accepts_multiple_paths(self) -> None:
        missing_path = str(self.image_dir / 'missing.jpg')
        response = self.client.post(
            '/api/thumbnails/queue',
            json={'paths': [str(self.sample_image), missing_path]},
        )
        self.assertEqual(response.status_code, 200)
        payload = response.get_json()
        self.assertEqual(len(payload['results']), 2)
        statuses = {item['status'] for item in payload['results']}
        self.assertIn('queued', statuses)
        self.assertIn('error', statuses)
        response.close()

    def test_fetch_thumbnail_invalid_path_returns_404(self) -> None:
        response = self.client.get('/api/thumbnails', query_string={'path': str(self.image_dir / 'nope.jpg')})
        self.assertEqual(response.status_code, 404)
        response.close()

    def test_get_images_returns_directory_payload(self) -> None:
        second_image = self._create_image(self.image_dir / 'second.jpg')
        response = self.client.get('/api/images', query_string={'dir': str(self.image_dir)})
        self.assertEqual(response.status_code, 200)
        payload = response.get_json()
        self.assertEqual(payload['count'], 2)
        resolved_paths = {Path(img['path']).resolve() for img in payload['images']}
        self.assertIn(self.sample_image.resolve(), resolved_paths)
        self.assertIn(second_image.resolve(), resolved_paths)
        response.close()

    def test_get_images_without_directory_returns_error(self) -> None:
        response = self.client.get('/api/images')
        self.assertEqual(response.status_code, 400)
        response.close()

    def test_directory_listing_returns_subdirectories(self) -> None:
        nested_dir = self.image_dir / 'nested'
        nested_dir.mkdir()
        response = self.client.get('/api/directories', query_string={'base': str(self.image_dir)})
        self.assertEqual(response.status_code, 200)
        payload = response.get_json()
        self.assertEqual(payload['directory'], str(self.image_dir.resolve()))
        child_names = {entry['name'] for entry in payload['entries']}
        self.assertIn('nested', child_names)
        response.close()

    def test_tags_endpoints_roundtrip(self) -> None:
        response = self.client.get('/api/tags')
        self.assertEqual(response.status_code, 200)
        baseline = response.get_json()['tags']
        self.assertIn('comics', baseline)
        response.close()

        add_response = self.client.post('/api/tags', json={'tag': 'abstract'})
        self.assertEqual(add_response.status_code, 200)
        payload = add_response.get_json()
        self.assertTrue(payload['success'])
        self.assertIn('abstract', payload['tags'])
        add_response.close()

    def test_rename_endpoint_renames_file(self) -> None:
        file_to_rename = self._create_image(self.image_dir / 'rename-me.jpg')
        response = self.client.post(
            '/api/rename',
            json={
                'images': [str(file_to_rename)],
                'tags': ['test', 'batch'],
                'prefix': 'art',
                'suffix': 'collection',
            },
        )
        self.assertEqual(response.status_code, 200)
        payload = response.get_json()
        self.assertEqual(payload['success_count'], 1)
        result_entry = payload['results'][0]
        self.assertTrue(result_entry['success'])
        new_path = Path(result_entry['new_path']).resolve()
        self.assertTrue(new_path.exists())
        self.assertEqual(new_path.parent, file_to_rename.resolve().parent)
        response.close()


if __name__ == '__main__':
    unittest.main()
