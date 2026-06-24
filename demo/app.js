// ============================================
//  Lane Topology Demo — Application Logic
// ============================================

// ---- DATA ----

const evaluationData = {
    version_18: {
        turn: { f1: 0.3187, precision: 0.2505, recall: 0.4381 },
        slot: {
            left:     { f1: 0.6454 },
            through:  { f1: 0.6456 },
            right:    { f1: 0.5624 },
            approach: { f1: 0.7407 }
        },
        arm: {
            L:    { f1: 0.1135 },
            LT:   { f1: 0.6196 },
            T:    { f1: 0.2565 },
            TR:   { f1: 0.5583 },
            R:    { f1: 0.1756 },
            mean: { f1: 0.3902 }
        }
    },
    version_41: {
        turn: { f1: 0.4149, precision: 0.3539, recall: 0.5013 },
        slot: {
            left:     { f1: 0.6738 },
            through:  { f1: 0.7003 },
            right:    { f1: 0.6729 },
            approach: { f1: 0.8100 }
        },
        arm: {
            L:    { f1: 0.1434 },
            LT:   { f1: 0.5580 },
            T:    { f1: 0.1866 },
            TR:   { f1: 0.4553 },
            R:    { f1: 0.1392 },
            mean: { f1: 0.3658 }
        }
    },
    version_43: {
        turn: { f1: 0.4311, precision: 0.4421, recall: 0.4206 },
        slot: {
            left:     { f1: 0.6094 },
            through:  { f1: 0.6948 },
            right:    { f1: 0.6142 },
            approach: { f1: 0.7968 }
        },
        arm: {
            L:    { f1: 0.0995 },
            LT:   { f1: 0.4862 },
            T:    { f1: 0.2935 },
            TR:   { f1: 0.4471 },
            R:    { f1: 0.1238 },
            mean: { f1: 0.3503 }
        }
    },
    version_45: {
        turn: { f1: 0.4902, precision: 0.4680, recall: 0.5146 },
        slot: {
            left:     { f1: 0.6823 },
            through:  { f1: 0.8136 },
            right:    { f1: 0.6414 },
            approach: { f1: 0.8006 }
        },
        arm: {
            L:    { f1: 0.0163 },
            LT:   { f1: 0.6864 },
            T:    { f1: 0.4644 },
            TR:   { f1: 0.5897 },
            R:    { f1: 0.0648 },
            mean: { f1: 0.4845 }
        }
    }
};

const baseline = {
    L:    { f1: 0.5680 },
    LT:   { f1: 0.8370 },
    T:    { f1: 0.6087 },
    TR:   { f1: 0.7239 },
    R:    { f1: 0.4768 },
    mean: { f1: 0.6890 }
};

const laneTypes = [
    { type: 'LT-type',  count: 1728, color: '#6366f1' },
    { type: 'T-type',   count: 1605, color: '#818cf8' },
    { type: 'TR-type',  count: 1358, color: '#2dd4bf' },
    { type: 'R-type',   count: 834,  color: '#38bdf8' },
    { type: 'L-type',   count: 613,  color: '#f59e0b' },
    { type: 'LTR-type', count: 134,  color: '#f43f5e' },
    { type: 'LR-type',  count: 107,  color: '#a855f7' }
];

// ---- SAMPLE IMAGES ----
// Grab a subset of images from the data directory for the gallery
const sampleImages = [
    'a_109295.png', 'a_110385.png', 'a_108425.png', 'a_113485.png',
    'a_107131.png', 'a_110241.png', 'a_109116.png', 'a_108586.png',
    'a_111366.png', 'a_112951.png', 'a_113009.png', 'a_111698.png',
    'a_110300.png', 'a_108916.png', 'a_114550.png', 'a_110482.png',
    'a_111033.png', 'a_113389.png', 'a_113467.png', 'a_113886.png'
];

let imageIndex = 0;
const IMAGES_PER_LOAD = 8;

// ---- INITIALIZATION ----

document.addEventListener('DOMContentLoaded', () => {
    initImageGallery();
    initLaneTypeChart();
    initVersionSelector();
    renderMetrics('version_45');
    initScrollAnimations();
    initNavHighlight();
    initMapDemo();
});

// ---- IMAGE GALLERY ----

function initImageGallery() {
    loadMoreImages();
}

function loadMoreImages() {
    const gallery = document.getElementById('image-gallery');
    const btn = document.getElementById('load-more-btn');
    const end = Math.min(imageIndex + IMAGES_PER_LOAD, sampleImages.length);

    for (let i = imageIndex; i < end; i++) {
        const img = document.createElement('img');
        img.className = 'gallery-img fade-in';
        img.src = `../main_task/data/${sampleImages[i]}`;
        img.alt = `Intersection arm ${sampleImages[i].replace('.png', '')}`;
        img.loading = 'lazy';
        img.addEventListener('click', () => openLightbox(img.src));
        gallery.appendChild(img);

        // Trigger fade-in
        requestAnimationFrame(() => {
            requestAnimationFrame(() => img.classList.add('visible'));
        });
    }

    imageIndex = end;
    if (imageIndex >= sampleImages.length) {
        btn.style.display = 'none';
    }
}

function openLightbox(src) {
    const lb = document.createElement('div');
    lb.className = 'lightbox';
    lb.innerHTML = `<img src="${src}" alt="Enlarged view">`;
    lb.addEventListener('click', () => lb.remove());
    document.body.appendChild(lb);
}

// ---- LANE TYPE CHART ----

function initLaneTypeChart() {
    const container = document.getElementById('lane-type-chart');
    const maxCount = Math.max(...laneTypes.map(lt => lt.count));

    laneTypes.forEach(lt => {
        const pct = (lt.count / maxCount) * 100;
        const row = document.createElement('div');
        row.className = 'lane-bar-row';
        row.innerHTML = `
            <span class="lane-bar-label">${lt.type}</span>
            <div class="lane-bar-track">
                <div class="lane-bar-fill" style="width: 0%; background: ${lt.color};"></div>
            </div>
            <span class="lane-bar-count">${lt.count.toLocaleString()}</span>
        `;
        container.appendChild(row);

        // Animate in
        setTimeout(() => {
            row.querySelector('.lane-bar-fill').style.width = pct + '%';
        }, 100);
    });
}

// ---- VERSION SELECTOR ----

function initVersionSelector() {
    document.querySelectorAll('.version-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            document.querySelectorAll('.version-btn').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            renderMetrics(btn.dataset.version);
        });
    });
}

// ---- RENDER METRICS ----

function renderMetrics(version) {
    const data = evaluationData[version];
    renderTurnLevel(data.turn);
    renderSlotLevel(data.slot);
    renderArmLevel(data.arm);
}

function renderTurnLevel(data) {
    const container = document.getElementById('turn-level-metrics');
    container.innerHTML = '';

    const metrics = [
        { label: 'F1 Score', value: data.f1, color: '#6366f1' },
        { label: 'Precision', value: data.precision, color: '#2dd4bf' },
        { label: 'Recall', value: data.recall, color: '#38bdf8' }
    ];

    metrics.forEach(m => {
        const row = document.createElement('div');
        row.className = 'metric-row';
        row.innerHTML = `
            <span class="metric-label">${m.label}</span>
            <div class="metric-track">
                <div class="metric-fill" style="width: 0%; background: ${m.color};"></div>
            </div>
            <span class="metric-value">${m.value.toFixed(4)}</span>
        `;
        container.appendChild(row);
        setTimeout(() => {
            row.querySelector('.metric-fill').style.width = (m.value * 100) + '%';
        }, 50);
    });
}

function renderSlotLevel(data) {
    const container = document.getElementById('slot-level-metrics');
    container.innerHTML = '';

    const colors = { left: '#f59e0b', through: '#6366f1', right: '#2dd4bf', approach: '#38bdf8' };

    Object.entries(data).forEach(([key, val]) => {
        const row = document.createElement('div');
        row.className = 'metric-row';
        row.innerHTML = `
            <span class="metric-label">${key.charAt(0).toUpperCase() + key.slice(1)}</span>
            <div class="metric-track">
                <div class="metric-fill" style="width: 0%; background: ${colors[key]};"></div>
            </div>
            <span class="metric-value">${val.f1.toFixed(4)}</span>
        `;
        container.appendChild(row);
        setTimeout(() => {
            row.querySelector('.metric-fill').style.width = (val.f1 * 100) + '%';
        }, 50);
    });
}

function renderArmLevel(data) {
    const container = document.getElementById('arm-level-metrics');
    container.innerHTML = '';

    const types = ['L', 'LT', 'T', 'TR', 'R', 'mean'];

    types.forEach(type => {
        const modelF1 = data[type].f1;
        const baseF1 = baseline[type].f1;
        const isBetter = modelF1 >= baseF1;

        const card = document.createElement('div');
        card.className = 'arm-card';
        card.innerHTML = `
            <div class="arm-type">${type === 'mean' ? 'Mean' : type + '-type'}</div>
            <div class="arm-values">
                <div class="arm-val-row">
                    <span class="arm-val-label">Model</span>
                    <span class="arm-val-num ${isBetter ? 'better' : 'worse'}">${modelF1.toFixed(4)}</span>
                </div>
                <div class="arm-val-row">
                    <span class="arm-val-label">Baseline</span>
                    <span class="arm-val-num baseline">${baseF1.toFixed(4)}</span>
                </div>
                <div class="arm-val-row">
                    <span class="arm-val-label">Δ</span>
                    <span class="arm-val-num ${isBetter ? 'better' : 'worse'}">${(modelF1 - baseF1) >= 0 ? '+' : ''}${(modelF1 - baseF1).toFixed(4)}</span>
                </div>
            </div>
        `;
        container.appendChild(card);
    });
}

// ---- SCROLL ANIMATIONS ----

function initScrollAnimations() {
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('visible');
            }
        });
    }, { threshold: 0.1 });

    document.querySelectorAll('.pipeline-stage, .data-card, .results-card, .arch-card, .ref-card, .pph-rules-card, .loss-card, .paper-comparison').forEach(el => {
        el.classList.add('fade-in');
        observer.observe(el);
    });
}

// ---- NAV HIGHLIGHT ----

function initNavHighlight() {
    const sections = document.querySelectorAll('section');
    const navLinks = document.querySelectorAll('.nav-link');

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const id = entry.target.id;
                navLinks.forEach(link => {
                    link.classList.toggle('active', link.getAttribute('href') === `#${id}`);
                });
            }
        });
    }, { threshold: 0.3 });

    sections.forEach(section => observer.observe(section));
}

// ============================================
//  MAP DEMO IMPLEMENTATION
// ============================================

let mapInstance = null;
let mapMode = 'processed'; // 'processed' or 'raw'
let currentIntersection = 'inter_1';
let activeLanes = [];
let activeTurns = [];
let selectedLaneElement = null;
let selectedLaneData = null;

const intersections = {
    inter_1: {
        id: "53585",
        name: "George St & Park St",
        location: "Sydney CBD",
        lat: -33.87304,
        lon: 151.20698,
        zoom: 18,
        speedLimit: 40,
        routeInfo: "10:15 AM • 12 min • 4.8 km",
        description: "Balanced 4-way CBD intersection with heavy pedestrian crossing and public transit routes.",
        arms: [
            {
                name: "North Approach (George St)",
                street: "George St",
                bearing: 3,
                approachLanes: 2,
                exitLanes: 2,
                lanes: [
                    {
                        index: 0, // Left/Through lane
                        turns: {
                            processed: [
                                { toArm: 1, toLane: 0, type: 'left', prob: 0.94 },
                                { toArm: 2, toLane: 0, type: 'through', prob: 0.89 }
                            ],
                            raw: [
                                { toArm: 1, toLane: 0, type: 'left', prob: 0.94 },
                                { toArm: 2, toLane: 0, type: 'through', prob: 0.89 },
                                { toArm: 3, toLane: 0, type: 'right', prob: 0.62 } // ILLEGAL: Left lane making right turn (Rule 4 violation)
                            ]
                        }
                    },
                    {
                        index: 1, // Through/Right lane
                        turns: {
                            processed: [
                                { toArm: 2, toLane: 1, type: 'through', prob: 0.91 },
                                { toArm: 3, toLane: 1, type: 'right', prob: 0.87 }
                            ],
                            raw: [
                                { toArm: 2, toLane: 1, type: 'through', prob: 0.91 },
                                { toArm: 3, toLane: 1, type: 'right', prob: 0.87 },
                                { toArm: 1, toLane: 1, type: 'left', prob: 0.58 } // ILLEGAL: Right lane making left turn (Rule 3 violation)
                            ]
                        }
                    }
                ]
            },
            {
                name: "East Approach (Park St)",
                street: "Park St",
                bearing: 93,
                approachLanes: 2,
                exitLanes: 2,
                lanes: [
                    {
                        index: 0,
                        turns: {
                            processed: [
                                { toArm: 2, toLane: 0, type: 'left', prob: 0.95 },
                                { toArm: 3, toLane: 0, type: 'through', prob: 0.92 }
                            ],
                            raw: [
                                { toArm: 2, toLane: 0, type: 'left', prob: 0.95 },
                                { toArm: 3, toLane: 0, type: 'through', prob: 0.92 }
                            ]
                        }
                    },
                    {
                        index: 1,
                        turns: {
                            processed: [
                                { toArm: 3, toLane: 1, type: 'through', prob: 0.90 },
                                { toArm: 0, toLane: 1, type: 'right', prob: 0.85 }
                            ],
                            raw: [
                                { toArm: 3, toLane: 1, type: 'through', prob: 0.90 },
                                { toArm: 0, toLane: 1, type: 'right', prob: 0.85 }
                            ]
                        }
                    }
                ]
            },
            {
                name: "South Approach (George St)",
                street: "George St",
                bearing: 183,
                approachLanes: 2,
                exitLanes: 2,
                lanes: [
                    {
                        index: 0,
                        turns: {
                            processed: [
                                { toArm: 3, toLane: 0, type: 'left', prob: 0.93 },
                                { toArm: 0, toLane: 0, type: 'through', prob: 0.88 }
                            ],
                            raw: [
                                { toArm: 3, toLane: 0, type: 'left', prob: 0.93 },
                                { toArm: 0, toLane: 0, type: 'through', prob: 0.88 }
                            ]
                        }
                    },
                    {
                        index: 1,
                        turns: {
                            processed: [
                                { toArm: 0, toLane: 1, type: 'through', prob: 0.92 },
                                { toArm: 1, toLane: 1, type: 'right', prob: 0.86 }
                            ],
                            raw: [
                                { toArm: 0, toLane: 1, type: 'through', prob: 0.92 },
                                { toArm: 1, toLane: 1, type: 'right', prob: 0.86 }
                            ]
                        }
                    }
                ]
            },
            {
                name: "West Approach (Park St)",
                street: "Park St",
                bearing: 273,
                approachLanes: 2,
                exitLanes: 2,
                lanes: [
                    {
                        index: 0,
                        turns: {
                            processed: [
                                { toArm: 0, toLane: 0, type: 'left', prob: 0.96 },
                                { toArm: 1, toLane: 0, type: 'through', prob: 0.91 }
                            ],
                            raw: [
                                { toArm: 0, toLane: 0, type: 'left', prob: 0.96 },
                                { toArm: 1, toLane: 0, type: 'through', prob: 0.91 }
                            ]
                        }
                    },
                    {
                        index: 1,
                        turns: {
                            processed: [
                                { toArm: 1, toLane: 1, type: 'through', prob: 0.89 },
                                { toArm: 2, toLane: 1, type: 'right', prob: 0.84 }
                            ],
                            raw: [
                                { toArm: 1, toLane: 1, type: 'through', prob: 0.89 },
                                { toArm: 2, toLane: 1, type: 'right', prob: 0.84 }
                            ]
                        }
                    }
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
        routeInfo: "10:18 AM • 15 min • 6.2 km",
        description: "A 3-way T-junction connecting Glebe Point Road with Francis Street, featuring clean approach paths.",
        arms: [
            {
                name: "South Approach (Glebe Point Rd)",
                street: "Glebe Point Rd",
                bearing: 187,
                approachLanes: 1,
                exitLanes: 1,
                lanes: [
                    {
                        index: 0,
                        turns: {
                            processed: [
                                { toArm: 2, toLane: 0, type: 'through', prob: 0.94 },
                                { toArm: 1, toLane: 0, type: 'left', prob: 0.90 }
                            ],
                            raw: [
                                { toArm: 2, toLane: 0, type: 'through', prob: 0.94 },
                                { toArm: 1, toLane: 0, type: 'left', prob: 0.90 }
                            ]
                        }
                    }
                ]
            },
            {
                name: "West Approach (Francis St)",
                street: "Francis St",
                bearing: 268,
                approachLanes: 1,
                exitLanes: 1,
                lanes: [
                    {
                        index: 0,
                        turns: {
                            processed: [
                                { toArm: 2, toLane: 0, type: 'left', prob: 0.91 },
                                { toArm: 0, toLane: 0, type: 'right', prob: 0.88 }
                            ],
                            raw: [
                                { toArm: 2, toLane: 0, type: 'left', prob: 0.91 },
                                { toArm: 0, toLane: 0, type: 'right', prob: 0.88 },
                                { toArm: 0, toLane: 0, type: 'through', prob: 0.52 } // ILLEGAL: Through turn at a T-junction (violates physical layout)
                            ]
                        }
                    }
                ]
            },
            {
                name: "North Approach (Glebe Point Rd)",
                street: "Glebe Point Rd",
                bearing: 7,
                approachLanes: 1,
                exitLanes: 1,
                lanes: [
                    {
                        index: 0,
                        turns: {
                            processed: [
                                { toArm: 0, toLane: 0, type: 'through', prob: 0.93 },
                                { toArm: 1, toLane: 0, type: 'right', prob: 0.89 }
                            ],
                            raw: [
                                { toArm: 0, toLane: 0, type: 'through', prob: 0.93 },
                                { toArm: 1, toLane: 0, type: 'right', prob: 0.89 }
                            ]
                        }
                    }
                ]
            }
        ]
    },
    inter_3: {
        id: "366",
        name: "Epping Rd & Balaclava Rd",
        location: "Macquarie Park",
        lat: -33.777779,
        lon: 151.1081194,
        zoom: 18,
        speedLimit: 70,
        routeInfo: "10:25 AM • 22 min • 18.5 km",
        description: "Arterial dual-carriageway crossing with high-speed approaches, long slip lanes, and complex signal timing.",
        arms: [
            {
                name: "North Approach (Balaclava Rd)",
                street: "Balaclava Rd",
                bearing: 345,
                approachLanes: 2,
                exitLanes: 2,
                lanes: [
                    {
                        index: 0,
                        turns: {
                            processed: [
                                { toArm: 1, toLane: 0, type: 'left', prob: 0.95 },
                                { toArm: 2, toLane: 0, type: 'through', prob: 0.88 }
                            ],
                            raw: [
                                { toArm: 1, toLane: 0, type: 'left', prob: 0.95 },
                                { toArm: 2, toLane: 0, type: 'through', prob: 0.88 }
                            ]
                        }
                    },
                    {
                        index: 1,
                        turns: {
                            processed: [
                                { toArm: 2, toLane: 1, type: 'through', prob: 0.89 },
                                { toArm: 3, toLane: 1, type: 'right', prob: 0.84 }
                            ],
                            raw: [
                                { toArm: 2, toLane: 1, type: 'through', prob: 0.89 },
                                { toArm: 3, toLane: 1, type: 'right', prob: 0.84 }
                            ]
                        }
                    }
                ]
            },
            {
                name: "East Approach (Epping Rd)",
                street: "Epping Rd",
                bearing: 75,
                approachLanes: 2,
                exitLanes: 2,
                lanes: [
                    {
                        index: 0,
                        turns: {
                            processed: [
                                { toArm: 2, toLane: 0, type: 'left', prob: 0.93 },
                                { toArm: 3, toLane: 0, type: 'through', prob: 0.91 }
                            ],
                            raw: [
                                { toArm: 2, toLane: 0, type: 'left', prob: 0.93 },
                                { toArm: 3, toLane: 0, type: 'through', prob: 0.91 }
                            ]
                        }
                    },
                    {
                        index: 1,
                        turns: {
                            processed: [
                                { toArm: 3, toLane: 1, type: 'through', prob: 0.89 },
                                { toArm: 0, toLane: 1, type: 'right', prob: 0.83 }
                            ],
                            raw: [
                                { toArm: 3, toLane: 1, type: 'through', prob: 0.89 },
                                { toArm: 0, toLane: 1, type: 'right', prob: 0.83 }
                            ]
                        }
                    }
                ]
            },
            {
                name: "South Approach (Balaclava Rd)",
                street: "Balaclava Rd",
                bearing: 165,
                approachLanes: 2,
                exitLanes: 2,
                lanes: [
                    {
                        index: 0,
                        turns: {
                            processed: [
                                { toArm: 3, toLane: 0, type: 'left', prob: 0.92 },
                                { toArm: 0, toLane: 0, type: 'through', prob: 0.87 }
                            ],
                            raw: [
                                { toArm: 3, toLane: 0, type: 'left', prob: 0.92 },
                                { toArm: 0, toLane: 0, type: 'through', prob: 0.87 }
                            ]
                        }
                    },
                    {
                        index: 1,
                        turns: {
                            processed: [
                                { toArm: 0, toLane: 1, type: 'through', prob: 0.90 },
                                { toArm: 1, toLane: 1, type: 'right', prob: 0.85 }
                            ],
                            raw: [
                                { toArm: 0, toLane: 1, type: 'through', prob: 0.90 },
                                { toArm: 1, toLane: 1, type: 'right', prob: 0.85 }
                            ]
                        }
                    }
                ]
            },
            {
                name: "West Approach (Epping Rd)",
                street: "Epping Rd",
                bearing: 255,
                approachLanes: 2,
                exitLanes: 2,
                lanes: [
                    {
                        index: 0,
                        turns: {
                            processed: [
                                { toArm: 0, toLane: 0, type: 'left', prob: 0.94 },
                                { toArm: 1, toLane: 0, type: 'through', prob: 0.92 }
                            ],
                            raw: [
                                { toArm: 0, toLane: 0, type: 'left', prob: 0.94 },
                                { toArm: 1, toLane: 0, type: 'through', prob: 0.92 }
                            ]
                        }
                    },
                    {
                        index: 1,
                        turns: {
                            processed: [
                                { toArm: 1, toLane: 1, type: 'through', prob: 0.88 },
                                { toArm: 2, toLane: 1, type: 'right', prob: 0.82 }
                            ],
                            raw: [
                                { toArm: 1, toLane: 1, type: 'through', prob: 0.88 },
                                { toArm: 2, toLane: 1, type: 'right', prob: 0.82 }
                            ]
                        }
                    }
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
        routeInfo: "10:30 AM • 28 min • 22.1 km",
        description: "High-volume intersection connecting primary Sydney highways. Features skewed approach angles and distinct turning signals.",
        arms: [
            {
                name: "North-West Approach (Parramatta Rd)",
                street: "Parramatta Rd",
                bearing: 295,
                approachLanes: 2,
                exitLanes: 2,
                lanes: [
                    {
                        index: 0,
                        turns: {
                            processed: [
                                { toArm: 1, toLane: 0, type: 'left', prob: 0.95 },
                                { toArm: 2, toLane: 0, type: 'through', prob: 0.89 }
                            ],
                            raw: [
                                { toArm: 1, toLane: 0, type: 'left', prob: 0.95 },
                                { toArm: 2, toLane: 0, type: 'through', prob: 0.89 }
                            ]
                        }
                    },
                    {
                        index: 1,
                        turns: {
                            processed: [
                                { toArm: 2, toLane: 1, type: 'through', prob: 0.91 },
                                { toArm: 3, toLane: 1, type: 'right', prob: 0.85 }
                            ],
                            raw: [
                                { toArm: 2, toLane: 1, type: 'through', prob: 0.91 },
                                { toArm: 3, toLane: 1, type: 'right', prob: 0.85 }
                            ]
                        }
                    }
                ]
            },
            {
                name: "North-East Approach (Parramatta Rd)",
                street: "Parramatta Rd",
                bearing: 25,
                approachLanes: 2,
                exitLanes: 2,
                lanes: [
                    {
                        index: 0,
                        turns: {
                            processed: [
                                { toArm: 2, toLane: 0, type: 'left', prob: 0.93 },
                                { toArm: 3, toLane: 0, type: 'through', prob: 0.90 }
                            ],
                            raw: [
                                { toArm: 2, toLane: 0, type: 'left', prob: 0.93 },
                                { toArm: 3, toLane: 0, type: 'through', prob: 0.90 }
                            ]
                        }
                    },
                    {
                        index: 1,
                        turns: {
                            processed: [
                                { toArm: 3, toLane: 1, type: 'through', prob: 0.87 },
                                { toArm: 0, toLane: 1, type: 'right', prob: 0.84 }
                            ],
                            raw: [
                                { toArm: 3, toLane: 1, type: 'through', prob: 0.87 },
                                { toArm: 0, toLane: 1, type: 'right', prob: 0.84 }
                            ]
                        }
                    }
                ]
            },
            {
                name: "South-East Approach (Woodville Rd)",
                street: "Woodville Rd",
                bearing: 115,
                approachLanes: 2,
                exitLanes: 2,
                lanes: [
                    {
                        index: 0,
                        turns: {
                            processed: [
                                { toArm: 3, toLane: 0, type: 'left', prob: 0.91 },
                                { toArm: 0, toLane: 0, type: 'through', prob: 0.86 }
                            ],
                            raw: [
                                { toArm: 3, toLane: 0, type: 'left', prob: 0.91 },
                                { toArm: 0, toLane: 0, type: 'through', prob: 0.86 }
                            ]
                        }
                    },
                    {
                        index: 1,
                        turns: {
                            processed: [
                                { toArm: 0, toLane: 1, type: 'through', prob: 0.88 },
                                { toArm: 1, toLane: 1, type: 'right', prob: 0.83 }
                            ],
                            raw: [
                                { toArm: 0, toLane: 1, type: 'through', prob: 0.88 },
                                { toArm: 1, toLane: 1, type: 'right', prob: 0.83 }
                            ]
                        }
                    }
                ]
            },
            {
                name: "South-West Approach (Woodville Rd)",
                street: "Woodville Rd",
                bearing: 205,
                approachLanes: 2,
                exitLanes: 2,
                lanes: [
                    {
                        index: 0,
                        turns: {
                            processed: [
                                { toArm: 0, toLane: 0, type: 'left', prob: 0.94 },
                                { toArm: 1, toLane: 0, type: 'through', prob: 0.91 }
                            ],
                            raw: [
                                { toArm: 0, toLane: 0, type: 'left', prob: 0.94 },
                                { toArm: 1, toLane: 0, type: 'through', prob: 0.91 }
                            ]
                        }
                    },
                    {
                        index: 1,
                        turns: {
                            processed: [
                                { toArm: 1, toLane: 1, type: 'through', prob: 0.89 },
                                { toArm: 2, toLane: 1, type: 'right', prob: 0.81 }
                            ],
                            raw: [
                                { toArm: 1, toLane: 1, type: 'through', prob: 0.89 },
                                { toArm: 2, toLane: 1, type: 'right', prob: 0.81 }
                            ]
                        }
                    }
                ]
            }
        ]
    }
};

let mapMarkers = {};

function drawAllIntersectionMarkers() {
    // Clear existing markers if any
    Object.values(mapMarkers).forEach(m => mapInstance.removeLayer(m));
    mapMarkers = {};

    Object.entries(intersections).forEach(([id, inter]) => {
        const customIcon = L.divIcon({
            className: 'custom-map-marker',
            html: `<div class="marker-pulse"></div><div class="marker-dot"></div>`,
            iconSize: [20, 20],
            iconAnchor: [10, 10]
        });

        const marker = L.marker([inter.lat, inter.lon], { icon: customIcon }).addTo(mapInstance);
        
        const popupContent = `
            <div style="font-family: var(--font-sans); padding: 4px; width: 180px;">
                <h4 style="margin: 0 0 4px 0; color: #3b82f6; font-size: 0.85rem; font-weight: 600;">${inter.name}</h4>
                <p style="margin: 0 0 6px 0; font-size: 0.75rem; color: #64748b;">${inter.location}</p>
                <div style="font-size: 0.7rem; border-top: 1px solid #e2e8f0; padding-top: 4px; margin-bottom: 6px;">
                    OSM ID: <strong style="font-family: var(--font-mono);">${inter.id}</strong>
                </div>
                <button onclick="changeIntersectionFromMarker('${id}')" style="width:100%; border:none; background:#3b82f6; color:white; padding:4px 8px; border-radius:4px; font-size:0.75rem; cursor:pointer; font-weight:500; transition: background 0.2s;" onmouseover="this.style.background='#2563eb'" onmouseout="this.style.background='#3b82f6'">
                    Load Dashboard
                </button>
            </div>
        `;
        marker.bindPopup(popupContent);
        mapMarkers[id] = marker;
    });
}

function changeIntersectionFromMarker(interId) {
    const selectEl = document.getElementById('intersection-select');
    if (selectEl) selectEl.value = interId;
    changeIntersection(interId);
}

function initMapDemo() {
    const startInter = intersections[currentIntersection];
    
    // Base Layers
    const osmLayer = L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        maxZoom: 19,
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
    });

    const esriLayer = L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}', {
        maxZoom: 19,
        attribution: 'Tiles &copy; Esri &mdash; Source: Esri, i-cubed, USDA, USGS, AEX, GeoEye, Getmapping, Aerogrid, IGN, IGP, UPR-EGP, and the GIS User Community'
    });

    mapInstance = L.map('osm-map', {
        zoomControl: true,
        scrollWheelZoom: false,
        layers: [osmLayer]
    }).setView([startInter.lat, startInter.lon], startInter.zoom);

    // Layer Control positioned in the bottom-right corner
    const baseMaps = {
        "Road Map (OSM)": osmLayer,
        "Satellite (Esri)": esriLayer
    };
    L.control.layers(baseMaps, null, { position: 'bottomright' }).addTo(mapInstance);

    drawAllIntersectionMarkers();

    renderIntersection(currentIntersection);
    startClock();

    // Open first marker popup after a brief delay
    setTimeout(() => {
        if (mapMarkers[currentIntersection]) {
            mapMarkers[currentIntersection].openPopup();
        }
    }, 500);
}

function changeIntersection(interId) {
    currentIntersection = interId;
    const inter = intersections[interId];
    if (mapInstance && inter) {
        mapInstance.setView([inter.lat, inter.lon], inter.zoom);
        renderIntersection(interId);
        
        // Highlight marker by opening its popup
        if (mapMarkers[interId]) {
            mapMarkers[interId].openPopup();
        }
    }
}

function setMapMode(mode) {
    mapMode = mode;
    document.querySelectorAll('.toggle-btn').forEach(btn => btn.classList.remove('active'));
    if (mode === 'processed') {
        document.getElementById('mode-processed').classList.add('active');
    } else {
        document.getElementById('mode-raw').classList.add('active');
    }
    
    clearTurns();
    if (selectedLaneData) {
        drawTurnsForLane(selectedLaneData.armIdx, selectedLaneData.laneData);
        updateHudNavCard(selectedLaneData.armIdx, selectedLaneData.laneData.index);
    }
}

function clearLanes() {
    activeLanes.forEach(layer => mapInstance.removeLayer(layer));
    activeLanes = [];
}

function clearTurns() {
    activeTurns.forEach(layer => mapInstance.removeLayer(layer));
    activeTurns = [];
}

function renderIntersection(interId) {
    clearLanes();
    clearTurns();
    selectedLaneElement = null;
    selectedLaneData = null;

    const inter = intersections[interId];
    if (!inter) return;

    // Update HUD Speed Limit
    const speedLimitVal = document.getElementById('hud-speed-val');
    if (speedLimitVal) speedLimitVal.textContent = inter.speedLimit || 60;

    // Update HUD Route Info
    const routeTimeEl = document.getElementById('hud-route-time');
    if (routeTimeEl) routeTimeEl.textContent = inter.routeInfo || "10:00 AM • 19 min • 15 km";

    // Rotate Compass Needle to first arm's bearing
    const compassNeedle = document.getElementById('compass-needle');
    if (compassNeedle && inter.arms && inter.arms[0]) {
        compassNeedle.style.transform = `rotate(${inter.arms[0].bearing}deg)`;
    }

    // Reset Navigation Card
    resetHudNavCard();

    const detailsContainer = document.getElementById('map-inter-details');
    detailsContainer.innerHTML = `
        <div class="detail-row">
            <span class="label">OSM ID</span>
            <span class="value">${inter.id}</span>
        </div>
        <div class="detail-row">
            <span class="label">Location</span>
            <span class="value">${inter.location}</span>
        </div>
        <div class="detail-row">
            <span class="label">Latitude</span>
            <span class="value">${inter.lat.toFixed(5)}</span>
        </div>
        <div class="detail-row">
            <span class="label">Longitude</span>
            <span class="value">${inter.lon.toFixed(5)}</span>
        </div>
        <div style="font-size: 0.8rem; line-height: 1.4; color: var(--text-secondary); margin-top: 10px; border-top: 1px solid var(--border-subtle); padding-top: 10px;">
            ${inter.description}
        </div>
    `;

    const centerLat = inter.lat;
    const centerLon = inter.lon;

    const scaleLat = 0.000009; 
    const scaleLon = 0.000009 / Math.cos(centerLat * Math.PI / 180); 

    const laneWidth = 3.2; 
    const stopDistance = 12.0; 
    const armLength = 55.0; 

    inter.arms.forEach((arm, armIdx) => {
        const rad = arm.bearing * Math.PI / 180;
        const cosRad = Math.cos(rad);
        const sinRad = Math.sin(rad);

        const outwardLat = cosRad;
        const outwardLon = sinRad;

        const perpRad = (arm.bearing - 90) * Math.PI / 180;
        const perpLat = Math.cos(perpRad);
        const perpLon = Math.sin(perpRad);

        // 1. Draw Exit Lanes
        arm.exitLanePts = [];
        for (let i = 0; i < arm.exitLanes; i++) {
            const laneOffset = - (i + 0.5) * laneWidth; 
            const offsetLat = perpLat * laneOffset * scaleLat;
            const offsetLon = perpLon * laneOffset * scaleLon;

            const stopPt = [
                centerLat + (outwardLat * stopDistance * scaleLat) + offsetLat,
                centerLon + (outwardLon * stopDistance * scaleLon) + offsetLon
            ];
            const endPt = [
                centerLat + (outwardLat * armLength * scaleLat) + offsetLat,
                centerLon + (outwardLon * armLength * scaleLon) + offsetLon
            ];

            arm.exitLanePts[i] = stopPt;

            const poly = L.polyline([stopPt, endPt], {
                color: '#10b981', 
                weight: 4,
                opacity: 0.8,
                lineCap: 'round'
            }).addTo(mapInstance);
            
            poly.bindTooltip(`Exit Lane ${i + 1}`, { sticky: true });
            activeLanes.push(poly);
        }

        // 2. Draw Approach Lanes
        arm.approachLanePts = [];
        for (let i = 0; i < arm.approachLanes; i++) {
            const laneOffset = (i + 0.5) * laneWidth; 
            const offsetLat = perpLat * laneOffset * scaleLat;
            const offsetLon = perpLon * laneOffset * scaleLon;

            const startPt = [
                centerLat + (outwardLat * armLength * scaleLat) + offsetLat,
                centerLon + (outwardLon * armLength * scaleLon) + offsetLon
            ];
            const stopPt = [
                centerLat + (outwardLat * stopDistance * scaleLat) + offsetLat,
                centerLon + (outwardLon * stopDistance * scaleLon) + offsetLon
            ];

            arm.approachLanePts[i] = stopPt;

            const laneData = arm.lanes[i] || { index: i, turns: { processed: [], raw: [] } };

            const poly = L.polyline([startPt, stopPt], {
                color: '#3b82f6', 
                weight: 5,
                opacity: 0.8,
                lineCap: 'round',
                className: 'leaflet-interactive'
            }).addTo(mapInstance);

            poly.bindTooltip(`Approach Lane ${i + 1} (Click to see turns)`, { sticky: true });

            poly.on('mouseover', function() {
                if (selectedLaneElement !== this) {
                    this.setStyle({ color: '#60a5fa', weight: 7 });
                }
            });
            poly.on('mouseout', function() {
                if (selectedLaneElement !== this) {
                    this.setStyle({ color: '#3b82f6', weight: 5 });
                }
            });

            poly.on('click', function() {
                if (selectedLaneElement) {
                    selectedLaneElement.setStyle({ color: '#3b82f6', weight: 5 });
                }

                selectedLaneElement = this;
                selectedLaneData = { armIdx, laneData };
                this.setStyle({ color: '#f59e0b', weight: 7 }); 

                drawTurnsForLane(armIdx, laneData);

                // Update HUD Navigation Card
                updateHudNavCard(armIdx, laneData.index);

                // Rotate Compass Needle to match the approach arm's bearing
                const compassNeedle = document.getElementById('compass-needle');
                if (compassNeedle) {
                    compassNeedle.style.transform = `rotate(${arm.bearing}deg)`;
                }
            });

            activeLanes.push(poly);
        }
    });
}

function drawTurnsForLane(approachArmIdx, laneData) {
    clearTurns();

    const inter = intersections[currentIntersection];
    const approachArm = inter.arms[approachArmIdx];
    const startPt = approachArm.approachLanePts[laneData.index];

    if (!startPt) return;

    const turnsList = mapMode === 'processed' ? laneData.turns.processed : laneData.turns.raw;

    turnsList.forEach(turn => {
        const exitArm = inter.arms[turn.toArm];
        const endPt = exitArm.exitLanePts[turn.toLane];

        if (!endPt) return;

        const controlPt = [inter.lat, inter.lon];
        const curvePoints = [];
        const steps = 15;

        for (let j = 0; j <= steps; j++) {
            const t = j / steps;
            const lat = (1 - t) * (1 - t) * startPt[0] + 2 * (1 - t) * t * controlPt[0] + t * t * endPt[0];
            const lon = (1 - t) * (1 - t) * startPt[1] + 2 * (1 - t) * t * controlPt[1] + t * t * endPt[1];
            curvePoints.push([lat, lon]);
        }

        let color = '#6366f1'; 
        if (turn.type === 'left') color = '#ef4444'; 
        if (turn.type === 'right') color = '#f59e0b'; 

        const flowLine = L.polyline(curvePoints, {
            color: color,
            weight: 3,
            opacity: 0.9,
            className: 'animated-flow'
        }).addTo(mapInstance);

        const baseLine = L.polyline(curvePoints, {
            color: color,
            weight: 5,
            opacity: 0.3
        }).addTo(mapInstance);

        const typeLabel = turn.type.charAt(0).toUpperCase() + turn.type.slice(1);
        const popupContent = `
            <div style="font-family: var(--font-sans); padding: 4px;">
                <h4 style="margin: 0 0 6px 0; color: ${color}; font-size: 0.9rem;">${typeLabel} Turn Path</h4>
                <p style="margin: 0; font-size: 0.8rem; color: var(--text-secondary);">
                    Probability: <strong style="color: var(--text-primary); font-family: var(--font-mono);">${turn.prob.toFixed(2)}</strong>
                </p>
                ${mapMode === 'raw' && turn.prob < 0.7 ? '<p style="margin: 4px 0 0 0; font-size: 0.75rem; color: var(--accent-rose);">⚠️ Illegal / cross-lane turn prediction</p>' : ''}
            </div>
        `;
        flowLine.bindPopup(popupContent);
        baseLine.bindPopup(popupContent);

        activeTurns.push(flowLine);
        activeTurns.push(baseLine);
    });
}

// ---- HUD NAVIGATION WIDGET ACTIONS ----

function startClock() {
    const timeEl = document.getElementById('sys-time');
    if (!timeEl) return;
    const update = () => {
        const now = new Date();
        let hours = now.getHours();
        const minutes = now.getMinutes();
        const ampm = hours >= 12 ? 'PM' : 'AM';
        hours = hours % 12;
        hours = hours ? hours : 12;
        const minStr = minutes < 10 ? '0' + minutes : minutes;
        timeEl.textContent = `${hours}:${minStr} ${ampm}`;
    };
    update();
    setInterval(update, 30000);
}

function resetMapView() {
    const inter = intersections[currentIntersection];
    if (mapInstance && inter) {
        mapInstance.setView([inter.lat, inter.lon], inter.zoom);
    }
}

function resetHudNavCard() {
    document.getElementById('hud-nav-dist').textContent = '--- m';
    document.getElementById('hud-nav-street').textContent = 'Select approach lane';
    setDefaultNavIcon();
    document.getElementById('hud-nav-lanes').innerHTML = '';
}

function updateHudNavCard(armIdx, selectedLaneIdx) {
    const inter = intersections[currentIntersection];
    const arm = inter.arms[armIdx];
    const lanesContainer = document.getElementById('hud-nav-lanes');
    if (!lanesContainer) return;
    lanesContainer.innerHTML = '';

    // Create lane indicators
    for (let i = 0; i < arm.approachLanes; i++) {
        const laneData = arm.lanes[i] || { index: i, turns: { processed: [], raw: [] } };
        const turnsList = mapMode === 'processed' ? laneData.turns.processed : laneData.turns.raw;
        
        let arrowText = '↑';
        const hasLeft = turnsList.some(t => t.type === 'left');
        const hasThrough = turnsList.some(t => t.type === 'through');
        const hasRight = turnsList.some(t => t.type === 'right');
        
        if (hasLeft && hasThrough && hasRight) arrowText = '↰↑↱';
        else if (hasLeft && hasThrough) arrowText = '↰↑';
        else if (hasThrough && hasRight) arrowText = '↑↱';
        else if (hasLeft && hasRight) arrowText = '↰↱';
        else if (hasLeft) arrowText = '↰';
        else if (hasRight) arrowText = '↱';
        else if (hasThrough) arrowText = '↑';

        const laneEl = document.createElement('span');
        laneEl.className = 'hud-lane-icon' + (i === selectedLaneIdx ? ' active' : '');
        laneEl.textContent = arrowText;
        lanesContainer.appendChild(laneEl);
    }

    // Get selected lane data
    const activeLane = arm.lanes[selectedLaneIdx];
    if (!activeLane) {
        document.getElementById('hud-nav-dist').textContent = '--- m';
        document.getElementById('hud-nav-street').textContent = 'Select approach lane';
        setDefaultNavIcon();
        return;
    }

    const activeTurns = mapMode === 'processed' ? activeLane.turns.processed : activeLane.turns.raw;
    
    if (activeTurns.length === 0) {
        document.getElementById('hud-nav-dist').textContent = '--- m';
        document.getElementById('hud-nav-street').textContent = 'No turns predicted';
        setNoTurnIcon();
        return;
    }

    // Find primary turn (highest probability)
    const primaryTurn = activeTurns.reduce((max, t) => t.prob > max.prob ? t : max, activeTurns[0]);
    const exitStreet = inter.arms[primaryTurn.toArm] ? inter.arms[primaryTurn.toArm].street : 'Next Street';
    
    // Set distance
    const mockDist = (selectedLaneIdx + 1) * 50 + 50;
    document.getElementById('hud-nav-dist').textContent = `${mockDist} m`;

    if (primaryTurn.type === 'left') {
        document.getElementById('hud-nav-street').textContent = `Turn Left onto ${exitStreet}`;
        setLeftTurnIcon();
    } else if (primaryTurn.type === 'right') {
        document.getElementById('hud-nav-street').textContent = `Turn Right onto ${exitStreet}`;
        setRightTurnIcon();
    } else {
        document.getElementById('hud-nav-street').textContent = `Go straight onto ${exitStreet}`;
        setStraightTurnIcon();
    }
}

function setDefaultNavIcon() {
    const iconEl = document.getElementById('hud-nav-icon');
    if (!iconEl) return;
    iconEl.innerHTML = `
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
            <path d="M12 19V5M5 12l7-7 7 7"/>
        </svg>
    `;
}

function setNoTurnIcon() {
    const iconEl = document.getElementById('hud-nav-icon');
    if (!iconEl) return;
    iconEl.innerHTML = `
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
            <circle cx="12" cy="12" r="10"/>
            <line x1="12" y1="8" x2="12" y2="16"/>
            <line x1="8" y1="12" x2="16" y2="12"/>
        </svg>
    `;
}

function setLeftTurnIcon() {
    const iconEl = document.getElementById('hud-nav-icon');
    if (!iconEl) return;
    iconEl.innerHTML = `
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
            <path d="M19 19h-6a4 4 0 0 1-4-4V5M9 5L5 9m4-4l4 4"/>
        </svg>
    `;
}

function setRightTurnIcon() {
    const iconEl = document.getElementById('hud-nav-icon');
    if (!iconEl) return;
    iconEl.innerHTML = `
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
            <path d="M5 19h6a4 4 0 0 0 4-4V5M15 5l-4 4m4-4l4 4"/>
        </svg>
    `;
}

function setStraightTurnIcon() {
    const iconEl = document.getElementById('hud-nav-icon');
    if (!iconEl) return;
    iconEl.innerHTML = `
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
            <path d="M12 19V5M5 12l7-7 7 7"/>
        </svg>
    `;
}
