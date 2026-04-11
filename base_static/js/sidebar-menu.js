(function () {
    const menu = document.getElementById('mySidenav');
    const overlay = document.getElementById('sideMenuOverlay');

    if (!menu || !overlay) {
        return;
    }

    function openNav() {
        menu.classList.add('is-open');
        overlay.classList.add('is-open');
        menu.setAttribute('aria-hidden', 'false');
        document.body.classList.add('side-menu-open');
    }

    function closeNav() {
        menu.classList.remove('is-open');
        overlay.classList.remove('is-open');
        menu.setAttribute('aria-hidden', 'true');
        document.body.classList.remove('side-menu-open');
    }

    function handleEscape(event) {
        if (event.key === 'Escape') {
            closeNav();
        }
    }

    overlay.addEventListener('click', closeNav);
    document.addEventListener('keydown', handleEscape);

    const links = menu.querySelectorAll('.sidenav__link');
    links.forEach((link) => {
        link.addEventListener('click', closeNav);
    });

    window.openNav = openNav;
    window.closeNav = closeNav;
})();