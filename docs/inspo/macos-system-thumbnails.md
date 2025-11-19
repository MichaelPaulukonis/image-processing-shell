# macOS System Thumbnail Integration

**Status:** Future Enhancement / Day 2 Feature  
**Date:** November 19, 2025

## Overview

macOS automatically generates thumbnails for images viewed in Finder. These could potentially be leveraged to speed up initial thumbnail loading in the Image Tagger & Renamer application.

## Current Approach (MVP)

The PRD specifies using **Pillow (PIL)** to generate custom thumbnails:
- Size: 150x150px
- Cache location: `~/.image-tagger-renamer/cache/thumbnails/`
- Format: JPEG at quality 85 for web optimization
- Filename: `md5(original_path).jpg`

**Advantages:**
- Full control over size and quality
- Consistent behavior across all image formats (JPG, PNG, JP2)
- Reliable and predictable
- Simple implementation

## Potential Enhancement: QuickLook Integration

### What is QuickLook?

macOS's QuickLook framework generates thumbnails for files throughout the system. These are stored in a system database and used by Finder, Preview, and other apps.

### Access Methods

#### Option 1: Command-Line Tool (`qlmanage`)

```python
import subprocess
import os

def generate_thumbnail_quicklook(image_path, output_dir, size=150):
    """Generate thumbnail using macOS QuickLook"""
    try:
        result = subprocess.run(
            ['qlmanage', '-t', '-s', str(size), image_path, '-o', output_dir],
            capture_output=True,
            timeout=5
        )
        if result.returncode == 0:
            # qlmanage creates files with .png extension
            thumbnail_path = os.path.join(output_dir, 
                                         os.path.basename(image_path) + '.png')
            return thumbnail_path if os.path.exists(thumbnail_path) else None
    except (subprocess.TimeoutExpired, Exception) as e:
        return None
```

#### Option 2: QuickLook Framework (via PyObjC)

```python
from Quartz import QLThumbnailImageCreate
from CoreFoundation import CFURLCreateWithFileSystemPath, kCFAllocatorDefault

def get_quicklook_thumbnail(image_path, size=150):
    """Get thumbnail using QuickLook framework directly"""
    url = CFURLCreateWithFileSystemPath(kCFAllocatorDefault, 
                                        image_path, 0, False)
    thumbnail = QLThumbnailImageCreate(kCFAllocatorDefault, 
                                       url, (size, size), {})
    # Convert CGImage to format usable by web app
    # ... additional conversion code needed
```

### Hybrid Approach

Combine both methods for best performance:

```python
def get_thumbnail(image_path, cache_dir, size=150):
    """
    Get thumbnail with fallback chain:
    1. Check custom cache
    2. Try QuickLook (if available)
    3. Generate with Pillow
    """
    cache_key = hashlib.md5(image_path.encode()).hexdigest()
    cache_path = os.path.join(cache_dir, f"{cache_key}.jpg")
    
    # 1. Check custom cache first
    if os.path.exists(cache_path):
        return cache_path
    
    # 2. Try QuickLook (fast if already generated)
    ql_thumb = try_quicklook_thumbnail(image_path, cache_dir, size)
    if ql_thumb:
        # Convert to our cache format and return
        return convert_and_cache(ql_thumb, cache_path)
    
    # 3. Fallback to Pillow
    return generate_pillow_thumbnail(image_path, cache_path, size)
```

## Performance Analysis

### Scenario 1: Fresh Import (500 Images, No System Thumbnails)

- **Pillow only**: ~2-3 seconds initial load
- **Hybrid**: ~2-3 seconds (no benefit, same fallback)

### Scenario 2: Previously Viewed in Finder (500 Images)

- **Pillow only**: ~2-3 seconds initial load (first app run)
- **Hybrid**: ~0.5-1 second (QuickLook thumbnails already exist)

### Scenario 3: Subsequent Loads (Custom Cache Exists)

- **Both approaches**: Instant (loading from cache)

## Trade-offs

### Pros of QuickLook Integration

1. **Faster first load** for files previously viewed in Finder
2. **System consistency** - thumbnails match Finder appearance
3. **Reduced CPU usage** if thumbnails already exist
4. **No redundant work** - leverage existing system resources

### Cons of QuickLook Integration

1. **Increased complexity** - more code paths to maintain
2. **Unreliable** - thumbnails may not exist or may be stale
3. **Inconsistent sizing** - may not match exact 150x150px requirement
4. **Format issues** - QuickLook generates PNG, needs conversion for web optimization
5. **macOS-specific** - reduces portability if app is ever shared to Linux/Windows
6. **Dependency on system tools** - `qlmanage` or PyObjC required

## Recommendation

### For MVP (Current)

**Stick with Pillow-only approach:**
- Simpler, more predictable
- Cross-platform if app is shared later
- Still very fast (2-3 seconds is acceptable per PRD)
- Custom cache provides instant subsequent loads

### For Future Enhancement

Consider hybrid approach if:
- Performance profiling shows thumbnail generation is a bottleneck
- Users regularly work with 1000+ image folders
- Users frequently switch between folders (cache misses common)

## Implementation Notes

### If Implementing QuickLook Support

1. **Make it optional** - Don't fail if QuickLook unavailable
2. **Always maintain Pillow fallback** - Ensures reliability
3. **Normalize output** - Convert all thumbnails to consistent format/size
4. **Cache everything** - Store normalized version in custom cache
5. **Add feature flag** - Easy to disable if issues arise

### Testing Considerations

- Test with images never opened in Finder (fresh downloads)
- Test with images recently viewed in Finder
- Test with JP2 format (may have limited QuickLook support)
- Measure actual performance difference on target hardware
- Test with folders of 100, 500, 1000+ images

## Related Resources

- [Apple QuickLook Documentation](https://developer.apple.com/documentation/quicklook)
- [qlmanage man page](https://ss64.com/osx/qlmanage.html)
- [PyObjC Project](https://pyobjc.readthedocs.io/)

## Decision Log

- **2025-11-19**: Decided to implement Pillow-only for MVP (simpler, cross-platform)
- **Future**: Revisit QuickLook integration if performance becomes an issue

---

*This document captures the exploration of macOS system thumbnail integration for potential future optimization.*
