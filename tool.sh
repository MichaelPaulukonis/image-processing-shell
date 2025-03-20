#!/usr/bin/env zsh

DIR="$(pwd)"
# --- Configuration ---
# Default values for script parameters
ROOT="${HOME}/projects/images" # Default root directory
SUFFIX="png"                   # Default image suffix
PREFIX=""                      # Default prefix for output files
GRIDSIZE="10"                  # Default grid size for montage
FPS="10"                       # Default frames per second for video
RESOLUTION="720"               # Default resolution for video
VERBOSE=false                  # Default to not verbose

# --- Functions ---

# display usage information
usage() {
    cat <<_EOF_

Image processing actions I use often

Options:
  -t | --target <folder>     Target folder containing images. (Required)
  -d | --destination <folder> Destination folder for output. (Required)
  -n | --name <name>         Base name for output files. (Required)
  -s | --suffix <suffix>     Image suffix (default: $SUFFIX).
  -p | --prefix <prefix>     Prefix for output files.
  -g | --gridSize <size>     Grid size for montage (default: $GRIDSIZE).
  -f | --fps <fps>           Frames per second for video (default: $FPS).
  -r | --resolution <res>    Resolution for video (default: $RESOLUTION).
  -v | --video               Create a video.
  -m | --montage             Create a montage.
  -w | --slice               Slice images into a grid.
  -rs | --resize             Resize images in a folder.
  --verbose                  Enable verbose output.
  -h | --help                Display this help message.

_EOF_
}

# prepare the output directory
prepOut() {
    local DESTINATION_FOLDER="$1"
    mkdir -p "$ROOT/$DESTINATION_FOLDER"
}

# slice images into a grid
sliceGrid() {
    local TARGET_FOLDER="$1"
    local DESTINATION_FOLDER="$2"
    local OUTPUT_PREFIX="$3"
    prepOut $DESTINATION_FOLDER

    convert -crop 256x256 "$ROOT/$TARGET_FOLDER/*.$SUFFIX" "$ROOT/$DESTINATION_FOLDER/$OUTPUT_PREFIX.%03d.$SUFFIX"
}

# TODO: should be able to pad smaller images
# ffmpeg -r 10 -f image2 -s 768x768 -pattern_type glob -i "/Users/michaelpaulukonis/projects/images/robot_guy_sorted/*.png" -vf pad="ceil(max(iw\,ih)/2)*2:ow:(ow-iw)/2:(oh-ih)/2" -vcodec libx264 -crf 17 -pix_fmt yuv420p /Users/michaelpaulukonis/projects/images/robot_guy_sorted/robot_guy_sorted.10.768.mp4

# create a video
makevideo() {
    local FPS="$1"
    local RESOLUTION="$2"
    local TARGET_FOLDER="$3"
    local DESTINATION_FOLDER="$4"
    local OUTPUT_NAME="$5"

    prepOut $DESTINATION_FOLDER

    local FFMPEG_OPTIONS="-vcodec libx264 -crf 17 -pix_fmt yuv420p"
    local PADDING_FILTER="scale=$RESOLUTION:$RESOLUTION:force_original_aspect_ratio=decrease,pad=$RESOLUTION:$RESOLUTION:(ow-iw)/2:(oh-ih)/2"

    local COMMAND="ffmpeg -r $FPS -f image2 -s ${RESOLUTION}x${RESOLUTION} -pattern_type glob -i \"$ROOT/$TARGET_FOLDER/*.png\" -vf \"$PADDING_FILTER\" $FFMPEG_OPTIONS \"$ROOT/$DESTINATION_FOLDER/$OUTPUT_NAME.$FPS.$RESOLUTION.mp4\""

    if [[ "$VERBOSE" == true ]]; then
        echo "$COMMAND"
    fi

    # eval "$COMMAND"
}

# create multiple videos with different FPS values
makevideos() {

    local TARGET_FOLDER="$1"
    local DESTINATION_FOLDER="$2"
    local OUTPUT_NAME="$3"
    local RESOLUTION="$4"

    local FPS_VALUES=(5 10 20 30)

    if [ -n "$FPS" ]; then
        makevideo "$FPS" "$RESOLUTION" "$TARGET_FOLDER" "$DESTINATION_FOLDER" "$OUTPUT_NAME"
        return
    fi

    for i in "${FPS_VALUES[@]}"; do
        makevideo "$i" "$RESOLUTION" "$TARGET_FOLDER" "$DESTINATION_FOLDER" "$OUTPUT_NAME"
    done
}

# create a montage
makeMontage() {
    local TARGET_FOLDER="$1"
    local DESTINATION_FOLDER="$2"
    local OUTPUT_NAME="$3"

    prepOut $DESTINATION_FOLDER

    montage -geometry 128x128+0+0 -tile "$GRIDSIZE"x"$GRIDSIZE" -background black "$ROOT/$TARGET_FOLDER/*.$SUFFIX" "$ROOT/$DESTINATION_FOLDER/$OUTPUT_NAME.montage.$GRIDSIZE.%02d.$SUFFIX"
}

# resize images in a folder
resizeFolder() {
    local TARGET_FOLDER="$1"
    local DESTINATION_FOLDER="$2"
    local IMAGE_SUFFIX="$3"
    local NEW_RESOLUTION="$4"

    prepOut "$DESTINATION_FOLDER"

    # `smartresize` was taken from [this article](https://www.smashingmagazine.com/2015/06/efficient-image-resizing-with-imagemagick/)
    # for f in /Users/michaelpaulukonis/projects/images/35.marilyns/*.png;  do smartresize ${f} 300 /Users/michaelpaulukonis/projects/images/marilyns.resized/; done;
    # smartresize is defined in /Users/michaelpaulukonis/.zshenv

    for f in "$ROOT/$TARGET_FOLDER/*.$IMAGE_SUFFIX"; do
        smartresize "$f" "$NEW_RESOLUTION" "$ROOT/$DESTINATION_FOLDER"
    done

    for f in "$ROOT/$DESTINATION_FOLDER/*.$IMAGE_SUFFIX"; do
        magick "$f" \( +clone -rotate 90 +clone -mosaic +level-colors white \) +swap -gravity center -composite "$f"
    done
}

debug() {
    echo "--- debug Output ---"
    echo "TARGET_FOLDER: $TARGET_FOLDER"
    echo "DESTINATION_FOLDER: $DESTINATION_FOLDER"
    echo "OUTPUT_NAME: $OUTPUT_NAME"
    echo "SUFFIX: $SUFFIX"
    echo "PREFIX: $PREFIX"
    echo "GRIDSIZE: $GRIDSIZE"
    echo "FPS: $FPS"
    echo "RESOLUTION: $RESOLUTION"
    echo "VIDEO: $VIDEO"
    echo "MONTAGE: $MONTAGE"
    echo "SLICE: $SLICE"
    echo "RESIZE: $RESIZE"
    echo "VERBOSE: $VERBOSE"
    echo "VIDEO: $VIDEO"
    echo "HELP: $HELP"
    echo "--- End debug Output ---"
}


# --- Main Script ---

ACTION=""
TARGET_FOLDER=""
DESTINATION_FOLDER=""
OUTPUT_NAME=""
OUTPUT_PREFIX=""
## TODO: add a 'dry-run' option
## TODO: sanity-check

local -a destination_folder
local -a fps
local -a gridsize
local -a help
local -a montage
local -a output_name
local -a prefix
local -a resize
local -a resolution
local -a slice
local -a suffix
local -a target_folder
local -a verbose
local -a video

# Parse command-line arguments
# zparseopts -D -E \
#     a=flag_a \           # -a can be used without a value
#     b:=value_b \         # -b MUST have a value (required)
#     c::=optional_c       # -c can have an optional value

# Initialize zparseopts
zparseopts -D -E \
    d:=destination_folder -destination:=destination_folder \
    f:=fps -fps:=fps \
    g:=gridsize -gridsize:=gridsize \
    h=help -help=help \
    m=montage -montage=montage \
    n:=output_name -name:=output_name \
    p:=prefix -prefix:=prefix \
    r:=resolution -resolution:=resolution \
    rs=resize -resize:=resize \
    s:=suffix -suffix:=suffix \
    t:=target_folder -target:=target_folder \
    {v,-video}=video \
    {verbose,-verbose}=verbose \
    w=slice -slice=slice \

if [[ -n "$verbose" ]]; then
VERBOSE=true
    echo "\nVerbose output enabled\n"
    # --- Debugging zparseopts Output ---
    echo "\n--- zparseopts output ---"
    echo "destination_folder: $destination_folder"
    echo "fps: $fps"
    echo "gridsize: $gridsize"
    echo "help: $help"
    echo "montage: $montage"
    echo "output_name: $output_name"
    echo "prefix: $prefix"
    echo "resize: $resize"
    echo "resolution: $resolution"
    echo "slice: $slice"
    echo "suffix: $suffix"
    echo "target_folder: $target_folder"
    echo "verbose: $verbose"
    echo "video: $video"
    echo "--- end zparseopts output ---"
fi

# Check for help flag first
if [[ -n "$help" ]]; then
    echo "\nhelp selected"
    usage
    exit 0
fi

# --- Assign Params ---
TARGET_FOLDER="${target_folder[2]}"
DESTINATION_FOLDER="${destination_folder[2]}"
FPS="${fps[2]}"
GRIDSIZE="${gridsize[2]}"
HELP="${help}"
MONTAGE="${montage}"
OUTPUT_NAME="${output_name[2]}"
PREFIX="${prefix[2]}"
RESIZE="${resize}"
SLICE="${slice}"
SUFFIX="${suffix[2]}"
VIDEO="${video}"


if [[ ! -z "$resolution" ]] || [[ ${#resolution[@]} -gt 0 ]]; then
    RESOLUTION="${resolution[2]:-$RESOLUTION}"
fi

# # Check for required arguments
if [[ -z "$TARGET_FOLDER" ]] || [[ -z "$DESTINATION_FOLDER" ]] || [[ -z "$OUTPUT_NAME" ]]; then
    echo "Error: TARGET, DESTINATION and NAME are required arguments." >&2
    usage
    exit 1
fi


if [[ -n "$VIDEO" ]]; then
    makevideos "$TARGET_FOLDER" "$DESTINATION_FOLDER" "$OUTPUT_NAME" "$RESOLUTION"

elif [[ -n "$MONTAGE" ]]; then
    makeMontage "$TARGET_FOLDER" "$DESTINATION_FOLDER" "$OUTPUT_NAME"

elif [[ -n "$SLICE" ]]; then
    sliceGrid "$TARGET_FOLDER" "$DESTINATION_FOLDER" "$PREFIX"

elif [[ -n "$RESIZE" ]]; then
    resizeFolder "$TARGET_FOLDER" "$DESTINATION_FOLDER" "$SUFFIX" "$RESOLUTION"
    ;
else
    echo "No valid action specified"
    usage
    exit 1
fi

echo "Completed processing for target: $ROOT/$TARGET_FOLDER"
