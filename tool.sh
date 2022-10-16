#!/bin/zsh

DIR="`pwd`"
source $DIR/tool.config

usage()
{
cat << _EOF_
Utilities for animated output
Moves images into associated folders and build gifs or mp4 files
NOTE: gif-construction takes a looooong time

options

  -a | --all   

  -s | --suffix

  -p | --prefix

  -d | --destination

  -t | --target

  -h | --help   print this file

_EOF_
}

prepOut() {
    DEST=$1
    mkdir -p $ROOT/$DEST
}

sliceGrid() {
    TARG=$1
    DEST=$2
    PREFIX=$3
    mkdir -p $ROOT/$DEST
    convert -crop 256x256 $ROOT/$TARG/*.$SUFFIX $ROOT/$DEST/$PREFIX.%03d.$SUFFIX
}

sliceWombo() {
    TARG=$1
    DEST=$2
    PREFIX=$3
    # debug
    mkdir -p $ROOT/$DEST
    # this is not quite right, but less than 4 is wrong - there are 2s and 4s, think some val is off w/ location?
    # there is a 1px black line between tiles, and 2px modified on either side.
    # so....... not divisible by 2
    convert -repage 960x960-60-220 -crop 320x320 +repage $ROOT/$TARG/*.$SUFFIX $ROOT/$DEST/$PREFIX.%03d.$SUFFIX && mogrify $ROOT/$DEST/$PREFIX.* -shave 4x4 $ROOT/$DEST/$PREFIX.*
}

# TODO: should be able to pad smaller images
# ffmpeg -r 10 -f image2 -s 768x768 -pattern_type glob -i "/Users/michaelpaulukonis/projects/images/robot_guy_sorted/*.png" -vf pad="ceil(max(iw\,ih)/2)*2:ow:(ow-iw)/2:(oh-ih)/2" -vcodec libx264 -crf 17 -pix_fmt yuv420p /Users/michaelpaulukonis/projects/images/robot_guy_sorted/robot_guy_sorted.10.768.mp4

makeVideo() {
    FPS=$1
    RES=$2
    # ffmpeg -r $FPS -f image2 -s 1024x1024 -pattern_type glob -i "$ROOT/$TARG/*.png" -vcodec libx264 -crf 17 -filter:v scale=$RES:-1 -pix_fmt yuv420p $ROOT/$DEST/$NAME.$FPS.$RES.mp4
    # ffmpeg -r $FPS -f image2 -s 768x768 -pattern_type glob -i "$ROOT/$TARG/*.png" -vcodec libx264 -crf 17 -vf pad="ceil(max(iw\,ih)/2)*2:ow:(ow-iw)/2:(oh-ih)/2" -pix_fmt yuv420p $ROOT/$DEST/$NAME.$FPS.$RES.mp4

    echo ffmpeg -r $FPS -f image2 -s $RES"x"$RES -pattern_type glob -i "$ROOT/$TARG/*.png" -vf "scale=$RES:$RES:force_original_aspect_ratio=decrease,pad=$RES:$RES:(ow-iw)/2:(oh-ih)/2" -vcodec libx264 -crf 17 -pix_fmt yuv420p $ROOT/$DEST/$NAME.$FPS.$RES.mp4

    ffmpeg -r $FPS -f image2 -s $RES"x"$RES -pattern_type glob -i "$ROOT/$TARG/*.png" -vf "scale=$RES:$RES:force_original_aspect_ratio=decrease,pad=$RES:$RES:(ow-iw)/2:(oh-ih)/2" -vcodec libx264 -crf 17 -pix_fmt yuv420p $ROOT/$DEST/$NAME.$FPS.$RES.mp4

}

makeVideos() {
    TARG=$1
    DEST=$2
    NAME=$3
    prepOut $DEST

    RES=$RESOLUTION

    if [ -n "$FPS" ] ; then
        makeVideo $FPS $RES
        exit
    fi
    
    f=(5 10 20 30)

    for i in $f; do
        makeVideo $i $RES
    done
}


makeMontage() {
    TARG=$1
    DEST=$2
    NAME=$3
    prepOut $DEST

    # montage -geometry 64x64+0+0 -tile "$GRIDSIZEx$GRIDSIZE" -background black "$ROOT/$TARG/*.png" $ROOT/$DEST/$NAME.montage.$GRIDSIZE.%02d.$SUFFIX
    montage -geometry 128x128+0+0 -tile "$GRIDSIZE"x"$GRIDSIZE" -background black "$ROOT/$TARG/*.png" $ROOT/$DEST/$NAME.montage.$GRIDSIZE.%02d.$SUFFIX
    # montage -geometry 64x97+0+0 -tile "$GRIDSIZE" -background black "$ROOT/$TARG/*.png" $ROOT/$DEST/$NAME.montage.$GRIDSIZE.%02d.$SUFFIX

}

debug() {
    echo TARG: $TARG
    echo DEST: $DEST
    echo NAME: $NAME
    echo ROOT: $ROOT
    echo PREFIX: $PREFIX
    echo SUFFIX: $SUFFIX
}

## MAIN


while [ "$1" != "" ]; do
    case $1 in
        -s | --suffix )
            shift
            SUFFIX=$1
        ;;
        -p | --prefix )
            shift
            PREFIX=$1
        ;;
        -d | --destination )
            shift
            DESTINATION=$1
        ;;
        -t | --target )
            shift
            TARGET=$1
        ;;
        -n | --name )
            shift
            NAME=$1
        ;;
        -g | --gridSize )
            shift
            GRIDSIZE=$1
        ;;
        -f | --fps )
            shift
            FPS=$1
        ;;
        -r | --resolution )
            shift
            RESOLUTION=$1
        ;;
        -v | --video )
            makeVideos $TARGET $DESTINATION $NAME
            exit
        ;;
        -m | --montage )
            makeMontage $TARGET $DESTINATION $NAME
            exit
        ;;;
        -w | --wombo )
            sliceWombo $TARGET $DESTINATION $PREFIX
            exit
        ;;;
        -h | --help )
            usage
            exit
        ;;
        * )
            usage
            exit 1
    esac
    shift
done

echo $TARGET

# default action

# sliceGrid $TARGET $DESTINATION $PREFIX

usage
