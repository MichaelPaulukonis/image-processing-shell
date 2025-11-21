"""
Image Tagger & Renamer - Flask Application Entry Point

A locally-hosted web application for viewing, tagging, and batch-renaming 
image files for generative art workflows.
"""
import argparse
import atexit
import logging
from pathlib import Path
from typing import Optional

from flask import Flask  # type: ignore[import-untyped]

from config import ConfigManager
from models.tag_manager import TagManager
from models.thumbnail_manager import ThumbnailManager, DEFAULT_SIZE as DEFAULT_THUMBNAIL_SIZE


def create_app(
    folder_path: Optional[str] = None,
    config_manager: Optional[ConfigManager] = None,
    thumbnail_manager: Optional[ThumbnailManager] = None,
    tag_manager: Optional[TagManager] = None,
):
    """
    Application factory for creating Flask app instance.
    
    Args:
        folder_path: Optional initial folder path to load images from
        
    Returns:
        Flask application instance
    """
    app = Flask(__name__)
    
    # Initialize configuration
    config_manager = config_manager or ConfigManager()
    config_manager.initialize_tags()
    
    # Initialize thumbnail manager (allows injection for tests)
    if thumbnail_manager is None:
        configured_size = config_manager.get('thumbnail_size', DEFAULT_THUMBNAIL_SIZE) or DEFAULT_THUMBNAIL_SIZE
        thumbnail_manager = ThumbnailManager(
            cache_root=config_manager.config_dir,
            size=int(configured_size),
        )
        atexit.register(thumbnail_manager.shutdown)

    if tag_manager is None:
        tag_manager = TagManager(config_dir=config_manager.config_dir)

    # Store managers in app context
    app.config['CONFIG_MANAGER'] = config_manager
    app.config['THUMBNAIL_MANAGER'] = thumbnail_manager
    app.config['TAG_MANAGER'] = tag_manager
    
    # Store initial folder path if provided
    if folder_path:
        resolved_folder = Path(folder_path).expanduser().resolve()
        if resolved_folder.exists() and resolved_folder.is_dir():
            app.config['INITIAL_FOLDER'] = str(resolved_folder)
            config_manager.set('last_directory', str(resolved_folder))
            logging.info(f"Initial folder set to: {resolved_folder}")
        else:
            logging.warning(f"Invalid folder path: {folder_path}")
    
    # Import and register routes
    from routes.main import main_bp
    app.register_blueprint(main_bp)
    
    # TODO: Register API blueprint once implemented
    # from routes.api import api_bp
    # app.register_blueprint(api_bp)
    
    logging.info("Application initialized successfully")
    return app


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description='Image Tagger & Renamer - View, tag, and batch-rename images'
    )
    parser.add_argument(
        'folder',
        nargs='?',
        help='Initial folder path to load images from'
    )
    parser.add_argument(
        '--port',
        type=int,
        default=5000,
        help='Port to run the application on (default: 5000)'
    )
    parser.add_argument(
        '--host',
        default='127.0.0.1',
        help='Host to run the application on (default: 127.0.0.1)'
    )
    parser.add_argument(
        '--debug',
        action='store_true',
        help='Run in debug mode'
    )
    
    return parser.parse_args()


def main():
    """Main entry point for the application."""
    args = parse_arguments()
    
    # Create Flask app
    app = create_app(folder_path=args.folder)
    
    # Run the application
    print(f"\n{'='*60}")
    print(f"  Image Tagger & Renamer")
    print(f"{'='*60}")
    print(f"\n  Access the application at: http://{args.host}:{args.port}")
    print(f"\n  Press CTRL+C to quit\n")
    
    app.run(
        host=args.host,
        port=args.port,
        debug=args.debug
    )


if __name__ == '__main__':
    main()
