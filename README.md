# image-processing-shell

A couple of random scripts I use often

See `docs/notes.md` for random notes on command-line usage etc.

## panorama

Some notes and scripts that attempted to force joins where joins should not be.

## renamer-browser

browser-based app that that allows me to go through a directory of images and rename them with a series of tags. Basically, the filenames will server as meta-data.

### Usage

```shell
cd renamer-browser

source venv/bin/activate

python app.py --debug [~/Pictures]
```

Then open browser to `http://127.0.0.1:5000/`

### screenshot

![screenshot of renamer-browser showing thumbnails and rename option panel](./docs/screenshots/renamer-browser-screenshot-00.png)