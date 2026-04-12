# extract_woodcuts.py

Extracts woodcut illustrations from historical book-page scans using
computer-vision techniques tuned for aged paper, fine engraved linework,
decorative borders, and embedded inline illustrations.

## Requirements

```
opencv-python
numpy
```

Install into a virtual environment:

```bash
python -m venv venv
source venv/bin/activate
pip install opencv-python numpy
```

## Usage

```bash
# Single page
python extract_woodcuts.py page001.jpg

# Multiple pages (shell glob)
python extract_woodcuts.py pages/*.jpg -o output_dir/

# Entire directory
python extract_woodcuts.py --dir ../scans/ -o extracted/

# Mix: explicit files plus a directory
python extract_woodcuts.py cover.jpg --dir ../pages/ -o extracted/

# Debug mode — saves intermediate images alongside results
python extract_woodcuts.py page.jpg --debug
```

## Options

| Flag | Default | Description |
|------|---------|-------------|
| `-d / --dir DIR` | — | Process all images (jpg/jpeg/png/tif/tiff) in DIR |
| `-o / --output DIR` | `extracted` | Output directory |
| `--min-area` | `0.005` | Min candidate area as fraction of image |
| `--max-area` | `0.35` | Max candidate area as fraction of image |
| `--min-pixels` | `2000` | Absolute minimum pixel area |
| `--border-pct` | `0.05` | Fraction of width to suppress on each side |
| `--header-pct` | `0.07` | Fraction of height to suppress at top (running header) |
| `--footer-pct` | `0.05` | Fraction of height to suppress at bottom |
| `--blocksize` | `51` | Adaptive threshold block size (must be odd) |
| `--C` | `15` | Adaptive threshold constant |
| `--dilation-kernel` | `20` | Kernel size for blob dilation — controls how far apart strokes can be and still be treated as one region |
| `--min-density` | `0.05` | Minimum ink density inside a candidate bounding box |
| `--max-density` | `0.90` | Maximum ink density inside a candidate bounding box |
| `--max-regularity` | `0.25` | Reject candidates whose inter-line gap pattern looks text-like (raise to keep borderline regions) |
| `--text-height-mult` | `3.0` | Minimum candidate height as a multiple of estimated text height |
| `--merge-gap` | `80` | Maximum pixel gap between blobs to consider merging into one figure |
| `--no-merge` | off | Disable smart merging of split figures |
| `--padding` | `15` | Padding around each crop in pixels |
| `--debug` | off | Save intermediate images: threshold, blobs, zones overlay, annotated |

## Pipeline

1. **Contrast normalisation** — CLAHE equalisation handles aged/uneven paper tone
2. **Content mask** — suppresses decorative border, running header, and footer before any processing
3. **Adaptive threshold** — binarises with a large local window suited to scan resolution and engraved linework
4. **Text-height estimation** — samples connected components to find the median character height; candidates must be at least `--text-height-mult` times this tall
5. **Horizontal projection** — identifies candidate illustration zones (tall bands of continuous ink) to further constrain the search
6. **Blob dilation** — merges nearby ink strokes into region-level blobs for contour detection; `--dilation-kernel` is the primary tuning knob
7. **Candidate filtering** — area, height, aspect ratio, ink density, horizontal regularity, and zone membership
8. **Smart merging** — groups nearby blobs that plausibly belong to the same illustration (split hands, multi-part compositions); touching blobs are always merged regardless of size difference

## Debug images

With `--debug`, for each input file the script writes:

| File | Contents |
|------|----------|
| `*_threshold.png` | Binarised, masked image after noise removal |
| `*_blobs.png` | After dilation — what contour detection operates on |
| `*_zones.png` | Illustration zones (blue) overlaid on the original |
| `*_annotated.png` | Final extractions (green) and rejected blobs (blue, labelled with rejection reason) |

## Tuning for a new book

Start with `--debug` and inspect `*_blobs.png`:

- **Everything merges into one blob** → lower `--dilation-kernel` (try halving it)
- **Woodcut strokes don't connect** → raise `--dilation-kernel`
- **Border or header captured** → raise `--border-pct` or `--header-pct`
- **Text blocks pass the filter** → lower `--max-regularity` (e.g. `0.20`)
- **Real illustrations rejected** → raise `--max-regularity` or lower `--text-height-mult`
- **Split figures not merging** → raise `--merge-gap`

### Known good settings for *A Curious Hieroglyphick Bible* scans

```bash
python extract_woodcuts.py --dir ../scans/ -o extracted/ --dilation-kernel 12
```
