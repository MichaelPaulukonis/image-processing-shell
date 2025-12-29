import unittest
import tempfile
import shutil
from pathlib import Path
from urllib.parse import quote
from flask import Flask
from routes.main import main_bp
from config import ConfigManager
from models.thumbnail_manager import ThumbnailManager
from models.tag_manager import TagManager

class TestServeImage(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.app = Flask(__name__)
        self.app.register_blueprint(main_bp)
        self.app.config['TESTING'] = True
        
        # Mock managers
        self.config_manager = ConfigManager() # Uses default or temp
        self.app.config['CONFIG_MANAGER'] = self.config_manager
        
        self.client = self.app.test_client()
        
        # Create a dummy image file
        self.image_path = Path(self.test_dir) / "test_image.png"
        with open(self.image_path, "wb") as f:
            f.write(b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\nIDATx\x9cc\x00\x01\x00\x00\x05\x00\x01\r\n-\xb4\x00\x00\x00\x00IEND\xaeB`\x82")

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_serve_image_absolute_path(self):
        """Test serving an image using its absolute path via query parameter."""
        # Using query parameter, so simple quote is enough (though requests handles params usually)
        # client.get accepts query_string or just in URL
        encoded_path = quote(str(self.image_path))
        response = self.client.get(f'/api/preview-image?path={encoded_path}')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.mimetype, 'image/png')

    def test_serve_image_not_found(self):
        """Test serving a non-existent image."""
        non_existent = Path(self.test_dir) / "missing.png"
        encoded_path = quote(str(non_existent))
        response = self.client.get(f'/api/preview-image?path={encoded_path}')
        self.assertEqual(response.status_code, 404)

    def test_serve_image_invalid_type(self):
        """Test serving a file that is not a supported image."""
        text_file = Path(self.test_dir) / "test.txt"
        with open(text_file, "w") as f:
            f.write("hello")
        encoded_path = quote(str(text_file))
        response = self.client.get(f'/api/preview-image?path={encoded_path}')
        self.assertEqual(response.status_code, 400)

if __name__ == '__main__':
    unittest.main()