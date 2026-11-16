(function () {
    'use strict';
    const menu = document.querySelector('[data-landing-menu]');
    const desktop = window.matchMedia('(min-width: 901px)');
    if (menu) {
        function updateMenu() { menu.open = desktop.matches; }
        updateMenu();
        desktop.addEventListener('change', updateMenu);
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

    const form = document.querySelector('[data-demo-form]');
    if (form) {
        const input = form.querySelector('[data-demo-name]');
        const code = document.querySelector('[data-demo-code]');
        const output = document.querySelector('[data-demo-output]');
        const run = form.querySelector('[data-demo-run]');
        const name = function () { return input.value.trim().replace(/[\r\n]/g, ' ') || 'Мир'; };
        function updateCode() {
            code.textContent = 'name = ' + JSON.stringify(name()) + '\nprint(f"Привет, {name}!")';
        }
        input.addEventListener('input', updateCode);
        form.addEventListener('submit', function (event) {
            event.preventDefault();
            updateCode();
            // This bounded example illustrates two fixed Python statements.
            // User input is never evaluated as JavaScript or Python.
            output.textContent = 'Привет, ' + name() + '!';
        });
        run.disabled = false;
        updateCode();
    }

    const mobileCta = document.querySelector('[data-mobile-cta]');
    if (mobileCta && 'IntersectionObserver' in window) {
        const targets = document.querySelectorAll('.hero-primary-cta, .signup-cta');
        const visible = new Map();
        const mobile = window.matchMedia('(max-width: 700px)');
        function updateCta() {
            mobileCta.hidden = !mobile.matches || window.scrollY < 200 || Array.from(visible.values()).some(Boolean);
        }
        const observer = new IntersectionObserver(function (entries) {
            entries.forEach(function (entry) { visible.set(entry.target, entry.isIntersecting); });
            updateCta();
        });
        targets.forEach(function (target) { observer.observe(target); });
        mobile.addEventListener('change', updateCta);
        window.addEventListener('scroll', updateCta, {passive: true});
    }
})();
