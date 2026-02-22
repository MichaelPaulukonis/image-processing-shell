# image-processing-shell

A couple of random scripts I use often

## tool.sh

CLI utility for batch image-processing operations (video, montage, slicing, resizing).

**See [docs/tool-sh/README.md](docs/tool-sh/README.md) for full documentation.**

See `docs/notes.md` for random notes on command-line usage etc.

## panorama

Some notes and scripts that attempted to force joins where joins should not be.

## renamer-browser

A local-first web application for organizing, tagging, and batch-renaming images. 

**See [renamer-browser/README.md](renamer-browser/README.md) for full documentation.**

### Quick Start

```shell
cd renamer-browser
source venv/bin/activate
python app.py --debug [~/Pictures]
```

Open `http://127.0.0.1:5000/`

### Screenshot

![screenshot of renamer-browser showing thumbnails and rename option panel](./docs/screenshots/renamer-browser-screenshot-00.png)