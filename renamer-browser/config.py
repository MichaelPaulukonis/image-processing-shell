"""
Configuration management for Image Tagger & Renamer application.
Handles reading/writing JSON configuration files and managing user preferences.
"""
import json
import os
from pathlib import Path
from datetime import datetime
import logging


class ConfigManager:
    """Manages application configuration and user preferences."""
    
    def __init__(self):
        """Initialize configuration manager with default paths."""
        self.config_dir = Path.home() / ".image-tagger-renamer"
        self.config_file = self.config_dir / "config.json"
        self.tags_file = self.config_dir / "tags.json"
        self.log_file = self.config_dir / "app.log"
        self.cache_dir = self.config_dir / "cache" / "thumbnails"
        
        # Create directories if they don't exist
        self._ensure_directories()
        
        # Load or initialize configuration
        self.config = self._load_config()
        
        # Setup logging
        self._setup_logging()
    
    def _ensure_directories(self):
        """Create necessary directories if they don't exist."""
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
    
    def _load_config(self):
        """Load configuration from file or create with defaults."""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError) as e:
                logging.warning(f"Error loading config, using defaults: {e}")
                return self._default_config()
        else:
            config = self._default_config()
            self.save_config(config)
            return config
    
    def _default_config(self):
        """Return default configuration."""
        return {
            "version": "1.0.0",
            "thumbnail_size": 150,
            "thumbnail_cache_path": str(self.cache_dir),
            "log_level": "INFO",
            "default_numbering_format": "{:03d}",
            "supported_formats": ["jpg", "jpeg", "png", "jp2"],
            "last_directory": None,
            "analytics_enabled": True
        }
    
    def save_config(self, config=None):
        """Save configuration to file."""
        if config is None:
            config = self.config
        
        try:
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=2)
        except IOError as e:
            logging.error(f"Error saving config: {e}")
    
    def _setup_logging(self):
        """Setup logging configuration."""
        log_level = getattr(logging, self.config.get('log_level', 'INFO'))
        
        logging.basicConfig(
            filename=self.log_file,
            level=log_level,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # Also log to console
        console_handler = logging.StreamHandler()
        console_handler.setLevel(log_level)
        console_formatter = logging.Formatter('%(levelname)s - %(message)s')
        console_handler.setFormatter(console_formatter)
        logging.getLogger().addHandler(console_handler)
    
    def get(self, key, default=None):
        """Get configuration value by key."""
        return self.config.get(key, default)
    
    def set(self, key, value):
        """Set configuration value and save."""
        self.config[key] = value
        self.save_config()
    
    def initialize_tags(self):
        """Initialize tags file with default tags if it doesn't exist."""
        if not self.tags_file.exists():
            default_tags = {
                "tags": [
                    "comics", "nancy", "sluggo", "popart", "warhol",
                    "fineart", "advertising", "logos", "food", "horror", "western"
                ],
                "created": datetime.now().isoformat(),
                "last_modified": datetime.now().isoformat(),
                "version": "1.0.0"
            }
            
            try:
                with open(self.tags_file, 'w') as f:
                    json.dump(default_tags, f, indent=2)
                logging.info("Initialized default tags")
            except IOError as e:
                logging.error(f"Error initializing tags: {e}")
                raise
