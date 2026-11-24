(function () {
    'use strict';
    const menu = document.querySelector('[data-files-menu]');
    const desktop = window.matchMedia('(min-width: 1025px)');
    if (menu) {
        function syncMenu() { menu.open = desktop.matches; }
        syncMenu();
        desktop.addEventListener('change', syncMenu);
        menu.addEventListener('click', function (event) {
            if (event.target.closest('a') && !desktop.matches) menu.open = false;
        });
        document.addEventListener('keydown', function (event) {
            if (event.key === 'Escape' && menu.open && !desktop.matches) {
                menu.open = false;
                menu.querySelector('summary').focus();
            }
        });
    }
    const demo = document.querySelector('[data-files-demo]');
    if (!demo) return;
    const input = demo.querySelector('[data-demo-name]');
    const code = demo.querySelector('[data-demo-code]');
    const fileName = demo.querySelector('[data-demo-filename]');
    const status = demo.querySelector('[data-demo-status]');
    const files = demo.querySelectorAll('[data-demo-file]');
    const download = demo.querySelector('[data-demo-download]');
    let active = 'main';
    function profile() {
        return {name: input.value.trim() || 'Алексей', skills: ['Python', 'Функции']};
    }
    function renderFile() {
        const content = {
            main: 'from storage import save_profile\n\nprofile = ' + JSON.stringify(profile(), null, 4) + '\n\nsave_profile(profile)',
            storage: 'import json\nfrom pathlib import Path\n\ndef save_profile(profile):\n    path = Path("data/profile.json")\n    path.parent.mkdir(exist_ok=True)\n    path.write_text(\n        json.dumps(profile, ensure_ascii=False, indent=2),\n        encoding="utf-8"\n    )',
            json: JSON.stringify(profile(), null, 2)
        };
        fileName.textContent = {main: 'main.py', storage: 'storage.py', json: 'data/profile.json'}[active];
        code.textContent = content[active];
        files.forEach(function (button) { button.setAttribute('aria-pressed', String(button.dataset.demoFile === active)); });
    }
    files.forEach(function (button) {
        button.disabled = false;
        button.addEventListener('click', function () { active = button.dataset.demoFile; renderFile(); });
    });
    input.addEventListener('input', function () {
        renderFile();
        status.textContent = 'Пример обновлён. Файл будет содержать введённое имя.';
    });
    download.disabled = false;
    download.addEventListener('click', function () {
        const blob = new Blob([JSON.stringify(profile(), null, 2)], {type: 'application/json;charset=utf-8'});
        const url = URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.download = 'profile.json';
        document.body.appendChild(link);
        link.click();
        link.remove();
        window.setTimeout(function () { URL.revokeObjectURL(url); }, 1000);
        active = 'json';
        renderFile();
        status.textContent = 'Файл profile.json подготовлен для скачивания.';
    });
    renderFile();
})();
