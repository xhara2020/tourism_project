document.addEventListener('DOMContentLoaded', function () {
  const btn = document.getElementById('map-fullscreen-toggle');
  const mapEl = document.getElementById('map');
  if (!btn || !mapEl) return;

  function enterFullscreen() {
    mapEl.classList.add('map-fullscreen');
    document.documentElement.style.overflow = 'hidden';
    if (window.turizmiMap && typeof window.turizmiMap.updateSize === 'function') {
      setTimeout(() => window.turizmiMap.updateSize(), 250);
    }
    btn.textContent = 'Exit map fullscreen';
  }

  function exitFullscreen() {
    mapEl.classList.remove('map-fullscreen');
    document.documentElement.style.overflow = '';
    if (window.turizmiMap && typeof window.turizmiMap.updateSize === 'function') {
      setTimeout(() => window.turizmiMap.updateSize(), 250);
    }
    btn.textContent = 'Open map fullscreen';
  }

  function toggleFullscreen(e) {
    e.preventDefault();
    if (mapEl.classList.contains('map-fullscreen')) exitFullscreen(); else enterFullscreen();
  }

  btn.addEventListener('click', toggleFullscreen);

  // Exit on ESC
  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape' && mapEl.classList.contains('map-fullscreen')) exitFullscreen();
  });
});
