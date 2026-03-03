document.addEventListener('DOMContentLoaded', function () {
  const listEl = document.getElementById('offers-list');
  if (!listEl) return;

  function renderOffers(items) {
    listEl.innerHTML = '';
    items.forEach(o => {
      const li = document.createElement('li');
      li.className = 'offer-item';
      const a = document.createElement('a');
      a.href = `/offers/${encodeURIComponent(o.slug)}/`;
      a.textContent = o.title;
      const p = document.createElement('div');
      p.className = 'small text-muted';
      p.textContent = o.summary || '';
      li.appendChild(a);
      li.appendChild(p);
      listEl.appendChild(li);
    });
  }

  // Try fetching offers JSON; fallback to static example list
  fetch('/offers/json/').then(r => r.ok ? r.json() : null).then(data => {
    if (data && data.offers) renderOffers(data.offers);
    else renderOffers([
      {slug: 'summer-beach-package', title: 'Summer Beach Package', summary: '4-night seaside stay + boat tour.'},
      {slug: 'heritage-city-break', title: 'Heritage City Break', summary: '2-night guided city tour and museum passes.'},
      {slug: 'adventure-mountains', title: 'Adventure in the Mountains', summary: '3-day hiking and local food experience.'}
    ]);
  }).catch(() => {
    renderOffers([
      {slug: 'summer-beach-package', title: 'Summer Beach Package', summary: '4-night seaside stay + boat tour.'},
      {slug: 'heritage-city-break', title: 'Heritage City Break', summary: '2-night guided city tour and museum passes.'},
      {slug: 'adventure-mountains', title: 'Adventure in the Mountains', summary: '3-day hiking and local food experience.'}
    ]);
  });
});
