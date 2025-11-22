"""Integration tests for the parse-filenames API endpoint."""
import json
import sys
import tempfile
import unittest
from pathlib import Path

# Ensure the renamer-browser package root is on sys.path
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app import create_app
from models.tag_manager import TagManager


class ParseFilenamesAPITestCase(unittest.TestCase):
    """Test the /api/parse-filenames endpoint."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.TemporaryDirectory()
        
        # Create tag manager with known tags
        self.tag_manager = TagManager(
            config_dir=self.temp_dir.name,
            default_tags=['comics', 'nancy', 'sluggo', 'popart']
        )
        
        # Create test app
        self.app = create_app(tag_manager=self.tag_manager)
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()

    def tearDown(self):
        """Clean up test fixtures."""
        self.temp_dir.cleanup()

    def test_parse_filenames_success(self):
        """Test successful filename parsing."""
        payload = {
            'filenames': [
                'comics_nancy_001.jpg',
                'comics_nancy_002.jpg',
                'comics_nancy_003.jpg',
            ]
        }
        response = self.client.post(
            '/api/parse-filenames',
            data=json.dumps(payload),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        
        # Check structure
        self.assertIn('suggested_tags', data)
        self.assertIn('suggested_prefix', data)
        self.assertIn('suggested_suffix', data)
        self.assertIn('analysis', data)
        
        # Check content
        self.assertEqual(set(data['suggested_tags']), {'comics', 'nancy'})

    def test_parse_filenames_with_common_prefix(self):
        """Test detecting common prefix."""
        payload = {
            'filenames': [
                'myproject_comics_001.jpg',
                'myproject_nancy_002.jpg',
                'myproject_sluggo_003.jpg',
            ]
        }
        response = self.client.post(
            '/api/parse-filenames',
            data=json.dumps(payload),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['suggested_prefix'], 'myproject')

    def test_parse_filenames_with_common_suffix(self):
        """Test detecting common suffix."""
        payload = {
            'filenames': [
                'comics_final.jpg',
                'nancy_final.jpg',
                'sluggo_final.jpg',
            ]
        }
        response = self.client.post(
            '/api/parse-filenames',
            data=json.dumps(payload),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['suggested_suffix'], 'final')

    def test_parse_filenames_empty_array(self):
        """Test with empty filenames array."""
        payload = {'filenames': []}
        response = self.client.post(
            '/api/parse-filenames',
            data=json.dumps(payload),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn('error', data)

    def test_parse_filenames_missing_field(self):
        """Test with missing filenames field."""
        payload = {}
        response = self.client.post(
            '/api/parse-filenames',
            data=json.dumps(payload),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn('error', data)

    def test_parse_filenames_invalid_data_type(self):
        """Test with non-array filenames."""
        payload = {'filenames': 'not-an-array'}
        response = self.client.post(
            '/api/parse-filenames',
            data=json.dumps(payload),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn('error', data)

    def test_parse_filenames_non_string_items(self):
        """Test with non-string items in array."""
        payload = {'filenames': ['valid.jpg', 123, 'another.jpg']}
        response = self.client.post(
            '/api/parse-filenames',
            data=json.dumps(payload),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn('error', data)

    def test_parse_filenames_invalid_json(self):
        """Test with invalid JSON."""
        response = self.client.post(
            '/api/parse-filenames',
            data='not-valid-json',
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 400)

    def test_parse_filenames_tag_frequency(self):
        """Test that tag frequency is included in response."""
        payload = {
            'filenames': [
                'comics_nancy_001.jpg',
                'comics_sluggo_002.jpg',
                'comics_003.jpg',
                'popart_004.jpg',
            ]
        }
        response = self.client.post(
            '/api/parse-filenames',
            data=json.dumps(payload),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        
        self.assertIn('tag_frequency', data)
        self.assertEqual(data['tag_frequency']['comics'], 3)
        self.assertEqual(data['tag_frequency']['nancy'], 1)
        self.assertEqual(data['tag_frequency']['sluggo'], 1)
        self.assertEqual(data['tag_frequency']['popart'], 1)

    def test_parse_filenames_analysis_metadata(self):
        """Test that analysis metadata is correct."""
        payload = {
            'filenames': [
                'prefix_comics_nancy_suffix.jpg',
                'prefix_comics_sluggo_suffix.jpg',
            ]
        }
        response = self.client.post(
            '/api/parse-filenames',
            data=json.dumps(payload),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        
        analysis = data['analysis']
        self.assertEqual(analysis['total_files'], 2)
        self.assertTrue(analysis['has_common_prefix'])
        self.assertTrue(analysis['has_common_suffix'])
        self.assertGreater(analysis['unique_tags_found'], 0)

    def test_parse_filenames_single_file(self):
        """Test parsing a single file."""
        payload = {
            'filenames': ['comics_nancy_sluggo.jpg']
        }
        response = self.client.post(
            '/api/parse-filenames',
            data=json.dumps(payload),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        
        # All found tags should be suggested for a single file
        self.assertEqual(
            set(data['suggested_tags']), 
            {'comics', 'nancy', 'sluggo'}
        )

    def test_parse_filenames_no_matching_tags(self):
        """Test with filenames that don't match any known tags."""
        payload = {
            'filenames': [
                'random_file_001.jpg',
                'random_file_002.jpg',
                'random_file_003.jpg',
            ]
        }
        response = self.client.post(
            '/api/parse-filenames',
            data=json.dumps(payload),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        
        # Should still work, just with no tags suggested
        self.assertEqual(data['suggested_tags'], [])
        # But should detect the common prefix
        self.assertEqual(data['suggested_prefix'], 'random_file')

    def test_parse_filenames_unicode(self):
        """Test with unicode filenames."""
        payload = {
            'filenames': [
                '文件_comics_001.jpg',
                '文件_nancy_002.jpg',
                '文件_sluggo_003.jpg',
            ]
        }
        response = self.client.post(
            '/api/parse-filenames',
            data=json.dumps(payload),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        
        # Should handle unicode prefix
        self.assertEqual(data['suggested_prefix'], '文件')

    def test_parse_filenames_large_batch(self):
        """Test parsing a large batch of files."""
        payload = {
            'filenames': [f'comics_nancy_{i:04d}.jpg' for i in range(100)]
        }
        response = self.client.post(
            '/api/parse-filenames',
            data=json.dumps(payload),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        
        self.assertEqual(set(data['suggested_tags']), {'comics', 'nancy'})
        self.assertEqual(data['analysis']['total_files'], 100)


if __name__ == '__main__':
    unittest.main()
