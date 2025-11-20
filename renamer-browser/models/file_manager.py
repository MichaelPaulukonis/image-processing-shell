"""
File system operations for Image Tagger & Renamer.
Handles directory scanning, filename generation, and file renaming operations.
"""
import logging
import shutil
from pathlib import Path
from typing import List, Tuple, Optional, Union, Dict, Callable


logger = logging.getLogger(__name__)


# Supported image file extensions
SUPPORTED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".jp2"}


def scan_directory(dir_path: Union[str, Path]) -> List[Path]:
    """
    Scan directory for supported image files.
    
    Args:
        dir_path: Path to directory to scan
        
    Returns:
        Sorted list of Path objects for supported image files
        
    Raises:
        ValueError: If directory path is invalid
        PermissionError: If directory is not accessible
    """
    try:
        dir_path_obj = Path(dir_path).expanduser().resolve()
        
        if not dir_path_obj.exists():
            raise ValueError(f"Directory does not exist: {dir_path_obj}")
        
        if not dir_path_obj.is_dir():
            raise ValueError(f"Path is not a directory: {dir_path_obj}")
        
        # Scan for supported image files
        image_files = [
            f for f in dir_path_obj.iterdir()
            if f.is_file() and f.suffix.lower() in SUPPORTED_EXTENSIONS
        ]
        
        # Sort by filename for consistent ordering
        image_files.sort()
        
        logger.info(f"Found {len(image_files)} images in {dir_path_obj}")
        return image_files
        
    except PermissionError as e:
        logger.error(f"Permission denied accessing directory: {dir_path_obj}")
        raise PermissionError(f"Cannot access directory: {dir_path_obj}") from e
    except Exception as e:
        logger.error(f"Error scanning directory {dir_path}: {str(e)}")
        raise


def get_supported_extensions() -> List[str]:
    """
    Get list of supported image file extensions.
    
    Returns:
        List of supported extensions (e.g., ['.jpg', '.jpeg', '.png', '.jp2'])
    """
    return sorted(SUPPORTED_EXTENSIONS)


def is_supported_image(file_path: Path) -> bool:
    """
    Check if a file is a supported image format.
    
    Args:
        file_path: Path to file to check
        
    Returns:
        True if file has a supported image extension
    """
    return file_path.suffix.lower() in SUPPORTED_EXTENSIONS


def get_image_count(dir_path: Union[str, Path]) -> int:
    """
    Get count of supported images in directory without loading full list.
    
    Args:
        dir_path: Path to directory to count images in
        
    Returns:
        Number of supported image files in directory
    """
    try:
        dir_path_obj = Path(dir_path).expanduser().resolve()
        
        if not dir_path_obj.exists() or not dir_path_obj.is_dir():
            return 0
        
        count = sum(
            1 for f in dir_path_obj.iterdir()
            if f.is_file() and f.suffix.lower() in SUPPORTED_EXTENSIONS
        )
        
        return count
        
    except Exception as e:
        logger.error(f"Error counting images in {dir_path}: {str(e)}")
        return 0


def generate_filename(
    prefix: str = "",
    tags: Optional[List[str]] = None,
    suffix: str = "",
    extension: str = "",
    counter: int = 0
) -> str:
    """
    Generate filename with alphabetically sorted tags and numbering.
    
    Format: [prefix]_[tag1]_[tag2]_[tagN]_[suffix]_[000].ext
    
    Args:
        prefix: Optional prefix for filename
        tags: List of tags to include (will be sorted alphabetically)
        suffix: Optional suffix for filename
        extension: File extension (including dot, e.g., '.jpg')
        counter: Numeric counter for duplicate handling (default: 0)
        
    Returns:
        Generated filename string
        
    Examples:
        >>> generate_filename("art", ["comics", "nancy"], "collection", ".png", 0)
        'art_comics_nancy_collection_000.png'
        
        >>> generate_filename("", ["warhol", "popart"], "", ".jpg", 5)
        'popart_warhol_005.jpg'
    """
    if tags is None:
        tags = []
    
    # Sort tags alphabetically (case-insensitive)
    sorted_tags = sorted(tags, key=str.lower)
    
    # Build filename parts (only include non-empty parts)
    parts = []
    
    if prefix:
        parts.append(prefix)
    
    parts.extend(sorted_tags)
    
    if suffix:
        parts.append(suffix)
    
    # Join parts with underscores
    filename = "_".join(parts) if parts else "untitled"
    
    # Add counter (always include, even for first file)
    filename += f"_{counter:03d}"
    
    # Add extension
    if extension and not extension.startswith('.'):
        extension = '.' + extension
    
    return f"{filename}{extension}"


def parse_filename_parts(filename: str) -> Tuple[str, List[str], str, str, int]:
    """
    Parse a generated filename back into its components.
    
    Args:
        filename: Generated filename to parse
        
    Returns:
        Tuple of (prefix, tags, suffix, extension, counter)
        
    Note: This is best-effort parsing and may not perfectly reconstruct
    the original components if tags contain underscores.
    """
    # Extract extension
    path = Path(filename)
    extension = path.suffix
    name_without_ext = path.stem
    
    # Extract counter (last 3 digits)
    parts = name_without_ext.split('_')
    
    counter = 0
    if parts and parts[-1].isdigit() and len(parts[-1]) == 3:
        counter = int(parts[-1])
        parts = parts[:-1]
    
    # Remaining parts could be prefix, tags, and suffix
    # Without additional context, we can't definitively separate them
    # Return them all as tags for simplicity
    return ("", parts, "", extension, counter)


def rename_file(
    src_path: Union[str, Path],
    dest_dir: Union[str, Path],
    prefix: str = "",
    tags: Optional[List[str]] = None,
    suffix: str = "",
    counter: int = 0
) -> Dict[str, Union[str, int]]:
    """
    Atomically rename a file with duplicate detection.
    
    Uses shutil.move() for atomic operation. If destination file exists,
    automatically increments counter until unique filename is found.
    
    Args:
        src_path: Source file path to rename
        dest_dir: Destination directory (can be same as source)
        prefix: Optional prefix for new filename
        tags: List of tags to include in filename
        suffix: Optional suffix for new filename
        counter: Starting counter value (default: 0)
        
    Returns:
        Dictionary with keys:
        - 'success': bool indicating success
        - 'old_path': str original file path
        - 'new_path': str new file path
        - 'filename': str final filename used
        - 'counter': int final counter value used
        - 'error': str error message (only if success=False)
        
    Raises:
        ValueError: If source file doesn't exist or isn't supported format
        PermissionError: If file operations are not permitted
        
    Examples:
        >>> rename_file(
        ...     '/path/to/image.jpg',
        ...     '/path/to/',
        ...     prefix='art',
        ...     tags=['comics', 'nancy'],
        ...     suffix='collection'
        ... )
        {'success': True, 'old_path': '/path/to/image.jpg', 
         'new_path': '/path/to/art_comics_nancy_collection_000.jpg',
         'filename': 'art_comics_nancy_collection_000.jpg', 'counter': 0}
    """
    try:
        src_path_obj = Path(src_path).expanduser().resolve()
        dest_dir_obj = Path(dest_dir).expanduser().resolve()
        
        # Validate source file
        if not src_path_obj.exists():
            raise ValueError(f"Source file does not exist: {src_path_obj}")
        
        if not src_path_obj.is_file():
            raise ValueError(f"Source path is not a file: {src_path_obj}")
        
        if not is_supported_image(src_path_obj):
            raise ValueError(
                f"File format not supported: {src_path_obj.suffix}. "
                f"Supported formats: {', '.join(get_supported_extensions())}"
            )
        
        # Validate/create destination directory
        if not dest_dir_obj.exists():
            logger.info(f"Creating destination directory: {dest_dir_obj}")
            dest_dir_obj.mkdir(parents=True, exist_ok=True)
        
        if not dest_dir_obj.is_dir():
            raise ValueError(f"Destination path is not a directory: {dest_dir_obj}")
        
        # Get file extension from source
        extension = src_path_obj.suffix
        
        # Find unique filename by incrementing counter
        original_counter = counter
        while True:
            new_filename = generate_filename(prefix, tags, suffix, extension, counter)
            dest_path = dest_dir_obj / new_filename
            
            # Check if destination already exists
            if not dest_path.exists():
                break
            
            # If destination is the same as source, we're done
            if dest_path.samefile(src_path_obj):
                logger.info(f"File already has target name: {new_filename}")
                return {
                    'success': True,
                    'old_path': str(src_path_obj),
                    'new_path': str(dest_path),
                    'filename': new_filename,
                    'counter': counter,
                    'skipped': True,
                    'reason': 'File already has target name'
                }
            
            # Increment counter and try again
            counter += 1
            
            # Safety check to prevent infinite loop
            if counter > 9999:
                raise ValueError(
                    f"Could not find unique filename after 9999 attempts. "
                    f"Too many files with similar names in {dest_dir_obj}"
                )
        
        # Perform atomic rename using shutil.move()
        logger.info(f"Renaming: {src_path_obj.name} -> {new_filename}")
        new_path = shutil.move(str(src_path_obj), str(dest_path))
        
        counter_info = ""
        if counter != original_counter:
            counter_info = f" (counter incremented from {original_counter} to {counter})"
        
        logger.info(f"Successfully renamed to: {new_filename}{counter_info}")
        
        return {
            'success': True,
            'old_path': str(src_path_obj),
            'new_path': str(new_path),
            'filename': new_filename,
            'counter': counter
        }
        
    except (ValueError, PermissionError) as e:
        logger.error(f"Error renaming file {src_path}: {str(e)}")
        return {
            'success': False,
            'old_path': str(src_path),
            'new_path': '',
            'filename': '',
            'counter': counter,
            'error': str(e)
        }
    except Exception as e:
        logger.error(f"Unexpected error renaming file {src_path}: {str(e)}")
        return {
            'success': False,
            'old_path': str(src_path),
            'new_path': '',
            'filename': '',
            'counter': counter,
            'error': f"Unexpected error: {str(e)}"
        }


def batch_rename_files(
    file_paths: List[Union[str, Path]],
    dest_dir: Union[str, Path],
    prefix: str = "",
    tags: Optional[List[str]] = None,
    suffix: str = "",
    start_counter: int = 0,
    progress_callback: Optional[Callable[[int, int, Dict], None]] = None
) -> Dict[str, Union[int, List[Dict]]]:
    """
    Batch rename multiple files with progress tracking.
    
    Renames files sequentially, handling duplicates and tracking progress.
    Continues processing even if individual files fail, collecting all results.
    
    Args:
        file_paths: List of source file paths to rename
        dest_dir: Destination directory for renamed files
        prefix: Optional prefix for new filenames
        tags: List of tags to include in filenames
        suffix: Optional suffix for new filenames
        start_counter: Starting counter value (default: 0)
        progress_callback: Optional callback function(current, total, result)
                          called after each file is processed
        
    Returns:
        Dictionary with keys:
        - 'total': int total files processed
        - 'successful': int number of successful renames
        - 'failed': int number of failed renames
        - 'skipped': int number of skipped files
        - 'results': List[Dict] individual results for each file
        - 'errors': List[Dict] only the failed operations with error details
        
    Examples:
        >>> def progress(current, total, result):
        ...     print(f"Processing {current}/{total}: {result['filename']}")
        ...
        >>> batch_rename_files(
        ...     ['/path/img1.jpg', '/path/img2.jpg'],
        ...     '/output/',
        ...     tags=['comics', 'nancy'],
        ...     progress_callback=progress
        ... )
        {'total': 2, 'successful': 2, 'failed': 0, 'skipped': 0, 
         'results': [...], 'errors': []}
    """
    results = []
    errors = []
    successful = 0
    failed = 0
    skipped = 0
    
    counter = start_counter
    total_files = len(file_paths)
    
    logger.info(
        f"Starting batch rename of {total_files} files "
        f"(prefix={prefix}, tags={tags}, suffix={suffix})"
    )
    
    for index, file_path in enumerate(file_paths, 1):
        try:
            # Attempt to rename the file
            result = rename_file(
                file_path,
                dest_dir,
                prefix=prefix,
                tags=tags,
                suffix=suffix,
                counter=counter
            )
            
            results.append(result)
            
            # Track statistics
            if result['success']:
                if result.get('skipped'):
                    skipped += 1
                    logger.info(
                        f"[{index}/{total_files}] Skipped: {Path(file_path).name}"
                    )
                else:
                    successful += 1
                    # Increment counter for next file only on actual rename
                    counter = int(result['counter']) + 1
                    logger.info(
                        f"[{index}/{total_files}] Renamed: "
                        f"{Path(file_path).name} -> {result['filename']}"
                    )
            else:
                failed += 1
                errors.append(result)
                logger.error(
                    f"[{index}/{total_files}] Failed: {Path(file_path).name} - "
                    f"{result.get('error', 'Unknown error')}"
                )
            
            # Call progress callback if provided
            if progress_callback:
                try:
                    progress_callback(index, total_files, result)
                except Exception as e:
                    logger.error(f"Error in progress callback: {str(e)}")
                    
        except Exception as e:
            # Catch any unexpected errors in the batch loop itself
            error_result = {
                'success': False,
                'old_path': str(file_path),
                'new_path': '',
                'filename': '',
                'counter': counter,
                'error': f"Batch processing error: {str(e)}"
            }
            results.append(error_result)
            errors.append(error_result)
            failed += 1
            logger.error(
                f"[{index}/{total_files}] Exception processing {file_path}: {str(e)}"
            )
    
    summary = {
        'total': total_files,
        'successful': successful,
        'failed': failed,
        'skipped': skipped,
        'results': results,
        'errors': errors
    }
    
    logger.info(
        f"Batch rename complete: {successful} successful, "
        f"{failed} failed, {skipped} skipped out of {total_files} total"
    )
    
    return summary


def get_batch_preview(
    file_paths: List[Union[str, Path]],
    prefix: str = "",
    tags: Optional[List[str]] = None,
    suffix: str = "",
    start_counter: int = 0
) -> List[Dict[str, str]]:
    """
    Preview what filenames would be generated for a batch rename without performing it.
    
    Args:
        file_paths: List of source file paths
        prefix: Optional prefix for new filenames
        tags: List of tags to include in filenames
        suffix: Optional suffix for new filenames
        start_counter: Starting counter value (default: 0)
        
    Returns:
        List of dictionaries with keys:
        - 'old_name': str original filename
        - 'new_name': str generated filename
        - 'old_path': str full original path
        - 'counter': int counter that would be used
        
    Examples:
        >>> get_batch_preview(
        ...     ['/path/img1.jpg', '/path/img2.png'],
        ...     tags=['comics', 'nancy']
        ... )
        [
            {'old_name': 'img1.jpg', 'new_name': 'comics_nancy_000.jpg', 
             'old_path': '/path/img1.jpg', 'counter': 0},
            {'old_name': 'img2.png', 'new_name': 'comics_nancy_001.png',
             'old_path': '/path/img2.png', 'counter': 1}
        ]
    """
    previews = []
    counter = start_counter
    
    for file_path in file_paths:
        try:
            path_obj = Path(file_path)
            
            # Skip if not a supported image
            if not is_supported_image(path_obj):
                continue
            
            extension = path_obj.suffix
            new_filename = generate_filename(prefix, tags, suffix, extension, counter)
            
            previews.append({
                'old_name': path_obj.name,
                'new_name': new_filename,
                'old_path': str(path_obj),
                'counter': counter
            })
            
            counter += 1
            
        except Exception as e:
            logger.error(f"Error generating preview for {file_path}: {str(e)}")
            continue
    
    return previews


def validate_rename_operation(
    src_path: Union[str, Path],
    dest_dir: Union[str, Path],
    prefix: str = "",
    tags: Optional[List[str]] = None,
    suffix: str = ""
) -> Dict[str, Union[bool, str, List[str]]]:
    """
    Validate a rename operation before executing it.
    
    Checks for common issues that would prevent a successful rename:
    - Source file existence and format
    - Destination directory writability
    - Filename validity
    
    Args:
        src_path: Source file path to validate
        dest_dir: Destination directory to validate
        prefix: Prefix for filename validation
        tags: Tags for filename validation
        suffix: Suffix for filename validation
        
    Returns:
        Dictionary with keys:
        - 'valid': bool indicating if operation is valid
        - 'error': str error message (only if valid=False)
        - 'warnings': List[str] non-fatal issues
        
    Examples:
        >>> validate_rename_operation('/path/img.jpg', '/output/', tags=['test'])
        {'valid': True, 'warnings': []}
    """
    warnings = []
    
    try:
        src_path_obj = Path(src_path).expanduser().resolve()
        dest_dir_obj = Path(dest_dir).expanduser().resolve()
        
        # Check source file
        if not src_path_obj.exists():
            return {
                'valid': False,
                'error': f"Source file does not exist: {src_path_obj}",
                'warnings': warnings
            }
        
        if not src_path_obj.is_file():
            return {
                'valid': False,
                'error': f"Source path is not a file: {src_path_obj}",
                'warnings': warnings
            }
        
        if not is_supported_image(src_path_obj):
            return {
                'valid': False,
                'error': f"Unsupported file format: {src_path_obj.suffix}",
                'warnings': warnings
            }
        
        # Check destination directory
        if dest_dir_obj.exists():
            if not dest_dir_obj.is_dir():
                return {
                    'valid': False,
                    'error': f"Destination path exists but is not a directory: {dest_dir_obj}",
                    'warnings': warnings
                }
            
            # Test write permissions
            try:
                test_file = dest_dir_obj / ".write_test_tmp"
                test_file.touch()
                test_file.unlink()
            except PermissionError:
                return {
                    'valid': False,
                    'error': f"No write permission for destination directory: {dest_dir_obj}",
                    'warnings': warnings
                }
        else:
            # Check if parent directory is writable for creating dest_dir
            parent = dest_dir_obj.parent
            if not parent.exists():
                warnings.append(f"Parent directory will be created: {parent}")
            elif not parent.is_dir():
                return {
                    'valid': False,
                    'error': f"Parent path exists but is not a directory: {parent}",
                    'warnings': warnings
                }
        
        # Validate filename components
        if prefix and not prefix.replace('_', '').replace('-', '').isalnum():
            warnings.append(f"Prefix contains special characters: '{prefix}'")
        
        if suffix and not suffix.replace('_', '').replace('-', '').isalnum():
            warnings.append(f"Suffix contains special characters: '{suffix}'")
        
        if tags:
            for tag in tags:
                if not tag.replace('_', '').replace('-', '').isalnum():
                    warnings.append(f"Tag contains special characters: '{tag}'")
        
        return {
            'valid': True,
            'warnings': warnings
        }
        
    except Exception as e:
        logger.error(f"Error validating rename operation: {str(e)}")
        return {
            'valid': False,
            'error': f"Validation error: {str(e)}",
            'warnings': warnings
        }


def get_error_recovery_suggestions(error: str) -> List[str]:
    """
    Provide recovery suggestions based on error message.
    
    Args:
        error: Error message string
        
    Returns:
        List of suggested recovery actions
        
    Examples:
        >>> get_error_recovery_suggestions("Permission denied")
        ['Check file permissions', 'Ensure file is not open in another program', ...]
    """
    suggestions = []
    
    error_lower = error.lower()
    
    if "permission" in error_lower or "access" in error_lower:
        suggestions.extend([
            "Check file and directory permissions",
            "Ensure files are not open in another program",
            "Try running with appropriate user permissions",
            "Check if directory is read-only"
        ])
    
    if "does not exist" in error_lower or "not found" in error_lower:
        suggestions.extend([
            "Verify the file path is correct",
            "Check if the file was moved or deleted",
            "Ensure the directory exists"
        ])
    
    if "not a directory" in error_lower or "not a file" in error_lower:
        suggestions.extend([
            "Verify the path points to the correct type (file vs directory)",
            "Check for typos in the path"
        ])
    
    if "unsupported" in error_lower or "format" in error_lower:
        suggestions.extend([
            f"Supported formats: {', '.join(get_supported_extensions())}",
            "Convert the file to a supported format",
            "Check if the file extension is correct"
        ])
    
    if "duplicate" in error_lower or "exists" in error_lower:
        suggestions.extend([
            "The system will auto-increment filenames to avoid conflicts",
            "Check if you need to clean up old files first"
        ])
    
    if not suggestions:
        suggestions.extend([
            "Check application logs for detailed error information",
            "Verify all file paths are correct",
            "Ensure sufficient disk space is available"
        ])
    
    return suggestions
