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

    function openModal() {
        els.folderModal.classList.remove('hidden');
        els.folderInput.focus();
    }

    function closeModal() {
        els.folderModal.classList.add('hidden');
        els.folderInput.value = '';
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

    function bindEvents() {
        els.changeFolder.addEventListener('click', () => {
            openModal();
        });
        els.folderCancel.addEventListener('click', () => closeModal());
        els.folderSelect.addEventListener('click', () => {
            const path = els.folderInput.value.trim();
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
    }

    async function init() {
        bindEvents();
        await loadTags();
        updateSelectionUI();
    }

    document.addEventListener('DOMContentLoaded', init);
})();
