document.addEventListener('DOMContentLoaded', function () {
    const iframe = document.getElementById('lesson-video-frame');
    const switchRoot = document.getElementById('video-source-switch');
    const warningBox = document.getElementById('video-source-warning');
    const prevBtn = document.getElementById('playlist-prev');
    const nextBtn = document.getElementById('playlist-next');
    const playlistViewport = document.getElementById('playlist-viewport');

    if (iframe && switchRoot) {
        const sourceButtons = switchRoot.querySelectorAll('[data-source]');
        const dataNode = document.getElementById('video-sources-data');
        const sources = dataNode ? JSON.parse(dataNode.textContent) : {};
        const STORAGE_KEY = 'preferred_video_platform';

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
                const sourceName = btn.dataset.source;
                setPlayerSource(sourceName, false);
            });
        });

        const savedSource = localStorage.getItem(STORAGE_KEY);
        const initialSource = savedSource || getFirstAvailableSource();

        if (initialSource && sources[initialSource]) {
            setPlayerSource(initialSource, false);
        } else {
            const fallbackSource = getFirstAvailableSource();
            if (fallbackSource) {
                setPlayerSource(fallbackSource, Boolean(savedSource));
            }
        }
    }

    if (playlistViewport && prevBtn && nextBtn) {
        const scrollAmount = 320;

        prevBtn.addEventListener('click', function () {
            playlistViewport.scrollBy({ left: -scrollAmount, behavior: 'smooth' });
        });

        nextBtn.addEventListener('click', function () {
            playlistViewport.scrollBy({ left: scrollAmount, behavior: 'smooth' });
        });
    }
});