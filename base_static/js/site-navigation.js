(function () {
    'use strict';
    const header = document.querySelector('[data-site-nav]');
    if (!header) return;
    const mobile = header.querySelector('[data-nav-mobile]');
    const groups = Array.from(header.querySelectorAll('[data-nav-group]'));
    const desktop = window.matchMedia('(min-width: 801px)');
    function closeGroups() { groups.forEach(function (group) { group.open = false; }); }
    function syncViewport() { closeGroups(); mobile.open = desktop.matches; }
    syncViewport();
    desktop.addEventListener('change', syncViewport);
    groups.forEach(function (group) {
        group.addEventListener('toggle', function () {
            if (group.open) groups.forEach(function (other) { if (other !== group) other.open = false; });
        });
    });
    header.addEventListener('click', function (event) {
        if (!event.target.closest('a')) return;
        closeGroups();
        if (!desktop.matches) mobile.open = false;
    });
    document.addEventListener('click', function (event) {
        if (header.contains(event.target)) return;
        closeGroups();
        if (!desktop.matches) mobile.open = false;
    });
    document.addEventListener('keydown', function (event) {
        if (event.key !== 'Escape') return;
        const openGroup = groups.find(function (group) { return group.open; });
        if (openGroup) {
            openGroup.open = false;
            openGroup.querySelector('summary').focus();
        } else if (!desktop.matches && mobile.open) {
            mobile.open = false;
            mobile.querySelector('summary').focus();
        }
    });
    // Avoid leaving a desktop dropdown behind when keyboard focus moves on.
    header.addEventListener('focusout', function () {
        window.setTimeout(function () {
            if (!header.contains(document.activeElement)) closeGroups();
        }, 0);
    });
    header.querySelectorAll('nav a').forEach(function (link) {
        if (link.origin === location.origin && !link.hash && link.pathname === location.pathname) {
            link.setAttribute('aria-current', 'page');
            const group = link.closest('[data-nav-group]');
            if (group) group.classList.add('is-current');
        }
    });
})();
