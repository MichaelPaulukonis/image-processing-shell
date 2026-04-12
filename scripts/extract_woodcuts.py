#!/usr/bin/env python3
"""
Woodcut Extractor v2 - PAGE-AWARE WITH SMART MERGING
=====================================================

Extracts woodcut illustrations from historical book pages with:
- CLAHE contrast normalization for aged/uneven paper
- Explicit border, header, and footer suppression
- Text-height estimation to distinguish text from illustrations
- Horizontal projection analysis to locate illustration zones
- Ink density scoring
- Smart merging of split figures

Usage:
    python extract_woodcuts_v2.py input_image.jpg
    python extract_woodcuts_v2.py pages/*.jpg -o output_dir
    python extract_woodcuts_v2.py page.jpg --debug --merge-gap 60
    python extract_woodcuts_v2.py page.jpg --border-pct 0.06 --header-pct 0.08

Author: Generated for michael paulukonis
Date: March 2026
"""

import cv2
import numpy as np
import argparse
import os
from pathlib import Path


# ---------------------------------------------------------------------------
# Preprocessing helpers
# ---------------------------------------------------------------------------

def normalize_contrast(gray):
    """Apply CLAHE to normalize contrast across aged/uneven paper."""
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(16, 16))
    return clahe.apply(gray)


def create_content_mask(img_height, img_width, border_pct=0.05,
                        header_pct=0.07, footer_pct=0.05):
    """
    Build a mask that suppresses the decorative border, running header,
    and footer before contour detection.

    The border is excluded by a lateral margin on all four sides.
    The header zone (top) and footer zone (bottom) are excluded separately
    so they can be tuned independently from the side margins.
    """
    mask = np.zeros((img_height, img_width), dtype=np.uint8)
    bx = int(img_width * border_pct)
    top = int(img_height * header_pct)
    bottom = img_height - int(img_height * footer_pct)
    mask[top:bottom, bx:img_width - bx] = 255
    return mask


# ---------------------------------------------------------------------------
# Text-height estimation
# ---------------------------------------------------------------------------

def estimate_text_height(thresh, mask):
    """
    Estimate the median character height from connected components.

    Filters to components whose size and aspect ratio are consistent with
    individual glyphs (not whole words, not illustrations).  Returns the
    median height, which is then used as a yardstick: illustrations must
    be at least N× this tall.
    """
    masked = cv2.bitwise_and(thresh, mask)
    n_labels, _labels, stats, _ = cv2.connectedComponentsWithStats(
        masked, connectivity=8
    )
    char_heights = []
    for i in range(1, n_labels):
        h = stats[i, cv2.CC_STAT_HEIGHT]
        w = stats[i, cv2.CC_STAT_WIDTH]
        area = stats[i, cv2.CC_STAT_AREA]
        aspect = w / h if h > 0 else 0
        # Accept components that plausibly represent a single character
        if 8 <= h <= 100 and 5 <= w <= 200 and area >= 20 and 0.1 <= aspect <= 6.0:
            char_heights.append(h)
    if not char_heights:
        return 30  # safe fallback
    return max(int(np.median(char_heights)), 15)


# ---------------------------------------------------------------------------
# Horizontal projection / illustration-zone detection
# ---------------------------------------------------------------------------

def get_horizontal_projection(thresh, mask):
    """Count foreground pixels per row within the content mask."""
    masked = cv2.bitwise_and(thresh, mask)
    return np.sum(masked > 0, axis=1).astype(np.float32)


def find_illustration_zones(h_proj, img_width, text_height):
    """
    Identify candidate illustration zones from the horizontal projection.

    Text lines produce moderate, spread-out ink coverage.  Illustration
    blocks interrupt text flow and appear as tall continuous bands of
    content.  Any contiguous band of inked rows taller than
    3× text_height is treated as a candidate zone.

    Returns a list of (top_row, bottom_row) tuples.  Returns [] if nothing
    qualifies — callers should skip zone-filtering when the list is empty.
    """
    row_threshold = img_width * 0.02  # row must have at least 2% ink coverage
    in_content = h_proj > row_threshold

    # Collect contiguous content bands
    bands = []
    start = None
    for i, is_content in enumerate(in_content):
        if is_content and start is None:
            start = i
        elif not is_content and start is not None:
            bands.append((start, i))
            start = None
    if start is not None:
        bands.append((start, len(h_proj)))

    # Merge bands separated by a small gap (inter-line whitespace)
    merged = []
    for top, bottom in bands:
        if merged and top - merged[-1][1] <= text_height:
            merged[-1] = (merged[-1][0], bottom)
        else:
            merged.append([top, bottom])

    return [
        (top, bottom)
        for top, bottom in merged
        if (bottom - top) >= text_height * 3
    ]


def in_illustration_zone(y, h, zones, overlap_threshold=0.4):
    """
    Return True if the bounding box overlaps at least overlap_threshold
    of its height with any known illustration zone.

    If zones is empty the check is skipped (returns True) so that the
    absence of detected zones does not block all candidates.
    """
    if not zones:
        return True
    box_top, box_bottom = y, y + h
    for zone_top, zone_bottom in zones:
        overlap = max(0, min(box_bottom, zone_bottom) - max(box_top, zone_top))
        if h > 0 and overlap / h >= overlap_threshold:
            return True
    return False


# ---------------------------------------------------------------------------
# Ink density
# ---------------------------------------------------------------------------

def ink_density(thresh, x, y, w, h):
    """Ratio of foreground pixels to bounding-box area."""
    if w <= 0 or h <= 0:
        return 0.0
    roi = thresh[y:y + h, x:x + w]
    return float(np.sum(roi > 0)) / roi.size


def horizontal_regularity(thresh, x, y, w, h):
    """
    Fraction of rows within the bounding box whose ink count is below
    30% of the mean row ink count.

    Text blocks have regular inter-line gaps (many near-empty rows) →
    high regularity score.  Woodcut illustrations have more continuous
    ink distribution → lower regularity score.

    Returns a value in [0, 1].  A score above ~0.35 is text-like.
    """
    if w <= 0 or h <= 0:
        return 1.0
    roi = thresh[y:y + h, x:x + w]
    row_sums = np.sum(roi > 0, axis=1).astype(float)
    if row_sums.max() == 0:
        return 1.0
    mean_ink = row_sums.mean()
    return float(np.sum(row_sums < mean_ink * 0.3) / len(row_sums))


# ---------------------------------------------------------------------------
# Smart merging
# ---------------------------------------------------------------------------

def smart_merge_boxes(boxes, max_gap=80, size_tolerance=0.6):
    """
    Merge bounding boxes that are likely parts of the same woodcut.

    Merging criteria:
    - Boxes are within max_gap pixels of each other
    - Boxes are roughly aligned horizontally or vertically
    - Boxes are of similar size (within size_tolerance ratio)

    Args:
        boxes: list of (x, y, w, h, area, contour) tuples
        max_gap: maximum pixel gap to consider merging
        size_tolerance: maximum fractional size difference allowed

    Returns:
        list of (x, y, w, h, area, None) tuples
    """
    if not boxes:
        return []

    boxes = sorted(boxes, key=lambda b: (b[1], b[0]))
    merged = []
    used = set()

    for i, (x1, y1, w1, h1, area1, cnt1) in enumerate(boxes):
        if i in used:
            continue

        group = [(x1, y1, w1, h1, area1, cnt1)]
        group_idx = [i]

        for j, (x2, y2, w2, h2, area2, cnt2) in enumerate(boxes):
            if j <= i or j in used:
                continue

            x1_max, y1_max = x1 + w1, y1 + h1
            x2_max, y2_max = x2 + w2, y2 + h2

            h_gap = max(0, max(x1, x2) - min(x1_max, x2_max))
            v_gap = max(0, max(y1, y2) - min(y1_max, y2_max))
            x_overlap = max(0, min(x1_max, x2_max) - max(x1, x2))
            y_overlap = max(0, min(y1_max, y2_max) - max(y1, y2))

            # Gap = distance between nearest edges in the separating dimension(s).
            # Previous min() was wrong: two boxes far apart in X but vertically
            # overlapping got gap=0 and merged spuriously.
            if x_overlap > 0 and y_overlap > 0:
                gap = 0           # actually overlapping
            elif x_overlap > 0:
                gap = v_gap       # same column, separated vertically
            elif y_overlap > 0:
                gap = h_gap       # same row band, separated horizontally
            else:
                gap = max(h_gap, v_gap)  # diagonal — both dims must be close

            if gap > max_gap:
                continue

            h_aligned = y_overlap > min(h1, h2) * 0.3
            v_aligned = x_overlap > min(w1, w2) * 0.3
            if not (h_aligned or v_aligned) and gap > 40:
                continue

            # When gap > 20, enforce size similarity to avoid merging distinct
            # illustrations.  When gap <= 20 (touching or overlapping), always
            # merge — the piece is almost certainly part of the same figure.
            size_ratio = max(area1, area2) / (min(area1, area2) + 1)
            if size_ratio > (1 + size_tolerance) and gap > 20:
                continue

            group.append((x2, y2, w2, h2, area2, cnt2))
            group_idx.append(j)

        for idx in group_idx:
            used.add(idx)

        if len(group) > 1:
            all_x     = [b[0]           for b in group]
            all_y     = [b[1]           for b in group]
            all_x_max = [b[0] + b[2]    for b in group]
            all_y_max = [b[1] + b[3]    for b in group]
            mx, my = min(all_x), min(all_y)
            mw = max(all_x_max) - mx
            mh = max(all_y_max) - my
            ma = sum(b[4] for b in group)
            print(f"    \u2713 Merged {len(group)} boxes into {mw}\u00d7{mh}px")
            merged.append((mx, my, mw, mh, ma, None))
        else:
            merged.append((x1, y1, w1, h1, area1, cnt1))

    return merged


# ---------------------------------------------------------------------------
# Main extraction function
# ---------------------------------------------------------------------------

def extract_woodcuts(image_path, output_dir='extracted',
                     min_area_pct=0.005, max_area_pct=0.35,
                     min_pixels=2000,
                     padding=15, blocksize=51, C=15,
                     debug=False, merge_gap=80, enable_merging=True,
                     border_pct=0.05, header_pct=0.07, footer_pct=0.05,
                     dilation_kernel=20,
                     min_density=0.05, max_density=0.90,
                     text_height_multiplier=3.0,
                     max_regularity=0.25):
    """
    Extract woodcut illustrations from a historical book-page scan.

    Pipeline:
      1. Normalize contrast (CLAHE) for aged/uneven paper.
      2. Mask out the decorative border, running header, and footer.
      3. Adaptive threshold with scan-tuned parameters.
      4. Estimate text character height from connected components.
      5. Horizontal projection analysis to locate illustration zones.
      6. Denoise, then dilate to merge strokes into region blobs.
      7. Find contours; filter by area, height, aspect, density, zone.
      8. Optionally merge split figures.
      9. Crop and save.

    Args:
        image_path:            Input image file path.
        output_dir:            Directory for extracted images.
        min_area_pct:          Minimum contour area as fraction of image.
        max_area_pct:          Maximum contour area as fraction of image.
        min_pixels:            Absolute minimum pixel area.
        padding:               Padding around each extracted crop (px).
        blocksize:             Adaptive threshold block size (must be odd).
        C:                     Adaptive threshold constant.
        debug:                 Save intermediate images when True.
        merge_gap:             Max pixel gap for smart merging.
        enable_merging:        Enable smart box merging.
        border_pct:            Fraction of image width to suppress on each side.
        header_pct:            Fraction of image height to suppress at top.
        footer_pct:            Fraction of image height to suppress at bottom.
        dilation_kernel:       Square kernel size for blob dilation.
        min_density:           Minimum ink density inside bounding box.
        max_density:           Maximum ink density inside bounding box.
        text_height_multiplier: Candidate must be at least this many × text height.

    Returns:
        List of dicts with 'filename', 'area', 'bbox'.
    """
    img = cv2.imread(image_path)
    if img is None:
        raise ValueError(f"Could not load image: {image_path}")

    img_height, img_width = img.shape[:2]
    img_area = img_height * img_width

    print(f"\n{'='*70}")
    print(f"Processing: {os.path.basename(image_path)}")
    print(f"Image size: {img_width}x{img_height} pixels")
    print(f"{'='*70}")

    os.makedirs(output_dir, exist_ok=True)
    stem = Path(image_path).stem

    # 1. Contrast normalisation
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gray_norm = normalize_contrast(gray)

    # 2. Content mask — suppresses border, header, footer
    content_mask = create_content_mask(
        img_height, img_width, border_pct, header_pct, footer_pct
    )
    # Precompute zone boundaries for bounding-box edge checks later
    mask_x0 = int(img_width * border_pct)
    mask_x1 = img_width - mask_x0
    mask_y0 = int(img_height * header_pct)
    mask_y1 = img_height - int(img_height * footer_pct)

    # 3. Adaptive threshold
    thresh = cv2.adaptiveThreshold(
        gray_norm, 255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY_INV,
        blockSize=blocksize,
        C=C
    )
    thresh_masked = cv2.bitwise_and(thresh, content_mask)

    # 4. Estimate text height
    text_height = estimate_text_height(thresh_masked, content_mask)
    min_candidate_height = text_height * text_height_multiplier
    print(f"  Estimated text height: {text_height}px  "
          f"(min candidate height: {min_candidate_height:.0f}px)")

    # 5. Illustration zones from horizontal projection
    h_proj = get_horizontal_projection(thresh_masked, content_mask)
    illustration_zones = find_illustration_zones(h_proj, img_width, text_height)
    print(f"  Illustration zones: {len(illustration_zones)}")
    if debug:
        for i, (top, bottom) in enumerate(illustration_zones):
            print(f"    Zone {i+1}: rows {top}–{bottom} ({bottom - top}px)")

    # 6. Denoise then dilate into blobs
    kernel_small = np.ones((3, 3), np.uint8)
    thresh_clean = cv2.morphologyEx(thresh_masked, cv2.MORPH_OPEN, kernel_small)

    kernel_large = np.ones((dilation_kernel, dilation_kernel), np.uint8)
    thresh_blobs = cv2.dilate(thresh_clean, kernel_large, iterations=1)
    # Re-apply mask so dilation cannot push border/header/footer blobs inward
    thresh_blobs = cv2.bitwise_and(thresh_blobs, content_mask)

    if debug:
        cv2.imwrite(os.path.join(output_dir, f"{stem}_threshold.png"), thresh_clean)
        cv2.imwrite(os.path.join(output_dir, f"{stem}_blobs.png"), thresh_blobs)
        zone_vis = img.copy()
        for top, bottom in illustration_zones:
            cv2.rectangle(zone_vis, (0, top), (img_width, bottom), (255, 0, 0), 3)
        cv2.imwrite(os.path.join(output_dir, f"{stem}_zones.png"), zone_vis)
        print(f"  [DEBUG] Saved threshold, blobs, and zones images")

    # 7. Find and filter contours
    contours, _ = cv2.findContours(
        thresh_blobs, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
    )
    print(f"  Found {len(contours)} raw contours")

    min_area = max(img_area * min_area_pct, min_pixels)
    max_area = img_area * max_area_pct
    print(f"  Area filter: {min_area:,.0f}–{max_area:,.0f} px  "
          f"({min_area_pct*100:.1f}%–{max_area_pct*100:.1f}%)")

    candidates = []
    # Collect all evaluated blobs for debug visualisation (before final filters)
    debug_blobs = []  # list of (x, y, w, h, reject_reason_or_None)

    for contour in contours:
        area = cv2.contourArea(contour)
        if area < min_area or area > max_area:
            continue

        x, y, w, h = cv2.boundingRect(contour)

        # Reject blobs whose bounding box starts inside the border/header/footer
        # exclusion zones.  Checking bbox edges (not centroid) catches narrow
        # border-ornament strips that dilation has pushed into the content area.
        if x < mask_x0 or (x + w) > mask_x1 or y < mask_y0 or (y + h) > mask_y1:
            debug_blobs.append((x, y, w, h, "bbox in exclusion zone"))
            continue

        # Must be substantially taller than typical text
        if h < min_candidate_height:
            debug_blobs.append((x, y, w, h, f"height {h:.0f}<{min_candidate_height:.0f}"))
            continue

        # Reject extremely elongated regions (text lines, rules)
        aspect = w / h if h > 0 else 0
        if aspect > 8 or aspect < 0.1:
            debug_blobs.append((x, y, w, h, f"aspect {aspect:.2f}"))
            continue

        # Ink density check on the clean (non-dilated) threshold
        density = ink_density(thresh_clean, x, y, w, h)
        if density < min_density or density > max_density:
            debug_blobs.append((x, y, w, h, f"density {density:.2f}"))
            continue

        # Zone check — skip if zones were detected and this box isn't in one
        if not in_illustration_zone(y, h, illustration_zones):
            debug_blobs.append((x, y, w, h, "not in zone"))
            continue

        # Reject text-like blobs via horizontal regularity score
        regularity = horizontal_regularity(thresh_clean, x, y, w, h)
        if regularity > max_regularity:
            debug_blobs.append((x, y, w, h, f"regularity {regularity:.2f}"))
            continue

        debug_blobs.append((x, y, w, h, None))  # passed all filters
        candidates.append((x, y, w, h, area, contour, regularity))

    print(f"  Found {len(candidates)} candidate regions")

    if debug and candidates:
        print(f"\n  {'#':>3}  {'pos (x,y)':>14}  {'size (w×h)':>12}  "
              f"{'density':>8}  {'h/txt':>6}  {'regularity':>11}")
        print(f"  {'-'*3}  {'-'*14}  {'-'*12}  {'-'*8}  {'-'*6}  {'-'*11}")
        for idx, (x, y, w, h, area, _cnt, regularity) in enumerate(candidates):
            density = ink_density(thresh_clean, x, y, w, h)
            print(f"  {idx:>3}  ({x:>5},{y:>5})    {w:>5}×{h:<5}   "
                  f"{density:>7.3f}   {h/text_height:>5.1f}×   {regularity:>10.3f}")
        print()

    # Strip regularity from candidates tuple before passing downstream
    candidates = [(x, y, w, h, area, cnt) for x, y, w, h, area, cnt, _reg in candidates]

    print(f"  Found {len(candidates)} candidate regions")

    # 8. Smart merging
    if enable_merging and candidates:
        print(f"  Applying smart merging (max gap: {merge_gap}px)…")
        merged_boxes = smart_merge_boxes(candidates, max_gap=merge_gap)
        print(f"  Result: {len(merged_boxes)} final woodcuts")
    else:
        merged_boxes = candidates

    merged_boxes.sort(key=lambda b: (b[1], b[0]))

    # 9. Crop and save
    extracts = []
    for x, y, w, h, area, _ in merged_boxes:
        x_pad = max(0, x - padding)
        y_pad = max(0, y - padding)
        w_pad = min(img_width  - x_pad, w + 2 * padding)
        h_pad = min(img_height - y_pad, h + 2 * padding)
        extracts.append({
            'image': img[y_pad:y_pad + h_pad, x_pad:x_pad + w_pad],
            'area':  area,
            'bbox':  (x_pad, y_pad, w_pad, h_pad),
        })

    saved_files = []
    for idx, extract in enumerate(extracts):
        out_path = os.path.join(output_dir, f"{stem}_woodcut_{idx:02d}.png")
        cv2.imwrite(out_path, extract['image'])
        saved_files.append({
            'filename': os.path.basename(out_path),
            'area':     extract['area'],
            'bbox':     extract['bbox'],
        })
        x, y, w, h = extract['bbox']
        print(f"    {idx+1}. {os.path.basename(out_path)} — "
              f"{w}×{h}px  (area: {extract['area']:,.0f})")

    if debug:
        annotated = img.copy()

        # Blue = rejected blobs (with reason label), Green = saved extractions
        font = cv2.FONT_HERSHEY_SIMPLEX
        for x, y, w, h, reason in debug_blobs:
            if reason is not None:
                cv2.rectangle(annotated, (x, y), (x + w, y + h), (200, 100, 0), 1)
                cv2.putText(annotated, reason, (x, max(y - 4, 10)),
                            font, 0.45, (200, 100, 0), 1, cv2.LINE_AA)
        for extract in extracts:
            x, y, w, h = extract['bbox']
            cv2.rectangle(annotated, (x, y), (x + w, y + h), (0, 220, 0), 3)

        cv2.imwrite(os.path.join(output_dir, f"{stem}_annotated.png"), annotated)
        print(f"  [DEBUG] Saved annotated image  "
              f"(blue=rejected, green=saved)")

    print(f"\nExtracted {len(saved_files)} woodcuts to {output_dir}/")
    return saved_files


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description='Extract woodcut illustrations from historical book pages',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  Single page:
    %(prog)s page001.jpg

  Multiple pages:
    %(prog)s pages/*.jpg -o all_woodcuts

  Debug mode:
    %(prog)s page.jpg --debug --merge-gap 60

  Tune page template (larger header, tight border):
    %(prog)s page.jpg --header-pct 0.10 --border-pct 0.06

  Disable merging:
    %(prog)s page.jpg --no-merge
        """,
    )

    parser.add_argument('images', nargs='*', help='Input image file(s)')
    parser.add_argument('-d', '--dir', metavar='DIR',
                        help='Process all images in DIR (jpg/jpeg/png/tif/tiff)')
    parser.add_argument('-o', '--output', default='extracted',
                        help='Output directory (default: extracted)')

    # Area filters
    parser.add_argument('--min-area', type=float, default=0.005,
                        help='Min area as fraction of image (default: 0.005)')
    parser.add_argument('--max-area', type=float, default=0.35,
                        help='Max area as fraction of image (default: 0.35)')
    parser.add_argument('--min-pixels', type=int, default=2000,
                        help='Absolute minimum pixel area (default: 2000)')

    # Page-template zones
    parser.add_argument('--border-pct', type=float, default=0.05,
                        help='Fraction of width to suppress on each side (default: 0.05)')
    parser.add_argument('--header-pct', type=float, default=0.07,
                        help='Fraction of height to suppress at top (default: 0.07)')
    parser.add_argument('--footer-pct', type=float, default=0.05,
                        help='Fraction of height to suppress at bottom (default: 0.05)')

    # Thresholding
    parser.add_argument('--blocksize', type=int, default=51,
                        help='Adaptive threshold block size, must be odd (default: 51)')
    parser.add_argument('--C', type=int, default=15,
                        help='Adaptive threshold constant (default: 15)')

    # Dilation / density
    parser.add_argument('--dilation-kernel', type=int, default=20,
                        help='Dilation kernel size for blob merging (default: 20)')
    parser.add_argument('--min-density', type=float, default=0.05,
                        help='Minimum ink density inside bounding box (default: 0.05)')
    parser.add_argument('--max-density', type=float, default=0.90,
                        help='Maximum ink density inside bounding box (default: 0.90)')
    parser.add_argument('--max-regularity', type=float, default=0.25,
                        help='Max horizontal regularity score — higher = more text-like '
                             '(default: 0.25; raise to keep borderline regions)')
    parser.add_argument('--text-height-mult', type=float, default=3.0,
                        help='Min candidate height as multiple of text height (default: 3.0)')

    # Merging / output
    parser.add_argument('--merge-gap', type=int, default=80,
                        help='Max gap for merging split figures (default: 80)')
    parser.add_argument('--no-merge', action='store_true',
                        help='Disable smart box merging')
    parser.add_argument('--padding', type=int, default=15,
                        help='Padding around each crop in pixels (default: 15)')
    parser.add_argument('--debug', action='store_true',
                        help='Save intermediate processing images')

    args = parser.parse_args()

    # Build file list
    image_paths = list(args.images)
    if args.dir:
        if not os.path.isdir(args.dir):
            print(f"Error: {args.dir} is not a directory")
            return
        exts = {'.jpg', '.jpeg', '.png', '.tif', '.tiff'}
        dir_files = sorted(
            p for p in Path(args.dir).iterdir()
            if p.is_file() and p.suffix.lower() in exts
        )
        if not dir_files:
            print(f"No image files found in {args.dir}")
            return
        print(f"Found {len(dir_files)} image(s) in {args.dir}")
        image_paths.extend(str(p) for p in dir_files)

    if not image_paths:
        parser.error("Provide at least one image file or use --dir")

    # blocksize must be odd
    if args.blocksize % 2 == 0:
        args.blocksize += 1

    total = 0
    for image_path in image_paths:
        if not os.path.exists(image_path):
            print(f"Warning: {image_path} not found, skipping")
            continue
        try:
            results = extract_woodcuts(
                image_path,
                output_dir=args.output,
                min_area_pct=args.min_area,
                max_area_pct=args.max_area,
                min_pixels=args.min_pixels,
                padding=args.padding,
                blocksize=args.blocksize,
                C=args.C,
                debug=args.debug,
                merge_gap=args.merge_gap,
                enable_merging=not args.no_merge,
                border_pct=args.border_pct,
                header_pct=args.header_pct,
                footer_pct=args.footer_pct,
                dilation_kernel=args.dilation_kernel,
                min_density=args.min_density,
                max_density=args.max_density,
                text_height_multiplier=args.text_height_mult,
                max_regularity=args.max_regularity,
            )
            total += len(results)
        except Exception as e:
            print(f"Error processing {image_path}: {e}")
            if args.debug:
                import traceback
                traceback.print_exc()

    print(f"\n{'='*70}")
    print(f"COMPLETE: Extracted {total} woodcuts from {len(image_paths)} pages")
    print(f"{'='*70}")


if __name__ == '__main__':
    main()
