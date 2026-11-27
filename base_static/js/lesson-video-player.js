(function () {
    'use strict';
    // One delegated handler works for every block, including restored markup.
    document.addEventListener('click', function (event) {
        const button = event.target.closest('button[data-video-source]');
        if (!button) return;
        const player = button.closest('[data-video-player]');
        if (!player) return;
        const frame = player.querySelector('.course-video-player__frame');
        const url = button.dataset.videoUrl;
        if (!frame || !url) return;
        if (frame.getAttribute('src') !== url) {
            // A fresh frame stops the previous provider and avoids retaining its state.
            const nextFrame = frame.cloneNode(false);
            nextFrame.title = frame.dataset.videoTitle + ' — ' + button.textContent.trim();
            nextFrame.src = url;
            frame.replaceWith(nextFrame);
        }
        player.querySelectorAll('button[data-video-source]').forEach(function (item) {
            const selected = item === button;
            item.classList.toggle('is-active', selected);
            item.setAttribute('aria-pressed', String(selected));
        });
    });
})();
