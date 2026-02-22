# tool.sh — Batch Image Processing CLI

> Fast local image transforms for slicing, montage generation, video rendering, and batch resize workflows.

![Status](https://img.shields.io/badge/status-experimental-orange)
![Shell](https://img.shields.io/badge/shell-zsh-1f425f)
![Dependencies](https://img.shields.io/badge/deps-ffmpeg%20%7C%20ImageMagick-blue)
![Platform](https://img.shields.io/badge/platform-macOS%20%7C%20Linux-lightgrey)

`tool.sh` is a personal-but-reusable command-line script in this repository for common image-processing batch tasks.

- Create square-padded MP4 videos from image sequences
- Generate tiled montage sheets
- Slice images into uniform chunks
- Resize a full folder using a custom smart-resize helper

If you need the web UI workflow, see [renamer-browser](../../renamer-browser/README.md).

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
  - [Quick Start](#quick-start)
- [Usage](#usage)
  - [Command Syntax](#command-syntax)
  - [Actions](#actions)
  - [Examples](#examples)
  - [Advanced Scenarios](#advanced-scenarios)
- [Configuration](#configuration)
- [Development](#development)
- [Project Structure](#project-structure)
- [Troubleshooting](#troubleshooting)
- [FAQ](#faq)
- [Roadmap](#roadmap)
- [Contributing](#contributing)
- [License](#license)
- [Changelog](#changelog)
- [Acknowledgments](#acknowledgments)
- [Related Resources](#related-resources)

## Overview

This script targets local, file-based image processing when you want repeatable command-line operations instead of GUI workflows.

**Project information**

- **Name:** Various image-processing projects (`tool.sh` module)
- **Type:** CLI tool (shell script)
- **Main technology:** `zsh` + `ffmpeg` + ImageMagick (`convert`, `montage`, `magick`)
- **Target audience:** Developers / technical creatives doing batch image pipelines
- **Status:** Experimental and actively evolved

## Features

- **Video rendering:** Converts image sequences to MP4 (`libx264`) with center padding to square output.
- **Montage sheets:** Generates tiled contact sheets with configurable grid size.
- **Grid slicing:** Crops source images into fixed-size chunks.
- **Folder resize pipeline:** Applies `smartresize` and post-processes each file.
- **Verbose mode:** Prints generated commands for easier debugging.

### What makes it useful

- Minimal dependencies beyond common media CLI tools
- Fast to run locally on directories of images
- Easy to script in larger shell workflows

## Getting Started

### Prerequisites

- macOS or Linux
- `zsh`
- `ffmpeg`
- ImageMagick (`convert`, `montage`, `magick`)
- Optional helper: `smartresize` function/command (used by `--resize` action)

Install common dependencies on macOS:

```bash
brew install ffmpeg imagemagick
```

### Installation

From repository root:

```bash
chmod +x tool.sh
```

Optional: add a shell alias in your shell config:

```bash
alias imgtool="$PWD/tool.sh"
```

### Quick Start

Create a montage from PNG images:

```bash
./tool.sh -t input_folder -d output_folder -n sample -m
```

Create a square MP4 video at 720px:

```bash
./tool.sh -t input_folder -d output_folder -n sample -v -f 10 -r 720
```

## Usage

### Command Syntax

```bash
./tool.sh -t <target> -d <destination> -n <name> [action] [options]
```

Required arguments:

- `-t | --target <folder>` source image folder (relative to root path)
- `-d | --destination <folder>` destination folder (relative to root path)
- `-n | --name <name>` output base name

Action flags (choose one):

- `-v | --video` create MP4 video(s)
- `-m | --montage` create montage sheet(s)
- `-w | --slice` slice images into grid chunks
- `-rs | --resize` resize image folder

Common options:

- `-s | --suffix <suffix>` image extension (default `png`)
- `-p | --prefix <prefix>` output prefix (primarily for slicing)
- `-g | --gridSize <size>` montage grid size (default `10`)
- `-f | --fps <fps>` video FPS (default `10`)
- `-r | --resolution <res>` output square resolution (default `720`)
- `--verbose` print detailed command info
- `-h | --help` show help

### Actions

#### 1) Video (`--video`)

Builds MP4 from image files and pads to square dimensions:

```bash
./tool.sh -t robot_frames -d exports -n robot -v -f 20 -r 1024 --verbose
```

Output pattern:

```text
<root>/<destination>/<name>.<fps>.<resolution>.mp4
```

#### 2) Montage (`--montage`)

Creates tiled contact sheet(s):

```bash
./tool.sh -t robot_frames -d exports -n robot -m -g 12 -s png
```

#### 3) Slice (`--slice`)

Crops images into `256x256` chunks:

```bash
./tool.sh -t originals -d slices -n sliceset -w -p tile
```

#### 4) Resize (`--resize`)

Runs smart-resize and post-processing steps:

```bash
./tool.sh -t originals -d resized -n resized_batch -rs -s png -r 300
```

### Examples

Batch video creation with defaults:

```bash
./tool.sh -t robot_guy_sorted -d robot_guy_videos -n robot_guy -v
```

Custom montage + suffix:

```bash
./tool.sh -t scans_jpg -d contact_sheets -n scans -m -g 8 -s jpg
```

### Advanced Scenarios

- **Integrate in scripts:** call `tool.sh` from a `Makefile` or shell loop.
- **Preflight check:** use `--verbose` first to inspect generated commands.
- **Multi-output runs:** invoke once per action for deterministic artifacts.

## Configuration

Current behavior is primarily configured in-script (top of `tool.sh`).

Related config file:

- [tool.config](../../tool.config) currently defines values like `ROOT`, `SUFFIX`, `GRIDSIZE`, and `RESOLUTION`, but `tool.sh` does not automatically source this file.

Important runtime defaults in script:

- `ROOT="${HOME}/projects/images"`
- `SUFFIX="png"`
- `GRIDSIZE="10"`
- `FPS="10"`
- `RESOLUTION="720"`

## Development

### Local setup

```bash
git clone <repo-url>
cd image-processing
chmod +x tool.sh
```

### Validate shell script quality

```bash
brew install shellcheck
shellcheck tool.sh
```

### Suggested workflow

1. Update `tool.sh`
2. Run with `--verbose` on small sample input
3. Validate output files in destination folder
4. Commit focused changes

### Debugging tips

- Add `--verbose` to inspect generated commands.
- Use `-h` to verify expected flags.
- Ensure input file suffix matches `-s`.

## Project Structure

```text
image-processing/
├── tool.sh                # CLI script for batch image processing
├── tool.config            # companion config values (not auto-sourced)
├── docs/
│   └── notes.md           # command-line usage notes
└── renamer-browser/       # separate web app for interactive image renaming
```

### How components work together

- `tool.sh` performs batch operations directly against filesystem folders.
- `tool.config` provides reference defaults and can be manually aligned with script defaults.
- `docs/notes.md` captures additional command examples and experiments.

## Troubleshooting

### Common problems

**`command not found: ffmpeg` / ImageMagick tools**

- Install dependencies and ensure they are on `PATH`.

**`smartresize: command not found` during `--resize`**

- Define `smartresize` in your shell environment or replace that call with your preferred resize command.

**`No valid action specified`**

- Include one of: `-v`, `-m`, `-w`, `-rs`.

**No output files created**

- Verify source folder exists under the configured `ROOT` path.
- Confirm extension with `-s` (e.g., `png`, `jpg`).

### Setup caveat

Usage text shows `--long-options`, but parser behavior is currently tied to `zparseopts` configuration in `tool.sh`. If a long option does not parse as expected, use the short flag equivalent.

## FAQ

**Can I process non-square videos?**

Current video mode pads output to square dimensions by design.

**Can I run multiple actions in one command?**

No. Run one action flag per invocation for predictable output.

**Does `tool.sh` read `tool.config` automatically?**

Not currently.

## Roadmap

- Add dry-run mode
- Add stronger argument validation / sanity checks
- Optionally source config from `tool.config`
- Improve long-option consistency

## Contributing

Contributions are welcome for script hardening and portability.

1. Open an issue describing the workflow/problem.
2. Create a focused branch.
3. Add or update usage examples in docs.
4. Validate script with real sample data.
5. Submit a pull request with before/after behavior.

## License

No project-level license file is currently defined in this repository.

## Changelog

This script currently follows repository history in Git commits.

## Acknowledgments

- `ffmpeg` for robust media encoding
- ImageMagick for image transforms and compositing

## Related Resources

- [ffmpeg Documentation](https://ffmpeg.org/documentation.html)
- [ImageMagick Documentation](https://imagemagick.org/script/)
- [Top-level repository README](../../README.md)
- [Renamer Browser README](../../renamer-browser/README.md)