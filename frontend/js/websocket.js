/**
 * websocket.js - WebSocket connection manager
 * Connects to the backend, handles reconnection, and dispatches events.
 */

const eventBus = {
  _listeners: {},
  on(event, callback) {
    if (!this._listeners[event]) {
      this._listeners[event] = [];
    }
    this._listeners[event].push(callback);
    return () => this.off(event, callback);
  },
  off(event, callback) {
    const listeners = this._listeners[event];
    if (listeners) {
      this._listeners[event] = listeners.filter(cb => cb !== callback);
    }
  },
  emit(event, data) {
    const listeners = this._listeners[event];
    if (listeners) {
      listeners.forEach(cb => {
        try { cb(data); } catch (e) { console.error(`[eventBus] Error in handler for "${event}":`, e); }
      });
    }
  },
  clear() {
    this._listeners = {};
  }
};

let ws = null;
let wsReconnectTimer = null;
let wsUrl = 'ws://localhost:8000/ws';
let isConnected = false;
let reconnectAttempts = 0;
const MAX_RECONNECT_ATTEMPTS = 50;
const RECONNECT_INTERVAL = 2000;

/**
 * Connect to the WebSocket server.
 * @param {string} [url] - WebSocket URL
 * @returns {WebSocket}
 */
function connectWS(url) {
  if (url) wsUrl = url;
  if (ws && (ws.readyState === WebSocket.OPEN || ws.readyState === WebSocket.CONNECTING)) {
    return ws;
  }

  reconnectAttempts = 0;
  _createConnection();
  return ws;
}

function _createConnection() {
  if (wsReconnectTimer) {
    clearTimeout(wsReconnectTimer);
    wsReconnectTimer = null;
  }

  try {
    ws = new WebSocket(wsUrl);
  } catch (e) {
    console.error('[WS] Failed to create WebSocket:', e);
    _scheduleReconnect();
    return;
  }

  ws.onopen = function () {
    console.log('[WS] Connected to', wsUrl);
    isConnected = true;
    reconnectAttempts = 0;
    eventBus.emit('ws_connected', {});
  };

  ws.onmessage = function (event) {
    try {
      const msg = JSON.parse(event.data);
      _handleMessage(msg);
    } catch (e) {
      console.error('[WS] Failed to parse message:', e, event.data);
    }
  };

  ws.onerror = function (err) {
    console.error('[WS] Error:', err);
  };

  ws.onclose = function (event) {
    console.log('[WS] Disconnected (code:', event.code, 'reason:', event.reason, ')');
    isConnected = false;
    ws = null;
    eventBus.emit('ws_disconnected', { code: event.code, reason: event.reason });
    _scheduleReconnect();
  };
}

function _scheduleReconnect() {
  if (wsReconnectTimer) return;
  if (reconnectAttempts >= MAX_RECONNECT_ATTEMPTS) {
    console.warn('[WS] Max reconnect attempts reached, giving up.');
    return;
  }

  reconnectAttempts++;
  const delay = Math.min(RECONNECT_INTERVAL * Math.pow(1.5, reconnectAttempts - 1), 30000);
  console.log(`[WS] Reconnecting in ${delay}ms (attempt ${reconnectAttempts}/${MAX_RECONNECT_ATTEMPTS})...`);

  wsReconnectTimer = setTimeout(() => {
    wsReconnectTimer = null;
    _createConnection();
  }, delay);
}

function _handleMessage(msg) {
  const type = msg.type || msg.event_type || '';
  const data = msg.data || msg;

  switch (type) {
    case 'state':
      // Backend sends 'state' type with full game state
      eventBus.emit('game_state', data);
      break;

    case 'event':
      // Backend sends 'event' type with a GameEvent object
      eventBus.emit('event', data);
      break;

    case 'game_over':
      eventBus.emit('game_over', data);
      break;

    case 'pong':
      // Heartbeat response, ignore
      break;

    default:
      // Try to handle as a raw state or event
      if (data && (data.turn !== undefined || data.civilizations)) {
        eventBus.emit('game_state', data);
      } else if (data && (data.type || data.description || data.message)) {
        eventBus.emit('event', data);
      } else {
        eventBus.emit('raw_message', msg);
      }
      break;
  }
}

/**
 * Send a JSON message through the WebSocket.
 */
function wsSend(data) {
  if (ws && ws.readyState === WebSocket.OPEN) {
    ws.send(JSON.stringify(data));
    return true;
  }
  console.warn('[WS] Cannot send: not connected');
  return false;
}

/**
 * Disconnect the WebSocket.
 */
function disconnectWS() {
  if (wsReconnectTimer) {
    clearTimeout(wsReconnectTimer);
    wsReconnectTimer = null;
  }
  reconnectAttempts = MAX_RECONNECT_ATTEMPTS;
  if (ws) {
    ws.close();
    ws = null;
  }
  isConnected = false;
}

// Export globally
window.eventBus = eventBus;
window.connectWS = connectWS;
window.wsSend = wsSend;
window.disconnectWS = disconnectWS;
