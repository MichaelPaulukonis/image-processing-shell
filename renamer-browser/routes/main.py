"""
Main routes for Image Tagger & Renamer application.
"""
from flask import Blueprint, render_template


main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def index():
    """Render the main application UI."""
    return render_template('index.html')


@main_bp.route('/health')
def health():
    """Health check endpoint."""
    return {'status': 'ok', 'message': 'Image Tagger & Renamer is running'}, 200
