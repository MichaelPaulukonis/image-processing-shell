# B&W to B&Transparent Batch Converter - Development Plan

## Overview
Add a black-and-white to black-and-transparent batch converter feature to `tool.sh` that processes entire directories of images.

## Analysis of Current `tool.sh` Structure

### Existing Patterns
- Uses `zparseopts` for command-line argument parsing
- Follows a pattern of: `prep output → process files → save to destination`
- Has existing batch operations: `sliceGrid`, `resizeFolder`, `makeMontage`, `makevideos`
- Uses `ROOT` directory structure (`~/projects/images` by default)
- Supports configurable suffixes (default: `png`)
- Has verbose output option for debugging

### Current Actions
- `--video` / `-v`: Create videos from image sequences
- `--montage` / `-m`: Create image montages
- `--slice` / `-w`: Slice images into grids
- `--resize` / `-rs`: Resize images in folders

## Feature Requirements

### Primary Goal
Convert all black-and-white images in a directory to black-and-transparent images, making non-black pixels transparent while preserving black pixels.

### Functional Requirements
1. **Batch Processing**: Process all images in a target directory
2. **Format Support**: Handle PNG files (primary), potentially JPG input → PNG output
3. **Transparency Methods**: Support multiple conversion approaches
4. **Output Management**: Save to destination directory with appropriate naming
5. **Error Handling**: Graceful handling of invalid files or processing errors
6. **Progress Feedback**: Show processing status (especially with verbose mode)

## Design Decisions & Questions

### 1. Command-Line Interface Options

**Option A: New Flag Approach** (Recommended)
```bash
./tool.sh --target input_folder --destination output_folder --name batch_name --transparent
# or
./tool.sh -t input_folder -d output_folder -n batch_name --btrans
```

**Option B: Method Parameter Approach**
```bash
./tool.sh --target input_folder --destination output_folder --name batch_name --method transparent
```

**Question**: Which CLI approach do you prefer? Option A follows the existing pattern better.

### 2. Transparency Conversion Methods

**Option A: Simple White-to-Transparent** (Recommended for most cases)
```bash
convert input.png -transparent white output.png
```

**Option B: Fuzz Tolerance Method** (Better for varied inputs)
```bash
convert input.png -fuzz 10% -transparent white output.png
```

**Option C: Preserve-Black-Only Method** (Most precise)
```bash
convert input.png -alpha set -background none -fill none +opaque black output.png
```

**Questions**: 
- Should we support all three methods with a parameter?
- Should we default to one method or detect the best method per image?
- Should fuzz tolerance be configurable?

### 3. File Handling Strategy

**Input Format Support**:
- PNG files (native transparency support)
- JPG/JPEG files (convert to PNG for transparency)
- Other formats?

**Output Naming**:
- `original_name_transparent.png`
- `original_name.transparent.png`
- `prefix_###.png` (numbered sequence)
- Maintain original names in destination folder?

**Question**: What naming convention would work best for your workflow?

### 4. Error Handling Approach

**File Validation**:
- Check if files are valid images
- Verify they are actually black-and-white
- Handle corrupted files gracefully

**Processing Errors**:
- Continue processing on individual file failures
- Report failed files at end
- Option to stop on first error?

## Implementation Plan

### Phase 1: Core Function Development
1. **Create `makeTransparent()` function**
   - Parameter validation
   - File discovery and filtering
   - Single image conversion logic
   - Error handling per file

2. **Add CLI argument parsing**
   - New flag for transparent action
   - Optional method parameter
   - Optional fuzz tolerance parameter

3. **Integrate with main script flow**
   - Add to the main if/elif chain
   - Follow existing patterns for output preparation

### Phase 2: Testing & Validation
1. **Unit Testing** (manual)
   - Test with various B&W image types
   - Test with non-B&W images (error cases)
   - Test with different file formats
   - Test with empty directories
   - Test with large directories

2. **Integration Testing**
   - Test with existing tool.sh flags
   - Verify no conflicts with other operations
   - Test verbose output
   - Test with different ROOT directories

3. **Edge Case Testing**
   - Files with permissions issues
   - Very large images
   - Images with alpha channels already
   - Non-image files in directory

### Phase 3: Enhancement & Optimization
1. **Performance Optimization**
   - Parallel processing for large batches
   - Progress indicators
   - Memory usage optimization

2. **Advanced Features**
   - Automatic B&W detection
   - Quality/method auto-selection
   - Backup option for originals

## Testing Strategy

### Test Data Requirements
1. **Sample B&W Images**:
   - Pure black/white PNG
   - Grayscale PNG
   - B&W JPEG
   - B&W with anti-aliasing
   - Large images (>2MB)
   - Small images (<100KB)

2. **Edge Case Files**:
   - Already transparent images
   - Color images (should skip or convert)
   - Corrupted image files
   - Text files with image extensions

### Test Scenarios

#### Basic Functionality Tests
```bash
# Test 1: Basic conversion
./tool.sh -t test_bw_images -d test_output -n transparent_test --transparent

# Test 2: With verbose output
./tool.sh -t test_bw_images -d test_output -n transparent_test --transparent --verbose

# Test 3: Different suffix
./tool.sh -t test_bw_images -d test_output -n transparent_test --transparent -s jpg
```

#### Error Handling Tests
```bash
# Test 4: Empty directory
./tool.sh -t empty_folder -d test_output -n empty_test --transparent

# Test 5: Non-existent source
./tool.sh -t nonexistent -d test_output -n error_test --transparent

# Test 6: Permission denied destination
./tool.sh -t test_bw_images -d /root/forbidden -n perm_test --transparent
```

#### Integration Tests
```bash
# Test 7: Ensure no conflict with existing functions
./tool.sh -t test_images -d test_output -n video_test --video
./tool.sh -t test_images -d test_output -n montage_test --montage
```

## Implementation Details

### Function Signature (Draft)
```bash
makeTransparent() {
    local TARGET_FOLDER="$1"
    local DESTINATION_FOLDER="$2"
    local OUTPUT_NAME="$3"
    local METHOD="${4:-white}"      # white, fuzz, preserve-black
    local FUZZ_TOLERANCE="${5:-10}" # percentage for fuzz method
}
```

### CLI Arguments to Add
```bash
# In zparseopts section:
bt=transparent -transparent=transparent \
btm:=trans_method -trans-method:=trans_method \
btf:=trans_fuzz -trans-fuzz:=trans_fuzz \
```

### Error Handling Strategy
- Use `set -e` for the function to catch ImageMagick errors
- Implement file-by-file error logging
- Provide summary of successful/failed conversions
- Continue processing after individual file failures

## Final Design Decisions (User Selected)

1. **CLI Design**: ✅ Use `--transparent` flag
2. **Conversion Method**: ✅ Preserve-black-only method (`+opaque black`)
3. **File Naming**: ✅ Add suffix `_transparent.png`
4. **Input Formats**: ✅ Only process PNG files
5. **Error Handling**: ✅ Continue processing on file errors, stop only for input/output location errors

6. **Testing Priority**: Which test scenarios are most important for your use case?

## Timeline Estimate
- **Phase 1**: 2-3 hours (core implementation)
- **Phase 2**: 2-4 hours (testing and validation)  
- **Phase 3**: 1-2 hours (enhancements)
- **Total**: 5-9 hours for complete implementation and testing

## Implementation Status ✅ COMPLETED

The B&W to B&Transparent batch converter has been successfully implemented and tested in `tool.sh`.

### Features Implemented
- ✅ `--transparent` flag for CLI
- ✅ Preserve-black-only conversion method using `+opaque black`
- ✅ Output files named with `_transparent.png` suffix
- ✅ PNG-only processing
- ✅ Continue processing on individual file errors
- ✅ Stop on input/output location errors
- ✅ Verbose output support
- ✅ Progress reporting (processed count, error count)
- ✅ Empty directory handling
- ✅ Integration with existing tool.sh patterns

### Usage
```bash
# Basic usage
./tool.sh --target input_folder --destination output_folder --name batch_name --transparent

# With verbose output
./tool.sh -t input_folder -d output_folder -n batch_name --transparent --verbose
```

### Testing Results
- ✅ Successfully processes B&W PNG files
- ✅ Creates output files with `_transparent.png` suffix
- ✅ Handles empty directories gracefully
- ✅ Proper error handling for non-existent directories
- ✅ Continues processing after individual file errors
- ✅ Maintains existing tool.sh functionality
- ✅ Help documentation includes new option

## Success Criteria
- [ ] Successfully converts directories of B&W images to B&Transparent
- [ ] Maintains existing tool.sh functionality
- [ ] Provides clear error messages and progress feedback
- [ ] Handles edge cases gracefully
- [ ] Follows existing code patterns and conventions
- [ ] Includes comprehensive testing coverage