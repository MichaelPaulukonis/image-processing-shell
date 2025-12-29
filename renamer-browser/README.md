# Image Tagger & Renamer

**A local-first web application for efficient image organization, tagging, and batch renaming.**

Image Tagger & Renamer is a lightweight, Python-based tool designed for artists and power users who manage large local image collections. It provides a streamlined web-interface for browsing directories, applying reusable tags, and renaming files in bulk with consistent naming conventions.

![Application Screenshot](../docs/screenshots/renamer-browser-screenshot-00.png)

## Table of Contents

1. [Getting Started](#getting-started)
2. [Usage Documentation](#usage-documentation)
3. [Features & Capabilities](#features--capabilities)
4. [Configuration](#configuration)
5. [Development Setup](#development-setup)
6. [Project Structure](#project-structure)
7. [Troubleshooting](#troubleshooting)

---

## Getting Started

### Prerequisites

* **Python 3.10+**
* **pip** (Python package installer)
* **Modern Web Browser** (Chrome, Firefox, Safari, Edge)

### Installation

1. **Navigate to the project directory:**

    ```bash
    cd renamer-browser
    ```

2. **Create and activate a virtual environment:**

    ```bash
    # macOS/Linux
    python3 -m venv venv
    source venv/bin/activate

    # Windows
    python -m venv venv
    .\venv\Scripts\activate
    ```

3. **Install dependencies:**

    ```bash
    pip install -r requirements.txt
    ```

### Quick Start

Run the application pointing to your image directory:

```bash
python app.py ~/Pictures/generative-art
```

Open your web browser and navigate to:
`http://127.0.0.1:5000`

---

## Usage Documentation

### Core Workflow

1. **Browse:** Use the "Change Folder" button to navigate your local filesystem and load a directory of images.
2. **Select:** Click thumbnails to select images.
    * **Multi-Select:** Enabled by default. Click multiple images to build a selection.
    * **Range Select:** Hold `Shift` to select a range of images (feature dependent on browser/implementation).
    * **Toggle:** Click a selected image to deselect it.
3. **Tag:**
    * **Apply Tags:** Click existing tags in the "Tags" panel to toggle them for all selected images.
    * **Create Tags:** Click "+ Add New Tag" to create persistent tags.
4. **Rename:**
    * Enter a **Prefix** (optional).
    * Enter a **Suffix** (optional).
    * The **Filename Preview** updates automatically: `[prefix]_[tag1]_[tag2]_[suffix]_[000].ext`
    * Click **Rename Selected Images** to commit changes.

### Keyboard Shortcuts

| Key | Context | Action |
| --- | --- | --- |
| `Enter` | Thumbnail | Toggle selection |
| `Double Click` | Thumbnail | Open full-size preview modal |
| `Escape` | Preview Modal | Close modal |
| `Arrow Left` | Preview Modal | Navigate to previous image |
| `Arrow Right` | Preview Modal | Navigate to next image |
| `Cmd/Ctrl` + `Left` | Preview Modal | Jump to first image |
| `Cmd/Ctrl` + `Right` | Preview Modal | Jump to last image |
| `Space` | Preview Modal | Toggle selection of current image |

---

## Features & Capabilities

* **Local-First Architecture:** Runs entirely on your machine; no images are uploaded to the cloud.
* **Visual File Management:** Browse directories with a responsive thumbnail grid.
* **Smart Caching:** Thumbnails are generated once and cached locally for performance.
* **Batch Renaming:** deterministic renaming engine that handles numbering and duplicates automatically.
* **Tag Management:** Persistent tag library that allows for consistent naming across sessions.
* **Image Preview:** High(er)-resolution modal viewer with keyboard navigation and selection toggling.
* **Filename Parsing:** Analyzes existing filenames to pre-fill tags and patterns when possible.

---

## Configuration

The application stores user configuration and persistent data in your home directory:

* **Config Directory:** `~/.image-tagger-renamer/`
* **Configuration File:** `~/.image-tagger-renamer/config.json` (Stores last directory, preferences)
* **Tags Database:** `~/.image-tagger-renamer/tags.json`
* **Thumbnail Cache:** `~/.image-tagger-renamer/cache/thumbnails/`

You generally do not need to edit these files manually.

---

## Development Setup

### Running in Debug Mode

For development, run the Flask app with debug mode enabled to support auto-reloading:

```bash
python app.py --debug
```

### Running Tests

The project includes a `unittest` suite covering core logic (file management, tagging, routes).

```bash
# Run all tests
python -m unittest discover tests

# Run specific test file
python -m unittest tests.test_filename_parser
```

### Key Libraries

* **Flask:** Web framework.
* **Pillow (PIL):** Image processing and thumbnail generation.
* **Werkzeug:** WSGI utilities.

---

## Project Structure

```text
renamer-browser/
├── app.py                 # Application entry point and CLI argument parser
├── config.py              # Configuration management (paths, logging)
├── requirements.txt       # Python dependencies
├── models/                # Core business logic
│   ├── file_manager.py    # Filesystem operations (scanning, renaming)
│   ├── tag_manager.py     # JSON-based tag persistence
│   ├── thumbnail_manager.py # Image processing and caching
│   └── filename_parser.py # Logic for parsing existing filenames
├── routes/
│   └── main.py            # Flask API endpoints and view routes
├── static/
│   ├── css/               # Application styling (Dark mode default)
│   └── js/                # Client-side logic (Vanilla JS)
├── templates/
│   ├── index.html         # Main application view
│   └── image-preview-modal.html # Modal component
└── tests/                 # Unit tests
```

---

## Troubleshooting

### Common Issues

**Thumbnails not showing?**
The cache might be stale or corrupted. You can safely delete the cache directory to force regeneration:
`rm -rf ~/.image-tagger-renamer/cache/thumbnails/`

**"Image not found" in preview?**
Ensure the application has read permissions for the directory you are browsing.

**Rename fails?**
Check the application logs (printed to console) for details. Common causes include file permission errors or trying to rename a file to a name that already exists (though the system attempts to auto-increment counters).
