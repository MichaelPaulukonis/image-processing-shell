/* UI interactions for Image Tagger & Renamer. */
(() => {
    'use strict';

    const state = {
        directory: null,
        images: [],
        selected: new Set(),
        tags: [],
        activeTags: new Set(),
        multiSelect: false,
        prefix: '',
        suffix: '',
        folderBrowser: {
            current: '',
            parent: null,
            selected: '',
        },
    };

    const els = {
        changeFolder: document.getElementById('change-folder'),
        folderModal: document.getElementById('folder-select-modal'),
        folderInput: document.getElementById('folder-path'),
        folderSelect: document.getElementById('select-folder-button'),
        folderCancel: document.getElementById('cancel-folder-button'),
        currentDirectory: document.getElementById('current-directory'),
        loadingIndicator: document.getElementById('loading-indicator'),
        errorDisplay: document.getElementById('error-display'),
        errorMessage: document.querySelector('#error-display .error-message'),
        dismissError: document.getElementById('dismiss-error'),
        imageGrid: document.getElementById('image-grid'),
        imageTemplate: document.getElementById('image-card-template'),
        noImages: document.getElementById('no-images'),
        multiSelectToggle: document.getElementById('multi-select-toggle'),
        selectAll: document.getElementById('select-all'),
        clearSelection: document.getElementById('clear-selection'),
        selectedCount: document.getElementById('selected-count'),
        totalCount: document.getElementById('total-count'),
        prefixInput: document.getElementById('prefix-input'),
        suffixInput: document.getElementById('suffix-input'),
        renameButton: document.getElementById('rename-button'),
        renameHint: document.querySelector('.rename-hint'),
        filenamePreview: document.getElementById('filename-preview'),
        tagContainer: document.getElementById('tag-container'),
        tagTemplate: document.getElementById('tag-pill-template'),
        addTagButton: document.getElementById('add-tag-button'),
        addTagInputContainer: document.getElementById('add-tag-input-container'),
        newTagInput: document.getElementById('new-tag-input'),
        saveTagButton: document.getElementById('save-tag-button'),
        cancelTagButton: document.getElementById('cancel-tag-button'),
        taggingPanel: document.querySelector('.tagging-panel'),
        togglePanelButton: document.getElementById('toggle-panel-button'),
        folderList: document.getElementById('folder-list'),
        folderBreadcrumb: document.getElementById('folder-breadcrumb'),
        folderUpButton: document.getElementById('folder-up-button'),
        folderRefreshButton: document.getElementById('folder-refresh-button'),
    };

    const api = {
        async getTags() {
            const res = await fetch('/api/tags');
            if (!res.ok) throw new Error('Unable to load tags');
            return res.json();
        },
        async addTag(tag) {
            const res = await fetch('/api/tags', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ tag }),
            });
            const payload = await res.json();
            if (!res.ok) throw new Error(payload.error || 'Failed to add tag');
            return payload;
        },
        async getImages(directory) {
            const query = new URLSearchParams({ dir: directory }).toString();
            const res = await fetch(`/api/images?${query}`);
            const payload = await res.json();
            if (!res.ok) throw new Error(payload.error || 'Unable to load images');
            return payload;
        },
        async renameImages(payload) {
            const res = await fetch('/api/rename', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload),
            });
            const data = await res.json();
            if (!res.ok) throw new Error(data.error || 'Rename failed');
            return data;
        },
        async getDirectories(basePath) {
            const params = new URLSearchParams();
            if (basePath) params.set('base', basePath);
            const query = params.toString();
            const url = query ? `/api/directories?${query}` : '/api/directories';
            const res = await fetch(url);
            const data = await res.json();
            if (!res.ok) throw new Error(data.error || 'Unable to list folders');
            return data;
        },
    };

    function setLoading(isLoading) {
        els.loadingIndicator.classList.toggle('hidden', !isLoading);
    }

    function showError(message) {
        els.errorMessage.textContent = message;
        els.errorDisplay.classList.remove('hidden');
    }

    function hideError() {
        els.errorDisplay.classList.add('hidden');
        els.errorMessage.textContent = '';
    }

    function setFolderListStatus(message) {
        if (!els.folderList) return;
        const status = document.createElement('p');
        status.className = 'folder-list__status';
        status.textContent = message;
        els.folderList.innerHTML = '';
        els.folderList.appendChild(status);
    }

    function highlightSelectedFolder() {
        if (!els.folderList) return;
        const rows = els.folderList.querySelectorAll('.folder-row');
        rows.forEach((row) => {
            const isSelected = row.dataset.path === state.folderBrowser.selected;
            row.setAttribute('aria-selected', String(isSelected));
        });
    }

    function selectFolder(path) {
        state.folderBrowser.selected = path;
        if (path) {
            els.folderInput.value = path;
        }
        highlightSelectedFolder();
    }

    function renderFolderList(entries) {
        if (!els.folderList) return;
        if (!entries.length) {
            setFolderListStatus('No subfolders found');
            return;
        }
        const fragment = document.createDocumentFragment();
        entries.forEach((entry) => {
            const row = document.createElement('button');
            row.type = 'button';
            row.className = 'folder-row';
            row.dataset.path = entry.path;
            row.setAttribute('role', 'option');

            const name = document.createElement('span');
            name.className = 'folder-row__name';
            name.textContent = entry.name || entry.path;

            const meta = document.createElement('span');
            meta.className = 'folder-row__meta';
            meta.textContent = entry.is_hidden ? 'Hidden' : '';

            row.appendChild(name);
            row.appendChild(meta);
            row.addEventListener('click', () => selectFolder(entry.path));
            row.addEventListener('dblclick', () => loadFolderBrowser(entry.path));
            fragment.appendChild(row);
        });
        els.folderList.innerHTML = '';
        els.folderList.appendChild(fragment);
        highlightSelectedFolder();
    }

    async function loadFolderBrowser(targetPath) {
        if (!els.folderList) return;
        setFolderListStatus('Loading folders...');
        try {
            const payload = await api.getDirectories(targetPath);
            state.folderBrowser.current = payload.directory;
            state.folderBrowser.parent = payload.parent;
            if (els.folderBreadcrumb) {
                els.folderBreadcrumb.textContent = payload.directory;
            }
            if (els.folderUpButton) {
                els.folderUpButton.disabled = !payload.has_parent;
            }
            renderFolderList(payload.entries || []);
            selectFolder(payload.directory);
        } catch (error) {
            setFolderListStatus(error.message);
        }
    }

    function openModal() {
        els.folderModal.classList.remove('hidden');
        els.folderInput.focus();
        const seedPath = els.folderInput.value.trim() || state.directory || state.folderBrowser.current;
        loadFolderBrowser(seedPath);
    }

    function closeModal() {
        els.folderModal.classList.add('hidden');
        els.folderInput.value = '';
        state.folderBrowser.selected = '';
    }

    function updateSelectionUI() {
        els.selectedCount.textContent = state.selected.size.toString();
        els.totalCount.textContent = state.images.length.toString();
        const hasSelection = state.selected.size > 0;
        els.clearSelection.disabled = !hasSelection;
        els.renameButton.disabled = !hasSelection;
        els.selectAll.disabled = state.images.length === 0;
        updatePreview();
    }

    function updatePreview() {
        if (!state.selected.size) {
            els.filenamePreview.textContent = 'No files selected';
            return;
        }
        const sortedTags = Array.from(state.activeTags).sort((a, b) => a.localeCompare(b));
        const parts = [state.prefix.trim(), ...sortedTags, state.suffix.trim()].filter(Boolean);
        const previewName = `${parts.join('_') || 'untitled'}_000`; 
        els.filenamePreview.textContent = `${previewName}.ext`;
    }

    function renderImages(images) {
        els.imageGrid.innerHTML = '';
        if (!images.length) {
            els.noImages.classList.remove('hidden');
            return;
        }
        els.noImages.classList.add('hidden');
        const fragment = document.createDocumentFragment();
        images.forEach((image) => {
            const template = els.imageTemplate.content.cloneNode(true);
            const card = template.querySelector('.image-card');
            const img = template.querySelector('[data-thumbnail]');
            const name = template.querySelector('[data-filename]');
            card.dataset.path = image.path;
            card.setAttribute('aria-pressed', state.selected.has(image.path));
            card.addEventListener('click', () => toggleSelection(image.path));
            card.addEventListener('keydown', (event) => {
                if (event.key === 'Enter' || event.key === ' ') {
                    event.preventDefault();
                    toggleSelection(image.path);
                }
            });
            img.src = image.thumbnail;
            img.alt = `Thumbnail for ${image.name}`;
            name.textContent = image.name;
            fragment.appendChild(template);
        });
        els.imageGrid.appendChild(fragment);
        updateSelectionUI();
    }

    function renderTags(tags) {
        els.tagContainer.innerHTML = '';
        const fragment = document.createDocumentFragment();
        tags.forEach((tag) => {
            const template = els.tagTemplate.content.cloneNode(true);
            const pill = template.querySelector('.tag-pill');
            const label = template.querySelector('.tag-label');
            pill.dataset.tag = tag;
            pill.setAttribute('aria-pressed', state.activeTags.has(tag));
            label.textContent = tag;
            pill.addEventListener('click', () => toggleTag(tag));
            fragment.appendChild(template);
        });
        els.tagContainer.appendChild(fragment);
    }

    function toggleSelection(path) {
        if (!state.multiSelect) {
            state.selected.clear();
        }
        if (state.selected.has(path)) {
            state.selected.delete(path);
        } else {
            state.selected.add(path);
        }
        document.querySelectorAll('.image-card').forEach((card) => {
            const isSelected = state.selected.has(card.dataset.path);
            card.setAttribute('aria-pressed', isSelected);
        });
        updateSelectionUI();
    }

    function toggleTag(tag) {
        if (state.activeTags.has(tag)) {
            state.activeTags.delete(tag);
        } else {
            state.activeTags.add(tag);
        }
        renderTags(state.tags);
        updatePreview();
    }

    function selectAllImages() {
        state.images.forEach((img) => state.selected.add(img.path));
        renderImages(state.images);
    }

    function clearSelection() {
        state.selected.clear();
        renderImages(state.images);
    }

    async function loadDirectory(directory) {
        if (!directory) return;
        hideError();
        setLoading(true);
        try {
            const payload = await api.getImages(directory);
            state.directory = payload.directory;
            state.images = payload.images || [];
            state.selected.clear();
            els.currentDirectory.textContent = payload.directory || directory;
            state.folderBrowser.current = payload.directory;
            state.folderBrowser.selected = payload.directory;
            renderImages(state.images);
        } catch (error) {
            showError(error.message);
        } finally {
            setLoading(false);
        }
    }

    async function loadTags() {
        try {
            const payload = await api.getTags();
            state.tags = payload.tags || [];
            renderTags(state.tags);
        } catch (error) {
            showError(error.message);
        }
    }

    async function handleAddTag() {
        const newTag = els.newTagInput.value.trim();
        if (!newTag) return;
        try {
            await api.addTag(newTag);
            els.newTagInput.value = '';
            toggleAddTagInput(false);
            await loadTags();
        } catch (error) {
            showError(error.message);
        }
    }

    async function handleRename() {
        if (!state.selected.size) return;
        const payload = {
            images: Array.from(state.selected),
            tags: Array.from(state.activeTags),
            prefix: state.prefix,
            suffix: state.suffix,
        };
        try {
            setLoading(true);
            const result = await api.renameImages(payload);
            showRenameResult(result);
            await loadDirectory(state.directory);
        } catch (error) {
            showError(error.message);
        } finally {
            setLoading(false);
        }
    }

    function showRenameResult(result) {
        const successes = result.success_count ?? 0;
        const failures = result.error_count ?? 0;
        let message = `Renamed ${successes} file(s)`;
        if (failures) {
            message += `, ${failures} failed.`;
        }
        showError(message);
    }

    function toggleAddTagInput(forceVisibility) {
        const isVisible = typeof forceVisibility === 'boolean'
            ? forceVisibility
            : els.addTagInputContainer.classList.contains('hidden');
        els.addTagInputContainer.classList.toggle('hidden', !isVisible);
        els.addTagButton.setAttribute('aria-expanded', String(isVisible));
        if (isVisible) {
            els.newTagInput.focus();
        } else {
            els.newTagInput.value = '';
        }
    }

    function setPanelCollapsed(collapsed) {
        if (!els.taggingPanel || !els.togglePanelButton) return;
        els.taggingPanel.classList.toggle('is-collapsed', collapsed);
        els.togglePanelButton.setAttribute('aria-expanded', String(!collapsed));
        const label = els.togglePanelButton.querySelector('.toggle-text');
        if (label) {
            label.textContent = collapsed ? 'Expand panel' : 'Collapse panel';
        }
    }

    function bindEvents() {
        els.changeFolder.addEventListener('click', () => {
            openModal();
        });
        els.folderCancel.addEventListener('click', () => closeModal());
        els.folderSelect.addEventListener('click', () => {
            const path = state.folderBrowser.selected || els.folderInput.value.trim();
            if (!path) {
                showError('Select or enter a folder path first');
                return;
            }
            closeModal();
            loadDirectory(path);
        });
        els.folderModal.addEventListener('click', (event) => {
            if (event.target === els.folderModal) {
                closeModal();
            }
        });
        document.addEventListener('keydown', (event) => {
            if (event.key === 'Escape' && !els.folderModal.classList.contains('hidden')) {
                closeModal();
            }
        });
        if (els.folderUpButton) {
            els.folderUpButton.addEventListener('click', () => {
                if (state.folderBrowser.parent) {
                    loadFolderBrowser(state.folderBrowser.parent);
                }
            });
        }
        if (els.folderRefreshButton) {
            els.folderRefreshButton.addEventListener('click', () => {
                const target = state.folderBrowser.current || els.folderInput.value.trim();
                loadFolderBrowser(target);
            });
        }
        els.dismissError.addEventListener('click', hideError);
        els.multiSelectToggle.addEventListener('change', (event) => {
            state.multiSelect = event.target.checked;
            if (!state.multiSelect && state.selected.size > 1) {
                const first = state.selected.values().next().value;
                state.selected = new Set(first ? [first] : []);
                renderImages(state.images);
            }
        });
        els.selectAll.addEventListener('click', selectAllImages);
        els.clearSelection.addEventListener('click', clearSelection);
        els.prefixInput.addEventListener('input', (event) => {
            state.prefix = event.target.value;
            updatePreview();
        });
        els.suffixInput.addEventListener('input', (event) => {
            state.suffix = event.target.value;
            updatePreview();
        });
        els.folderInput.addEventListener('input', () => {
            state.folderBrowser.selected = '';
            highlightSelectedFolder();
        });
        els.addTagButton.addEventListener('click', () => toggleAddTagInput());
        els.cancelTagButton.addEventListener('click', () => toggleAddTagInput(false));
        els.saveTagButton.addEventListener('click', handleAddTag);
        els.newTagInput.addEventListener('keydown', (event) => {
            if (event.key === 'Enter') {
                event.preventDefault();
                handleAddTag();
            }
        });
        els.renameButton.addEventListener('click', handleRename);
        if (els.togglePanelButton) {
            els.togglePanelButton.addEventListener('click', () => {
                const collapsed = !els.taggingPanel.classList.contains('is-collapsed');
                setPanelCollapsed(collapsed);
            });
        }
    }

    async function init() {
        bindEvents();
        await loadTags();
        updateSelectionUI();
        setPanelCollapsed(false);
    }

    document.addEventListener('DOMContentLoaded', init);
})();
