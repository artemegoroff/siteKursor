(function () {
    'use strict';
    const menu = document.querySelector('[data-dj-menu]');
    const wide = window.matchMedia('(min-width: 1025px)');
    if (menu) {
        function syncMenu() { menu.open = wide.matches; }
        syncMenu();
        wide.addEventListener('change', syncMenu);
        menu.addEventListener('click', function (event) {
            if (event.target.closest('a') && !wide.matches) menu.open = false;
        });
        document.addEventListener('keydown', function (event) {
            if (event.key === 'Escape' && menu.open && !wide.matches) {
                menu.open = false;
                menu.querySelector('summary').focus();
            }
        });
    }
    const lab = document.querySelector('[data-dj-lab]');
    if (!lab) return;
    // Fixed examples only: no Python execution, network requests or saved progress.
    const examples = {
        hello: {path: '/hello/', view: 'hello', text: 'Привет, Django!'},
        about: {path: '/about/', view: 'about', text: 'Этот сайт написан на Python.'}
    };
    const buttons = lab.querySelectorAll('[data-dj-route]');
    function select(key) {
        const example = examples[key];
        if (!example) return;
        buttons.forEach(function (button) {
            button.setAttribute('aria-pressed', String(button.dataset.djRoute === key));
        });
        lab.querySelector('[data-dj-code]').textContent = 'from django.http import HttpResponse\n\ndef ' + example.view + '(request):\n    return HttpResponse("' + example.text + '")';
        lab.querySelector('[data-dj-request]').textContent = 'GET ' + example.path + ' · 200 OK';
        lab.querySelector('[data-dj-response]').textContent = example.text;
    }
    buttons.forEach(function (button) {
        button.disabled = false;
        button.addEventListener('click', function () { select(button.dataset.djRoute); });
    });
    select('hello');
})();
