// ============================================
//  Lane Topology — Map Demo
//  Full-screen map with lane lines, turn arrows,
//  and click-to-show-turn-path annotation
// ============================================

// ---- State ----
let map = null;
let currentId = 'inter_1';
let dataMode = 'processed';
let laneLayer = null;       // L.layerGroup for all lane graphics
let turnPathLayer = null;   // L.layerGroup for highlighted turn paths
let selectedLane = null;
let tileLayerSatellite = null;
let tileLayerOSM = null;
let currentTile = 'satellite';

// ---- Intersection Data (corrected) ----
const intersections = {
    inter_1: {
        id: "53585", name: "Elizabeth St & Park St", location: "Sydney CBD",
        lat: -33.8732858, lon: 151.2099114, zoom: 19, speedLimit: 40,
        description: "4-way signalised CBD intersection. Elizabeth St (N-S, 3 NB + 2 SB lanes) crosses Park St (E-W, 3 EB + 2 WB lanes). Adjacent to Hyde Park.",
        arms: [
            { name: "North Approach (Elizabeth St)", street: "Elizabeth St", bearing: 2, approachLanes: 3, exitLanes: 2,
              lanes: [
                { index: 0, turns: { processed: [{ toArm: 1, toLane: 0, type: 'left', prob: 0.95 }], raw: [{ toArm: 1, toLane: 0, type: 'left', prob: 0.95 }, { toArm: 2, toLane: 0, type: 'through', prob: 0.41 }] }},
                { index: 1, turns: { processed: [{ toArm: 2, toLane: 0, type: 'through', prob: 0.93 }], raw: [{ toArm: 2, toLane: 0, type: 'through', prob: 0.93 }, { toArm: 1, toLane: 0, type: 'left', prob: 0.38 }] }},
                { index: 2, turns: { processed: [{ toArm: 2, toLane: 1, type: 'through', prob: 0.90 }, { toArm: 3, toLane: 1, type: 'right', prob: 0.87 }], raw: [{ toArm: 2, toLane: 1, type: 'through', prob: 0.90 }, { toArm: 3, toLane: 1, type: 'right', prob: 0.87 }] }}
              ]},
            { name: "East Approach (Park St)", street: "Park St", bearing: 94, approachLanes: 3, exitLanes: 2,
              lanes: [
                { index: 0, turns: { processed: [{ toArm: 2, toLane: 0, type: 'left', prob: 0.94 }], raw: [{ toArm: 2, toLane: 0, type: 'left', prob: 0.94 }, { toArm: 3, toLane: 0, type: 'through', prob: 0.35 }] }},
                { index: 1, turns: { processed: [{ toArm: 3, toLane: 0, type: 'through', prob: 0.92 }], raw: [{ toArm: 3, toLane: 0, type: 'through', prob: 0.92 }] }},
                { index: 2, turns: { processed: [{ toArm: 3, toLane: 1, type: 'through', prob: 0.88 }, { toArm: 0, toLane: 1, type: 'right', prob: 0.85 }], raw: [{ toArm: 3, toLane: 1, type: 'through', prob: 0.88 }, { toArm: 0, toLane: 1, type: 'right', prob: 0.85 }, { toArm: 0, toLane: 0, type: 'right', prob: 0.52 }] }}
              ]},
            { name: "South Approach (Elizabeth St)", street: "Elizabeth St", bearing: 182, approachLanes: 2, exitLanes: 3,
              lanes: [
                { index: 0, turns: { processed: [{ toArm: 3, toLane: 0, type: 'left', prob: 0.92 }, { toArm: 0, toLane: 0, type: 'through', prob: 0.88 }], raw: [{ toArm: 3, toLane: 0, type: 'left', prob: 0.92 }, { toArm: 0, toLane: 0, type: 'through', prob: 0.88 }] }},
                { index: 1, turns: { processed: [{ toArm: 0, toLane: 1, type: 'through', prob: 0.91 }, { toArm: 1, toLane: 1, type: 'right', prob: 0.86 }], raw: [{ toArm: 0, toLane: 1, type: 'through', prob: 0.91 }, { toArm: 1, toLane: 1, type: 'right', prob: 0.86 }] }}
              ]},
            { name: "West Approach (Park St)", street: "Park St", bearing: 274, approachLanes: 2, exitLanes: 3,
              lanes: [
                { index: 0, turns: { processed: [{ toArm: 0, toLane: 0, type: 'left', prob: 0.93 }, { toArm: 1, toLane: 0, type: 'through', prob: 0.89 }], raw: [{ toArm: 0, toLane: 0, type: 'left', prob: 0.93 }, { toArm: 1, toLane: 0, type: 'through', prob: 0.89 }] }},
                { index: 1, turns: { processed: [{ toArm: 1, toLane: 1, type: 'through', prob: 0.90 }, { toArm: 2, toLane: 1, type: 'right', prob: 0.84 }], raw: [{ toArm: 1, toLane: 1, type: 'through', prob: 0.90 }, { toArm: 2, toLane: 1, type: 'right', prob: 0.84 }, { toArm: 2, toLane: 0, type: 'right', prob: 0.48 }] }}
              ]}
        ]
    },
    inter_2: {
        id: "128", name: "Glebe Point Rd & Francis St", location: "Glebe",
        lat: -33.8835982, lon: 151.1918044, zoom: 19, speedLimit: 50,
        description: "3-way T-junction. Glebe Point Rd (NW-SE, secondary) meets Francis St (NE). 1 lane per arm.",
        arms: [
            { name: "SE Approach (Glebe Point Rd)", street: "Glebe Point Rd", bearing: 130, approachLanes: 1, exitLanes: 1,
              lanes: [{ index: 0, turns: { processed: [{ toArm: 2, toLane: 0, type: 'through', prob: 0.94 }, { toArm: 1, toLane: 0, type: 'left', prob: 0.90 }], raw: [{ toArm: 2, toLane: 0, type: 'through', prob: 0.94 }, { toArm: 1, toLane: 0, type: 'left', prob: 0.90 }] }}]},
            { name: "NE Approach (Francis St)", street: "Francis St", bearing: 36, approachLanes: 1, exitLanes: 1,
              lanes: [{ index: 0, turns: { processed: [{ toArm: 2, toLane: 0, type: 'left', prob: 0.91 }, { toArm: 0, toLane: 0, type: 'right', prob: 0.88 }], raw: [{ toArm: 2, toLane: 0, type: 'left', prob: 0.91 }, { toArm: 0, toLane: 0, type: 'right', prob: 0.88 }, { toArm: 0, toLane: 0, type: 'through', prob: 0.52 }] }}]},
            { name: "NW Approach (Glebe Point Rd)", street: "Glebe Point Rd", bearing: 310, approachLanes: 1, exitLanes: 1,
              lanes: [{ index: 0, turns: { processed: [{ toArm: 0, toLane: 0, type: 'through', prob: 0.93 }, { toArm: 1, toLane: 0, type: 'right', prob: 0.89 }], raw: [{ toArm: 0, toLane: 0, type: 'through', prob: 0.93 }, { toArm: 1, toLane: 0, type: 'right', prob: 0.89 }] }}]}
        ]
    },
    inter_3: {
        id: "366", name: "Epping Rd & Balaclava Rd", location: "Macquarie Park",
        lat: -33.7777790, lon: 151.1081194, zoom: 18, speedLimit: 70,
        description: "Arterial dual-carriageway. Epping Rd (3-4 lanes/dir) meets Balaclava Rd. 2 dedicated right-turn lanes + left-turn slip lane.",
        arms: [
            { name: "NE Approach (Balaclava Rd)", street: "Balaclava Rd", bearing: 64, approachLanes: 3, exitLanes: 2,
              lanes: [
                { index: 0, turns: { processed: [{ toArm: 1, toLane: 0, type: 'left', prob: 0.95 }], raw: [{ toArm: 1, toLane: 0, type: 'left', prob: 0.95 }, { toArm: 2, toLane: 0, type: 'through', prob: 0.42 }] }},
                { index: 1, turns: { processed: [{ toArm: 2, toLane: 0, type: 'through', prob: 0.91 }], raw: [{ toArm: 2, toLane: 0, type: 'through', prob: 0.91 }] }},
                { index: 2, turns: { processed: [{ toArm: 2, toLane: 1, type: 'through', prob: 0.87 }, { toArm: 3, toLane: 1, type: 'right', prob: 0.84 }], raw: [{ toArm: 2, toLane: 1, type: 'through', prob: 0.87 }, { toArm: 3, toLane: 1, type: 'right', prob: 0.84 }] }}
              ]},
            { name: "SE Approach (Epping Rd)", street: "Epping Rd", bearing: 129, approachLanes: 4, exitLanes: 3,
              lanes: [
                { index: 0, turns: { processed: [{ toArm: 2, toLane: 0, type: 'left', prob: 0.96 }], raw: [{ toArm: 2, toLane: 0, type: 'left', prob: 0.96 }] }},
                { index: 1, turns: { processed: [{ toArm: 2, toLane: 1, type: 'left', prob: 0.91 }, { toArm: 3, toLane: 0, type: 'through', prob: 0.89 }], raw: [{ toArm: 2, toLane: 1, type: 'left', prob: 0.91 }, { toArm: 3, toLane: 0, type: 'through', prob: 0.89 }] }},
                { index: 2, turns: { processed: [{ toArm: 3, toLane: 1, type: 'through', prob: 0.93 }], raw: [{ toArm: 3, toLane: 1, type: 'through', prob: 0.93 }] }},
                { index: 3, turns: { processed: [{ toArm: 3, toLane: 2, type: 'through', prob: 0.88 }, { toArm: 0, toLane: 1, type: 'right', prob: 0.83 }], raw: [{ toArm: 3, toLane: 2, type: 'through', prob: 0.88 }, { toArm: 0, toLane: 1, type: 'right', prob: 0.83 }] }}
              ]},
            { name: "SW Approach (Balaclava Rd)", street: "Balaclava Rd", bearing: 240, approachLanes: 2, exitLanes: 3,
              lanes: [
                { index: 0, turns: { processed: [{ toArm: 3, toLane: 0, type: 'left', prob: 0.92 }, { toArm: 0, toLane: 0, type: 'through', prob: 0.87 }], raw: [{ toArm: 3, toLane: 0, type: 'left', prob: 0.92 }, { toArm: 0, toLane: 0, type: 'through', prob: 0.87 }] }},
                { index: 1, turns: { processed: [{ toArm: 0, toLane: 1, type: 'through', prob: 0.90 }, { toArm: 1, toLane: 1, type: 'right', prob: 0.85 }], raw: [{ toArm: 0, toLane: 1, type: 'through', prob: 0.90 }, { toArm: 1, toLane: 1, type: 'right', prob: 0.85 }] }}
              ]},
            { name: "NW Approach (Epping Rd)", street: "Epping Rd", bearing: 310, approachLanes: 4, exitLanes: 3,
              lanes: [
                { index: 0, turns: { processed: [{ toArm: 0, toLane: 0, type: 'left', prob: 0.94 }], raw: [{ toArm: 0, toLane: 0, type: 'left', prob: 0.94 }] }},
                { index: 1, turns: { processed: [{ toArm: 1, toLane: 0, type: 'through', prob: 0.92 }], raw: [{ toArm: 1, toLane: 0, type: 'through', prob: 0.92 }] }},
                { index: 2, turns: { processed: [{ toArm: 1, toLane: 1, type: 'through', prob: 0.90 }], raw: [{ toArm: 1, toLane: 1, type: 'through', prob: 0.90 }, { toArm: 2, toLane: 1, type: 'right', prob: 0.45 }] }},
                { index: 3, turns: { processed: [{ toArm: 2, toLane: 1, type: 'right', prob: 0.88 }], raw: [{ toArm: 2, toLane: 1, type: 'right', prob: 0.88 }, { toArm: 1, toLane: 2, type: 'through', prob: 0.51 }] }}
              ]}
        ]
    },
    inter_4: {
        id: "6762", name: "Parramatta Rd & Woodville Rd", location: "Granville",
        lat: -33.8275799, lon: 151.0047221, zoom: 18, speedLimit: 60,
        description: "High-volume junction. Church St (trunk, N), Parramatta Rd (trunk, 3-4 lanes/dir), Woodville Rd (primary, S, M4 access).",
        arms: [
            { name: "North Approach (Church St)", street: "Church St", bearing: 359, approachLanes: 3, exitLanes: 2,
              lanes: [
                { index: 0, turns: { processed: [{ toArm: 1, toLane: 0, type: 'left', prob: 0.95 }], raw: [{ toArm: 1, toLane: 0, type: 'left', prob: 0.95 }, { toArm: 2, toLane: 0, type: 'through', prob: 0.44 }] }},
                { index: 1, turns: { processed: [{ toArm: 2, toLane: 0, type: 'through', prob: 0.91 }], raw: [{ toArm: 2, toLane: 0, type: 'through', prob: 0.91 }] }},
                { index: 2, turns: { processed: [{ toArm: 2, toLane: 1, type: 'through', prob: 0.88 }, { toArm: 3, toLane: 1, type: 'right', prob: 0.85 }], raw: [{ toArm: 2, toLane: 1, type: 'through', prob: 0.88 }, { toArm: 3, toLane: 1, type: 'right', prob: 0.85 }] }}
              ]},
            { name: "ESE Approach (Parramatta Rd)", street: "Parramatta Rd", bearing: 111, approachLanes: 3, exitLanes: 3,
              lanes: [
                { index: 0, turns: { processed: [{ toArm: 2, toLane: 0, type: 'left', prob: 0.93 }], raw: [{ toArm: 2, toLane: 0, type: 'left', prob: 0.93 }, { toArm: 3, toLane: 0, type: 'through', prob: 0.39 }] }},
                { index: 1, turns: { processed: [{ toArm: 3, toLane: 0, type: 'through', prob: 0.90 }], raw: [{ toArm: 3, toLane: 0, type: 'through', prob: 0.90 }] }},
                { index: 2, turns: { processed: [{ toArm: 3, toLane: 1, type: 'through', prob: 0.87 }, { toArm: 0, toLane: 1, type: 'right', prob: 0.84 }], raw: [{ toArm: 3, toLane: 1, type: 'through', prob: 0.87 }, { toArm: 0, toLane: 1, type: 'right', prob: 0.84 }] }}
              ]},
            { name: "South Approach (Woodville Rd)", street: "Woodville Rd", bearing: 179, approachLanes: 3, exitLanes: 2,
              lanes: [
                { index: 0, turns: { processed: [{ toArm: 3, toLane: 0, type: 'left', prob: 0.91 }], raw: [{ toArm: 3, toLane: 0, type: 'left', prob: 0.91 }, { toArm: 0, toLane: 0, type: 'through', prob: 0.47 }] }},
                { index: 1, turns: { processed: [{ toArm: 0, toLane: 0, type: 'through', prob: 0.89 }], raw: [{ toArm: 0, toLane: 0, type: 'through', prob: 0.89 }] }},
                { index: 2, turns: { processed: [{ toArm: 0, toLane: 1, type: 'through', prob: 0.86 }, { toArm: 1, toLane: 1, type: 'right', prob: 0.83 }], raw: [{ toArm: 0, toLane: 1, type: 'through', prob: 0.86 }, { toArm: 1, toLane: 1, type: 'right', prob: 0.83 }] }}
              ]},
            { name: "WNW Approach (Parramatta Rd)", street: "Parramatta Rd", bearing: 282, approachLanes: 4, exitLanes: 3,
              lanes: [
                { index: 0, turns: { processed: [{ toArm: 0, toLane: 0, type: 'left', prob: 0.94 }], raw: [{ toArm: 0, toLane: 0, type: 'left', prob: 0.94 }] }},
                { index: 1, turns: { processed: [{ toArm: 1, toLane: 0, type: 'through', prob: 0.92 }], raw: [{ toArm: 1, toLane: 0, type: 'through', prob: 0.92 }] }},
                { index: 2, turns: { processed: [{ toArm: 1, toLane: 1, type: 'through', prob: 0.89 }], raw: [{ toArm: 1, toLane: 1, type: 'through', prob: 0.89 }, { toArm: 2, toLane: 1, type: 'right', prob: 0.43 }] }},
                { index: 3, turns: { processed: [{ toArm: 2, toLane: 1, type: 'right', prob: 0.87 }], raw: [{ toArm: 2, toLane: 1, type: 'right', prob: 0.87 }, { toArm: 1, toLane: 2, type: 'through', prob: 0.49 }] }}
              ]}
        ]
    }
};

// ---- Constants ----
const LANE_WIDTH_METERS = 3.5;  // standard lane width
const LANE_LENGTH_METERS = 35;  // how far lanes extend from center
const COLORS = {
    approach: '#3b82f6',
    exit: '#22c55e',
    divider: '#facc15',
    selected: '#e879f9',
    turnPath: '#f97316',
    leftArrow: '#facc15',
    throughArrow: '#ffffff',
    rightArrow: '#f97316'
};

const TURN_ICONS = { left: '↰', through: '↑', right: '↱' };
const TURN_LABELS = { left: 'Left Turn', through: 'Straight', right: 'Right Turn' };

// ---- Geo Utilities ----
function offsetLatLon(lat, lon, bearingDeg, distMeters) {
    const R = 6378137;
    const brng = bearingDeg * Math.PI / 180;
    const dLat = (distMeters * Math.cos(brng)) / R;
    const dLon = (distMeters * Math.sin(brng)) / (R * Math.cos(lat * Math.PI / 180));
    return [lat + dLat * 180 / Math.PI, lon + dLon * 180 / Math.PI];
}

function perpendicularOffset(lat, lon, bearingDeg, offsetMeters) {
    // Positive offset = bearing + 90 direction
    // For bearing 0° (north): positive → east (RIGHT side)
    // LHT Australia: approach on LEFT (negative), exit on RIGHT (positive)
    return offsetLatLon(lat, lon, bearingDeg + 90, offsetMeters);
}

// ---- Initialize Map ----
function initMap() {
    const inter = intersections[currentId];
    map = L.map('map', {
        center: [inter.lat, inter.lon],
        zoom: inter.zoom,
        zoomControl: false
    });

    // Zoom control bottom-right
    L.control.zoom({ position: 'bottomright' }).addTo(map);

    // Tile layers
    tileLayerSatellite = L.tileLayer(
        'https://mt1.google.com/vt/lyrs=s&x={x}&y={y}&z={z}',
        { maxZoom: 22, attribution: '© Google Maps' }
    );

    tileLayerOSM = L.tileLayer(
        'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',
        { maxZoom: 19, attribution: '© OpenStreetMap' }
    );

    tileLayerSatellite.addTo(map);

    // Layer groups
    laneLayer = L.layerGroup().addTo(map);
    turnPathLayer = L.layerGroup().addTo(map);

    // Event: click map to deselect
    map.on('click', function() {
        clearSelection();
    });

    // Draw intersection
    drawIntersection();
    updateInfo();

    // Dropdown event
    document.getElementById('intersection-select').addEventListener('change', function() {
        currentId = this.value;
        changeIntersection();
    });
}

// ---- Tile Layer Toggle ----
function setTileLayer(type) {
    currentTile = type;
    if (type === 'satellite') {
        map.removeLayer(tileLayerOSM);
        tileLayerSatellite.addTo(map);
    } else {
        map.removeLayer(tileLayerSatellite);
        tileLayerOSM.addTo(map);
    }
    document.getElementById('btn-satellite').classList.toggle('active', type === 'satellite');
    document.getElementById('btn-osm').classList.toggle('active', type === 'osm');
}

// ---- Data Mode Toggle ----
function setDataMode(mode) {
    dataMode = mode;
    document.getElementById('btn-processed').classList.toggle('active', mode === 'processed');
    document.getElementById('btn-raw').classList.toggle('active', mode === 'raw');
    clearSelection();
    drawIntersection();
}

// ---- Change Intersection ----
function changeIntersection() {
    const inter = intersections[currentId];
    map.setView([inter.lat, inter.lon], inter.zoom);
    clearSelection();
    drawIntersection();
    updateInfo();
}

// ---- Update Info Panel ----
function updateInfo() {
    const inter = intersections[currentId];
    document.getElementById('info-name').textContent = inter.name;
    document.getElementById('info-location').textContent = inter.location;
    document.getElementById('info-desc').textContent = inter.description;
}

// ---- Clear Selection ----
function clearSelection() {
    turnPathLayer.clearLayers();
    selectedLane = null;
    document.getElementById('turn-info').classList.add('hidden');
    // Redraw to reset colors
    drawIntersection();
}

function closeTurnInfo() {
    clearSelection();
}

// ============================================
//  DRAWING ENGINE
// ============================================

function drawIntersection() {
    laneLayer.clearLayers();
    turnPathLayer.clearLayers();

    const inter = intersections[currentId];
    const center = [inter.lat, inter.lon];

    inter.arms.forEach((arm, armIdx) => {
        drawArm(inter, arm, armIdx, center);
    });
}

function drawArm(inter, arm, armIdx, center) {
    const bearing = arm.bearing;
    // Bearing points AWAY from intersection along the arm
    // Approach traffic travels at oppBearing (toward intersection)
    const oppBearing = (bearing + 180) % 360;

    const totalApproach = arm.approachLanes;
    const totalExit = arm.exitLanes;

    // Arm near point (slightly offset from center to avoid overlap)
    const armNear = offsetLatLon(center[0], center[1], bearing, 8);
    // Arm far point (where lanes end, away from intersection)
    const armFar = offsetLatLon(center[0], center[1], bearing, LANE_LENGTH_METERS);

    // In LHT (Australia): approaching traffic drives on LEFT from driver's view.
    // Looking OUTWARD from intersection along bearing, driver's LEFT = RIGHT side.
    // So: approach = POSITIVE offset (RIGHT), exit = NEGATIVE offset (LEFT)

    // ---- Draw Approach Lanes (RIGHT side looking outward, positive offset) ----
    // In LHT: lane 0 (left-turn) is at the curb (largest offset), last lane (right-turn)
    // is nearest the divider (smallest offset).
    for (let i = 0; i < totalApproach; i++) {
        const laneOffset = (totalApproach - i - 0.5) * LANE_WIDTH_METERS;
        // Approach goes from far point toward intersection
        const startPt = perpendicularOffset(armFar[0], armFar[1], bearing, laneOffset);
        const endPt = perpendicularOffset(armNear[0], armNear[1], bearing, laneOffset);

        const isSelected = selectedLane && selectedLane.armIdx === armIdx && selectedLane.laneIdx === i;
        const color = isSelected ? COLORS.selected : COLORS.approach;

        const laneLine = L.polyline([startPt, endPt], {
            color: color,
            weight: 6,
            opacity: 0.85,
            lineCap: 'butt'
        });

        laneLine.on('click', function(e) {
            L.DomEvent.stopPropagation(e);
            selectLane(armIdx, i, inter);
        });

        // Tooltip showing lane assignment
        const lane = arm.lanes[i];
        if (lane) {
            const turns = lane.turns[dataMode];
            const labels = turns.map(t => TURN_ICONS[t.type] || '?').join(' ');
            laneLine.bindTooltip(
                `<b>${arm.street} — Lane ${i + 1}</b><br>${labels}`,
                { className: 'lane-tooltip', sticky: true }
            );
        }

        laneLayer.addLayer(laneLine);

        // Draw turn arrow marker at 40% along lane (closer to intersection)
        if (lane) {
            const turns = lane.turns[dataMode];
            const arrowFrac = 0.6; // 60% from far to near
            const midLat = armFar[0] + (armNear[0] - armFar[0]) * arrowFrac;
            const midLon = armFar[1] + (armNear[1] - armFar[1]) * arrowFrac;
            const midPt = perpendicularOffset(midLat, midLon, bearing, laneOffset);
            drawTurnArrows(midPt, oppBearing, turns);
        }
    }

    // ---- Draw Exit Lanes (LEFT side looking outward, negative offset) ----
    for (let i = 0; i < totalExit; i++) {
        const laneOffset = -(totalExit - i - 0.5) * LANE_WIDTH_METERS;
        // Exit goes from intersection outward
        const startPt = perpendicularOffset(armNear[0], armNear[1], bearing, laneOffset);
        const endPt = perpendicularOffset(armFar[0], armFar[1], bearing, laneOffset);

        const exitLine = L.polyline([startPt, endPt], {
            color: COLORS.exit,
            weight: 4,
            opacity: 0.5,
            lineCap: 'butt',
            dashArray: '10, 8'
        });
        laneLayer.addLayer(exitLine);
    }

    // ---- Draw center divider (between approach and exit, at offset 0) ----
    const divStart = [armNear[0], armNear[1]];
    const divEnd = [armFar[0], armFar[1]];
    const divider = L.polyline([divStart, divEnd], {
        color: COLORS.divider,
        weight: 2,
        opacity: 0.6,
        dashArray: '6, 10'
    });
    laneLayer.addLayer(divider);

    // ---- Street name label at arm end ----
    const labelPt = offsetLatLon(armFar[0], armFar[1], bearing, 8);
    const label = L.marker(labelPt, {
        icon: L.divIcon({
            className: 'arm-label',
            html: `<div style="transform:rotate(${bearing > 180 ? bearing - 270 : bearing - 90}deg)">${arm.street}</div>`,
            iconSize: [80, 20],
            iconAnchor: [40, 10]
        }),
        interactive: false
    });
    laneLayer.addLayer(label);
}

// ---- Draw Turn Arrow Markers ----
function drawTurnArrows(latlng, travelBearing, turns) {
    // travelBearing = direction the vehicle is moving (toward intersection)
    // Get unique turn types for this lane
    const types = [...new Set(turns.map(t => t.type))];
    const arrowText = types.map(t => {
        const icon = TURN_ICONS[t] || '?';
        const color = t === 'left' ? COLORS.leftArrow : t === 'right' ? COLORS.rightArrow : COLORS.throughArrow;
        return `<span style="color:${color};font-size:20px;font-weight:bold;text-shadow:0 0 6px rgba(0,0,0,0.9),0 0 12px rgba(0,0,0,0.5)">${icon}</span>`;
    }).join('');

    // Rotate so arrows face the travel direction
    // CSS rotate(0) = pointing up = north. travelBearing is degrees from north.
    const arrowMarker = L.marker(latlng, {
        icon: L.divIcon({
            className: '',
            html: `<div style="display:flex;gap:3px;transform:rotate(${travelBearing}deg);pointer-events:none">${arrowText}</div>`,
            iconSize: [types.length * 24, 24],
            iconAnchor: [types.length * 12, 12]
        }),
        interactive: false,
        zIndexOffset: 100
    });
    laneLayer.addLayer(arrowMarker);
}

// ============================================
//  LANE CLICK → SHOW TURN PATH
// ============================================

function selectLane(armIdx, laneIdx, inter) {
    clearSelection();
    selectedLane = { armIdx, laneIdx };

    const arm = inter.arms[armIdx];
    const lane = arm.lanes[laneIdx];
    if (!lane) return;

    const turns = lane.turns[dataMode];
    const center = [inter.lat, inter.lon];

    // Draw turn path curves
    turns.forEach(turn => {
        const destArm = inter.arms[turn.toArm];
        if (!destArm) return;

        // Source: approach lane position
        const srcBearing = arm.bearing;
        const srcOffset = computeLaneOffset(arm, laneIdx, false);
        const srcStart = offsetLatLon(center[0], center[1], srcBearing, LANE_LENGTH_METERS);
        const srcPt = perpendicularOffset(srcStart[0], srcStart[1], srcBearing, srcOffset);
        const srcMid = perpendicularOffset(
            offsetLatLon(center[0], center[1], srcBearing, 8)[0],
            offsetLatLon(center[0], center[1], srcBearing, 8)[1],
            srcBearing, srcOffset
        );

        // Destination: exit lane position
        const dstBearing = destArm.bearing;
        const dstOffset = computeLaneOffset(destArm, turn.toLane, true);
        const dstEnd = offsetLatLon(center[0], center[1], dstBearing, LANE_LENGTH_METERS);
        const dstPt = perpendicularOffset(dstEnd[0], dstEnd[1], dstBearing, dstOffset);
        const dstMid = perpendicularOffset(
            offsetLatLon(center[0], center[1], dstBearing, 8)[0],
            offsetLatLon(center[0], center[1], dstBearing, 8)[1],
            dstBearing, dstOffset
        );

        // Draw curved path: source → center area → destination
        const pathColor = turn.type === 'left' ? COLORS.leftArrow :
                          turn.type === 'right' ? COLORS.rightArrow : COLORS.throughArrow;

        const path = L.polyline([srcPt, srcMid, center, dstMid, dstPt], {
            color: pathColor,
            weight: 4,
            opacity: 0.9,
            dashArray: '10, 6',
            className: 'turn-path-anim'
        });
        turnPathLayer.addLayer(path);

        // Arrow at destination
        const destMarker = L.circleMarker(dstPt, {
            radius: 6,
            color: pathColor,
            fillColor: pathColor,
            fillOpacity: 0.9,
            weight: 2
        });
        turnPathLayer.addLayer(destMarker);
    });

    // Rebuild lanes to show selected state
    drawIntersection();

    // Show turn info panel
    showTurnInfo(arm, lane, inter);
}

function computeLaneOffset(arm, laneIdx, isExit) {
    // LHT: approach = positive (right looking outward), exit = negative (left looking outward)
    // Lane 0 = curb side (largest offset), last lane = divider side (smallest offset)
    if (isExit) {
        return -(arm.exitLanes - laneIdx - 0.5) * LANE_WIDTH_METERS;
    } else {
        return (arm.approachLanes - laneIdx - 0.5) * LANE_WIDTH_METERS;
    }
}

// ---- Turn Info Panel ----
function showTurnInfo(arm, lane, inter) {
    const turns = lane.turns[dataMode];
    const panel = document.getElementById('turn-info');
    const title = document.getElementById('turn-info-title');
    const body = document.getElementById('turn-info-body');

    title.textContent = `${arm.street} — Lane ${lane.index + 1}`;

    let html = '';
    turns.forEach(turn => {
        const destArm = inter.arms[turn.toArm];
        const icon = TURN_ICONS[turn.type] || '?';
        const typeClass = turn.type;
        const destName = destArm ? destArm.street : 'Unknown';
        const label = TURN_LABELS[turn.type] || turn.type;
        const prob = Math.round(turn.prob * 100);

        html += `
            <div class="turn-item">
                <div class="turn-icon ${typeClass}">${icon}</div>
                <div class="turn-detail">
                    <div class="turn-type">${label}</div>
                    <div class="turn-dest">→ ${destName} (Lane ${turn.toLane + 1})</div>
                </div>
                <div class="turn-prob">${prob}%</div>
            </div>
        `;
    });

    body.innerHTML = html;
    panel.classList.remove('hidden');
}

// ---- Init ----
document.addEventListener('DOMContentLoaded', initMap);
