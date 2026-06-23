/* site/js/map.js — shared Leaflet map helpers */

// ── Color scales ─────────────────────────────────────────────

function housingColor(score) {
  if (score == null || isNaN(score)) return '#e8e4dc';
  const colors = ['#dce8f5','#aec9e8','#7aaad0','#4a80b5','#2c4a7c','#1a2d4f'];
  const i = Math.min(Math.floor(score * colors.length), colors.length - 1);
  return colors[i];
}

function foodColor(miles) {
  if (miles == null || isNaN(miles)) return '#e8e4dc';
  const breaks = [0.5, 0.75, 1.0, 1.5, 2.0];
  const colors = ['#d4ede9','#96cfc8','#5aadad','#2d8080','#2d6a6a','#1a3d3d'];
  for (let i = 0; i < breaks.length; i++) {
    if (miles <= breaks[i]) return colors[i];
  }
  return colors[colors.length - 1];
}

function overlapColor(feature) {
  const p = feature.properties;
  const highHousing = (p.housing_score ?? 0) > 0.5;
  const highFood    = (p.nearest_grocery_miles ?? 0) > 1;
  if (highHousing && highFood) return '#7b2d2d';
  if (highHousing)             return '#2c4a7c';
  if (highFood)                return '#2d6a6a';
  return '#e8e4dc';
}

// ── Popup builders ───────────────────────────────────────────

function housingPopup(props) {
  const pct = v => v != null ? Math.round(v * 100) + '%' : '—';
  const fmt = v => v != null ? v.toFixed(2) : '—';
  const income = props.B19013_001E != null
    ? '$' + Math.round(props.B19013_001E).toLocaleString()
    : '—';
  return `<div class="popup-inner">
    <strong>Block Group ${props.GEOID ?? ''}</strong>
    <div class="popup-row"><span>Housing insecurity score</span><span class="popup-val">${fmt(props.housing_score)}</span></div>
    <div class="popup-row"><span>Poverty rate</span><span class="popup-val">${pct(props.poverty_rate)}</span></div>
    <div class="popup-row"><span>Median household income</span><span class="popup-val">${income}</span></div>
  </div>`;
}

function foodPopup(props) {
  const dist = props.nearest_grocery_miles;
  const distStr = dist != null ? dist.toFixed(2) + ' mi' : '—';
  const desert1  = props.LILATracts_1And10    === 1 ? 'Yes' : 'No';
  const desert05 = props.LILATracts_halfAnd10 === 1 ? 'Yes' : 'No';
  const pct = v => v != null ? Math.round(v * 100) + '%' : '—';
  return `<div class="popup-inner">
    <strong>Block Group ${props.GEOID ?? ''}</strong>
    <div class="popup-row"><span>Nearest grocery store</span><span class="popup-val">${distStr}</span></div>
    <div class="popup-row"><span>Food desert (1-mile)</span><span class="popup-val">${desert1}</span></div>
    <div class="popup-row"><span>Food desert (0.5-mile)</span><span class="popup-val">${desert05}</span></div>
    <div class="popup-row"><span>Poverty rate</span><span class="popup-val">${pct(props.poverty_rate)}</span></div>
  </div>`;
}

function overlapPopup(props) {
  const dist = props.nearest_grocery_miles;
  const distStr = dist != null ? dist.toFixed(2) + ' mi' : '—';
  const fmt  = v => v != null ? v.toFixed(2) : '—';
  const pct  = v => v != null ? Math.round(v * 100) + '%' : '—';
  const highHousing = (props.housing_score ?? 0) > 0.5;
  const highFood    = (dist ?? 0) > 1;
  let category = 'Low insecurity (both)';
  if (highHousing && highFood) category = 'High housing + food insecurity';
  else if (highHousing)        category = 'High housing insecurity only';
  else if (highFood)           category = 'High food insecurity only';
  return `<div class="popup-inner">
    <strong>Block Group ${props.GEOID ?? ''}</strong>
    <div class="popup-row"><span>Category</span><span class="popup-val">${category}</span></div>
    <div class="popup-row"><span>Housing score</span><span class="popup-val">${fmt(props.housing_score)}</span></div>
    <div class="popup-row"><span>Nearest grocery</span><span class="popup-val">${distStr}</span></div>
    <div class="popup-row"><span>Poverty rate</span><span class="popup-val">${pct(props.poverty_rate)}</span></div>
  </div>`;
}

// ── Layer loaders ────────────────────────────────────────────

function loadChoropleth(map, url, colorFn, popupFn, options = {}) {
  return fetch(url)
    .then(r => {
      if (!r.ok) throw new Error('Failed to load ' + url);
      return r.json();
    })
    .then(data => {
      const layer = L.geoJSON(data, {
        style: feature => ({
          fillColor: colorFn(feature),
          fillOpacity: 0.75,
          color: '#fff',
          weight: 0.5,
          opacity: 0.6,
        }),
        onEachFeature: (feature, layer) => {
          if (popupFn) {
            layer.bindPopup(popupFn(feature.properties), { maxWidth: 280 });
          }
          layer.on('mouseover', function() {
            this.setStyle({ fillOpacity: 0.95, weight: 1.5, color: '#333' });
          });
          layer.on('mouseout', function() {
            this.setStyle({ fillOpacity: 0.75, weight: 0.5, color: '#fff' });
          });
        },
      });
      if (map) layer.addTo(map);
      if (map && options.fitBounds !== false) {
        try { map.fitBounds(layer.getBounds()); } catch(e) {}
      }
      return layer;
    })
    .catch(err => {
      console.warn('loadChoropleth error:', err);
      return null;
    });
}

function loadPoints(map, url, color, label) {
  return fetch(url)
    .then(r => {
      if (!r.ok) throw new Error('Failed to load ' + url);
      return r.json();
    })
    .then(data => {
      const layer = L.geoJSON(data, {
        pointToLayer: (feature, latlng) => L.circleMarker(latlng, {
          radius: 6,
          fillColor: color,
          color: '#fff',
          weight: 1.5,
          fillOpacity: 0.9,
        }),
        onEachFeature: (feature, layer) => {
          const p = feature.properties;
          const name = p.Store_Name ?? p.name ?? p.Name ?? label;
          const addr = p.Store_Street_Address ?? p.address ?? p.Address ?? '';
          layer.bindPopup(`<div class="popup-inner">
            <strong>${name}</strong>
            ${addr ? `<div class="popup-row"><span>${addr}</span></div>` : ''}
            <div class="popup-row"><span>Type</span><span class="popup-val">${label}</span></div>
          </div>`, { maxWidth: 240 });
        },
      });
      if (map) layer.addTo(map);
      return layer;
    })
    .catch(err => {
      console.warn('loadPoints error:', err);
      return null;
    });
}
