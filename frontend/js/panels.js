/**
 * panels.js - UI panel management
 * Functions to update civilization tabs, detail panels, event logs, and god interventions.
 */

const CIV_COLORS = ['#e74c3c', '#3498db', '#2ecc71', '#f39c12'];

/**
 * Update civilization tab buttons.
 * @param {Array} civilizations - List of civ objects (from /api/civilizations or full state)
 * @param {number|string} selectedCivId - Currently selected civ ID
 */
function updateCivTabs(civilizations, selectedCivId) {
  const container = document.getElementById('civ-tabs');
  if (!container) return;

  if (!civilizations || civilizations.length === 0) {
    container.innerHTML = '<div class="civ-tab" style="flex:1; text-align:center; padding:12px; color:var(--text-muted); font-size:13px;">' +
      (window._t ? window._t('no_data') : '暂无数据') + '</div>';
    return;
  }

  container.innerHTML = '';
  civilizations.forEach((civ, index) => {
    const color = civ.color || CIV_COLORS[index % CIV_COLORS.length];
    const isAlive = civ.is_alive !== false;
    const isActive = String(civ.id) === String(selectedCivId);

    const tab = document.createElement('button');
    tab.className = 'civ-tab' + (isActive ? ' active' : '');
    tab.dataset.civId = civ.id;
    tab.style.borderBottomColor = isActive ? color : 'transparent';

    const statusText = isAlive
      ? (window._t ? window._t('alive') : '存活')
      : (window._t ? window._t('defeated') : '已灭亡');

    tab.innerHTML = `
      <span class="civ-color-dot" style="background:${color}; opacity:${isAlive ? '1' : '0.4'}"></span>
      <span class="civ-name" style="opacity:${isAlive ? '1' : '0.5'}">${civ.name || 'Civilization ' + (index + 1)}</span>
      <span class="civ-status">${statusText}</span>
    `;

    tab.addEventListener('click', function () {
      eventBus.emit('select_civ', civ.id);
    });

    container.appendChild(tab);
  });
}

/**
 * Update the civilization detail panel.
 * @param {Object} civ - Civilization detail object (full from /api/civilizations/{id} or embedded in state)
 */
function updateCivDetail(civ) {
  const container = document.getElementById('civ-detail');
  if (!container) return;

  if (!civ) {
    container.innerHTML = '<div style="padding:12px; text-align:center; color:var(--text-muted); font-size:13px;">' +
      (window._t ? window._t('select_civ_prompt') : '选择一个文明查看详情') + '</div>';
    return;
  }

  const color = civ.color || CIV_COLORS[0];
  const cities = civ.cities || [];
  const resources = civ.resources || {};

  // Resources from the full Resources model
  const resourceFields = ['food', 'production', 'gold', 'science', 'culture', 'defense'];
  let resourcesHtml = '';
  const resourceEntries = resourceFields.filter(k => resources[k] !== undefined);
  if (resourceEntries.length > 0) {
    resourcesHtml = '<div class="resource-breakdown" style="margin-top:4px;">';
    const resourceIcons = { food: '🍖', production: '⚒', gold: '💰', science: '🔬', culture: '🎭', defense: '🛡' };
    resourceEntries.forEach(key => {
      const icon = resourceIcons[key] || '📊';
      const label = key.charAt(0).toUpperCase() + key.slice(1);
      resourcesHtml += '<div class="resource-item"><span>' + icon + ' ' + label + '</span><span>' + resources[key] + '</span></div>';
    });
    resourcesHtml += '</div>';
  }

  // Cities display
  let citiesHtml = '';
  if (cities.length > 0) {
    citiesHtml = '<div class="resource-breakdown" style="margin-top:4px;">' +
      '<div style="color:var(--text-secondary); font-weight:600; margin-bottom:4px;">' +
      (window._t ? window._t('cities') : '城市') + ' (' + cities.length + ')</div>';
    cities.forEach(city => {
      const cityName = city.name || 'Unknown';
      const pop = city.population || 0;
      const cRes = city.get_output ? {} : {};
      // City resources from city fields
      const terrainLabel = city.terrain || '';
      citiesHtml += '<div class="city-entry">🏙 ' + cityName + ' (👥 ' + pop + ')' +
        (terrainLabel ? ' [' + terrainLabel + ']' : '') +
        '</div>';
    });
    citiesHtml += '</div>';
  }

  // Handle both full civ objects and summary objects
  const population = cities.reduce ? cities.reduce((sum, c) => sum + (c.population || 0), 0) : (civ.total_population || civ.population || 0);
  const cityCount = cities.length || civ.city_count || 0;
  const military = civ.military !== undefined ? civ.military : 0;
  const happiness = civ.happiness !== undefined ? civ.happiness : 0;

  container.innerHTML = `
    <div class="civ-name-title" style="color:${color}">${civ.name || 'Unknown'}</div>
    <div class="stat-row">
      <span>${window._t ? window._t('population') : '总人口'}</span>
      <span class="stat-value">${population}</span>
    </div>
    <div class="stat-row">
      <span>${window._t ? window._t('cities_count') : '城市数量'}</span>
      <span class="stat-value">${cityCount}</span>
    </div>
    <div class="stat-row">
      <span>⚔ ${window._t ? window._t('military') : '军事力量'}</span>
      <span class="stat-value ${military > 0 ? 'positive' : ''}">${military}</span>
    </div>
    <div class="stat-row">
      <span>😊 ${window._t ? window._t('happiness') : '幸福度'}</span>
      <span class="stat-value ${happiness >= 5 ? 'positive' : happiness < 3 ? 'negative' : ''}">${happiness}</span>
    </div>
    ${resourcesHtml}
    ${citiesHtml}
  `;
}

/**
 * Update the event log with new events.
 * @param {Array} events - List of event objects (GameEvent model format)
 */
function updateEventLog(events) {
  const container = document.getElementById('event-log-list');
  if (!container) return;

  if (!events || events.length === 0) {
    container.innerHTML = '<div class="log-entry" style="color:var(--text-muted); text-align:center; padding:12px;">' +
      (window._t ? window._t('no_events') : '暂无事件') + '</div>';
    return;
  }

  const reversed = [...events].reverse();
  const limited = reversed.slice(0, 100);

  container.innerHTML = '';
  limited.forEach(event => {
    const entry = document.createElement('div');
    const eventType = (event.type || event.event_type || 'info').toLowerCase();
    // Map backend event types to CSS classes
    let cssClass = 'event-neutral';
    if (eventType.includes('war') || eventType.includes('wrath') || eventType.includes('drought') || eventType.includes('plague') || eventType.includes('earthquake') || eventType.includes('flood')) {
      cssClass = 'event-war';
    } else if (eventType.includes('trade') || eventType.includes('bless')) {
      cssClass = 'event-trade';
    } else if (eventType.includes('city') || eventType.includes('harvest') || eventType.includes('golden')) {
      cssClass = 'event-city';
    } else if (eventType.includes('divine') || eventType.includes('oracle')) {
      cssClass = 'event-divine';
    } else if (eventType.includes('info') || eventType.includes('discovery')) {
      cssClass = 'event-info';
    }

    entry.className = 'log-entry ' + cssClass;

    const turnStr = event.turn !== undefined ? '[' + event.turn + '] ' : '';
    const msg = event.description || event.message || event.title || event.text || '';

    // Fallback to showing event type + id if no description
    const displayMsg = msg || (event.type || 'event') + ' #' + (event.id || '');

    entry.innerHTML = `<span class="log-time">${turnStr}</span><span class="log-msg">${_escapeHtml(displayMsg)}</span>`;
    container.appendChild(entry);
  });
}

/**
 * Show the god intervention panel.
 * @param {Array} civilizations - List of civilization objects
 */
function showGodPanel(civilizations) {
  const container = document.getElementById('god-panel');
  if (!container) return;

  if (!civilizations || civilizations.length === 0) {
    container.innerHTML = `
      <div class="panel-title"><span class="icon">⚡</span>${window._t ? window._t('god_intervention') : '神祇干预'}</div>
      <div class="god-controls">
        <select id="god-target" disabled><option>${window._t ? window._t('no_civs') : '无可用文明'}</option></select>
        <div class="god-buttons">
          <button class="btn btn-success" disabled>${window._t ? window._t('bless') : '赐福'}</button>
          <button class="btn btn-danger" disabled>${window._t ? window._t('wrath') : '天罚'}</button>
          <button class="btn btn-gold" disabled>${window._t ? window._t('oracle') : '神谕'}</button>
        </div>
      </div>
    `;
    return;
  }

  const aliveCivs = civilizations.filter(c => c.is_alive !== false);

  container.innerHTML = `
    <div class="panel-title"><span class="icon">⚡</span>${window._t ? window._t('god_intervention') : '神祇干预'}</div>
    <div class="god-controls">
      <select id="god-target">
        ${aliveCivs.map(c => `<option value="${c.id}">${c.name}</option>`).join('')}
      </select>
      <div class="god-buttons">
        <button class="btn btn-success" onclick="window.divineAction('blessing')">${window._t ? window._t('bless') : '赐福'}</button>
        <button class="btn btn-danger" onclick="window.divineAction('wrath')">${window._t ? window._t('wrath') : '天罚'}</button>
        <button class="btn btn-gold" onclick="window.divineAction('oracle')">${window._t ? window._t('oracle') : '神谕'}</button>
      </div>
    </div>
  `;
}

// ===== Helpers =====

function _escapeHtml(str) {
  if (typeof str !== 'string') return String(str);
  const div = document.createElement('div');
  div.textContent = str;
  return div.innerHTML;
}

// Export globally
window.updateCivTabs = updateCivTabs;
window.updateCivDetail = updateCivDetail;
window.updateEventLog = updateEventLog;
window.showGodPanel = showGodPanel;
