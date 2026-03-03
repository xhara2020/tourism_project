document.addEventListener('DOMContentLoaded', function () {
  const menu = document.getElementById('hist-periods-menu');
  const toggle = document.getElementById('histPeriodsDropdown');
  const parent = toggle ? toggle.closest('.dropdown') : null;
  if (!menu || !toggle || !parent) return;

  const fallback = [
    {slug: 'prehistoric-period', name: 'Prehistoric Period'},
    {slug: 'chalcolithic-bronze-iron-ages', name: 'Chalcolithic, Bronze and Iron Ages'},
    {slug: 'hellenic-hellenistic-periods', name: 'Hellenic and Hellenistic Periods'},
    {slug: 'roman-period', name: 'Roman Period'},
    {slug: 'byzantine-period', name: 'Byzantine Period'},
    {slug: 'medieval-pre-ottoman', name: 'Medieval Period (Pre-Ottoman)'},
    {slug: 'ottoman-period', name: 'Ottoman Period'},
    {slug: 'modern-period', name: 'Modern Period'}
  ];

  function populate(list) {
    menu.innerHTML = '';
    list.forEach(p => {
      const a = document.createElement('a');
      a.className = 'dropdown-item';
      a.href = `/periods/${encodeURIComponent(p.slug)}/`;
      a.textContent = p.name || '';
      menu.appendChild(a);
    });
  }

  function setupDropdownInteractions() {
    let isOpen = false;
    const openMenu = () => {
      if (isOpen) return;
      isOpen = true;
      menu.classList.add('show');
      toggle.classList.add('show');
      toggle.setAttribute('aria-expanded', 'true');
    };
    const closeMenu = () => {
      if (!isOpen) return;
      isOpen = false;
      menu.classList.remove('show');
      toggle.classList.remove('show');
      toggle.setAttribute('aria-expanded', 'false');
    };
    const toggleMenu = function (evt) {
      evt.preventDefault();
      evt.stopPropagation();
      isOpen ? closeMenu() : openMenu();
    };

    toggle.addEventListener('click', toggleMenu);

    // Desktop hover support
    if (window.matchMedia && window.matchMedia('(hover: hover) and (pointer: fine)').matches) {
      parent.addEventListener('mouseenter', openMenu);
      parent.addEventListener('mouseleave', closeMenu);
    }

    // Close when clicking outside
    document.addEventListener('click', function (e) {
      if (!parent.contains(e.target)) closeMenu();
    });

    // Close when selecting an item
    menu.addEventListener('click', function (e) {
      if (e.target && e.target.classList && e.target.classList.contains('dropdown-item')) closeMenu();
    });

    // Close on ESC key
    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape') closeMenu();
    });
  }

  function initMenu() {
    setupDropdownInteractions();
  }

  fetch('/api/periods/').then(r => r.ok ? r.json() : null).then(periods => {
    if (periods && periods.length) populate(periods);
    else populate(fallback);
  }).catch(() => populate(fallback)).finally(initMenu);
});
