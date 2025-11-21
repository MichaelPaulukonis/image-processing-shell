# Image Tagger & Renamer (renamer-browser) — Project Snapshot

Last updated: 2025-11-21

This document captures a high-level overview of the `renamer-browser/` sub-project, highlights the current architecture and development posture, and calls out the next improvements to keep the MVP moving toward production readiness.

---

## 1. Project Overview

| Item | Details |
| --- | --- |
| **Project Name & Purpose** | Image Tagger & Renamer — a local-first web app that lets artists browse folders, apply reusable tags, and batch-rename large image sets with consistent filenames. |
| **Technology Stack** | Python 3.10+, Flask 2.3, Pillow 10, vanilla HTML/CSS/JS, browser-based UI. |
| **Project Type** | Single-user Flask web application with REST-style JSON endpoints. |
| **Target Audience** | Power users / generative-art practitioners who manage hundreds of local images per session. |
| **Current Status** | MVP feature-complete (Tasks 1-7 done). Working prototype with tests; moving toward polish and automation. |

---

## 2. Architecture Summary

- **Overall Architecture**: Thin Flask backend serving an SPA-like frontend. Core services live under `models/` and `routes/`. Browser JS orchestrates folder navigation, selections, tagging, and rename API calls. Thumbnails and user state persist on disk under `~/.image-tagger-renamer/`.
- **Key Components**:
  - `app.py`: Flask factory + CLI argument parsing.
  - `models/file_manager.py`: File scanning, filename generation, batch rename helpers.
  - `models/tag_manager.py`: Thread-safe tag catalog stored as JSON.
  - `models/thumbnail_manager.py`: Thread-pooled thumbnail generation & caching (JPEG output, transparency flattening).
  - `routes/main.py`: REST endpoints for thumbnails, directories, tags, rename, health.
  - `templates/index.html`, `static/css/styles.css`, `static/js/app.js`: UI layout, styling, and client logic.
- **Data Flow**: Browser calls `/api/images` → backend scans dir → enqueues thumbnails → responds with metadata & thumbnail URLs. Rename calls `/api/rename`, which leverages `file_manager.rename_file`. Tag CRUD flows through `/api/tags`. Config + tags persist via `ConfigManager` and `TagManager`.
- **External Dependencies**: None beyond standard Python libs and Flask/Pillow. No remote APIs or databases.
- **Design Patterns**: Factory pattern for Flask app creation, thin blueprint for routing, manager classes encapsulate persistence/IO, optimistic UI with async fetch calls.

---

## 3. Repository Structure Analysis

```text
renamer-browser/
├── app.py                # Entry point & CLI
├── config.py             # Config + logging + user dirs
├── models/
│   ├── file_manager.py
│   ├── tag_manager.py
│   └── thumbnail_manager.py
├── routes/
│   └── main.py
├── static/
│   ├── css/styles.css
│   └── js/app.js
├── templates/
│   └── index.html
├── tests/
│   ├── test_routes_thumbnails.py
│   ├── test_tag_manager.py
│   └── test_thumbnail_manager.py
├── requirements.txt
└── README.md
```

- **Key Files**: `app.py`, managers, blueprint, template + assets, tests, `requirements.txt`.
- **Configuration Files**: Runtime config lives in `$HOME/.image-tagger-renamer/config.json`, `tags.json`, and log/thumbnail cache directories; repo includes `config.py` to manage them. No `.env` provided.
- **Entry Points**: `python app.py [folder] [--port --host --debug]` as documented in README.
- **Build/Deploy**: Lightweight — install deps, run Flask dev server. No dedicated build scripts or deployment automation yet.

---

## 4. Feature Analysis

- **Core Features**: Folder selection modal, thumbnail grid with incremental loading, single/multi-select workflows, persistent tag pills + creation, filename preview, batch rename with deterministic formatting, cached thumbnails, queue-based pre-generation.
- **User Workflows**: Launch → choose directory → browse thumbnails → select subset → toggle tags/prefix/suffix → preview → rename → repeat or change folder.
- **API Endpoints** (routes/main.py):
  - `GET /` (UI), `GET /health`.
  - `GET /api/images?dir=` — list images and queue thumbnails.
  - `GET /api/thumbnails` (`mode=queue` optional) and `POST /api/thumbnails/queue` — fetch or enqueue thumbnails.
  - `GET /api/directories?base=` — folder tree for modal.
  - `GET/POST /api/tags` — list/add tags.
  - `POST /api/rename` — batch rename payload.
- **Data Models**: Filesystem-based; metadata assembled at runtime. No database schema.
- **Authentication**: None (local-only single-user tool). Runs on localhost.

---

## 5. Development Setup

- **Prerequisites**: Python 3.10+, pip/venv, modern browser. Optional watch tooling for autoreload.
- **Installation**:
  1. `cd renamer-browser && python -m venv venv && source venv/bin/activate`
  2. `pip install -r requirements.txt`
  3. `python app.py [~/Pictures]`
- **Workflow**: Standard edit→run loop. Taskmaster tracks work items in project root (`tm list`). Config + tags stored under `~/.image-tagger-renamer/`.
- **Testing Strategy**: `python -m unittest tests.test_thumbnail_manager tests.test_tag_manager tests.test_routes_thumbnails`. Coverage focuses on IO managers and main routes; frontend lacks automated tests.
- **Code Quality**: No linters configured; relies on readable Python + docstrings. Logging wired through `config.py`. Consider adding Ruff/black + pre-commit.

---

## 6. Documentation Assessment

| Area | Status |
| --- | --- |
| **README** | Strong: setup, usage, config paths, workflow, troubleshooting. Could add screenshots and roadmap summary. |
| **Inline Docs** | Docstrings present in managers/routes; JS/CSS lightly commented. Overall readable. |
| **API Docs** | Implicit via code/tests; no formal schema or examples outside README. |
| **Architecture Docs** | High-fidelity PRD in `docs/plans/image-tagger-renamer-prd.md`, but no concise architecture diagram. |
| **User Docs** | README doubles as user guide; no GIFs/tutorials yet. |

---

## 7. Missing Documentation Suggestions

| Doc Type | Suggestion |
| --- | --- |
| **PRD Link** | Promote existing `docs/plans/image-tagger-renamer-prd.md` via README “Requirements” section or relocate into `/docs/requirements/PRD.md`. |
| **Architecture Overview** | Add `/docs/architecture/overview.md` containing component diagram + data flow (reuse content from this snapshot). |
| **ADR Folder** | Create `/docs/decisions/ADR-0001-thumbnail-cache.md` etc. to record choices (local cache, JSON storage). |
| **API Docs** | `/docs/api/README.md` with endpoint table + sample payloads (derived from `routes/main.py`). |
| **Deployment Guide** | `/docs/deployment/local.md` describing environment variables, config dir, cache clearing. |
| **Contributing Guide** | Root-level `CONTRIBUTING.md` covering setup, lint/test commands, Taskmaster workflow. |
| **Changelog** | `CHANGELOG.md` with Keep a Changelog format; tie to Taskmaster tasks. |
| **Security Policy** | `SECURITY.md` clarifying local-only usage, data privacy stance. |

Template pointers: use GitHub’s standard templates (README/CONTRIBUTING/SECURITY), Microsoft ADR template, and OpenAPI-style table for API doc.

---

## 8. Technical Debt & Improvements

- **Code Quality**: Overall clean but long modules (`file_manager.py` >700 lines) could benefit from splitting into scanner/renamer helpers. Add type hints for JS interactions or convert to modules for maintainability.
- **Performance**: Thumbnail cache now flattens transparency; remaining bottleneck is manual cache invalidation after code changes (tracked via Task 8). Consider cache versioning or timestamped subfolders.
- **Security**: No path allowlist; relies on local user. Input validation exists but add rate limiting or hidden-file guards in rename operations. Consider sanitizing user-provided destination paths.
- **Scalability**: Listing large directories currently loads everything at once. Future: pagination or virtualized scrolling, rename queue status.
- **Dependency Management**: Requirements pinned but minimal. Add lock file and upgrade plan; ensure Flask/Pillow security updates.

---

## 9. Project Health Metrics (Qualitative)

| Metric | Rating | Notes |
| --- | --- | --- |
| **Code Complexity** | ⚖️ Moderate | Clear separation of concerns but large helper modules. |
| **Test Coverage** | ✅ Core services | Managers + routes covered; frontend untested. |
| **Documentation Coverage** | ⚖️ Moderate | README + PRD strong; missing API/ADR/Contrib docs. |
| **Maintainability** | ✅ Good | Configured managers, tests, Taskmaster tasks; lacking lint automation. |
| **Technical Debt Level** | ⚠️ Emerging | Cache invalidation, folder browser UX, future pagination flagged. |

---

## 10. Recommendations & Next Steps

1. **Critical**
   - Automate thumbnail cache invalidation/versioning (Task 8) to prevent stale assets after future processing tweaks.
   - Add error reporting for rename failures in UI (toast or inline list) so users can quickly retry.
2. **Documentation**
   - Promote PRD + add `/docs/architecture/overview.md` and `/docs/api/README.md` for quick onboarding.
   - Draft `CONTRIBUTING.md` with Taskmaster workflow, coding standards, test commands.
3. **Code Quality**
   - Split `file_manager.py` into `scanner.py`, `renamer.py`, `naming.py` modules; add unit tests around `batch_rename_files`.
   - Introduce lint/format tooling (Ruff or Flake8 + Black) and optionally ESLint for JS.
4. **Feature Gaps**
   - Folder-change warning (per PRD Day 2) and undo trail for rename operations.
   - Filtering/search UI for tags/filenames and destination folder selection.
5. **Infrastructure**
   - Create lightweight CI (GitHub Actions) running unit tests + lint.
   - Document how to clear caches, seed sample folders, and run watch scripts.

---

## Quick Start Guide (3 steps)

1. `python -m venv venv && source venv/bin/activate`
2. `pip install -r requirements.txt`
3. `python app.py ~/Pictures/generative-art` and open `http://127.0.0.1:5000`

---

## Key Contact Points & Resources

- **Maintainer**: Michael Paulukonis (per PRD author) — primary point for questions/issues.
- **Issue Tracking**: Taskmaster `renamer` tag or GitHub issues (repository root).
- **Related Docs**:
  - Product Requirements: `docs/plans/image-tagger-renamer-prd.md`
  - UI inspiration mockup: `docs/inspo/image_tagger_&_renamer_dashboard/`
  - Sample assets: `samples/`

---

## Project Roadmap (from PRD & repo context)

- **MVP (current)**: Directory browsing, tagging, batch rename, thumbnail caching, dark UI.
- **Day 2**: Folder-change confirmation, light/dark toggle, filtering, undo, JSON export.
- **Phase 2+**: Drag-and-drop folder organization, basic editing (crop/rotate), integration hooks for generative pipelines.

---

## Documentation Template Suggestions

- **README Enhancements**: Add sections for “Architecture Overview”, “Roadmap”, and “Quick Troubleshooting Table”. Include screenshots of the UI.
- **PRD Template**: Adopt existing doc into `/docs/requirements/PRD.md` with version history table + open questions.
- **Architecture Doc**: Template with Context → Container → Component diagrams (C4 style) under `/docs/architecture/`.
- **API Docs**: Table-driven reference (endpoint, method, request schema, response, sample curl). Consider auto-generating via OpenAPI.
- **Contributing**: Outline dev setup, coding standards, Taskmaster usage, PR review checklist.

---

_This snapshot can serve as an onboarding guide, stakeholder brief, and improvement backlog reference. Update it as major architectural or process changes land._
