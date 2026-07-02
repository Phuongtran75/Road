// ============================================
//  Lane Topology — Standalone Map Demo
// ============================================

// ---- Intersection Data (OSM-verified) ----

const intersections = {
    inter_1: {
        id: "53585",
        name: "Elizabeth St & Park St",
        location: "Sydney CBD",
        lat: -33.8732858,
        lon: 151.2099114,
        zoom: 19,
        speedLimit: 40,
        description: "4-way signalised CBD intersection. Elizabeth St (N-S, secondary, 3 NB + 2 SB lanes) crosses Park St (E-W, secondary, 3 EB + 2 WB lanes). Adjacent to Hyde Park.",
        arms: [
            {
                name: "North (Elizabeth St)", street: "Elizabeth St", bearing: 352,
                approachLanes: 3, exitLanes: 2,
                lanes: [
                    { index: 0, turns: {
                        processed: [
                            { toArm: 1, toLane: 0, type: 'left', prob: 0.95 }
                        ],
                        raw: [
                            { toArm: 1, toLane: 0, type: 'left', prob: 0.95 },
                            { toArm: 2, toLane: 0, type: 'through', prob: 0.41 }
                        ]
                    }},
                    { index: 1, turns: {
                        processed: [
                            { toArm: 2, toLane: 0, type: 'through', prob: 0.93 }
                        ],
                        raw: [
                            { toArm: 2, toLane: 0, type: 'through', prob: 0.93 },
                            { toArm: 1, toLane: 0, type: 'left', prob: 0.38 }
                        ]
                    }},
                    { index: 2, turns: {
                        processed: [
                            { toArm: 2, toLane: 1, type: 'through', prob: 0.90 },
                            { toArm: 3, toLane: 1, type: 'right', prob: 0.87 }
                        ],
                        raw: [
                            { toArm: 2, toLane: 1, type: 'through', prob: 0.90 },
                            { toArm: 3, toLane: 1, type: 'right', prob: 0.87 }
                        ]
                    }}
                ]
            },
            {
                name: "East (Park St)", street: "Park St", bearing: 100,
                approachLanes: 3, exitLanes: 2,
                lanes: [
                    { index: 0, turns: {
                        processed: [
                            { toArm: 2, toLane: 0, type: 'left', prob: 0.94 }
                        ],
                        raw: [
                            { toArm: 2, toLane: 0, type: 'left', prob: 0.94 },
                            { toArm: 3, toLane: 0, type: 'through', prob: 0.35 }
                        ]
                    }},
                    { index: 1, turns: {
                        processed: [
                            { toArm: 3, toLane: 0, type: 'through', prob: 0.92 }
                        ],
                        raw: [
                            { toArm: 3, toLane: 0, type: 'through', prob: 0.92 }
                        ]
                    }},
                    { index: 2, turns: {
                        processed: [
                            { toArm: 3, toLane: 1, type: 'through', prob: 0.88 },
                            { toArm: 0, toLane: 1, type: 'right', prob: 0.85 }
                        ],
                        raw: [
                            { toArm: 3, toLane: 1, type: 'through', prob: 0.88 },
                            { toArm: 0, toLane: 1, type: 'right', prob: 0.85 },
                            { toArm: 0, toLane: 0, type: 'right', prob: 0.52 }
                        ]
                    }}
                ]
            },
            {
                name: "South (Elizabeth St)", street: "Elizabeth St", bearing: 172,
                approachLanes: 2, exitLanes: 3,
                lanes: [
                    { index: 0, turns: {
                        processed: [
                            { toArm: 3, toLane: 0, type: 'left', prob: 0.92 },
                            { toArm: 0, toLane: 0, type: 'through', prob: 0.88 }
                        ],
                        raw: [
                            { toArm: 3, toLane: 0, type: 'left', prob: 0.92 },
                            { toArm: 0, toLane: 0, type: 'through', prob: 0.88 }
                        ]
                    }},
                    { index: 1, turns: {
                        processed: [
                            { toArm: 0, toLane: 1, type: 'through', prob: 0.91 },
                            { toArm: 1, toLane: 1, type: 'right', prob: 0.86 }
                        ],
                        raw: [
                            { toArm: 0, toLane: 1, type: 'through', prob: 0.91 },
                            { toArm: 1, toLane: 1, type: 'right', prob: 0.86 }
                        ]
                    }}
                ]
            },
            {
                name: "West (Park St)", street: "Park St", bearing: 280,
                approachLanes: 2, exitLanes: 3,
                lanes: [
                    { index: 0, turns: {
                        processed: [
                            { toArm: 0, toLane: 0, type: 'left', prob: 0.93 },
                            { toArm: 1, toLane: 0, type: 'through', prob: 0.89 }
                        ],
                        raw: [
                            { toArm: 0, toLane: 0, type: 'left', prob: 0.93 },
                            { toArm: 1, toLane: 0, type: 'through', prob: 0.89 }
                        ]
                    }},
                    { index: 1, turns: {
                        processed: [
                            { toArm: 1, toLane: 1, type: 'through', prob: 0.90 },
                            { toArm: 2, toLane: 1, type: 'right', prob: 0.84 }
                        ],
                        raw: [
                            { toArm: 1, toLane: 1, type: 'through', prob: 0.90 },
                            { toArm: 2, toLane: 1, type: 'right', prob: 0.84 },
                            { toArm: 2, toLane: 0, type: 'right', prob: 0.48 }
                        ]
                    }}
                ]
            }
        ]
    },
    inter_2: {
        id: "128",
        name: "Glebe Point Rd & Francis St",
        location: "Glebe",
        lat: -33.8835982,
        lon: 151.1918044,
        zoom: 19,
        speedLimit: 50,
        description: "3-way T-junction. Glebe Point Road (NW-SE, secondary) meets Francis Street (NE, residential).",
        arms: [
            {
                name: "SE (Glebe Point Rd)", street: "Glebe Point Rd", bearing: 130,
                approachLanes: 1, exitLanes: 1,
                lanes: [
                    { index: 0, turns: {
                        processed: [
                            { toArm: 2, toLane: 0, type: 'through', prob: 0.94 },
                            { toArm: 1, toLane: 0, type: 'left', prob: 0.90 }
                        ],
                        raw: [
                            { toArm: 2, toLane: 0, type: 'through', prob: 0.94 },
                            { toArm: 1, toLane: 0, type: 'left', prob: 0.90 }
                        ]
                    }}
                ]
            },
            {
                name: "NE (Francis St)", street: "Francis St", bearing: 36,
                approachLanes: 1, exitLanes: 1,
                lanes: [
                    { index: 0, turns: {
                        processed: [
                            { toArm: 2, toLane: 0, type: 'left', prob: 0.91 },
                            { toArm: 0, toLane: 0, type: 'right', prob: 0.88 }
                        ],
                        raw: [
                            { toArm: 2, toLane: 0, type: 'left', prob: 0.91 },
                            { toArm: 0, toLane: 0, type: 'right', prob: 0.88 },
                            { toArm: 0, toLane: 0, type: 'through', prob: 0.52 }
                        ]
                    }}
                ]
            },
            {
                name: "NW (Glebe Point Rd)", street: "Glebe Point Rd", bearing: 310,
                approachLanes: 1, exitLanes: 1,
                lanes: [
                    { index: 0, turns: {
                        processed: [
                            { toArm: 0, toLane: 0, type: 'through', prob: 0.93 },
                            { toArm: 1, toLane: 0, type: 'right', prob: 0.89 }
                        ],
                        raw: [
                            { toArm: 0, toLane: 0, type: 'through', prob: 0.93 },
                            { toArm: 1, toLane: 0, type: 'right', prob: 0.89 }
                        ]
                    }}
                ]
            }
        ]
    },
    inter_3: {
        id: "366",
        name: "Epping Rd & Balaclava Rd",
        location: "Macquarie Park",
        lat: -33.7777790,
        lon: 151.1081194,
        zoom: 18,
        speedLimit: 70,
        description: "Arterial dual-carriageway crossing. Epping Rd (NW-SE, primary, 3-4 lanes/dir) meets Balaclava Rd (NE-SW, secondary). Features 2 dedicated right-turn lanes and left-turn slip lane.",
        arms: [
            {
                name: "NE (Balaclava Rd)", street: "Balaclava Rd", bearing: 64,
                approachLanes: 3, exitLanes: 2,
                lanes: [
                    { index: 0, turns: { processed: [{ toArm: 1, toLane: 0, type: 'left', prob: 0.95 }], raw: [{ toArm: 1, toLane: 0, type: 'left', prob: 0.95 }, { toArm: 2, toLane: 0, type: 'through', prob: 0.42 }] }},
                    { index: 1, turns: { processed: [{ toArm: 2, toLane: 0, type: 'through', prob: 0.91 }], raw: [{ toArm: 2, toLane: 0, type: 'through', prob: 0.91 }] }},
                    { index: 2, turns: { processed: [{ toArm: 2, toLane: 1, type: 'through', prob: 0.87 }, { toArm: 3, toLane: 1, type: 'right', prob: 0.84 }], raw: [{ toArm: 2, toLane: 1, type: 'through', prob: 0.87 }, { toArm: 3, toLane: 1, type: 'right', prob: 0.84 }] }}
                ]
            },
            {
                name: "SE (Epping Rd)", street: "Epping Rd", bearing: 129,
                approachLanes: 4, exitLanes: 3,
                lanes: [
                    { index: 0, turns: { processed: [{ toArm: 2, toLane: 0, type: 'left', prob: 0.96 }], raw: [{ toArm: 2, toLane: 0, type: 'left', prob: 0.96 }] }},
                    { index: 1, turns: { processed: [{ toArm: 2, toLane: 1, type: 'left', prob: 0.91 }, { toArm: 3, toLane: 0, type: 'through', prob: 0.89 }], raw: [{ toArm: 2, toLane: 1, type: 'left', prob: 0.91 }, { toArm: 3, toLane: 0, type: 'through', prob: 0.89 }] }},
                    { index: 2, turns: { processed: [{ toArm: 3, toLane: 1, type: 'through', prob: 0.93 }], raw: [{ toArm: 3, toLane: 1, type: 'through', prob: 0.93 }] }},
                    { index: 3, turns: { processed: [{ toArm: 3, toLane: 2, type: 'through', prob: 0.88 }, { toArm: 0, toLane: 1, type: 'right', prob: 0.83 }], raw: [{ toArm: 3, toLane: 2, type: 'through', prob: 0.88 }, { toArm: 0, toLane: 1, type: 'right', prob: 0.83 }] }}
                ]
            },
            {
                name: "SW (Balaclava Rd)", street: "Balaclava Rd", bearing: 240,
                approachLanes: 2, exitLanes: 3,
                lanes: [
                    { index: 0, turns: { processed: [{ toArm: 3, toLane: 0, type: 'left', prob: 0.92 }, { toArm: 0, toLane: 0, type: 'through', prob: 0.87 }], raw: [{ toArm: 3, toLane: 0, type: 'left', prob: 0.92 }, { toArm: 0, toLane: 0, type: 'through', prob: 0.87 }] }},
                    { index: 1, turns: { processed: [{ toArm: 0, toLane: 1, type: 'through', prob: 0.90 }, { toArm: 1, toLane: 1, type: 'right', prob: 0.85 }], raw: [{ toArm: 0, toLane: 1, type: 'through', prob: 0.90 }, { toArm: 1, toLane: 1, type: 'right', prob: 0.85 }] }}
                ]
            },
            {
                name: "NW (Epping Rd)", street: "Epping Rd", bearing: 310,
                approachLanes: 4, exitLanes: 3,
                lanes: [
                    { index: 0, turns: { processed: [{ toArm: 0, toLane: 0, type: 'left', prob: 0.94 }], raw: [{ toArm: 0, toLane: 0, type: 'left', prob: 0.94 }] }},
                    { index: 1, turns: { processed: [{ toArm: 1, toLane: 0, type: 'through', prob: 0.92 }], raw: [{ toArm: 1, toLane: 0, type: 'through', prob: 0.92 }] }},
                    { index: 2, turns: { processed: [{ toArm: 1, toLane: 1, type: 'through', prob: 0.90 }], raw: [{ toArm: 1, toLane: 1, type: 'through', prob: 0.90 }, { toArm: 2, toLane: 1, type: 'right', prob: 0.45 }] }},
                    { index: 3, turns: { processed: [{ toArm: 2, toLane: 1, type: 'right', prob: 0.88 }], raw: [{ toArm: 2, toLane: 1, type: 'right', prob: 0.88 }, { toArm: 1, toLane: 2, type: 'through', prob: 0.51 }] }}
                ]
            }
        ]
    },
    inter_4: {
        id: "6762",
        name: "Parramatta Rd & Woodville Rd",
        location: "Granville",
        lat: -33.8275799,
        lon: 151.0047221,
        zoom: 18,
        speedLimit: 60,
        description: "High-volume junction: Church St (trunk, N), Parramatta Rd (trunk, ESE/WNW, 3-4 lanes/dir), Woodville Rd (primary, S, with M4 access). Features additional right-turn and left-turn bays.",
        arms: [
            {
                name: "North (Church St)", street: "Church St", bearing: 359,
                approachLanes: 3, exitLanes: 2,
                lanes: [
                    { index: 0, turns: { processed: [{ toArm: 1, toLane: 0, type: 'left', prob: 0.95 }], raw: [{ toArm: 1, toLane: 0, type: 'left', prob: 0.95 }, { toArm: 2, toLane: 0, type: 'through', prob: 0.44 }] }},
                    { index: 1, turns: { processed: [{ toArm: 2, toLane: 0, type: 'through', prob: 0.91 }], raw: [{ toArm: 2, toLane: 0, type: 'through', prob: 0.91 }] }},
                    { index: 2, turns: { processed: [{ toArm: 2, toLane: 1, type: 'through', prob: 0.88 }, { toArm: 3, toLane: 1, type: 'right', prob: 0.85 }], raw: [{ toArm: 2, toLane: 1, type: 'through', prob: 0.88 }, { toArm: 3, toLane: 1, type: 'right', prob: 0.85 }] }}
                ]
            },
            {
                name: "ESE (Parramatta Rd)", street: "Parramatta Rd", bearing: 111,
                approachLanes: 3, exitLanes: 3,
                lanes: [
                    { index: 0, turns: { processed: [{ toArm: 2, toLane: 0, type: 'left', prob: 0.93 }], raw: [{ toArm: 2, toLane: 0, type: 'left', prob: 0.93 }, { toArm: 3, toLane: 0, type: 'through', prob: 0.39 }] }},
                    { index: 1, turns: { processed: [{ toArm: 3, toLane: 0, type: 'through', prob: 0.90 }], raw: [{ toArm: 3, toLane: 0, type: 'through', prob: 0.90 }] }},
                    { index: 2, turns: { processed: [{ toArm: 3, toLane: 1, type: 'through', prob: 0.87 }, { toArm: 0, toLane: 1, type: 'right', prob: 0.84 }], raw: [{ toArm: 3, toLane: 1, type: 'through', prob: 0.87 }, { toArm: 0, toLane: 1, type: 'right', prob: 0.84 }] }}
                ]
            },
            {
                name: "South (Woodville Rd)", street: "Woodville Rd", bearing: 179,
                approachLanes: 3, exitLanes: 2,
                lanes: [
                    { index: 0, turns: { processed: [{ toArm: 3, toLane: 0, type: 'left', prob: 0.91 }], raw: [{ toArm: 3, toLane: 0, type: 'left', prob: 0.91 }, { toArm: 0, toLane: 0, type: 'through', prob: 0.47 }] }},
                    { index: 1, turns: { processed: [{ toArm: 0, toLane: 0, type: 'through', prob: 0.89 }], raw: [{ toArm: 0, toLane: 0, type: 'through', prob: 0.89 }] }},
                    { index: 2, turns: { processed: [{ toArm: 0, toLane: 1, type: 'through', prob: 0.86 }, { toArm: 1, toLane: 1, type: 'right', prob: 0.83 }], raw: [{ toArm: 0, toLane: 1, type: 'through', prob: 0.86 }, { toArm: 1, toLane: 1, type: 'right', prob: 0.83 }] }}
                ]
            },
            {
                name: "WNW (Parramatta Rd)", street: "Parramatta Rd", bearing: 282,
                approachLanes: 4, exitLanes: 3,
                lanes: [
                    { index: 0, turns: { processed: [{ toArm: 0, toLane: 0, type: 'left', prob: 0.94 }], raw: [{ toArm: 0, toLane: 0, type: 'left', prob: 0.94 }] }},
                    { index: 1, turns: { processed: [{ toArm: 1, toLane: 0, type: 'through', prob: 0.92 }], raw: [{ toArm: 1, toLane: 0, type: 'through', prob: 0.92 }] }},
                    { index: 2, turns: { processed: [{ toArm: 1, toLane: 1, type: 'through', prob: 0.89 }], raw: [{ toArm: 1, toLane: 1, type: 'through', prob: 0.89 }, { toArm: 2, toLane: 1, type: 'right', prob: 0.43 }] }},
                    { index: 3, turns: { processed: [{ toArm: 2, toLane: 1, type: 'right', prob: 0.87 }], raw: [{ toArm: 2, toLane: 1, type: 'right', prob: 0.87 }, { toArm: 1, toLane: 2, type: 'through', prob: 0.49 }] }}
                ]
            }
        ]
    }
};

// ---- State ----
let map = null;
let currentId = 'inter_1';
let mode = 'processed';
let activeLanes = [];
let activeTurns = [];
let selectedLane = null;
let selectedLaneData = null;
let markers = {};

// ---- Initialize ----
document.addEventListener('DOMContentLoaded', initMap);

function initMap() {
    const inter = intersections[currentId];

    // Populate dropdown
    const select = document.getElementById('intersection-select');
    Object.entries(intersections).forEach(([id, data]) => {
        const opt = document.createElement('option');
        opt.value = id;
        opt.textContent = `${data.name} — ${data.location}`;
        select.appendChild(opt);
    });

    // Base layers
    const googleSat = L.tileLayer('https://{s}.google.com/vt/lyrs=s&x={x}&y={y}&z={z}', {
        maxZoom: 21, subdomains: ['mt0','mt1','mt2','mt3'],
        attribution: '&copy; Google Maps'
    });

    const googleHybrid = L.tileLayer('https://{s}.google.com/vt/lyrs=y&x={x}&y={y}&z={z}', {
        maxZoom: 21, subdomains: ['mt0','mt1','mt2','mt3'],
        attribution: '&copy; Google Maps'
    });

    const osm = L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        maxZoom: 19,
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
    });

    const esri = L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}', {
        maxZoom: 19,
        attribution: 'Tiles &copy; Esri'
    });

    map = L.map('map', {
        zoomControl: true,
        layers: [googleSat]
    }).setView([inter.lat, inter.lon], inter.zoom);

    L.control.layers({
        "Google Satellite": googleSat,
        "Google Hybrid": googleHybrid,
        "OpenStreetMap": osm,
        "Esri Satellite": esri
    }, null, { position: 'bottomright' }).addTo(map);

    // Draw all markers
    drawMarkers();

    // Render first intersection
    renderIntersection(currentId);
}

// ---- Markers ----
function drawMarkers() {
    Object.entries(intersections).forEach(([id, inter]) => {
        const icon = L.divIcon({
            className: 'custom-map-marker',
            html: '<div class="marker-pulse"></div><div class="marker-dot"></div>',
            iconSize: [20, 20], iconAnchor: [10, 10]
        });

        const m = L.marker([inter.lat, inter.lon], { icon }).addTo(map);

        m.bindPopup(`
            <div style="font-family: var(--font-sans); padding: 4px; width: 200px;">
                <h4 style="margin:0 0 4px; color:#3b82f6; font-size:0.88rem; font-weight:600;">${inter.name}</h4>
                <p style="margin:0 0 4px; font-size:0.75rem; color:#94a3b8;">${inter.location} · OSM ${inter.id}</p>
                <p style="margin:0 0 8px; font-size:0.7rem; color:#64748b; line-height:1.4;">${inter.description}</p>
                <button onclick="flyToIntersection('${id}')" style="width:100%;border:none;background:#3b82f6;color:white;padding:6px;border-radius:8px;font-size:0.78rem;cursor:pointer;font-weight:500;font-family:var(--font-sans);">
                    Load Lanes
                </button>
            </div>
        `);

        markers[id] = m;
    });
}

function flyToIntersection(id) {
    document.getElementById('intersection-select').value = id;
    selectIntersection(id);
}

// ---- Intersection Selection ----
function selectIntersection(id) {
    currentId = id;
    const inter = intersections[id];
    if (!map || !inter) return;

    map.closePopup();
    map.flyTo([inter.lat, inter.lon], inter.zoom, { duration: 1.2 });

    setTimeout(() => renderIntersection(id), 400);
}

// ---- Mode Toggle ----
function setMode(m) {
    mode = m;
    document.getElementById('btn-processed').classList.toggle('active', m === 'processed');
    document.getElementById('btn-raw').classList.toggle('active', m === 'raw');

    clearTurns();
    if (selectedLaneData) {
        drawTurns(selectedLaneData.armIdx, selectedLaneData.laneData);
    }
}

// ---- Panel Toggle ----
function togglePanel() {
    document.getElementById('control-panel').classList.toggle('collapsed');
}

// ---- Clear Functions ----
function clearLanes() {
    activeLanes.forEach(l => map.removeLayer(l));
    activeLanes = [];
}

function clearTurns() {
    activeTurns.forEach(l => map.removeLayer(l));
    activeTurns = [];
}

// ---- Render Intersection ----
function renderIntersection(id) {
    clearLanes();
    clearTurns();
    selectedLane = null;
    selectedLaneData = null;

    const inter = intersections[id];
    if (!inter) return;

    // Update info panel
    const infoGrid = document.getElementById('info-grid');
    infoGrid.innerHTML = `
        <div class="info-row"><span class="label">Name</span><span class="value" style="font-family:var(--font-sans)">${inter.name}</span></div>
        <div class="info-row"><span class="label">Location</span><span class="value" style="font-family:var(--font-sans)">${inter.location}</span></div>
        <div class="info-row"><span class="label">OSM ID</span><span class="value">${inter.id}</span></div>
        <div class="info-row"><span class="label">Coordinates</span><span class="value">${inter.lat.toFixed(5)}, ${inter.lon.toFixed(5)}</span></div>
        <div class="info-row"><span class="label">Arms</span><span class="value">${inter.arms.length}</span></div>
        <div class="info-row"><span class="label">Speed Limit</span><span class="value">${inter.speedLimit} km/h</span></div>
        <div class="info-description">${inter.description}</div>
    `;

    // Hide turn info
    document.getElementById('turn-info-section').style.display = 'none';

    // Show tooltip
    const tooltip = document.getElementById('map-tooltip');
    tooltip.classList.remove('hidden');
    tooltip.innerHTML = 'Click an <strong>approach lane</strong> (blue) to see predicted turn connections';

    // Geometry
    const centerLat = inter.lat;
    const centerLon = inter.lon;
    const scaleLat = 0.000009;
    const scaleLon = 0.000009 / Math.cos(centerLat * Math.PI / 180);
    const laneWidth = 3.2;
    const stopDist = 12.0;
    const armLen = 55.0;

    inter.arms.forEach((arm, armIdx) => {
        const rad = arm.bearing * Math.PI / 180;
        const outLat = Math.cos(rad), outLon = Math.sin(rad);
        const pRad = (arm.bearing - 90) * Math.PI / 180;
        const pLat = Math.cos(pRad), pLon = Math.sin(pRad);

        // Exit lanes (green) — LEFT side for LHT
        arm.exitLanePts = [];
        for (let i = 0; i < arm.exitLanes; i++) {
            const off = (i + 0.5) * laneWidth;
            const oLat = pLat * off * scaleLat;
            const oLon = pLon * off * scaleLon;

            const stopPt = [centerLat + outLat * stopDist * scaleLat + oLat, centerLon + outLon * stopDist * scaleLon + oLon];
            const endPt  = [centerLat + outLat * armLen * scaleLat + oLat, centerLon + outLon * armLen * scaleLon + oLon];

            arm.exitLanePts[i] = stopPt;

            const poly = L.polyline([stopPt, endPt], {
                color: '#10b981', weight: 4, opacity: 0.8, lineCap: 'round'
            }).addTo(map);
            poly.bindTooltip(`Exit Lane ${i + 1}`, { sticky: true });
            activeLanes.push(poly);
        }

        // Approach lanes (blue) — RIGHT side for LHT
        arm.approachLanePts = [];
        for (let i = 0; i < arm.approachLanes; i++) {
            const off = -(i + 0.5) * laneWidth;
            const oLat = pLat * off * scaleLat;
            const oLon = pLon * off * scaleLon;

            const startPt = [centerLat + outLat * armLen * scaleLat + oLat, centerLon + outLon * armLen * scaleLon + oLon];
            const stopPt  = [centerLat + outLat * stopDist * scaleLat + oLat, centerLon + outLon * stopDist * scaleLon + oLon];

            arm.approachLanePts[i] = stopPt;

            const laneData = arm.lanes[i] || { index: i, turns: { processed: [], raw: [] } };

            const poly = L.polyline([startPt, stopPt], {
                color: '#3b82f6', weight: 5, opacity: 0.8, lineCap: 'round'
            }).addTo(map);

            poly.bindTooltip(`${arm.name} · Lane ${i + 1}`, { sticky: true });

            poly.on('mouseover', function() {
                if (selectedLane !== this) this.setStyle({ color: '#60a5fa', weight: 7 });
            });
            poly.on('mouseout', function() {
                if (selectedLane !== this) this.setStyle({ color: '#3b82f6', weight: 5 });
            });

            poly.on('click', function() {
                if (selectedLane) selectedLane.setStyle({ color: '#3b82f6', weight: 5 });
                selectedLane = this;
                selectedLaneData = { armIdx, laneData };
                this.setStyle({ color: '#f59e0b', weight: 7 });
                drawTurns(armIdx, laneData);
                showTurnDetails(armIdx, laneData);
            });

            activeLanes.push(poly);
        }
    });
}

// ---- Draw Turn Curves ----
function drawTurns(armIdx, laneData) {
    clearTurns();

    const inter = intersections[currentId];
    const arm = inter.arms[armIdx];
    const startPt = arm.approachLanePts[laneData.index];
    if (!startPt) return;

    const turns = mode === 'processed' ? laneData.turns.processed : laneData.turns.raw;

    turns.forEach(turn => {
        const exitArm = inter.arms[turn.toArm];
        const endPt = exitArm ? exitArm.exitLanePts[turn.toLane] : null;
        if (!endPt) return;

        const controlPt = [inter.lat, inter.lon];
        const curve = [];
        const steps = 15;

        for (let j = 0; j <= steps; j++) {
            const t = j / steps;
            curve.push([
                (1-t)*(1-t)*startPt[0] + 2*(1-t)*t*controlPt[0] + t*t*endPt[0],
                (1-t)*(1-t)*startPt[1] + 2*(1-t)*t*controlPt[1] + t*t*endPt[1]
            ]);
        }

        let color = '#6366f1';
        if (turn.type === 'left') color = '#ef4444';
        if (turn.type === 'right') color = '#f59e0b';

        const flow = L.polyline(curve, {
            color, weight: 3, opacity: 0.9, className: 'animated-flow'
        }).addTo(map);

        const base = L.polyline(curve, {
            color, weight: 5, opacity: 0.3
        }).addTo(map);

        const label = turn.type.charAt(0).toUpperCase() + turn.type.slice(1);
        const popup = `<div style="font-family:var(--font-sans);padding:2px;">
            <strong style="color:${color}">${label} Turn</strong><br>
            <span style="font-family:var(--font-mono);font-size:0.82rem;">P = ${turn.prob.toFixed(2)}</span>
            ${mode === 'raw' && turn.prob < 0.7 ? '<br><span style="color:#ef4444;font-size:0.75rem;">⚠ Low confidence / potential illegal</span>' : ''}
        </div>`;
        flow.bindPopup(popup);
        base.bindPopup(popup);

        activeTurns.push(flow, base);
    });

    // Update tooltip
    const tooltip = document.getElementById('map-tooltip');
    tooltip.innerHTML = `Showing <strong>${turns.length}</strong> turn${turns.length !== 1 ? 's' : ''} from <strong>${inter.arms[armIdx].name}</strong> · Lane ${laneData.index + 1}`;
}

// ---- Show Turn Details in Panel ----
function showTurnDetails(armIdx, laneData) {
    const inter = intersections[currentId];
    const arm = inter.arms[armIdx];
    const turns = mode === 'processed' ? laneData.turns.processed : laneData.turns.raw;

    const section = document.getElementById('turn-info-section');
    const container = document.getElementById('turn-details');

    if (turns.length === 0) {
        section.style.display = 'block';
        container.innerHTML = '<div style="font-size:0.75rem;color:var(--text-muted);padding:8px 0;">No turns predicted</div>';
        return;
    }

    section.style.display = 'block';
    container.innerHTML = turns.map(turn => {
        const exitArm = inter.arms[turn.toArm];
        const street = exitArm ? exitArm.street : '?';
        const warn = mode === 'raw' && turn.prob < 0.7;
        return `
            <div class="turn-card">
                <span class="turn-badge ${turn.type}">${turn.type}</span>
                <div class="turn-meta">
                    <div class="turn-street">→ ${street}</div>
                    <div class="turn-prob">P = ${turn.prob.toFixed(2)}</div>
                    ${warn ? '<div class="turn-warn">⚠ Low confidence</div>' : ''}
                </div>
            </div>
        `;
    }).join('');
}
