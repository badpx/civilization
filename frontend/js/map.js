/**
 * map.js - Canvas-based terrain map renderer
 * Renders a 30x20 grid with city positions on a canvas element.
 */

const TERRAIN_COLORS = {
  plains: '#8FBC8F',
  forest: '#228B22',
  hills: '#8B7355',
  mountain: '#696969',
  water: '#4682B4',
  desert: '#F5DEB3',
  grassland: '#90EE90'
};

const CANVAS_WIDTH = 750;
const CANVAS_HEIGHT = 500;
const GRID_COLS = 30;
const GRID_ROWS = 20;

/**
 * Draw the full map on a canvas element.
 * @param {HTMLCanvasElement} canvas - The canvas to draw on
 * @param {Object} mapData - Map data with terrain grid and cities
 * @param {Array} civilizations - List of civilization objects (for colors)
 */
function drawMap(canvas, mapData, civilizations) {
  if (!canvas || !mapData) return;

  const ctx = canvas.getContext('2d');
  canvas.width = CANVAS_WIDTH;
  canvas.height = CANVAS_HEIGHT;

  const tileW = CANVAS_WIDTH / GRID_COLS;
  const tileH = CANVAS_HEIGHT / GRID_ROWS;

  // Build a civ color lookup by civ_id
  const civColors = {};
  if (civilizations) {
    const colorPalette = ['#e74c3c', '#3498db', '#2ecc71', '#f39c12'];
    civilizations.forEach((civ, i) => {
      const color = civ.color || colorPalette[i % colorPalette.length];
      civColors[civ.id] = color;
    });
  }

  // Draw terrain tiles
  const terrain = mapData.terrain || mapData.grid || mapData.tiles || [];
  for (let row = 0; row < GRID_ROWS; row++) {
    for (let col = 0; col < GRID_COLS; col++) {
      let terrainType = 'plains';
      if (row < terrain.length && col < terrain[row].length) {
        terrainType = terrain[row][col];
      } else if (mapData.tiles && row < mapData.tiles.length && col < mapData.tiles[row]?.length) {
        terrainType = mapData.tiles[row][col];
      } else if (Array.isArray(terrain) && terrain.length === GRID_ROWS * GRID_COLS) {
        // Flat array format
        terrainType = terrain[row * GRID_COLS + col] || 'plains';
      }

      const color = TERRAIN_COLORS[terrainType] || TERRAIN_COLORS.plains;
      const x = col * tileW;
      const y = row * tileH;

      ctx.fillStyle = color;
      ctx.fillRect(x, y, tileW, tileH);

      // Subtle grid lines
      ctx.strokeStyle = 'rgba(0, 0, 0, 0.08)';
      ctx.lineWidth = 0.5;
      ctx.strokeRect(x, y, tileW, tileH);
    }
  }

  // Draw cities
  const cities = mapData.cities || mapData.settlements || [];
  if (cities.length > 0) {
    cities.forEach(city => {
      const cx = (city.x !== undefined ? city.x : city.col || 0) * tileW + tileW / 2;
      const cy = (city.y !== undefined ? city.y : city.row || 0) * tileH + tileH / 2;
      const civColor = civColors[city.civ_id || city.owner_id] || '#cccccc';
      const pop = city.population || city.pop || 0;
      const radius = Math.min(8 + pop * 0.5, 14);

      // Glow
      const glow = ctx.createRadialGradient(cx, cy, 0, cx, cy, radius * 2.5);
      glow.addColorStop(0, civColor + '44');
      glow.addColorStop(1, civColor + '00');
      ctx.fillStyle = glow;
      ctx.beginPath();
      ctx.arc(cx, cy, radius * 2.5, 0, Math.PI * 2);
      ctx.fill();

      // Dot
      ctx.fillStyle = civColor;
      ctx.beginPath();
      ctx.arc(cx, cy, radius, 0, Math.PI * 2);
      ctx.fill();

      // Border
      ctx.strokeStyle = '#ffffffcc';
      ctx.lineWidth = 1.5;
      ctx.beginPath();
      ctx.arc(cx, cy, radius, 0, Math.PI * 2);
      ctx.stroke();

      // City name label
      const name = city.name || city.city_name || '';
      if (name) {
        ctx.fillStyle = '#ffffff';
        ctx.font = 'bold 10px -apple-system, sans-serif';
        ctx.textAlign = 'center';
        ctx.shadowColor = 'rgba(0, 0, 0, 0.8)';
        ctx.shadowBlur = 3;
        ctx.fillText(name, cx, cy - radius - 4);
        ctx.shadowBlur = 0;
      }
    });
  }

  // Draw borders between civ territories (if available)
  if (mapData.borders || mapData.territories) {
    const territories = mapData.borders || mapData.territories;
    TerritoriesHelper.drawBorders(ctx, territories, civColors, tileW, tileH);
  }
}

/** Helper for territory border rendering */
const TerritoriesHelper = {
  drawBorders(ctx, territories, civColors, tileW, tileH) {
    for (let row = 0; row < GRID_ROWS; row++) {
      for (let col = 0; col < GRID_COLS; col++) {
        const ownerId = territories[row]?.[col];
        if (!ownerId) continue;
        const color = civColors[ownerId] || '#888888';

        // Check neighbors for border edges
        const neighbors = [
          { dr: -1, dc: 0 }, // top
          { dr: 0, dc: 1 },  // right
          { dr: 1, dc: 0 },  // bottom
          { dr: 0, dc: -1 }  // left
        ];

        neighbors.forEach((n, i) => {
          const nr = row + n.dr;
          const nc = col + n.dc;
          const neighborOwner = territories[nr]?.[nc];
          if (neighborOwner !== ownerId) {
            const x = col * tileW;
            const y = row * tileH;
            ctx.strokeStyle = color;
            ctx.lineWidth = 2;
            ctx.shadowColor = color + '66';
            ctx.shadowBlur = 6;
            ctx.beginPath();
            switch (i) {
              case 0: // top
                ctx.moveTo(x, y); ctx.lineTo(x + tileW, y); break;
              case 1: // right
                ctx.moveTo(x + tileW, y); ctx.lineTo(x + tileW, y + tileH); break;
              case 2: // bottom
                ctx.moveTo(x, y + tileH); ctx.lineTo(x + tileW, y + tileH); break;
              case 3: // left
                ctx.moveTo(x, y); ctx.lineTo(x, y + tileH); break;
            }
            ctx.stroke();
            ctx.shadowBlur = 0;
          }
        });
      }
    }
  }
};

// Export for use in other scripts
if (typeof module !== 'undefined' && module.exports) {
  module.exports = { drawMap, TERRAIN_COLORS };
}
