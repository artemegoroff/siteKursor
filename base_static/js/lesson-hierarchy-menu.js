(function () {
    const menu = document.getElementById('mySidenav');
    const overlay = document.getElementById('sideMenuOverlay');
    const toggle = document.querySelector('[data-menu-open]');

    if (!menu || !overlay || !toggle) {
        return;
    }

    const closeButton = menu.querySelector('[data-menu-close]');
    let previousFocus = null;

    function openMenu() {
        previousFocus = document.activeElement;

        menu.inert = false;
        menu.classList.add('is-open');
        overlay.classList.add('is-open');

        menu.setAttribute('aria-hidden', 'false');
        toggle.setAttribute('aria-expanded', 'true');

        document.body.classList.add('side-menu-open');

        closeButton.focus();

        const current = menu.querySelector(
            '[aria-current="page"]'
        );

        if (current) {
            current.scrollIntoView({
                block: 'nearest'
            });
        }
    }

    function closeMenu() {
        if (!menu.classList.contains('is-open')) {
            return;
        }

        (previousFocus || toggle).focus();

        menu.classList.remove('is-open');
        overlay.classList.remove('is-open');

        menu.setAttribute('aria-hidden', 'true');
        menu.inert = true;

        toggle.setAttribute('aria-expanded', 'false');
        document.body.classList.remove('side-menu-open');
    }

    toggle.addEventListener('click', openMenu);
    closeButton.addEventListener('click', closeMenu);
    overlay.addEventListener('click', closeMenu);

    menu.querySelectorAll('[data-lesson-link]').forEach(
        function (link) {
            link.addEventListener('click', closeMenu);
        }
    );

    document.addEventListener('keydown', function (event) {
        if (!menu.classList.contains('is-open')) {
            return;
        }

        if (event.key === 'Escape') {
            event.preventDefault();
            closeMenu();
        }

        if (event.key !== 'Tab') {
            return;
        }

        const elements = Array.from(
            menu.querySelectorAll(
                'a[href], button:not([disabled]), ' +
                'summary, [tabindex="0"]'
            )
        ).filter(function (element) {
            return element.getClientRects().length > 0;
        });

        const first = elements[0];
        const last = elements[elements.length - 1];

        if (
            event.shiftKey &&
            document.activeElement === first
        ) {
            event.preventDefault();
            last.focus();

        } else if (
            !event.shiftKey &&
            document.activeElement === last
        ) {
            event.preventDefault();
            first.focus();
        }
    });
})();