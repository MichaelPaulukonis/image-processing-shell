# Product Requirements Document: Image Tagger & Renamer

**Version:** 1.1  
**Date:** November 19, 2025  
**Status:** Implementation Ready  
**Author:** Michael Paulukonis

---

## Change Log

**v1.1 (2025-11-19):**
- Added UI mockup reference and implementation clarifications
- Clarified folder change behavior (initial selection only, warning for Day 2)
- Confirmed scroll-only navigation (no pagination for MVP)
- Specified dark mode as default with light/dark switcher for Day 2
- Documented error display approach (modals to be determined)
- Added Select All/Clear Selection to critical features
- Clarified filename format and tag sorting behavior
- Updated accessibility requirements

**v1.0 (2025-11-18):**
- Initial PRD based on discovery interview

---

## 1. Executive Summary

### Overview
Image Tagger & Renamer is a locally-hosted web application designed to streamline the process of viewing, tagging, and batch-renaming image files for generative art workflows. The tool provides a visual interface for organizing large collections of images through a flexible tagging system that generates consistent, searchable filenames.

### Key Value Proposition
- **Eliminates repetitive manual renaming** of hundreds of images with inconsistent naming conventions
- **Visual thumbnail-based workflow** that allows quick identification and selection of images
- **Flexible tagging system** that combines prefix/suffix with multiple tags to create descriptive, searchable filenames
- **Persistent tag library** that learns and adapts to user's evolving taxonomy

### Target Market
Primary: Personal use for organizing images used in generative art projects

Secondary: Open-source tool (MIT license) available for other creative professionals with similar needs (collage artists, digital archivists, art researchers)

---

## 2. Problem Statement

### Current Pain Points
1. **Time-consuming manual renaming**: Processing hundreds of images individually is tedious and error-prone, especially when images aren't pre-organized
2. **Inconsistent naming conventions**: Without a standardized system, files become difficult to search and organize later
3. **Repetitive typing**: Manually entering tags for similar images across multiple sessions leads to typos and inconsistencies
4. **Lack of visual context**: Command-line or file browser renaming doesn't provide adequate visual feedback for image identification

### User Frustrations
- Scrolling through file lists to rename images one-by-one or in small groups
- Losing track of which images have been processed
- Difficulty organizing mixed collections (e.g., 100 images where 50 are comics, 30 of those also Nancy-related, 20 are logos, etc.)
- Copy-paste doesn't work well when images need different tag combinations

### Market Opportunity
While commercial tools like Adobe Bridge, XnView, and Bulk Rename Utility exist, none provide a streamlined, tag-based visual workflow specifically optimized for organizing images for generative art pipelines. This tool fills that gap with a focused, purpose-built solution.

---

## 3. Product Vision & Goals

### Long-term Vision
A lightweight, fast, and intuitive tool that becomes the default solution for organizing images in creative workflows. The tool should be extensible to support folder organization, basic image editing, and integration with generative art pipelines.

### Key Objectives
1. **MVP Timeline**: Achieve working end-to-end functionality within days
2. **Immediate usability**: Quick launch and thumbnail view that provides instant access to images
3. **Workflow efficiency**: Reduce image organization time by eliminating manual typing and providing visual feedback

### Success Metrics
- **Primary**: Tool becomes the go-to solution based on intuitive feel and reliability
- **Adoption markers**: Successfully processes 500+ images within first few weeks
- **Quality indicators**: Consistently generates correctly-named files without errors

### Future Capabilities (Post-MVP)
- **Phase 2**: Drag-and-drop to folders for automatic organization
- **Phase 3**: Basic image editing (crop and rotate)
- **Day 2 Features**: 
  - Folder change warning popup (confirm/cancel when changing directories mid-session)
  - Light/dark theme switcher (unless trivial to add in MVP)
  - Filter by filename/tags to create copies
  - Export JSON for "virtual" folder organization
  - Enhanced search and filtering capabilities

### Out of Scope
- Cloud storage and synchronization
- Collaboration features
- Advanced image editing beyond crop/rotate
- Mobile application

---

## 4. Target Users & Personas

### Primary User: Solo Generative Artist

**Profile:**
- Comfortable with command-line tools and local development
- Works with hundreds of images per session for generative art projects
- Needs to organize mixed collections with overlapping categories
- Values speed and visual feedback over complex features

**Technical Level:**
- Can launch applications from command line or IDE
- Comfortable with localhost and basic web development concepts
- Doesn't require GUI installer - command-line setup is acceptable

**Typical Workflow:**
1. Downloads or creates 200+ images from various sources
2. Opens Image Tagger & Renamer via command line
3. Points app to folder containing mixed image collection
4. Scans thumbnails to identify image types
5. Selects groups of similar images (all comics, all logos, etc.)
6. Applies relevant tags from existing library or adds new ones
7. Renames batch and moves to next group
8. Organizes renamed images into folders for specific generative art use-cases

**Pain Points:**
- Needs to process images quickly between client projects
- Works with overlapping categories requiring flexible tagging
- Requires searchable filenames for later retrieval

**Goals:**
- Organize hundreds of images per week efficiently
- Maintain consistent naming conventions across projects
- Quickly find specific images for generative art inputs

---

## 5. Functional Requirements

### 5.1 Core Features (MVP)

#### FR-1: Directory Selection and Image Loading
- **Description**: User can select any directory on local filesystem to view images
- **Acceptance Criteria**:
  - App prompts for directory path on startup or provides file browser
  - Loads all supported image formats (JPG, PNG, JP2) from selected directory
  - Displays loading indicator while scanning directory
  - Shows error message if directory inaccessible or contains no images
- **Implementation Notes**:
  - Initial folder selection only for MVP
  - Changing folders mid-session clears all selections (no warning for MVP)
  - Folder change warning popup with confirm/cancel deferred to Day 2

#### FR-2: Thumbnail Grid Display
- **Description**: Display all images as thumbnails in a scrollable grid layout
- **Acceptance Criteria**:
  - Grid layout with multiple thumbnails visible simultaneously
  - Thumbnails sized for quick scanning (small enough to see many at once)
  - Smooth scrolling through large collections (500+ images)
  - Thumbnail generation cached for performance
  - Original filename displayed below each thumbnail
- **Implementation Notes**:
  - Scroll-only navigation (no pagination for MVP)
  - Loading indicator shown during initial thumbnail generation
  - No visual feedback needed for caching status

#### FR-3: Image Selection
- **Description**: Support both single and multiple image selection
- **Acceptance Criteria**:
  - Single-selection mode is default (clicking an image selects only that one)
  - Multiple-selection mode enabled via toggle in header
  - Selected images show checkmark overlay on thumbnail
  - Selection count displayed prominently (e.g., "Selected: 12 / 256")
  - "Select All" and "Clear Selection" buttons available in header
  - Selection state cleared when changing folders
- **Implementation Notes**:
  - Visual selection feedback: checkmark, border highlight, and semi-transparent overlay
  - Multi-select toggle must be clearly visible and labeled

#### FR-4: Tag Management System
- **Description**: Persistent tag library that users can add to and reuse across sessions
- **Acceptance Criteria**:
  - Pre-populated with starter tags: comics, nancy, popart, warhol, fineart, advertising, logos, sluggo, food, horror, western
  - Tags displayed as click-to-toggle pills/chips in UI
  - "Add New Tag" button allows user to create custom tags
  - New tags added to master list immediately
  - Tag library persists between sessions
  - Tags stored in local configuration file

#### FR-5: Prefix and Suffix Input
- **Description**: Allow user to specify optional prefix and suffix for filename
- **Acceptance Criteria**:
  - Text input fields for prefix and suffix
  - Both fields optional
  - Preview of filename format shown before rename
  - Prefix appears at start of filename, suffix at end before file extension

#### FR-6: Duplicate Numbering
- **Description**: Automatic numbering system to handle duplicate filenames
- **Acceptance Criteria**:
  - System checks for existing filenames before rename
  - If duplicate exists, appends `_000`, `_001`, `_002`, etc.
  - Numbering format uses 3-digit zero-padded numbers
  - No user configuration required (on by default)

#### FR-7: Batch Rename Execution
- **Description**: Rename selected images using prefix + tags + suffix + numbering
- **Acceptance Criteria**:
  - Tags sorted alphabetically in filename (NOT UI display order)
  - Format: `[prefix]_[tag1]_[tag2]_[tagN]_[suffix]_[number].ext`
  - Example: `monochrome_comics_food_nancy_sluggo_000.png`
  - Original filename is NOT included in output (completely replaced)
  - Rename happens immediately when user clicks "Rename" button
  - Original file extension preserved
  - Success confirmation shown after rename completes
  - Progress indicator for operations >1 second
- **Implementation Notes**:
  - Preview must accurately show final filename with alphabetically sorted tags
  - Button shows count: "Rename 12 Selected Images"
  - Post-rename behavior to be designed (success message, toast notification, or status area)

#### FR-8: Error Handling and Logging
- **Description**: Detailed logging and error reporting for troubleshooting
- **Acceptance Criteria**:
  - All operations logged with timestamps
  - Errors displayed to user with clear messages (file locked, permission denied, disk full, etc.)
  - Log file stored in app configuration directory
  - Console output available for command-line troubleshooting
- **Implementation Notes**:
  - Error display mechanism to be determined (modals, inline error area, or toast notifications)
  - Must not block workflow - user should be able to continue after error
  - Errors should be specific and actionable (not generic "An error occurred")

### 5.2 Advanced Features (Future Releases)

#### FR-9: Folder Organization (Phase 2)
- Drag-and-drop images to folders
- Auto-create folders based on tags
- Batch copy to multiple destinations

#### FR-10: Basic Image Editing (Phase 3)
- Simple crop tool
- 90-degree rotation (left/right)
- No filters, adjustments, or advanced editing

#### FR-11: Enhanced Filtering and Search (Day 2)
- Filter images by current filename
- Search by applied tags
- Create filtered copies to new location
- Export tag metadata as JSON

#### FR-12: Optional Undo System (Nice-to-Have)
- Track rename operations
- Simple undo/redo for recent actions
- Not required for MVP

### 5.3 User Stories

**US-1: Batch Tag Comics Collection**
> As a generative artist, I want to select all comic-related images in a folder and tag them with "comics" so I can quickly identify them later without reviewing each one individually.

**US-2: Multi-Category Tagging**
> As a user organizing 100 images where some overlap (30 comics that are also Nancy, 10 that are also horror), I want to select subsets and apply multiple tags so each image has accurate metadata reflected in its filename.

**US-3: Create and Reuse New Tags**
> As a user working with evolving categories, I want to add new tags like "sluggo" during a session and have them available in future sessions so I don't have to recreate my taxonomy.

**US-4: Process Large Batches Quickly**
> As a user with 500 images to organize, I want to see thumbnails load quickly and be able to scroll smoothly so I don't waste time waiting for the interface to respond.

**US-5: Find Images Later**
> As a user who organizes images by filename, I want consistent, searchable filenames (e.g., `fineart_warhol_popart_001.png`) so I can use filesystem search to find specific images for my generative art projects.

---

## 6. Technical Requirements

### 6.1 Platform and Architecture

**Technology Stack:**
- **Backend**: Python 3.10+ with Flask web framework
- **Frontend**: HTML5, CSS3, JavaScript (vanilla or lightweight framework)
- **Image Processing**: Pillow (PIL) for thumbnail generation and image operations
- **Data Storage**: JSON files for configuration and tag library

**Deployment Model:**
- Locally-hosted web server (Flask development server for MVP)
- Launched via command line: `python app.py` or similar
- Accessed via browser at `http://localhost:5000`
- Single-user, local-only (no remote access required)

### 6.2 File System Access

**Permissions:**
- Full read/write access to user-selected directories
- No sandbox or directory restrictions
- User explicitly selects directories to process

**Supported Image Formats:**
- JPG/JPEG
- PNG  
- JP2/JPEG2000
- Expandable to GIF, WebP, TIFF, BMP in future releases

### 6.3 Performance Requirements

**Thumbnail Generation:**
- Target: Display first page of thumbnails within 2-3 seconds for folders with 500+ images
- Approach: Generate thumbnails on-demand and cache to disk
- Cache location: `~/.image-tagger-renamer/cache/thumbnails/`
- Thumbnail size: 150x150px (or scaled to maintain aspect ratio)

**UI Responsiveness:**
- Smooth scrolling with 100+ thumbnails visible
- Selection operations should feel instantaneous (<100ms)
- Batch rename operations: Progress indicator for operations >1 second

**Scalability:**
- MVP target: Handle 1000 images per folder
- Future: Pagination or lazy-loading for 5000+ image folders

### 6.4 Data Persistence

**Configuration Storage:**
- Location: `~/.image-tagger-renamer/` (hidden folder in user's home directory)
- Files:
  - `config.json`: App settings and preferences
  - `tags.json`: Master tag library
  - `analytics.json`: Optional usage statistics
  - `app.log`: Detailed operation logs

**Tag Library Format (tags.json):**
```json
{
  "tags": [
    "comics",
    "nancy",
    "sluggo",
    "popart",
    "warhol",
    "fineart",
    "advertising",
    "logos",
    "food",
    "horror",
    "western"
  ],
  "created": "2025-11-18T10:30:00Z",
  "last_modified": "2025-11-18T14:45:00Z"
}
```

### 6.5 Security and Compliance

**File System Safety:**
- No automatic deletion of files
- Rename operations are atomic (fail entirely if any file fails)
- Detailed logging of all file operations for audit trail

**Data Privacy:**
- No cloud connectivity
- No external API calls
- All data stays on local machine
- Analytics data (if collected) stored locally only

### 6.6 Integration Requirements

**Current:** None required for MVP

**Future Potential:**
- Export tag metadata for use in other tools
- Integration with generative art pipelines via JSON export
- Folder structure generation based on tags

---

## 7. Design & UX Considerations

### 7.1 Key Design Principles

1. **Visual First**: Thumbnails are the primary interface element
2. **Mouse-Driven**: Optimized for point-and-click workflow, keyboard shortcuts optional
3. **Minimal Friction**: Reduce clicks and typing to absolute minimum
4. **Immediate Feedback**: Show results of actions instantly
5. **Forgiving**: Make it hard to make mistakes, easy to correct them

### 7.2 User Interface Layout

**UI Mockup Reference:**
- HTML/CSS mockup located at: `docs/inspo/image_tagger_&_renamer_dashboard/code.html`
- Screenshot available at: `docs/inspo/image_tagger_&_renamer_dashboard/screen.png`
- **Implementation approach**: Use mockup for visual design and layout, implement PRD specifications for logic and behavior

**Main Screen Components:**

```
┌─────────────────────────────────────────────────────────────┐
│ Image Tagger & Renamer                    [Directory: ...]  │
├─────────────────────────────────────────────────────────────┤
│ [Change Folder]  [Multi-Select: OFF]  [Select All] [Clear] │
│                                          [Selected: 0/245]   │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌───┐ ┌───┐ ┌───┐ ┌───┐ ┌───┐ ┌───┐ ┌───┐ ┌───┐ ┌───┐  │
│  │img│ │img│ │img│ │img│ │img│ │img│ │img│ │img│ │img│  │
│  └───┘ └───┘ └───┘ └───┘ └───┘ └───┘ └───┘ └───┘ └───┘  │
│  name  name  name  name  name  name  name  name  name     │
│                                                               │
│  [Scrollable grid of thumbnails continues...]                │
│                                                               │
├─────────────────────────────────────────────────────────────┤
│ Prefix: [________]  Suffix: [________]                      │
│                                                               │
│ Tags: [comics] [nancy] [sluggo] [popart] [warhol]           │
│       [fineart] [advertising] [logos] [food] [horror]       │
│       [western] [+ Add New Tag]                             │
│                                                               │
│ Preview: prefix_comics_food_nancy_sluggo_000.png            │
│                                                               │
│                    [Rename 12 Selected Images]               │
└─────────────────────────────────────────────────────────────┘
```

**Design Notes:**
- Dark mode as default theme
- Light/dark theme switcher deferred to Day 2 (unless trivial to implement)
- Mockup uses Tailwind CSS with Space Grotesk font
- Primary color: #0db9f2 (cyan/blue)
- Grid uses auto-fill layout with 150px minimum thumbnail size

### 7.3 Interaction Patterns

**Thumbnail Grid:**
- Small square thumbnails (150x150px) in responsive grid
- Hover shows slightly larger preview or full filename
- Click toggles selection (checkmark appears on selected)
- Multi-select mode: all clicks toggle selection until mode disabled

**Tag Selection:**
- Pills/chips UI pattern (rounded rectangles with text)
- Inactive: light gray background
- Active/selected: blue background with white text
- Click to toggle on/off
- Newly added tags appear at end of list

**Add New Tag Flow:**
1. Click "+ Add New Tag" button
2. Inline text input appears (in-place, not a modal)
3. Type tag name and press Enter (or click Save)
4. New tag added to list immediately and saved to tags.json
5. Input field disappears after save
6. New tag appears at end of tag list and is immediately usable

**Note:** Mockup shows "+ Add New Tag" button but not the inline input state - this must be implemented

**Rename Flow:**
1. Select image(s) via thumbnails
2. Set prefix/suffix (optional)
3. Select tags by clicking pills
4. Preview dynamically updates to show resulting filename with alphabetically sorted tags
5. Click "Rename X Selected Images" (button shows count)
6. Brief progress indicator (if multiple files or operation >1 second)
7. Success message confirms completion (mechanism TBD: toast, status area, or modal)
8. Thumbnails refresh to show new names
9. Selection state preserved or cleared (TBD based on UX testing)

**Note:** Mockup preview shows incorrect format - implementation must follow PRD specification with alphabetically sorted tags and no original filename

### 7.4 User Experience Goals

**Speed:**
- Minimize time from launch to first interaction
- No multi-step wizards or complex navigation
- One-screen workflow for 90% of use cases

**Confidence:**
- Preview shows exact filename before rename
- Clear visual feedback on selected images
- Confirmation messages for completed actions

**Flexibility:**
- Works with any folder structure
- Supports arbitrary tag combinations
- Doesn't force specific organization scheme

### 7.5 Accessibility Requirements

**MVP:**
- Keyboard-accessible (tab navigation through UI)
- Sufficient color contrast for readability
- Clear text labels for all controls
- Proper keyboard navigation for image selection (not relying solely on hidden checkboxes)
- Focus indicators visible on all interactive elements
- Semantic HTML structure

**Implementation Notes:**
- Mockup uses `opacity-0` checkboxes which may have accessibility issues
- Must ensure keyboard users can navigate and select images without mouse
- Consider arrow key navigation for image grid
- Tag pills must be keyboard accessible (Space/Enter to toggle)

**Future Enhancements:**
- Screen reader support with ARIA labels
- Keyboard shortcuts for power users (e.g., Ctrl+A for Select All)
- Customizable thumbnail size for visibility

---

## 8. Success Metrics & KPIs

### 8.1 Usage Analytics (Optional)

**Basic Tracking:**
- Session count and duration
- Images processed per session
- Average time per batch operation
- Tag usage frequency (identify most/least used tags)

**Storage:** All analytics stored locally in `~/.image-tagger-renamer/analytics.json`

**Format:**
```json
{
  "sessions": [
    {
      "date": "2025-11-18",
      "duration_minutes": 15,
      "images_processed": 247,
      "rename_operations": 5,
      "tags_used": ["comics", "nancy", "sluggo", "food"],
      "new_tags_created": ["monster"]
    }
  ],
  "totals": {
    "total_images_processed": 1247,
    "total_sessions": 12,
    "tag_usage": {
      "comics": 523,
      "nancy": 234,
      "fineart": 189
    }
  }
}
```

### 8.2 Quality Indicators

**Qualitative Success Factors:**
1. **Intuitive Feel**: Tool feels natural to use without referring to documentation
2. **Reliability**: Zero file corruption or loss incidents
3. **Speed**: Workflow feels faster than manual renaming
4. **Confidence**: User trusts rename operations without double-checking

**Quantitative Indicators:**
- Successfully process 500+ images within first 2 weeks
- Use tool for 3+ consecutive sessions without reverting to manual methods
- Create 5+ new tags that become part of regular workflow

### 8.3 Adoption Criteria

**Tool is considered successful when:**
1. It becomes the default/automatic choice for image organization tasks
2. User stops exploring alternative tools
3. Quick launch and thumbnail view work reliably
4. Rename operations execute without errors
5. Tag library grows organically to match user's actual needs

**Failure Indicators:**
- Frequent errors requiring troubleshooting
- Slower than manual renaming for typical batches
- UI requires multiple clicks to accomplish simple tasks
- Thumbnail generation too slow for practical use

---

## 9. Timeline & Milestones

### 9.1 Development Approach

**Strategy:** Build rough end-to-end functionality first, then iterate and polish

**Philosophy:**
- Get something working quickly that demonstrates core value
- Iterate based on actual usage experience
- Add features only when current version proves viable

### 9.2 Phase 1: MVP (Target: Days)

**Milestone 1.1: Project Setup**
- [ ] Initialize Flask project structure
- [ ] Set up basic routing and template structure
- [ ] Create configuration directory in home folder
- [ ] Implement logging framework

**Milestone 1.2: Core Backend (Day 1-2)**
- [ ] Directory scanning and image file detection
- [ ] Thumbnail generation with caching
- [ ] Tag library management (read/write JSON)
- [ ] Filename generation logic with duplicate detection
- [ ] File rename operations with error handling

**Milestone 1.3: Frontend UI (Day 2-3)**
- [ ] Thumbnail grid display with scrolling
- [ ] Image selection (single and multi-mode)
- [ ] Tag pill/chip UI with toggle functionality
- [ ] Prefix/suffix input fields
- [ ] Rename button and preview display

**Milestone 1.4: Integration & Testing (Day 3-4)**
- [ ] Connect frontend to backend API
- [ ] Test with 100+ image folder
- [ ] Verify rename operations work correctly
- [ ] Test duplicate numbering logic
- [ ] Validate tag persistence across sessions

**Milestone 1.5: Polish & Deploy (Day 4-5)**
- [ ] Error handling and user feedback messages
- [ ] Loading indicators and progress displays
- [ ] Basic documentation (README with setup instructions)
- [ ] Create launcher script for easy startup

### 9.3 Phase 2: Enhanced Features (Post-MVP)

**Milestone 2.1: Folder Organization**
- Drag-and-drop to folders
- Batch copy operations
- Folder creation based on tags

**Milestone 2.2: Basic Editing**
- Crop tool integration
- Rotation (90-degree increments)
- Preview before applying edits

### 9.4 Phase 3: Advanced Capabilities

**Milestone 3.1: Filtering & Search**
- Filter by filename patterns
- Search by tags
- Export filtered results

**Milestone 3.2: Export & Integration**
- JSON metadata export
- Virtual folder definitions
- Integration with generative art pipeline

### 9.5 Dependencies and Risks

**External Dependencies:**
- Python 3.10+ installed
- Flask and Pillow packages available via pip
- Modern web browser (Chrome, Firefox, Safari)

**Technical Risks:**
- **JP2 format support**: May require additional libraries or conversion
- **Thumbnail performance**: Large image files might be slow to process
- **File system permissions**: Some directories may be protected on macOS

**Mitigation Strategies:**
- Start with JPG/PNG, add JP2 in iteration if needed
- Implement lazy loading if thumbnail generation is too slow
- Clear error messages for permission issues with guidance

**Timeline Risks:**
- Client projects take priority (acknowledged and accepted)
- Flask learning curve may extend timeline slightly
- Scope creep from discovering new requirements during usage

**Mitigation:**
- Strict MVP feature set - defer all "nice-to-haves"
- Use Flask tutorials and examples for rapid learning
- Document feature requests but don't implement until MVP proven

---

## 10. Assumptions & Constraints

### 10.1 Key Assumptions

**Technical Assumptions:**
1. User has Python 3.10+ installed or can install it
2. macOS file system conventions apply (home directory structure)
3. User is comfortable with command-line application launch
4. Modern web browser available (Chrome, Firefox, Safari - last 2 versions)
5. Sufficient disk space available for thumbnail cache (estimate: 50MB per 1000 images)

**User Behavior Assumptions:**
1. User will work with folders containing 100-1000 images typically
2. Images are generally organized in folders by project or batch
3. User prefers visual identification over filename-based selection
4. Tag taxonomy will evolve over time (10-50 tags eventually)
5. User willing to accept occasional iteration and refinement of tool

**Workflow Assumptions:**
1. Single user, no concurrent access needed
2. No need for undo beyond file system backup
3. Rename operations are intentional (no accidental batch renames)
4. User understands filesystem concepts and permissions

### 10.2 Constraints

**Budget Constraints:**
- Zero budget - open source tools only
- No paid services or APIs
- Developer time limited by client work priorities

**Technical Constraints:**
- Must run entirely on local machine
- No cloud dependencies or external services
- Limited to Python ecosystem for ease of maintenance
- Flask development server acceptable for MVP (no production server needed)

**Timeline Constraints:**
- MVP must be achievable in days, not weeks
- Client projects interrupt development time
- Features deferred if they extend timeline significantly

**Scope Constraints:**
- Personal tool first, community tool second
- No mobile support (desktop/laptop only)
- No collaboration features
- No advanced image processing beyond basic crop/rotate

### 10.3 Technical Decisions

**Data Storage:**
- Configuration location: `~/.image-tagger-renamer/`
- Format: JSON (human-readable, easy to edit manually if needed)
- No database required for MVP

**JP2/JPEG2000 Support:**
- Initial support via Pillow if available
- If problematic, consider conversion workflow or defer to Phase 2
- Document any limitations in README

**Thumbnail Cache Strategy:**
- Cache generated thumbnails to disk
- Cache invalidation based on file modification time
- Clear cache option in UI (future enhancement)

### 10.4 Risks and Mitigation Strategies

| Risk | Impact | Likelihood | Mitigation |
|------|--------|------------|------------|
| Flask learning curve delays MVP | Medium | Low | Use tutorials, start with minimal routing |
| JP2 format causes thumbnail issues | Medium | Medium | Start with JPG/PNG, add JP2 incrementally |
| Large folders (1000+ images) cause performance problems | High | Medium | Implement pagination or lazy loading early if needed |
| File permissions block rename operations | Medium | Low | Clear error messages, document permission requirements |
| Tag library becomes unwieldy with 100+ tags | Low | Medium | Defer advanced tag management to Phase 2 |
| Scope creep during development | High | High | Strict MVP feature list, log ideas for post-MVP |
| User discovers tool doesn't meet needs | High | Low | Build rough e2e first for fast validation |

### 10.5 Success Criteria

**MVP is considered complete when:**
1. User can launch app from command line
2. User can select a folder and see thumbnails
3. User can select single or multiple images
4. User can apply tags from existing library
5. User can add new tags that persist
6. User can rename selected images with tags in alphabetical order
7. Duplicate filenames handled with numeric suffix
8. All operations logged for troubleshooting

**MVP is considered successful when:**
1. Tool is actually used for real image organization tasks
2. User prefers it to manual renaming
3. No critical bugs or data loss incidents
4. Performance is acceptable for 500+ image folders

---

## Appendix A: Example Workflows

### Workflow 1: Organizing Mixed Comic Collection

**Scenario:** User has 200 images - 80 comics (30 Nancy, 20 horror, 15 western), 60 logos, 40 fine art, 20 Warhol

**Steps:**
1. Launch app: `python app.py`
2. Select folder: `/Users/michael/Downloads/generative-sources/batch-2025-11-18`
3. Wait for thumbnails to load (2-3 seconds)
4. Enable multi-select mode
5. Scroll through, select all Nancy comics (30 images)
6. Set prefix: "comic"
7. Click tags: [comics] [nancy]
8. Preview shows: `comic_comics_nancy_000.png`
9. Click "Rename Selected Images"
10. Clear selection, scroll, select horror comics (20 images)
11. Tags: [comics] [horror]
12. Rename
13. Continue with western comics, logos, fine art, Warhol
14. Final results: 200 images with consistent, searchable names

**Time estimate:** 10-15 minutes (vs. 45+ minutes manual)

### Workflow 2: Adding New Tag Mid-Session

**Scenario:** User realizes some images need a new "monster" tag

**Steps:**
1. Working through image batch, selecting and tagging
2. Encounters group of monster-themed comics
3. Clicks "+ Add New Tag" button
4. Types "monster" in inline input
5. Presses Enter
6. New [monster] tag appears at end of tag list
7. Selects relevant images and applies [comics] [monster] [horror]
8. Renames batch
9. "monster" tag now available for future sessions

### Workflow 3: Large Batch Processing

**Scenario:** User has 800 images to organize over multiple mini-sessions

**Steps:**
1. Launch app, select folder with 800 images
2. Thumbnail cache builds over first 5 seconds
3. Process first 100 images (comics and Nancy subsets)
4. Close app to work on client project
5. Return later, launch app again
6. Thumbnails load instantly from cache
7. Scroll to unprocessed section (renamed files have consistent names, easier to identify)
8. Continue processing next 100 images
9. Repeat over several sessions until complete

---

## Appendix B: Technical Architecture

### Directory Structure
```
image-tagger-renamer/
├── app.py                 # Flask application entry point
├── requirements.txt       # Python dependencies
├── README.md             # Setup and usage instructions
├── config.py             # Configuration management
├── models/
│   ├── tag_manager.py    # Tag library operations
│   └── file_manager.py   # Image operations and renaming
├── routes/
│   ├── main.py           # Main UI routes
│   └── api.py            # JSON API endpoints
├── static/
│   ├── css/
│   │   └── styles.css
│   ├── js/
│   │   └── app.js
│   └── thumbnails/       # Cached thumbnails (symlink to ~/.image-tagger-renamer/cache/)
└── templates/
    └── index.html        # Main UI template
```

### API Endpoints (Preliminary)

```
GET  /                          # Main UI
GET  /api/images?dir=<path>     # List images in directory with thumbnail URLs
POST /api/rename                # Execute rename operation
GET  /api/tags                  # Get tag library
POST /api/tags                  # Add new tag
GET  /api/thumbnail/<path>      # Serve cached thumbnail
```

---

## Appendix C: Configuration File Examples

### ~/.image-tagger-renamer/config.json
```json
{
  "version": "1.0.0",
  "thumbnail_size": 150,
  "thumbnail_cache_path": "~/.image-tagger-renamer/cache/thumbnails/",
  "log_level": "INFO",
  "default_numbering_format": "{:03d}",
  "supported_formats": ["jpg", "jpeg", "png", "jp2"],
  "last_directory": "/Users/michael/Downloads/images",
  "analytics_enabled": true
}
```

### ~/.image-tagger-renamer/tags.json
```json
{
  "tags": [
    "comics",
    "nancy",
    "sluggo",
    "popart",
    "warhol",
    "fineart",
    "advertising",
    "logos",
    "food",
    "horror",
    "western",
    "monster"
  ],
  "created": "2025-11-18T10:30:00Z",
  "last_modified": "2025-11-18T14:45:00Z",
  "version": "1.0.0"
}
```

---

## Document Control

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.1 | 2025-11-19 | Michael Paulukonis | Added UI mockup clarifications and implementation notes |
| 1.0 | 2025-11-18 | Michael Paulukonis | Initial PRD based on discovery interview |

**Next Review Date:** Upon MVP completion

**Approval Status:** Implementation Ready - UI mockup evaluated and clarifications documented

---

## Appendix D: UI Mockup Evaluation Summary

**Mockup Location:** `docs/inspo/image_tagger_&_renamer_dashboard/`

### Key Agreements
- Grid layout with 150x150px thumbnails ✓
- Multi-select toggle in header ✓
- Tag pills/chips UI pattern ✓
- Prefix/suffix input fields ✓
- Preview display ✓
- Dark mode aesthetic ✓

### Critical Corrections Needed
1. **Filename preview format** - Mockup shows `genart_IMG_001_comics_abstract.jpg` but should be `genart_abstract_comics_000.jpg` (no original filename, alphabetically sorted tags, always include numbering)
2. **Tag sorting** - Must sort alphabetically in filename, not UI display order
3. **Missing features** - Select All/Clear Selection buttons must be added to header

### Implementation Priorities
1. Follow PRD for all naming logic and file operations
2. Use mockup for visual design, layout, and styling
3. Add missing UI elements (Select All, Clear, proper Add Tag flow)
4. Fix accessibility issues with hidden checkboxes
5. Design post-rename feedback mechanism (success message/toast)

### Deferred to Day 2
- Folder change warning popup
- Light/dark theme switcher (unless easy to add)
- Thumbnail cache status indicators
- Format preservation visual feedback

---

*End of Product Requirements Document*
