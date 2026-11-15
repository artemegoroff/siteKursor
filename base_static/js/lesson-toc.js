(function () {
    'use strict';

    const transliteration = {
        а: 'a', б: 'b', в: 'v', г: 'g', д: 'd', е: 'e', ё: 'yo',
        ж: 'zh', з: 'z', и: 'i', й: 'y', к: 'k', л: 'l', м: 'm',
        н: 'n', о: 'o', п: 'p', р: 'r', с: 's', т: 't', у: 'u',
        ф: 'f', х: 'kh', ц: 'ts', ч: 'ch', ш: 'sh', щ: 'shch',
        ъ: '', ы: 'y', ь: '', э: 'e', ю: 'yu', я: 'ya'
    };

    function slug(text) {
        return text.toLowerCase()
            .replace(/[а-яё]/g, letter => transliteration[letter])
            .normalize('NFKD').replace(/[\u0300-\u036f]/g, '')
            .replace(/[^a-z0-9]+/g, '-').replace(/^-+|-+$/g, '') || 'razdel';
    }

    function initialize() {
        const reading = document.querySelector('[data-lesson-reading]');
        if (!reading || reading.dataset.tocInitialized) return;
        reading.dataset.tocInitialized = 'true';
        const content = reading.querySelector('[data-lesson-content]');
        const toc = reading.querySelector('[data-lesson-toc]');
        if (!content || !toc) return;
        const desktop = window.matchMedia('(min-width: 1200px)');
        const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)');
        const details = toc.querySelector('details');
        const list = toc.querySelector('[data-toc-list]');
        const reserved = new Set(Array.from(document.querySelectorAll('[id]'), node => node.id));
        const entries = [];
        const entriesById = new Map();
        let lastSection = null;
        let activeEntry = null;
        let offset = 24;
        let scheduled = false;
        let userInteracted = false;

        function uniqueId(base) {
            let id = base;
            let suffix = 2;
            while (reserved.has(id)) id = base + '-' + suffix++;
            reserved.add(id);
            return id;
        }

        content.querySelectorAll('h2, h3').forEach(function (heading) {
            const title = heading.textContent.replace(/\s+/g, ' ').trim();
            if (!title || heading.closest('[hidden], [aria-hidden="true"], pre, code, template') || getComputedStyle(heading).display === 'none') return;
            if (!heading.id || document.getElementById(heading.id) !== heading) {
                heading.id = uniqueId(heading.id || slug(title));
            }
            if (!heading.hasAttribute('tabindex')) heading.tabIndex = -1;

            const previous = entries[entries.length - 1];
            const prose = heading.closest('.lesson-prose');
            // A block title may repeat the first heading inside its own text.
            if (previous && prose && prose.querySelector('h2, h3') === heading &&
                !previous.heading.closest('.lesson-prose') &&
                previous.heading.closest('.lesson-section') === heading.closest('.lesson-section') &&
                previous.title.toLocaleLowerCase() === title.toLocaleLowerCase()) {
                entriesById.set(heading.id, previous);
                return;
            }

            const item = document.createElement('li');
            const link = document.createElement('a');
            link.className = 'lesson-toc__link';
            link.href = '#' + encodeURIComponent(heading.id);
            link.textContent = title;
            item.append(link);
            if (heading.tagName === 'H3' && lastSection) {
                let children = lastSection.querySelector('ol');
                if (!children) {
                    children = document.createElement('ol');
                    children.className = 'lesson-toc__sublist';
                    lastSection.append(children);
                }
                children.append(item);
            } else {
                list.append(item);
                if (heading.tagName === 'H2') lastSection = item;
            }
            const entry = {heading: heading, link: link, title: title};
            entries.push(entry);
            entriesById.set(heading.id, entry);
        });

        const hasContents = entries.length >= 3;
        toc.hidden = !hasContents;
        reading.closest('.lesson-layout').classList.toggle('has-lesson-toc', hasContents);
        toc.querySelector('[data-toc-count]').textContent = String(entries.length);

        function headerOffset() {
            let height = 0;
            document.querySelectorAll('.clever-main-menu, [data-sticky-header]').forEach(function (header) {
                const position = getComputedStyle(header).position;
                const rect = header.getBoundingClientRect();
                if (header.closest('.sticky-wrapper')) {
                    // Reserve the future fixed menu even when clicking from the page top.
                    height = Math.max(height, rect.height);
                } else if ((position === 'fixed' || position === 'sticky') && rect.top <= 1 && rect.bottom > 0) {
                    height = Math.max(height, rect.bottom);
                }
            });
            const next = Math.ceil(height + 24);
            if (next !== offset) {
                offset = next;
                reading.style.setProperty('--lesson-anchor-offset', offset + 'px');
            }
        }

        function setActive(entry) {
            if (!entry || entry === activeEntry) return;
            if (activeEntry) {
                activeEntry.link.classList.remove('is-active');
                activeEntry.link.removeAttribute('aria-current');
            }
            activeEntry = entry;
            entry.link.classList.add('is-active');
            entry.link.setAttribute('aria-current', 'location');
            // Scroll the contents panel, never the document, for long outlines.
            if (hasContents && desktop.matches) {
                const panel = toc.getBoundingClientRect();
                const item = entry.link.getBoundingClientRect();
                if (panel.top < window.innerHeight && panel.bottom > 0) {
                    if (item.top < panel.top + 12) toc.scrollTop += item.top - panel.top - 12;
                    else if (item.bottom > panel.bottom - 12) toc.scrollTop += item.bottom - panel.bottom + 12;
                }
            }
        }

        function update() {
            scheduled = false;
            headerOffset();
            let current = entries[0];
            for (const entry of entries) {
                if (entry.heading.getBoundingClientRect().top <= offset + 32) current = entry;
                else break;
            }
            if (window.scrollY + window.innerHeight >= document.documentElement.scrollHeight - 4) {
                current = entries[entries.length - 1];
            }
            setActive(current);
        }

        function scheduleUpdate() {
            if (!scheduled) {
                scheduled = true;
                requestAnimationFrame(update);
            }
        }

        function hashTarget() {
            try {
                const id = decodeURIComponent(window.location.hash.slice(1));
                const target = document.getElementById(id);
                return target && content.contains(target) ? target : null;
            } catch (error) {
                return null; // Ignore malformed external fragment URLs.
            }
        }

        function goTo(target, smooth, focus) {
            headerOffset();
            if (focus) target.focus({preventScroll: true});
            window.scrollTo({
                top: Math.max(0, window.scrollY + target.getBoundingClientRect().top - offset - 8),
                behavior: smooth && !reducedMotion.matches ? 'smooth' : 'instant'
            });
            setActive(entriesById.get(target.id));
        }

        list.addEventListener('click', function (event) {
            if (event.defaultPrevented || event.button !== 0 || event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return;
            const link = event.target.closest('a.lesson-toc__link');
            if (!link) return;
            event.preventDefault();
            const id = decodeURIComponent(link.hash.slice(1));
            const target = document.getElementById(id);
            if (!target) return;
            if (!desktop.matches) details.open = false;
            if (window.location.hash !== link.hash) history.pushState(null, '', link.hash);
            goTo(target, true, true);
        });

        function applyViewport() {
            details.open = desktop.matches;
            scheduleUpdate();
        }
        desktop.addEventListener('change', applyViewport);
        window.addEventListener('scroll', scheduleUpdate, {passive: true});
        window.addEventListener('resize', scheduleUpdate);
        window.addEventListener('hashchange', function () {
            const target = hashTarget();
            if (target) goTo(target, false, true);
        });
        ['wheel', 'touchstart', 'pointerdown', 'keydown'].forEach(function (name) {
            window.addEventListener(name, function () { userInteracted = true; }, {passive: true});
        });
        applyViewport();
        requestAnimationFrame(function () {
            const target = hashTarget();
            if (target) goTo(target, false, false);
        });
        window.addEventListener('load', function () {
            const target = hashTarget();
            if (target && !userInteracted) goTo(target, false, false);
            scheduleUpdate();
        }, {once: true});
    }

    if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', initialize);
    else initialize();
})();
