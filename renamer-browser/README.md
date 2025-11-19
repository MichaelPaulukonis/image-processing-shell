# Image Tagger & Renamer

A locally-hosted web application for viewing, tagging, and batch-renaming image files for generative art workflows.

## Features

- Visual thumbnail-based interface for browsing images
- Flexible tagging system with persistent tag library
- Batch rename with prefix, tags (alphabetically sorted), suffix, and automatic numbering
- Support for JPG, PNG, and JP2 image formats
- Thumbnail caching for fast loading of large image collections
- Dark mode interface

## Requirements

- Python 3.10 or higher
- Flask 2.3.3
- Pillow 10.1.0
- Modern web browser (Chrome, Firefox, Safari)

## Installation

1. Clone or download this repository

2. Create and activate a virtual environment:

   ```bash
   # Create virtual environment
   python -m venv venv
   
   # Activate on macOS/Linux
   source venv/bin/activate
   
   # Activate on Windows
   venv\Scripts\activate
   ```

3. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

## Usage

### Basic Usage

Launch the application:
```bash
python app.py
```

Then open your browser to: http://127.0.0.1:5000

### Specify Initial Folder

Launch with a specific folder path:
```bash
python app.py /path/to/your/images
```

### Command Line Options

```bash
python app.py [folder] [options]

Positional arguments:
  folder                Initial folder path to load images from

Optional arguments:
  --port PORT          Port to run the application on (default: 5000)
  --host HOST          Host to run the application on (default: 127.0.0.1)
  --debug              Run in debug mode
```

### Examples

```bash
# Launch with default settings
python app.py

# Launch with specific folder
python app.py ~/Downloads/images

# Launch on different port
python app.py --port 8080

# Launch in debug mode
python app.py --debug

# Combine options
python app.py ~/Pictures/generative-art --port 8080 --debug
```

## Configuration

Configuration files are stored in `~/.image-tagger-renamer/`:

- `config.json` - Application settings
- `tags.json` - Tag library (persists between sessions)
- `app.log` - Application logs
- `cache/thumbnails/` - Cached thumbnails

## Workflow

1. Launch the application and select a folder
2. Browse thumbnails in the grid view
3. Select images (single or multi-select mode)
4. Enter optional prefix/suffix
5. Select tags from the library or add new ones
6. Preview the resulting filename
7. Click "Rename Selected Images"

## Filename Format

Renamed files follow this format:
```
[prefix]_[tag1]_[tag2]_[tagN]_[suffix]_[000].ext
```

- Tags are sorted alphabetically (not in UI selection order)
- Numbering starts at 000 for duplicates
- Original filename is completely replaced
- File extension is preserved

## Development Status

**Current Version:** MVP Development (v1.0.0)

This is an actively developed MVP. Core features are being implemented following the PRD specifications.

## License

MIT License - See LICENSE file for details

## Troubleshooting

**Application won't start:**
- Ensure Python 3.10+ is installed: `python --version`
- Verify dependencies are installed: `pip install -r requirements.txt`
- Check if port 5000 is available or use `--port` option

**Images not loading:**
- Verify folder path is correct and accessible
- Check supported formats: JPG, PNG, JP2
- Review logs in `~/.image-tagger-renamer/app.log`

**Permission errors:**
- Ensure read/write access to the selected folder
- Check permissions on `~/.image-tagger-renamer/` directory

For more help, check the logs or open an issue on GitHub.
