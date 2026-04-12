---
name: Woodcut extraction false-positive preference
description: User prefers over-capture (false positives, border bits, extra text) over splitting thematic images apart
type: feedback
---

When tuning image extraction from historical book pages, always prefer over-capture over under-capture.

**Why:** The user does post-processing on all extracted images — discarding false positives or trimming excess is easy. Merging two separately-extracted pieces of the same illustration is much harder.

**How to apply:** When there is a tension between:
- a filter that would remove false positives but risk splitting a real image, OR
- a looser threshold that keeps false positives but ensures thematic unity

→ always choose the looser threshold. Text-only crops, border fragments, and extra whitespace are all acceptable false positives.
