(function () {
    'use strict';

    const fieldsByKind = {
        text: ['content'],
        video: ['youtube_id', 'rutube_id'],
        practice: ['practice_url']
    };
    const typeFields = ['content', 'youtube_id', 'rutube_id', 'practice_url'];
    const callbackOptions = [
        'setup', 'init_instance_callback', 'file_picker_callback',
        'images_upload_handler', 'paste_postprocess', 'paste_preprocess',
        'urlconverter_callback', 'media_url_resolver'
    ];

    function initialize(group) {
        const fieldset = group.querySelector('fieldset.sortable');
        if (!fieldset || group.dataset.blocksInitialized) return;
        group.dataset.blocksInitialized = 'true';
        const pendingEditors = new Map();
        const status = group.querySelector('.lesson-blocks-status');
        const prefix = group.id.replace(/-group$/, '');
        const form = group.closest('form');

        function rows() {
            return Array.from(group.querySelectorAll('[data-lesson-block]:not(.empty-form)'));
        }

        function field(row, name) {
            return row.querySelector('[name$="-' + name + '"]');
        }

        function isDeleted(row) {
            const checkbox = field(row, 'DELETE');
            return checkbox && checkbox.checked;
        }

        function hasContent(row) {
            const id = field(row, 'id');
            return Boolean(id && id.value) || ['kind', 'title', ...typeFields].some(function (name) {
                const input = field(row, name);
                return input && input.value.trim();
            });
        }

        function refresh(writeOrder) {
            const all = rows();
            const active = all.filter(function (row) { return !isDeleted(row); });
            let order = 0;
            all.forEach(function (row) {
                const kind = field(row, 'kind');
                if (!kind) return; // Read-only inlines have no controls.
                // Sortable2 handles these rows too, including newly added ones.
                // Initialization runs after Django has created unsaved-row delete links.
                row.classList.add('has_original');
                const shownFields = fieldsByKind[kind.value] || [];
                typeFields.forEach(function (name) {
                    const input = field(row, name);
                    const container = input && input.closest('.form-row');
                    if (!container) return;
                    const visible = shownFields.includes(name) || Boolean(container.querySelector('.errorlist'));
                    container.hidden = !visible;
                    container.setAttribute('aria-hidden', String(!visible));
                    if (name === 'practice_url') {
                        input.type = kind.value === 'practice' ? 'url' : 'text';
                    }
                });
                row.classList.toggle('is-deleted', Boolean(isDeleted(row)));
                const position = active.indexOf(row);
                const title = field(row, 'title');
                const typeLabel = kind.value ? kind.options[kind.selectedIndex].text : 'Новый блок';
                row.querySelector('.inline_label').textContent =
                    'Блок ' + (position >= 0 ? position + 1 : '—') + ' · ' + typeLabel +
                    (title && title.value.trim() ? ' — ' + title.value.trim() : '');
                const up = row.querySelector('[data-block-move="up"]');
                const down = row.querySelector('[data-block-move="down"]');
                if (up) up.disabled = position <= 0;
                if (down) down.disabled = position < 0 || position === active.length - 1;
                if (writeOrder && !isDeleted(row)) {
                    const orderInput = field(row, 'sort_order');
                    // A completely blank extra form must stay unchanged and optional.
                    if (orderInput) orderInput.value = hasContent(row) ? String(++order) : '0';
                }
            });
        }

        function suspendEditors(row) {
            if (!window.tinymce) return;
            row.querySelectorAll('textarea.tinymce').forEach(function (area) {
                const editor = window.tinymce.get(area.id);
                if (!editor || !editor.initialized || pendingEditors.has(area)) return;
                const config = JSON.parse(area.dataset.mceConf);
                delete config.selector;
                callbackOptions.forEach(function (name) {
                    const callback = editor.options.get(name);
                    if (typeof callback === 'function') config[name] = callback;
                });
                const container = area.closest('.form-row');
                const minHeight = container.style.minHeight;
                container.style.minHeight = container.getBoundingClientRect().height + 'px';
                editor.save();
                editor.remove();
                pendingEditors.set(area, {config: config, container: container, minHeight: minHeight});
            });
        }

        function restoreEditors() {
            pendingEditors.forEach(function (saved, area) {
                pendingEditors.delete(area);
                if (!area.isConnected) return;
                // Django may have renumbered the IDs after removing an unsaved row.
                const config = Object.assign({}, saved.config, {target: area});
                window.tinymce.init(config).then(function () {
                    saved.container.style.minHeight = saved.minHeight;
                }).catch(function () {
                    saved.container.style.minHeight = saved.minHeight;
                    area.style.display = 'block';
                    status.textContent = 'Редактор не загрузился. Текст сохранён в поле; обновите редактор после сохранения урока.';
                });
            });
        }

        function afterMove() {
            requestAnimationFrame(function () {
                refresh(true);
                restoreEditors();
                status.textContent = 'Порядок изменён. Сохраните урок, чтобы применить изменения.';
            });
        }

        fieldset.addEventListener('choose', function (event) {
            if (event.item && event.item.matches('[data-lesson-block]')) suspendEditors(event.item);
        });
        fieldset.addEventListener('unchoose', function () {
            requestAnimationFrame(restoreEditors);
        });
        fieldset.addEventListener('end', afterMove);

        // Header buttons and deletion controls must not initiate a drag.
        ['mousedown', 'touchstart', 'pointerdown'].forEach(function (eventName) {
            group.addEventListener(eventName, function (event) {
                if (event.target.closest('h3 button, h3 input, h3 label, h3 a')) {
                    event.stopPropagation();
                }
            }, true);
        });

        group.addEventListener('click', function (event) {
            const button = event.target.closest('[data-block-move]');
            if (!button) return;
            const row = button.closest('[data-lesson-block]');
            const active = rows().filter(function (item) { return !isDeleted(item); });
            const index = active.indexOf(row);
            const direction = button.dataset.blockMove;
            const target = active[index + (direction === 'up' ? -1 : 1)];
            if (!target) return;
            suspendEditors(row);
            if (direction === 'up') target.before(row);
            else target.after(row);
            refresh(true);
            restoreEditors();
            const focusTarget = button.disabled
                ? row.querySelector('[data-block-move]:not(:disabled)') : button;
            if (focusTarget) focusTarget.focus();
            status.textContent = 'Блок перемещён. Сохраните урок, чтобы применить изменения.';
        });

        group.addEventListener('change', function () { refresh(false); });
        group.addEventListener('input', function (event) {
            if (event.target.name && event.target.name.endsWith('-title')) refresh(false);
        });
        document.addEventListener('formset:added', function (event) {
            if (event.detail.formsetName === prefix) refresh(true);
        });
        document.addEventListener('formset:removed', function (event) {
            if (event.detail.formsetName === prefix) afterMove();
        });
        document.addEventListener('click', function (event) {
            const link = event.target.closest('.inline-deletelink');
            if (link && group.contains(link)) {
                // Django reindexes subsequent unsaved rows, including textarea IDs.
                rows().forEach(suspendEditors);
                requestAnimationFrame(function () { refresh(true); restoreEditors(); });
            }
        }, true);
        form.addEventListener('submit', function () {
            if (window.tinymce) window.tinymce.triggerSave();
            refresh(true);
        });
        refresh(false);
    }

    function ready() {
        // Let Django finish wiring add/remove links before marking extra rows sortable.
        setTimeout(function () {
            document.querySelectorAll('[data-lesson-blocks]').forEach(initialize);
        }, 0);
    }
    if (document.readyState === 'complete') ready();
    else window.addEventListener('load', ready);
})();
