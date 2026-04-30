/**
 * app.js - Main application controller
 * i18n, game state, API calls, WebSocket event handlers, UI initialization.
 */

// ===== Internationalization =====
const i18n = {
  zh: {
    title: '🌍 文明纪元',
    turn: '回合',
    new_game: '新游戏',
    next_turn: '下一回合',
    auto_play: '自动进行',
    stop_auto: '停止',
    language: 'EN',
    alive: '存活',
    defeated: '已灭亡',
    population: '总人口',
    cities_count: '城市数量',
    military: '军事力量',
    happiness: '幸福度',
    cities: '城市',
    select_civ_prompt: '选择一个文明查看详情',
    no_events: '暂无事件',
    god_intervention: '⚡ 神祇干预',
    bless: '赐福',
    wrath: '天罚',
    oracle: '神谕',
    no_civs: '无可用文明',
    event_log: '📜 事件日志',
    loading: '加载中...',
    no_data: '暂无数据',
    confirm_new_game: '确定要开始新游戏吗？当前进度将丢失。',
    game_started: '🎮 新游戏开始！',
    divine_sent: '✨ 神力已降下',
    connection_lost: '⚠️ 连接断开，正在重连...',
    connection_restored: '✅ 连接已恢复',
    error_fetch: '获取数据失败',
    error_send: '发送指令失败',
  },
  en: {
    title: '🌍 Age of Civilization',
    turn: 'Turn',
    new_game: 'New Game',
    next_turn: 'Next Turn',
    auto_play: 'Auto Play',
    stop_auto: 'Stop',
    language: '中文',
    alive: 'Alive',
    defeated: 'Defeated',
    population: 'Total Population',
    cities_count: 'Cities',
    military: 'Military Power',
    happiness: 'Happiness',
    cities: 'Cities',
    select_civ_prompt: 'Select a civilization to view details',
    no_events: 'No events yet',
    god_intervention: '⚡ God Intervention',
    bless: 'Bless',
    wrath: 'Wrath',
    oracle: 'Oracle',
    no_civs: 'No civilizations available',
    event_log: '📜 Event Log',
    loading: 'Loading...',
    no_data: 'No data',
    confirm_new_game: 'Start a new game? Current progress will be lost.',
    game_started: '🎮 New game started!',
    divine_sent: '✨ Divine power has been unleashed',
    connection_lost: '⚠️ Connection lost, reconnecting...',
    connection_restored: '✅ Connection restored',
    error_fetch: 'Failed to fetch data',
    error_send: 'Failed to send command',
  }
};

let currentLang = 'zh';

/** Translate a key to the current language */
function _(key) {
  return (i18n[currentLang] && i18n[currentLang][key]) || i18n.zh[key] || key;
}
window._t = _;

/** Toggle between Chinese and English */
function toggleLang() {
  currentLang = currentLang === 'zh' ? 'en' : 'zh';
  localStorage.setItem('civ-lang', currentLang);
  renderAllText();
  return currentLang;
}
window.toggleLang = toggleLang;

/** Update all text content on the page based on current language */
function renderAllText() {
  const titleEl = document.getElementById('game-title');
  if (titleEl) titleEl.textContent = _('title');

  const langBtn = document.getElementById('btn-lang');
  if (langBtn) langBtn.textContent = _('language');

  const newGameBtn = document.getElementById('btn-new-game');
  if (newGameBtn) newGameBtn.textContent = _('new_game');

  const nextTurnBtn = document.getElementById('btn-next-turn');
  if (nextTurnBtn) nextTurnBtn.textContent = _('next_turn');

  const autoBtn = document.getElementById('btn-auto');
  if (autoBtn) {
    autoBtn.textContent = gameState.autoPlaying ? _('stop_auto') : _('auto_play');
  }

  const logHeader = document.getElementById('log-header');
  if (logHeader) logHeader.textContent = _('event_log');

  if (gameState.civilizations) {
    updateCivTabs(gameState.civilizations, gameState.selectedCivId);
    showGodPanel(gameState.civilizations);
    const selectedId = gameState.selectedCivId;
    const civ = gameState.civilizations.find(c => String(c.id) === String(selectedId));
    if (civ) updateCivDetail(civ);
  }
}

// ===== Game State =====
const gameState = {
  turn: 0,
  civilizations: [],
  selectedCivId: null,
  autoPlaying: false,
  events: [],
  mapData: null,
  connected: false
};

// ===== API Helpers =====
const API_BASE = '';

async function apiGet(path) {
  try {
    const res = await fetch(API_BASE + path, { headers: { 'Accept': 'application/json' } });
    if (!res.ok) throw new Error('HTTP ' + res.status);
    return await res.json();
  } catch (e) {
    console.error('[API] GET', path, 'failed:', e);
    throw e;
  }
}

async function apiPost(path, body) {
  try {
    const res = await fetch(API_BASE + path, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'Accept': 'application/json' },
      body: body ? JSON.stringify(body) : undefined
    });
    if (!res.ok) throw new Error('HTTP ' + res.status);
    return await res.json();
  } catch (e) {
    console.error('[API] POST', path, 'failed:', e);
    throw e;
  }
}

// ===== API Actions =====
async function newGame() {
  if (!confirm(_('confirm_new_game'))) return;
  try {
    showLoading(true);
    gameState.autoPlaying = false;
    updateAutoButton();
    const result = await apiPost('/api/game/start');
    addEvent({ type: 'info', description: _('game_started'), turn: 0, id: 'manual-' + Date.now() });
    await fetchGameState();
  } catch (e) {
    addEvent({ type: 'info', description: _('error_send') + ': ' + e.message, turn: gameState.turn, id: 'err-' + Date.now() });
  } finally {
    showLoading(false);
  }
}
window.newGame = newGame;

async function nextTurn() {
  try {
    showLoading(true);
    const result = await apiPost('/api/game/next-turn');
    if (result && result.turn !== undefined) {
      gameState.turn = result.turn;
      updateTurnDisplay();
    }
    await fetchGameState();
  } catch (e) {
    addEvent({ type: 'info', description: _('error_send') + ': ' + e.message, turn: gameState.turn, id: 'err-' + Date.now() });
  } finally {
    showLoading(false);
  }
}
window.nextTurn = nextTurn;

async function toggleAuto() {
  try {
    if (gameState.autoPlaying) {
      const result = await apiPost('/api/game/stop');
      gameState.autoPlaying = false;
    } else {
      const result = await apiPost('/api/game/auto');
      gameState.autoPlaying = true;
    }
    updateAutoButton();
  } catch (e) {
    addEvent({ type: 'info', description: _('error_send') + ': ' + e.message, turn: gameState.turn, id: 'err-' + Date.now() });
  }
}
window.toggleAuto = toggleAuto;

async function divineAction(type) {
  const targetSelect = document.getElementById('god-target');
  if (!targetSelect) return;
  const targetCivId = targetSelect.value;
  if (!targetCivId) return;

  try {
    showLoading(true);
    await apiPost('/api/divine/action', {
      action_type: type,
      target_civ_id: targetCivId,
      description: ''
    });
    addEvent({ type: 'divine', description: _('divine_sent'), turn: gameState.turn, id: 'divine-' + Date.now() });
    await fetchGameState();
  } catch (e) {
    addEvent({ type: 'info', description: _('error_send') + ': ' + e.message, turn: gameState.turn, id: 'err-' + Date.now() });
  } finally {
    showLoading(false);
  }
}
window.divineAction = divineAction;

/** Fetch the full game state from the backend */
async function fetchGameState() {
  try {
    const state = await apiGet('/api/state');
    updateFromState(state);
  } catch (e) {
    console.warn('[App] fetchGameState failed:', e);
    // Try to get at least the civ list
    try {
      const civs = await apiGet('/api/civilizations');
      if (civs && Array.isArray(civs)) {
        gameState.civilizations = civs;
        if (!gameState.selectedCivId && civs.length > 0) {
          gameState.selectedCivId = civs[0].id;
        }
        updateCivTabs(civs, gameState.selectedCivId);
        showGodPanel(civs);
        if (gameState.selectedCivId) {
          try {
            const detail = await apiGet('/api/civilizations/' + gameState.selectedCivId);
            updateCivDetail(detail);
          } catch (e2) { /* ignore */ }
        }
      }
    } catch (e2) {
      console.warn('[App] Failed to fetch civs:', e2);
    }
  }
}

/** Process a state object and update all UI */
function updateFromState(state) {
  if (!state) return;

  if (state.turn !== undefined) {
    gameState.turn = state.turn;
    updateTurnDisplay();
  }

  if (state.civilizations) {
    gameState.civilizations = state.civilizations;
    if (!gameState.selectedCivId && state.civilizations.length > 0) {
      gameState.selectedCivId = state.civilizations[0].id;
    }
    updateCivTabs(state.civilizations, gameState.selectedCivId);
    showGodPanel(state.civilizations);

    const selectedId = gameState.selectedCivId;
    const selectedCiv = state.civilizations.find(c => String(c.id) === String(selectedId));
    if (selectedCiv) updateCivDetail(selectedCiv);
  }

  if (state.map_grid) {
    gameState.mapData = { terrain: state.map_grid, cities: [] };
    // Extract cities from civilizations
    const allCities = [];
    if (state.civilizations) {
      state.civilizations.forEach(civ => {
        if (civ.cities) {
          civ.cities.forEach(city => {
            allCities.push({
              x: city.x,
              y: city.y,
              name: city.name,
              civ_id: civ.id,
              population: city.population
            });
          });
        }
      });
    }
    gameState.mapData.cities = allCities;
    renderMap();
  }

  if (state.events) {
    gameState.events = state.events;
    updateEventLog(state.events);
  }

  if (state.is_running !== undefined) {
    // auto-playing is determined by the backend auto endpoint, not is_running
  }
}

function updateTurnDisplay() {
  const el = document.getElementById('turn-display');
  if (el) el.textContent = _('turn') + ' ' + gameState.turn;
}

function updateAutoButton() {
  const btn = document.getElementById('btn-auto');
  if (btn) {
    btn.textContent = gameState.autoPlaying ? _('stop_auto') : _('auto_play');
    btn.className = gameState.autoPlaying ? 'btn btn-danger' : 'btn btn-success';
  }
}

function renderMap() {
  const canvas = document.getElementById('game-map');
  if (canvas && gameState.mapData) {
    drawMap(canvas, gameState.mapData, gameState.civilizations);
  }
}

function addEvent(event) {
  if (!event) return;
  gameState.events.push(event);
  if (gameState.events.length > 500) {
    gameState.events = gameState.events.slice(-300);
  }
  updateEventLog(gameState.events);
}

function showLoading(show) {
  const overlay = document.getElementById('loading-overlay');
  if (overlay) {
    overlay.className = show ? 'active' : '';
  }
}

// ===== WebSocket Event Handlers =====
function setupWebSocketHandlers() {
  eventBus.on('game_state', (data) => {
    console.log('[App] Game state received via WS, turn:', data.turn);
    updateFromState(data);
  });

  eventBus.on('event', (data) => {
    if (data) {
      addEvent(data);
    }
  });

  eventBus.on('game_over', (data) => {
    console.log('[App] Game over:', data);
    addEvent({ type: 'info', description: '🏆 ' + (data.winner ? 'Winner: ' + data.winner : 'Game Over'), turn: gameState.turn, id: 'gameover' });
  });

  eventBus.on('ws_connected', () => {
    gameState.connected = true;
    console.log('[App] WebSocket connected');
    addEvent({ type: 'info', description: _('connection_restored'), turn: gameState.turn, id: 'ws-' + Date.now() });
    // Refresh state on reconnect
    fetchGameState();
  });

  eventBus.on('ws_disconnected', () => {
    gameState.connected = false;
    console.log('[App] WebSocket disconnected');
    addEvent({ type: 'info', description: _('connection_lost'), turn: gameState.turn, id: 'ws-' + Date.now() });
  });

  eventBus.on('select_civ', (civId) => {
    gameState.selectedCivId = civId;
    updateCivTabs(gameState.civilizations, civId);
    // Try to get detailed civ info
    fetch(API_BASE + '/api/civilizations/' + civId)
      .then(r => r.json())
      .then(civ => updateCivDetail(civ))
      .catch(e => {
        const civ = gameState.civilizations.find(c => String(c.id) === String(civId));
        if (civ) updateCivDetail(civ);
      });
  });
}

// ===== Initialization =====
function init() {
  // Restore language preference
  const savedLang = localStorage.getItem('civ-lang');
  if (savedLang) currentLang = savedLang;
  window._t = _;
  window.currentLang = currentLang;

  renderAllText();

  setupWebSocketHandlers();

  try {
    connectWS();
  } catch (e) {
    console.warn('[App] WebSocket connection failed, will use HTTP polling:', e);
  }

  fetchGameState();

  // Periodic refresh fallback (every 10s if WS not connected)
  setInterval(() => {
    if (!gameState.connected) {
      fetchGameState();
    }
  }, 10000);

  window.addEventListener('resize', () => {
    renderMap();
  });

  console.log('[App] Civilization frontend initialized.');
}

if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', init);
} else {
  init();
}
