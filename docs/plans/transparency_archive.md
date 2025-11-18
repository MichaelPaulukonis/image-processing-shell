# Transparency Conversion Archive

Date: 2025-11-17
Branch: `transparency` (archive branch)

Summary:
This file documents the attempts to implement a black-and-transparent conversion for B/W PNGs in `tool.sh`.

What we tried:
- Basic `-transparent white` and `-fuzz` (10-25%) — worked in some cases but produced white haloing and failed to merge thin anti-aliased edges to black.
- `+opaque black` variations and `-threshold` methods combined with `-fuzz` — mixed results; some images became entirely or partially transparent.
- `-level 0%,80% -fuzz 10% -transparent white` — attempted to darken anti-aliased edge pixels before transparency; reduced some halos but not all.
- `-threshold 50% -fuzz 5% -transparent white` — forced grayscale pixels to black or white prior to making white transparent; this removed some gray anti-aliasing but caused loss of subtle detail in some images.

Observations:
- Comic/line-art images with anti-aliased strokes need different handling: pure thresholding loses thin details, whereas fuzz-based transparency leaves partially transparent edges.
- Anti-aliased pixels often require more targeted morphological operations before making white transparent: e.g., using contrast/level adjustments, morphological erosion/dilation, or `-alpha` channel manipulation.

Next steps (future follow-up):
- Consider adding a multi-step approach for different image types (line art vs. halftones):
  - Convert to grayscale, then use `-sigmoidal-contrast`, or `-contrast-stretch` to preserve line detail while removing grays.
  - Try `-morphology` operations like `Erode` then `Dilate` to consolidate edges before transparency.
  - Use `-alpha set -channel A -threshold` or `-compose CopyOpacity` with a binary alpha mask to create better crisp edges and avoid gray halos.
- Provide a CLI switch to select the method (e.g., `--method threshold | level | alpha-mask`) for user preference.

Commit details:
- Updated `tool.sh` to attempt a threshold + low-fuzz transparent approach and included verbose feedback.
- Added this archive file describing the methods tried and suggested next steps.

If you'd like, I can implement a `--method` flag to allow selecting between multiple conversion strategies and add automated tests for each strategy (sample images + assert resulting black pixels remain black and whites become fully transparent).
