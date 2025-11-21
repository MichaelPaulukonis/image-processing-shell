"""Main routes and API endpoints for Image Tagger & Renamer application."""
from __future__ import annotations

from pathlib import Path
from typing import Dict, List

from flask import (
    Blueprint,
    abort,
    current_app,
    jsonify,
    render_template,
    request,
    send_file,
    url_for,
)

from config import ConfigManager
from models.file_manager import is_supported_image, rename_file, scan_directory
from models.tag_manager import TagManager
from models.thumbnail_manager import ThumbnailManager


main_bp = Blueprint('main', __name__)


def _get_thumbnail_manager() -> ThumbnailManager:
    manager = current_app.config.get('THUMBNAIL_MANAGER')
    if not manager:
        abort(500, description='Thumbnail manager unavailable')
    return manager


def _get_config_manager() -> ConfigManager:
    manager = current_app.config.get('CONFIG_MANAGER')
    if not manager:
        abort(500, description='Config manager unavailable')
    return manager


def _get_tag_manager() -> TagManager:
    manager = current_app.config.get('TAG_MANAGER')
    if not manager:
        abort(500, description='Tag manager unavailable')
    return manager


def _validate_image_path(raw_path: str) -> Path:
    try:
        candidate = Path(raw_path).expanduser().resolve()
    except OSError as exc:  # Invalid paths, permission issues, etc.
        raise ValueError(str(exc)) from exc

    if not candidate.exists():
        raise FileNotFoundError(raw_path)
    if not candidate.is_file():
        raise ValueError('Path is not a file')
    if not is_supported_image(candidate):
        raise ValueError('Unsupported image format')

    return candidate


def _validate_directory_path(raw_path: str) -> Path:
    try:
        candidate = Path(raw_path).expanduser().resolve()
    except OSError as exc:
        raise ValueError(str(exc)) from exc

    if not candidate.exists():
        raise FileNotFoundError(raw_path)
    if not candidate.is_dir():
        raise ValueError('Path is not a directory')
    return candidate


def _serialize_image(path: Path) -> Dict[str, object]:
    stats = path.stat()
    return {
        'path': str(path),
        'name': path.name,
        'size': stats.st_size,
        'modified': stats.st_mtime,
        'thumbnail': url_for('main.fetch_thumbnail', path=str(path)),
    }


@main_bp.route('/')
def index():
    """Render the main application UI."""
    return render_template('index.html')


@main_bp.route('/health')
def health():
    """Health check endpoint."""
    return {'status': 'ok', 'message': 'Image Tagger & Renamer is running'}, 200


@main_bp.route('/api/thumbnails', methods=['GET'])
def fetch_thumbnail():
    """Return thumbnail file for requested image path (generates if needed)."""
    image_path_param = request.args.get('path')
    if not image_path_param:
        abort(400, description="Query parameter 'path' is required")

    try:
        image_path = _validate_image_path(image_path_param)
    except FileNotFoundError:
        abort(404, description='Image not found')
    except ValueError as exc:
        abort(400, description=str(exc))

    manager = _get_thumbnail_manager()

    if request.args.get('mode') == 'queue':
        manager.queue_thumbnail(image_path)
        return jsonify({'status': 'queued', 'path': str(image_path)})

    thumbnail_path = manager.get_thumbnail(image_path)
    return send_file(thumbnail_path, mimetype='image/jpeg')


@main_bp.route('/api/thumbnails/queue', methods=['POST'])
def queue_thumbnails():
    """Queue thumbnail generation for multiple image paths."""
    payload = request.get_json(silent=True) or {}
    raw_paths = payload.get('paths')

    if not isinstance(raw_paths, list) or not raw_paths:
        abort(400, description="Request JSON must include non-empty 'paths' array")

    manager = _get_thumbnail_manager()
    results: List[dict] = []

    for raw_path in raw_paths:
        if not isinstance(raw_path, str):
            results.append({'path': raw_path, 'status': 'error', 'message': 'Path must be a string'})
            continue

        try:
            resolved = _validate_image_path(raw_path)
        except FileNotFoundError:
            results.append({'path': raw_path, 'status': 'error', 'message': 'Image not found'})
            continue
        except ValueError as exc:
            results.append({'path': raw_path, 'status': 'error', 'message': str(exc)})
            continue

        manager.queue_thumbnail(resolved)
        results.append({'path': str(resolved), 'status': 'queued'})

    return jsonify({'results': results})


@main_bp.route('/api/images', methods=['GET'])
def list_images():
    """Return directory metadata and image entries for the requested folder."""
    requested_dir = request.args.get('dir')
    config_manager = _get_config_manager()
    directory = requested_dir or config_manager.get('last_directory')
    if not directory:
        return jsonify({'error': 'Directory parameter is required'}), 400

    try:
        resolved_dir = _validate_directory_path(directory)
        paths = scan_directory(resolved_dir)
        manager = _get_thumbnail_manager()
        images = []
        for image_path in paths:
            manager.queue_thumbnail(image_path)
            images.append(_serialize_image(image_path))
        config_manager.set('last_directory', str(resolved_dir))
        return jsonify({'directory': str(resolved_dir), 'count': len(images), 'images': images})
    except (ValueError, FileNotFoundError, PermissionError) as exc:
        current_app.logger.warning('Directory error: %s', exc)
        return jsonify({'error': str(exc)}), 400
    except Exception as exc:  # pragma: no cover - defensive logging
        current_app.logger.exception('Unexpected error listing images: %s', exc)
        return jsonify({'error': 'Unable to list images'}), 500


@main_bp.route('/api/tags', methods=['GET'])
def list_tags():
    """Return all saved tags and metadata."""
    tag_manager = _get_tag_manager()
    return jsonify({'tags': tag_manager.get_all_tags(), 'metadata': tag_manager.get_metadata()})


@main_bp.route('/api/tags', methods=['POST'])
def create_tag():
    """Add a new tag to the catalog."""
    payload = request.get_json(silent=True) or {}
    tag_value = payload.get('tag')
    if not isinstance(tag_value, str):
        return jsonify({'error': 'Request must include a tag string'}), 400

    tag_manager = _get_tag_manager()
    success, message = tag_manager.add_tag(tag_value)
    status = 200 if success else 400
    return jsonify({'success': success, 'message': message, 'tags': tag_manager.get_all_tags()}), status


@main_bp.route('/api/rename', methods=['POST'])
def rename_images():
    """Rename selected images according to prefix/tags/suffix payload."""
    payload = request.get_json(silent=True) or {}
    images = payload.get('images')
    tags = payload.get('tags', [])
    prefix = str(payload.get('prefix', '') or '')
    suffix = str(payload.get('suffix', '') or '')
    destination = payload.get('destination')

    if not isinstance(images, list) or not images:
        return jsonify({'error': 'Payload must include a non-empty images list'}), 400
    if not isinstance(tags, list):
        return jsonify({'error': 'tags field must be a list'}), 400

    if destination is not None and not isinstance(destination, str):
        return jsonify({'error': 'destination must be a string path'}), 400

    results = []
    success_count = 0
    error_count = 0

    target_dir = None
    if destination:
        try:
            target_dir = _validate_directory_path(destination)
        except (ValueError, FileNotFoundError) as exc:
            return jsonify({'error': str(exc)}), 400

    for raw_path in images:
        if not isinstance(raw_path, str):
            results.append({'path': raw_path, 'success': False, 'error': 'Image path must be a string'})
            error_count += 1
            continue

        try:
            resolved = _validate_image_path(raw_path)
        except FileNotFoundError:
            results.append({'path': raw_path, 'success': False, 'error': 'Image not found'})
            error_count += 1
            continue
        except ValueError as exc:
            results.append({'path': raw_path, 'success': False, 'error': str(exc)})
            error_count += 1
            continue

        rename_result = rename_file(
            resolved,
            target_dir or resolved.parent,
            prefix=prefix,
            tags=tags,
            suffix=suffix,
        )
        rename_result['path'] = str(resolved)
        results.append(rename_result)
        if rename_result.get('success'):
            success_count += 1
        else:
            error_count += 1

    status = 200 if error_count == 0 else 207  # Multi-status on partial failures
    return jsonify({'results': results, 'success_count': success_count, 'error_count': error_count}), status
