document.addEventListener('DOMContentLoaded', function () {
    const settings = document.querySelector('[data-table-settings]');
    if (!settings) return;
    function updateRow(row) {
        const visible = row.querySelector('[name="visible_fields"]');
        const editable = row.querySelector('[name="editable_fields"]');
        if (!editable) return;
        editable.disabled = !visible.checked;
        if (editable.disabled) editable.checked = false;
    }
    settings.querySelectorAll('[data-column-option]').forEach(function (row) {
        updateRow(row);
        row.querySelector('[name="visible_fields"]').addEventListener('change', function () { updateRow(row); });
    });
    let dirty = false;
    const list = document.getElementById('changelist-form');
    if (list) list.addEventListener('input', function (event) {
        if (event.target.name && event.target.name.startsWith('form-')) dirty = true;
    });
    settings.addEventListener('submit', function (event) {
        if (dirty && !window.confirm('В строках есть несохранённые изменения. Сменить настройки таблицы и отменить эти изменения?')) event.preventDefault();
    });
});
