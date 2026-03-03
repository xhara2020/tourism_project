// Minimal OpenLayers map loader that fetches points from API and plots them
document.addEventListener('DOMContentLoaded', function () {
  // Populate the periods dropdown on every page (map may or may not exist).
  // Map initialization is conditional and will only run when `#map` exists.

  // Only initialize the OpenLayers map and controls when the map container exists
  if (document.getElementById('map')) {
    // Base layers: OpenStreetMap and Esri World Imagery (satellite)
    const osmLayer = new ol.layer.Tile({
      source: new ol.source.OSM(),
      visible: true,
      title: 'OSM'
    });

    const satelliteLayer = new ol.layer.Tile({
      source: new ol.source.XYZ({
        url: 'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
        attributions: 'Tiles © Esri'
      }),
      visible: false,
      title: 'Satellite'
    });

    const map = new ol.Map({
      target: 'map',
      layers: [osmLayer, satelliteLayer],
      view: new ol.View({
        center: ol.proj.fromLonLat([19.817, 41.327]),
        zoom: 7
      })
    });
    // expose map globally so other scripts can call updateSize() when container changes
    try { window.turizmiMap = map; } catch (err) {}

    // Simple layer switcher control (OSM / Satellite)
    const layerSwitcherEl = document.createElement('div');
  layerSwitcherEl.className = 'ol-layer-switcher';
  layerSwitcherEl.style.cssText = 'position: absolute; top: 10px; right: 10px; background: rgba(255,255,255,0.9); padding:6px; border-radius:4px; box-shadow:0 1px 4px rgba(0,0,0,0.3); z-index:1000;';

  const osmBtn = document.createElement('button');
  osmBtn.innerText = 'OpenStreetMap';
  osmBtn.style.marginRight = '6px';
  osmBtn.className = 'active';

  const satBtn = document.createElement('button');
  satBtn.innerText = 'Satelit';

  layerSwitcherEl.appendChild(osmBtn);
  layerSwitcherEl.appendChild(satBtn);
  // overlay toggles container
  const overlaysContainer = document.createElement('div');
  overlaysContainer.style.marginTop = '8px';
  overlaysContainer.style.display = 'flex';
  overlaysContainer.style.flexDirection = 'column';
  overlaysContainer.style.gap = '4px';
  layerSwitcherEl.appendChild(overlaysContainer);

    const layerControl = new ol.control.Control({ element: layerSwitcherEl });
    map.addControl(layerControl);

  function setBaseLayer(name) {
    if (name === 'OSM') {
      osmLayer.setVisible(true);
      satelliteLayer.setVisible(false);
      osmBtn.classList.add('active');
      satBtn.classList.remove('active');
    } else {
      osmLayer.setVisible(false);
      satelliteLayer.setVisible(true);
      osmBtn.classList.remove('active');
      satBtn.classList.add('active');
    }
  }

    osmBtn.addEventListener('click', function () { setBaseLayer('OSM'); });
    satBtn.addEventListener('click', function () { setBaseLayer('SAT'); });

  // Info toggle button: when active, clicking features shows popup with info
  const infoBtn = document.createElement('button');
  infoBtn.innerText = 'Info';
  infoBtn.style.marginLeft = '6px';
  layerSwitcherEl.appendChild(infoBtn);

  let infoMode = false;
  function setInfoMode(on) {
    infoMode = !!on;
    if (infoMode) infoBtn.classList.add('active'); else infoBtn.classList.remove('active');
  }
    infoBtn.addEventListener('click', function () { setInfoMode(!infoMode); });

    // Popup overlay element
    const popup = document.createElement('div');
    popup.className = 'map-popup';
    popup.style.display = 'none';
    popup.innerHTML = '<a href="#" class="popup-closer">×</a><div class="popup-content"></div>';
    // Append popup to map container
    document.getElementById('map').appendChild(popup);

    const overlay = new ol.Overlay({
      element: popup,
      autoPan: true,
      autoPanAnimation: { duration: 250 }
    });
    map.addOverlay(overlay);

    const closer = popup.querySelector('.popup-closer');
    const contentEl = popup.querySelector('.popup-content');
    closer.addEventListener('click', function (e) { e.preventDefault(); overlay.setPosition(undefined); popup.style.display = 'none'; setInfoMode(false); });

  // Map click handler to show info
    map.on('singleclick', function (evt) {
    if (!infoMode) return;
    const pixel = evt.pixel;
    const clicked = map.forEachFeatureAtPixel(pixel, function (feat) { return feat; });
    if (!clicked) {
      overlay.setPosition(undefined);
      popup.style.display = 'none';
      return;
    }

    // If cluster, get inner features
    const features = clicked.get('features') ? clicked.get('features') : [clicked];
    let html = '';
    features.forEach(function (f, idx) {
      const props = f.getProperties();
      const title = props.title || props.name || (props.properties && props.properties.title) || 'Pa emër';
      const desc = props.description || props.desc || (props.properties && props.properties.description) || '';
      html += '<div class="popup-item">';
      html += '<div class="popup-title">' + title + '</div>';
      if (desc) html += '<div class="popup-desc">' + desc + '</div>';
      html += '</div>';
      if (idx < features.length - 1) html += '<hr />';
    });

    contentEl.innerHTML = html;
    popup.style.display = 'block';
    overlay.setPosition(evt.coordinate);
    });

    // helper to create cluster layer with given color and title
  function createClusterLayerFromGeoJSON(geojson, color) {
    const feats = new ol.format.GeoJSON().readFeatures(geojson, { featureProjection: 'EPSG:3857' });
    const src = new ol.source.Vector({ features: feats });
    const cluster = new ol.source.Cluster({ distance: 40, source: src });
    const layerStyle = function (feature) {
      const inner = feature.get('features');
      const size = inner ? inner.length : 1;
      return new ol.style.Style({
        image: new ol.style.Circle({ radius: Math.max(8, Math.min(20, size + 6)), fill: new ol.style.Fill({ color: color }), stroke: new ol.style.Stroke({ color: '#fff', width: 2 }) }),
        text: new ol.style.Text({ text: size > 1 ? String(size) : '', fill: new ol.style.Fill({ color: '#fff' }) })
      });
    };
    return new ol.layer.Vector({ source: cluster, style: layerStyle });
    }

    // container for overlay layers
    let destLayer = null;
    let bizLayer = null;

  // Fetch destinations and businesses in parallel
  Promise.all([
    fetch('/api/destinations/').then(r => r.ok ? r.json() : null).catch(() => null),
    fetch('/api/businesses/').then(r => r.ok ? r.json() : null).catch(() => null)
  ]).then(([destData, bizData]) => {
    // Destinations (orange)
    if (destData && destData.features && destData.features.length) {
      destLayer = createClusterLayerFromGeoJSON(destData, '#FF5722');
      map.addLayer(destLayer);
    }

    // Businesses (blue)
    if (bizData && bizData.features && bizData.features.length) {
      bizLayer = createClusterLayerFromGeoJSON(bizData, '#2196F3');
      map.addLayer(bizLayer);
    }

    // Add overlay toggles (checkboxes)
    function makeOverlayToggle(labelText, layer, checked=true) {
      const wrapper = document.createElement('label');
      wrapper.style.fontSize = '12px';
      wrapper.style.display = 'flex';
      wrapper.style.alignItems = 'center';
      const cb = document.createElement('input');
      cb.type = 'checkbox';
      cb.checked = checked;
      cb.style.marginRight = '6px';
      cb.addEventListener('change', function () {
        if (layer) layer.setVisible(cb.checked);
      });
      wrapper.appendChild(cb);
      const txt = document.createElement('span');
      txt.innerText = labelText;
      wrapper.appendChild(txt);
      overlaysContainer.appendChild(wrapper);
      // set initial visibility
      if (layer) layer.setVisible(checked);
    }

    makeOverlayToggle('Destinacionet', destLayer, true);
    makeOverlayToggle('Business (Bar/Hotel/Restaurant)', bizLayer, true);
    }).catch(console.error);
  } // end map init

  // Populate Historical Periods as top-level nav links (fallback to static list)
  // populatePeriodsNav removed from this file; historical periods dropdown is handled by static/js/periods-dropdown.js
});
