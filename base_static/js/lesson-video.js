document.addEventListener('DOMContentLoaded', function () {
    const iframe = document.getElementById('lesson-video-frame');
    const switchRoot = document.getElementById('video-source-switch');
    const warningBox = document.getElementById('video-source-warning');
    const prevBtn = document.getElementById('playlist-prev');
    const nextBtn = document.getElementById('playlist-next');
    const playlistViewport = document.getElementById('playlist-viewport');

    const STORAGE_KEY = 'preferred_video_platform';

    /* =========================
       VIDEO SOURCE SWITCH
    ========================= */
    if (iframe && switchRoot) {
        const sourceButtons = switchRoot.querySelectorAll('[data-source]');
        const dataNode = document.getElementById('video-sources-data');
        const sources = dataNode ? JSON.parse(dataNode.textContent) : {};

        function getFirstAvailableSource() {
            if (sources.rutube) return 'rutube';
            if (sources.youtube) return 'youtube';
            return null;
        }

        function updateButtons(activeSource) {
            sourceButtons.forEach((btn) => {
                const sourceName = btn.dataset.source;
                const isAvailable = Boolean(sources[sourceName]);

                btn.disabled = !isAvailable;
                btn.classList.toggle('is-active', sourceName === activeSource);
            });
        }

        function setPlayerSource(sourceName, showWarning = false) {
            const sourceData = sources[sourceName];
            if (!sourceData) return false;

            iframe.src = sourceData.embed_url;
            updateButtons(sourceName);
            localStorage.setItem(STORAGE_KEY, sourceName);

            if (warningBox) {
                warningBox.style.display = showWarning ? 'block' : 'none';
            }

            return true;
        }

        sourceButtons.forEach((btn) => {
            btn.addEventListener('click', function () {
                setPlayerSource(btn.dataset.source, false);
            });
        });

        const savedSource = localStorage.getItem(STORAGE_KEY);
        const preferredSource = savedSource || 'rutube';

        if (preferredSource && sources[preferredSource]) {
            setPlayerSource(preferredSource, false);
        } else {
            const fallbackSource = getFirstAvailableSource();
            if (fallbackSource) {
                setPlayerSource(fallbackSource, Boolean(savedSource));
            }
        }
    }

    /* =========================
       PLAYLIST BUTTONS
    ========================= */
    if (playlistViewport && prevBtn && nextBtn) {
        const scrollAmount = 320;

        prevBtn.addEventListener('click', function () {
            playlistViewport.scrollBy({
                left: -scrollAmount,
                behavior: 'smooth'
            });
        });

        nextBtn.addEventListener('click', function () {
            playlistViewport.scrollBy({
                left: scrollAmount,
                behavior: 'smooth'
            });
        });
    }

    /* =========================
       CENTER CURRENT VIDEO
    ========================= */
    function centerCurrentVideo() {
        const viewport = document.getElementById('playlist-viewport');
        const current = document.querySelector('.course-video-player__item--current');

        if (!viewport || !current) return;

        // Сначала сбрасываем случайно восстановленный браузером горизонтальный скролл
        viewport.scrollLeft = 0;

        const viewportRect = viewport.getBoundingClientRect();
        const currentRect = current.getBoundingClientRect();

        const currentCenterInViewportCoords =
            (currentRect.left - viewportRect.left) + (currentRect.width / 2);

        let targetLeft =
            currentCenterInViewportCoords - (viewport.clientWidth / 2);

        // targetLeft пока относительно текущего положения viewport,
        // поэтому добавляем текущий scrollLeft
        targetLeft += viewport.scrollLeft;

        const maxScrollLeft = Math.max(0, viewport.scrollWidth - viewport.clientWidth);

        if (targetLeft < 0) targetLeft = 0;
        if (targetLeft > maxScrollLeft) targetLeft = maxScrollLeft;

        viewport.scrollTo({
            left: targetLeft,
            behavior: 'auto'
        });
    }

    function centerCurrentVideoStable() {
        centerCurrentVideo();

        // повторно после layout
        requestAnimationFrame(() => {
            centerCurrentVideo();
        });

        setTimeout(() => {
            centerCurrentVideo();
        }, 120);

        setTimeout(() => {
            centerCurrentVideo();
        }, 300);
    }

    // После DOM
    centerCurrentVideoStable();

    // После полной загрузки страницы
    window.addEventListener('load', function () {
        centerCurrentVideoStable();
    });

    // После загрузки миниатюр
    const playlistImages = document.querySelectorAll('#playlist-viewport img');
    playlistImages.forEach((img) => {
        if (!img.complete) {
            img.addEventListener('load', centerCurrentVideoStable, { once: true });
            img.addEventListener('error', centerCurrentVideoStable, { once: true });
        }
    });

    // При ресайзе окна
    window.addEventListener('resize', function () {
        centerCurrentVideoStable();
    });
});