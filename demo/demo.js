// ============================================
//  Lane Topology Pipeline Demo — JavaScript
// ============================================

// ====== INTERSECTION DATA ======
const intersections = {
    inter_1: {
        id: "53585", name: "Elizabeth St & Park St", location: "Sydney CBD",
        lat: -33.8732858, lon: 151.2099114, zoom: 19,
        description: "4-way signalised CBD intersection.",
        arms: [
            { name: "North", street: "Elizabeth St", bearing: 2, approachLanes: 3, exitLanes: 2,
              lanes: [
                { index: 0, turns: { processed: [{ toArm: 1, toLane: 0, type: 'left', prob: 0.95 }], raw: [{ toArm: 1, toLane: 0, type: 'left', prob: 0.95 }, { toArm: 2, toLane: 0, type: 'through', prob: 0.41 }] }},
                { index: 1, turns: { processed: [{ toArm: 2, toLane: 0, type: 'through', prob: 0.93 }], raw: [{ toArm: 2, toLane: 0, type: 'through', prob: 0.93 }] }},
                { index: 2, turns: { processed: [{ toArm: 2, toLane: 1, type: 'through', prob: 0.90 }, { toArm: 3, toLane: 1, type: 'right', prob: 0.87 }], raw: [{ toArm: 2, toLane: 1, type: 'through', prob: 0.90 }, { toArm: 3, toLane: 1, type: 'right', prob: 0.87 }] }}
              ]},
            { name: "East", street: "Park St", bearing: 94, approachLanes: 3, exitLanes: 2,
              lanes: [
                { index: 0, turns: { processed: [{ toArm: 2, toLane: 0, type: 'left', prob: 0.94 }], raw: [{ toArm: 2, toLane: 0, type: 'left', prob: 0.94 }] }},
                { index: 1, turns: { processed: [{ toArm: 3, toLane: 0, type: 'through', prob: 0.92 }], raw: [{ toArm: 3, toLane: 0, type: 'through', prob: 0.92 }] }},
                { index: 2, turns: { processed: [{ toArm: 3, toLane: 1, type: 'through', prob: 0.88 }, { toArm: 0, toLane: 1, type: 'right', prob: 0.85 }], raw: [{ toArm: 3, toLane: 1, type: 'through', prob: 0.88 }, { toArm: 0, toLane: 1, type: 'right', prob: 0.85 }] }}
              ]},
            { name: "South", street: "Elizabeth St", bearing: 182, approachLanes: 2, exitLanes: 3,
              lanes: [
                { index: 0, turns: { processed: [{ toArm: 3, toLane: 0, type: 'left', prob: 0.92 }, { toArm: 0, toLane: 0, type: 'through', prob: 0.88 }], raw: [{ toArm: 3, toLane: 0, type: 'left', prob: 0.92 }, { toArm: 0, toLane: 0, type: 'through', prob: 0.88 }] }},
                { index: 1, turns: { processed: [{ toArm: 0, toLane: 1, type: 'through', prob: 0.91 }, { toArm: 1, toLane: 1, type: 'right', prob: 0.86 }], raw: [{ toArm: 0, toLane: 1, type: 'through', prob: 0.91 }, { toArm: 1, toLane: 1, type: 'right', prob: 0.86 }] }}
              ]},
            { name: "West", street: "Park St", bearing: 274, approachLanes: 2, exitLanes: 3,
              lanes: [
                { index: 0, turns: { processed: [{ toArm: 0, toLane: 0, type: 'left', prob: 0.93 }, { toArm: 1, toLane: 0, type: 'through', prob: 0.89 }], raw: [{ toArm: 0, toLane: 0, type: 'left', prob: 0.93 }, { toArm: 1, toLane: 0, type: 'through', prob: 0.89 }] }},
                { index: 1, turns: { processed: [{ toArm: 1, toLane: 1, type: 'through', prob: 0.90 }, { toArm: 2, toLane: 1, type: 'right', prob: 0.84 }], raw: [{ toArm: 1, toLane: 1, type: 'through', prob: 0.90 }, { toArm: 2, toLane: 1, type: 'right', prob: 0.84 }] }}
              ]}
        ]
    },
    inter_2: {
        id: "128", name: "Glebe Point Rd & Francis St", location: "Glebe",
        lat: -33.8835982, lon: 151.1918044, zoom: 19,
        description: "3-way T-junction.",
        arms: [
            { name: "SE", street: "Glebe Point Rd", bearing: 130, approachLanes: 1, exitLanes: 1,
              lanes: [{ index: 0, turns: { processed: [{ toArm: 2, toLane: 0, type: 'through', prob: 0.94 }, { toArm: 1, toLane: 0, type: 'left', prob: 0.90 }], raw: [{ toArm: 2, toLane: 0, type: 'through', prob: 0.94 }, { toArm: 1, toLane: 0, type: 'left', prob: 0.90 }] }}]},
            { name: "NE", street: "Francis St", bearing: 36, approachLanes: 1, exitLanes: 1,
              lanes: [{ index: 0, turns: { processed: [{ toArm: 2, toLane: 0, type: 'left', prob: 0.91 }, { toArm: 0, toLane: 0, type: 'right', prob: 0.88 }], raw: [{ toArm: 2, toLane: 0, type: 'left', prob: 0.91 }, { toArm: 0, toLane: 0, type: 'right', prob: 0.88 }] }}]},
            { name: "NW", street: "Glebe Point Rd", bearing: 310, approachLanes: 1, exitLanes: 1,
              lanes: [{ index: 0, turns: { processed: [{ toArm: 0, toLane: 0, type: 'through', prob: 0.93 }, { toArm: 1, toLane: 0, type: 'right', prob: 0.89 }], raw: [{ toArm: 0, toLane: 0, type: 'through', prob: 0.93 }, { toArm: 1, toLane: 0, type: 'right', prob: 0.89 }] }}]}
        ]
    },
    inter_3: {
        id: "366", name: "Epping Rd & Balaclava Rd", location: "Macquarie Park",
        lat: -33.7777790, lon: 151.1081194, zoom: 18,
        description: "Arterial dual-carriageway intersection.",
        arms: [
            { name: "NE", street: "Balaclava Rd", bearing: 64, approachLanes: 3, exitLanes: 2,
              lanes: [
                { index: 0, turns: { processed: [{ toArm: 1, toLane: 0, type: 'left', prob: 0.95 }], raw: [{ toArm: 1, toLane: 0, type: 'left', prob: 0.95 }] }},
                { index: 1, turns: { processed: [{ toArm: 2, toLane: 0, type: 'through', prob: 0.91 }], raw: [{ toArm: 2, toLane: 0, type: 'through', prob: 0.91 }] }},
                { index: 2, turns: { processed: [{ toArm: 2, toLane: 1, type: 'through', prob: 0.87 }, { toArm: 3, toLane: 1, type: 'right', prob: 0.84 }], raw: [{ toArm: 2, toLane: 1, type: 'through', prob: 0.87 }, { toArm: 3, toLane: 1, type: 'right', prob: 0.84 }] }}
              ]},
            { name: "SE", street: "Epping Rd", bearing: 129, approachLanes: 4, exitLanes: 3,
              lanes: [
                { index: 0, turns: { processed: [{ toArm: 2, toLane: 0, type: 'left', prob: 0.96 }], raw: [{ toArm: 2, toLane: 0, type: 'left', prob: 0.96 }] }},
                { index: 1, turns: { processed: [{ toArm: 2, toLane: 1, type: 'left', prob: 0.91 }, { toArm: 3, toLane: 0, type: 'through', prob: 0.89 }], raw: [{ toArm: 2, toLane: 1, type: 'left', prob: 0.91 }, { toArm: 3, toLane: 0, type: 'through', prob: 0.89 }] }},
                { index: 2, turns: { processed: [{ toArm: 3, toLane: 1, type: 'through', prob: 0.93 }], raw: [{ toArm: 3, toLane: 1, type: 'through', prob: 0.93 }] }},
                { index: 3, turns: { processed: [{ toArm: 3, toLane: 2, type: 'through', prob: 0.88 }, { toArm: 0, toLane: 1, type: 'right', prob: 0.83 }], raw: [{ toArm: 3, toLane: 2, type: 'through', prob: 0.88 }, { toArm: 0, toLane: 1, type: 'right', prob: 0.83 }] }}
              ]},
            { name: "SW", street: "Balaclava Rd", bearing: 240, approachLanes: 2, exitLanes: 3,
              lanes: [
                { index: 0, turns: { processed: [{ toArm: 3, toLane: 0, type: 'left', prob: 0.92 }, { toArm: 0, toLane: 0, type: 'through', prob: 0.87 }], raw: [{ toArm: 3, toLane: 0, type: 'left', prob: 0.92 }, { toArm: 0, toLane: 0, type: 'through', prob: 0.87 }] }},
                { index: 1, turns: { processed: [{ toArm: 0, toLane: 1, type: 'through', prob: 0.90 }, { toArm: 1, toLane: 1, type: 'right', prob: 0.85 }], raw: [{ toArm: 0, toLane: 1, type: 'through', prob: 0.90 }, { toArm: 1, toLane: 1, type: 'right', prob: 0.85 }] }}
              ]},
            { name: "NW", street: "Epping Rd", bearing: 310, approachLanes: 4, exitLanes: 3,
              lanes: [
                { index: 0, turns: { processed: [{ toArm: 0, toLane: 0, type: 'left', prob: 0.94 }], raw: [{ toArm: 0, toLane: 0, type: 'left', prob: 0.94 }] }},
                { index: 1, turns: { processed: [{ toArm: 1, toLane: 0, type: 'through', prob: 0.92 }], raw: [{ toArm: 1, toLane: 0, type: 'through', prob: 0.92 }] }},
                { index: 2, turns: { processed: [{ toArm: 1, toLane: 1, type: 'through', prob: 0.90 }], raw: [{ toArm: 1, toLane: 1, type: 'through', prob: 0.90 }] }},
                { index: 3, turns: { processed: [{ toArm: 2, toLane: 1, type: 'right', prob: 0.88 }], raw: [{ toArm: 2, toLane: 1, type: 'right', prob: 0.88 }] }}
              ]}
        ]
    },
    inter_4: {
        id: "6762", name: "Parramatta Rd & Woodville Rd", location: "Granville",
        lat: -33.8275799, lon: 151.0047221, zoom: 18,
        description: "High-volume junction.",
        arms: [
            { name: "North", street: "Church St", bearing: 359, approachLanes: 3, exitLanes: 2,
              lanes: [
                { index: 0, turns: { processed: [{ toArm: 1, toLane: 0, type: 'left', prob: 0.95 }], raw: [{ toArm: 1, toLane: 0, type: 'left', prob: 0.95 }] }},
                { index: 1, turns: { processed: [{ toArm: 2, toLane: 0, type: 'through', prob: 0.91 }], raw: [{ toArm: 2, toLane: 0, type: 'through', prob: 0.91 }] }},
                { index: 2, turns: { processed: [{ toArm: 2, toLane: 1, type: 'through', prob: 0.88 }, { toArm: 3, toLane: 1, type: 'right', prob: 0.85 }], raw: [{ toArm: 2, toLane: 1, type: 'through', prob: 0.88 }, { toArm: 3, toLane: 1, type: 'right', prob: 0.85 }] }}
              ]},
            { name: "ESE", street: "Parramatta Rd", bearing: 111, approachLanes: 3, exitLanes: 3,
              lanes: [
                { index: 0, turns: { processed: [{ toArm: 2, toLane: 0, type: 'left', prob: 0.93 }], raw: [{ toArm: 2, toLane: 0, type: 'left', prob: 0.93 }] }},
                { index: 1, turns: { processed: [{ toArm: 3, toLane: 0, type: 'through', prob: 0.90 }], raw: [{ toArm: 3, toLane: 0, type: 'through', prob: 0.90 }] }},
                { index: 2, turns: { processed: [{ toArm: 3, toLane: 1, type: 'through', prob: 0.87 }, { toArm: 0, toLane: 1, type: 'right', prob: 0.84 }], raw: [{ toArm: 3, toLane: 1, type: 'through', prob: 0.87 }, { toArm: 0, toLane: 1, type: 'right', prob: 0.84 }] }}
              ]},
            { name: "South", street: "Woodville Rd", bearing: 179, approachLanes: 3, exitLanes: 2,
              lanes: [
                { index: 0, turns: { processed: [{ toArm: 3, toLane: 0, type: 'left', prob: 0.91 }], raw: [{ toArm: 3, toLane: 0, type: 'left', prob: 0.91 }] }},
                { index: 1, turns: { processed: [{ toArm: 0, toLane: 0, type: 'through', prob: 0.89 }], raw: [{ toArm: 0, toLane: 0, type: 'through', prob: 0.89 }] }},
                { index: 2, turns: { processed: [{ toArm: 0, toLane: 1, type: 'through', prob: 0.86 }, { toArm: 1, toLane: 1, type: 'right', prob: 0.83 }], raw: [{ toArm: 0, toLane: 1, type: 'through', prob: 0.86 }, { toArm: 1, toLane: 1, type: 'right', prob: 0.83 }] }}
              ]},
            { name: "WNW", street: "Parramatta Rd", bearing: 282, approachLanes: 4, exitLanes: 3,
              lanes: [
                { index: 0, turns: { processed: [{ toArm: 0, toLane: 0, type: 'left', prob: 0.94 }], raw: [{ toArm: 0, toLane: 0, type: 'left', prob: 0.94 }] }},
                { index: 1, turns: { processed: [{ toArm: 1, toLane: 0, type: 'through', prob: 0.92 }], raw: [{ toArm: 1, toLane: 0, type: 'through', prob: 0.92 }] }},
                { index: 2, turns: { processed: [{ toArm: 1, toLane: 1, type: 'through', prob: 0.89 }], raw: [{ toArm: 1, toLane: 1, type: 'through', prob: 0.89 }] }},
                { index: 3, turns: { processed: [{ toArm: 2, toLane: 1, type: 'right', prob: 0.87 }], raw: [{ toArm: 2, toLane: 1, type: 'right', prob: 0.87 }] }}
              ]}
        ]
    }
};

// ====== STAGE DETAIL DATA ======
const stageDetails = {
    1: {
        title: 'Stage 1: Lane Object Detection',
        sections: [
            { heading: 'Architecture', content: 'Faster R-CNN with a frozen ResNet backbone, implemented via Detectron2. Only the final dense layer is trained; all other ResNet parameters are frozen.' },
            { heading: 'Training', content: '6,000 iterations, batch size 5, SGD optimizer (lr=0.001), Focal Loss. 431 annotated arm segments with 36 distinct object classes.' },
            { heading: 'Output', content: 'Per-object bounding boxes with class probabilities. These are summed and projected onto the image x-axis, compressed to a 220-dim feature vector (10 aggregated classes × 22 lane slots).' },
            { heading: 'Key Classes', content: 'Arrow markings (7 types), vehicles (forward/backward/other), line markings (dashed/solid/median), stop lines, pedestrian crossings, speed markings, split islands.' }
        ]
    },
    2: {
        title: 'Stage 2: Lane Detection',
        sections: [
            { heading: 'Architecture', content: 'ResNet-18 processes the arm image (512-dim features). An MLP processes the 220-dim object projections + 3-dim bearing offsets. Both are concatenated and fed through a combined MLP producing a 22×8 lane attribute matrix.' },
            { heading: 'Loss Function', content: 'Weighted Cross-Entropy + Soft Dice Loss, computed separately for each attribute category (lane, lane_type, turns, slip). N/P ratio weights handle class imbalance, capped at 30.' },
            { heading: 'Augmentation', content: 'Horizontal lane slot shifting (±11 slots in thesis). Increases training data by 23×. Shifts are constrained so no positive labels are dropped.' },
            { heading: 'Output Activations', content: 'Sigmoid for binary attributes (lane, left, through, right, slip). Softmax for lane_type (mutually exclusive: no_lane / approach / exit).' }
        ]
    },
    3: {
        title: 'Stage 3: Turn Detection',
        sections: [
            { heading: 'Architecture', content: 'ResNet-18 for intersection image + MLP for stacked lane attributes (4 arms × 22 slots × 8 attrs = 704 values) and 4-dim bearings. Combined MLP outputs a 4×22×66 adjacency matrix.' },
            { heading: 'Loss Function', content: 'CE + Soft Dice with "almost impossible" area masking. Cells with N/P ratio ≥ 1000 receive lower CE weight (0.20 vs 0.40). Prevents the model from wasting capacity on near-impossible connections.' },
            { heading: 'Transfer Learning', content: 'Phase 1: Train on ground-truth lane attributes. Phase 2: Load Phase 1 weights, fine-tune on predicted lane attributes from Stage 2. This two-step process provides a better initialization.' },
            { heading: 'Augmentation', content: 'Slot shift (±1 per arm, constrained) × Intersection rotation (0°/90°/180°/270°). Combined factor: 324×. Training set grows from 674 to 218,376 samples.' }
        ]
    },
    4: {
        title: 'Stage 4: Post-Processing Heuristic (PPH)',
        sections: [
            { heading: 'Algorithm', content: 'Two-phase approach: Phase 1 processes ALL turns in descending probability order, classifying each as consistent or inconsistent. Phase 2 applies a probability threshold only to the consistent turns.' },
            { heading: 'Rules', content: '(1) No exit lanes to the left of an approach lane on the same arm. (2) No approach lanes to the right of an exit lane. (3-5) Turn-type ordering: Left ≤ Through ≤ Right from left to right slots. (6) No duplicate connections from same approach arm to same exit slot.' },
            { heading: 'Impact', content: 'Minimal effect on results (F1 change < 0.02). This suggests the neural network already learns mostly topologically consistent predictions.' },
            { heading: 'Design Rationale', content: 'Greedy descending-probability processing ensures high-confidence turns are accepted first and constrain lower-confidence ones, mimicking how a human would resolve ambiguities.' }
        ]
    }
};

// ====== CONSTANTS ======
const LANE_WIDTH = 3.5;
const LANE_LENGTH = 35;
const COLORS = {
    approach: '#3b82f6', exit: '#22c55e', divider: '#facc15',
    selected: '#e879f9', leftArrow: '#facc15', throughArrow: '#ffffff', rightArrow: '#f97316'
};
const TURN_ICONS = { left: '↰', through: '↑', right: '↱' };
const TURN_LABELS = { left: 'Left Turn', through: 'Straight', right: 'Right Turn' };

// ====== MAP STATE ======
let leafletMap = null;
let laneLayer = null;
let turnPathLayer = null;
let selectedLane = null;
let mapCurrentId = 'inter_1';
let mapDataMode = 'processed';
let tileSat = null;
let tileOsm = null;

// ====== GEO UTILS ======
function offsetLatLon(lat, lon, bearingDeg, dist) {
    const R = 6378137;
    const b = bearingDeg * Math.PI / 180;
    const dLat = (dist * Math.cos(b)) / R;
    const dLon = (dist * Math.sin(b)) / (R * Math.cos(lat * Math.PI / 180));
    return [lat + dLat * 180 / Math.PI, lon + dLon * 180 / Math.PI];
}

function perpOffset(lat, lon, bearing, offset) {
    return offsetLatLon(lat, lon, bearing + 90, offset);
}

// ====== PIPELINE STAGE CLICK ======
document.querySelectorAll('.pipeline-stage').forEach(el => {
    el.addEventListener('click', () => {
        const stage = parseInt(el.dataset.stage);
        showStageDetail(stage);
    });
});

function showStageDetail(stage) {
    const data = stageDetails[stage];
    const panel = document.getElementById('stage-detail');
    const content = document.getElementById('stage-detail-content');

    let html = `<h3 class="detail-title">${data.title}</h3><div class="detail-grid">`;
    data.sections.forEach(s => {
        html += `<div class="detail-section"><h4>${s.heading}</h4><p>${s.content}</p></div>`;
    });
    html += '</div>';
    content.innerHTML = html;
    panel.classList.remove('hidden');
    panel.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

function closeDetail() {
    document.getElementById('stage-detail').classList.add('hidden');
}

// ====== ADJACENCY MATRIX ======
const adjData = [
    // Elizabeth St & Park St — 4 arms
    { name: "Elizabeth St & Park St", arms: 4, matrix: null },
    // Glebe Point Rd — 3 arms (4 with virtual)
    { name: "Glebe Point Rd & Francis St", arms: 3, matrix: null },
    // Epping Rd — 4 arms
    { name: "Epping Rd & Balaclava Rd", arms: 4, matrix: null }
];

let adjView = 'prob';
let adjCurrentInter = 0;
let adjCurrentArm = 0;

// Generate synthetic adjacency matrices from intersection data
function generateAdjMatrix(interKey) {
    const inter = intersections[interKey];
    const matrix = new Float32Array(22 * 66).fill(0);

    inter.arms.forEach((arm, armIdx) => {
        if (!arm.lanes) return;
        arm.lanes.forEach(lane => {
            const turns = lane.turns.processed;
            turns.forEach(turn => {
                const exitArmIdx = turn.toArm;
                const d = ((exitArmIdx - armIdx) % inter.arms.length + inter.arms.length) % inter.arms.length;
                let colBlock;
                if (d === 1) colBlock = 0;       // Left
                else if (d === 2) colBlock = 22;  // Through
                else colBlock = 44;               // Right

                const row = lane.index;
                const col = colBlock + turn.toLane;
                matrix[row * 66 + col] = turn.prob;
            });
        });
    });
    return matrix;
}

// Build matrices for each intersection×arm
function buildAllMatrices() {
    const keys = ['inter_1', 'inter_2', 'inter_3'];
    keys.forEach((key, idx) => {
        const inter = intersections[key];
        const matrices = [];
        for (let a = 0; a < 4; a++) {
            if (a < inter.arms.length) {
                const mat = new Float32Array(22 * 66).fill(0);
                inter.arms[a].lanes.forEach(lane => {
                    lane.turns.processed.forEach(turn => {
                        const d = ((turn.toArm - a) % inter.arms.length + inter.arms.length) % inter.arms.length;
                        let colBlock = d === 1 ? 0 : d === 2 ? 22 : 44;
                        // Add some noise around the main probability to make it look more realistic
                        mat[lane.index * 66 + colBlock + turn.toLane] = turn.prob;
                        // Add faint nearby probabilities for realism
                        for (let dr = -1; dr <= 1; dr++) {
                            for (let dc = -1; dc <= 1; dc++) {
                                if (dr === 0 && dc === 0) continue;
                                const nr = lane.index + dr;
                                const nc = colBlock + turn.toLane + dc;
                                if (nr >= 0 && nr < 22 && nc >= 0 && nc < 66) {
                                    const noise = turn.prob * (0.05 + Math.random() * 0.1);
                                    mat[nr * 66 + nc] = Math.max(mat[nr * 66 + nc], noise);
                                }
                            }
                        }
                    });
                });
                matrices.push(mat);
            } else {
                matrices.push(new Float32Array(22 * 66).fill(0));
            }
        }
        adjData[idx].matrix = matrices;
    });
}

function drawAdjMatrix() {
    const canvas = document.getElementById('adj-canvas');
    const ctx = canvas.getContext('2d');
    const W = canvas.width;
    const H = canvas.height;
    const cellW = W / 66;
    const cellH = H / 22;

    ctx.clearRect(0, 0, W, H);

    const mat = adjData[adjCurrentInter].matrix[adjCurrentArm];
    if (!mat) return;

    for (let r = 0; r < 22; r++) {
        for (let c = 0; c < 66; c++) {
            let val = mat[r * 66 + c];
            if (adjView === 'binary') val = val > 0.5 ? 1.0 : 0.0;

            if (val > 0.001) {
                const color = valToColor(val);
                ctx.fillStyle = color;
                ctx.fillRect(c * cellW, r * cellH, cellW + 0.5, cellH + 0.5);
            }
        }
    }

    // Draw group separators
    ctx.strokeStyle = 'rgba(255,255,255,0.15)';
    ctx.lineWidth = 1;
    [22, 44].forEach(c => {
        ctx.beginPath();
        ctx.moveTo(c * cellW, 0);
        ctx.lineTo(c * cellW, H);
        ctx.stroke();
    });
}

function valToColor(v) {
    // Dark blue -> indigo -> purple -> light yellow
    v = Math.max(0, Math.min(1, v));
    if (v < 0.2) {
        const t = v / 0.2;
        return `rgb(${Math.round(6 + t * 24)}, ${Math.round(6 + t * 21)}, ${Math.round(15 + t * 60)})`;
    } else if (v < 0.5) {
        const t = (v - 0.2) / 0.3;
        return `rgb(${Math.round(30 + t * 37)}, ${Math.round(27 + t * 29)}, ${Math.round(75 + t * 127)})`;
    } else if (v < 0.8) {
        const t = (v - 0.5) / 0.3;
        return `rgb(${Math.round(67 + t * 62)}, ${Math.round(56 + t * 84)}, ${Math.round(202 + t * 46)})`;
    } else {
        const t = (v - 0.8) / 0.2;
        return `rgb(${Math.round(129 + t * 125)}, ${Math.round(140 + t * 103)}, ${Math.round(248 - t * 49)})`;
    }
}

// Adjacency canvas hover
document.getElementById('adj-canvas').addEventListener('mousemove', function(e) {
    const rect = this.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;
    const col = Math.floor(x / (rect.width / 66));
    const row = Math.floor(y / (rect.height / 22));

    if (row < 0 || row >= 22 || col < 0 || col >= 66) {
        document.getElementById('adj-tooltip').classList.add('hidden');
        return;
    }

    const mat = adjData[adjCurrentInter].matrix[adjCurrentArm];
    const val = mat ? mat[row * 66 + col] : 0;
    const turnType = col < 22 ? 'Left' : col < 44 ? 'Through' : 'Right';
    const exitSlot = col % 22;

    const tt = document.getElementById('adj-tooltip');
    tt.innerHTML = `Slot ${row + 1} → ${turnType} Exit ${exitSlot + 1}<br>P = ${val.toFixed(3)}`;
    tt.style.left = (e.clientX + 16) + 'px';
    tt.style.top = (e.clientY - 10) + 'px';
    tt.classList.remove('hidden');
});

document.getElementById('adj-canvas').addEventListener('mouseleave', function() {
    document.getElementById('adj-tooltip').classList.add('hidden');
});

// Adjacency controls
document.getElementById('adj-intersection').addEventListener('change', function() {
    adjCurrentInter = parseInt(this.value);
    drawAdjMatrix();
});

document.getElementById('adj-arm').addEventListener('change', function() {
    adjCurrentArm = parseInt(this.value);
    drawAdjMatrix();
});

function setAdjView(mode) {
    adjView = mode;
    document.getElementById('adj-btn-prob').classList.toggle('active', mode === 'prob');
    document.getElementById('adj-btn-binary').classList.toggle('active', mode === 'binary');
    drawAdjMatrix();
}

// ====== MAP ======
function initMap() {
    const inter = intersections[mapCurrentId];
    leafletMap = L.map('demo-map', {
        center: [inter.lat, inter.lon], zoom: inter.zoom, zoomControl: false
    });
    L.control.zoom({ position: 'bottomright' }).addTo(leafletMap);

    tileSat = L.tileLayer('https://mt1.google.com/vt/lyrs=s&x={x}&y={y}&z={z}', { maxZoom: 22 });
    tileOsm = L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', { maxZoom: 19 });
    tileSat.addTo(leafletMap);

    laneLayer = L.layerGroup().addTo(leafletMap);
    turnPathLayer = L.layerGroup().addTo(leafletMap);

    leafletMap.on('click', clearMapSelection);
    drawMapIntersection();

    document.getElementById('map-intersection-select').addEventListener('change', function() {
        mapCurrentId = this.value;
        const inter = intersections[mapCurrentId];
        leafletMap.setView([inter.lat, inter.lon], inter.zoom);
        clearMapSelection();
        drawMapIntersection();
    });
}

function setMapTile(type) {
    if (type === 'satellite') { leafletMap.removeLayer(tileOsm); tileSat.addTo(leafletMap); }
    else { leafletMap.removeLayer(tileSat); tileOsm.addTo(leafletMap); }
    document.getElementById('map-btn-sat').classList.toggle('active', type === 'satellite');
    document.getElementById('map-btn-osm').classList.toggle('active', type === 'osm');
}

function setMapMode(mode) {
    mapDataMode = mode;
    document.getElementById('map-btn-proc').classList.toggle('active', mode === 'processed');
    document.getElementById('map-btn-raw').classList.toggle('active', mode === 'raw');
    clearMapSelection();
    drawMapIntersection();
}

function clearMapSelection() {
    turnPathLayer.clearLayers();
    selectedLane = null;
    document.getElementById('map-turn-info').classList.add('hidden');
    drawMapIntersection();
}

function closeMapTurnInfo() { clearMapSelection(); }

function drawMapIntersection() {
    laneLayer.clearLayers();
    turnPathLayer.clearLayers();
    const inter = intersections[mapCurrentId];
    const center = [inter.lat, inter.lon];
    inter.arms.forEach((arm, idx) => drawArm(inter, arm, idx, center));
}

function drawArm(inter, arm, armIdx, center) {
    const bearing = arm.bearing;
    const oppBearing = (bearing + 180) % 360;
    const armNear = offsetLatLon(center[0], center[1], bearing, 8);
    const armFar = offsetLatLon(center[0], center[1], bearing, LANE_LENGTH);

    // Approach lanes
    for (let i = 0; i < arm.approachLanes; i++) {
        const off = (i + 0.5) * LANE_WIDTH;
        const start = perpOffset(armFar[0], armFar[1], bearing, off);
        const end = perpOffset(armNear[0], armNear[1], bearing, off);
        const isSel = selectedLane && selectedLane.armIdx === armIdx && selectedLane.laneIdx === i;

        const line = L.polyline([start, end], {
            color: isSel ? COLORS.selected : COLORS.approach,
            weight: 6, opacity: 0.85, lineCap: 'butt'
        });
        line.on('click', function(e) { L.DomEvent.stopPropagation(e); selectMapLane(armIdx, i, inter); });

        const lane = arm.lanes[i];
        if (lane) {
            const turns = lane.turns[mapDataMode];
            const labels = turns.map(t => TURN_ICONS[t.type]).join(' ');
            line.bindTooltip(`<b>${arm.street} — Lane ${i+1}</b><br>${labels}`, { className: 'lane-tooltip', sticky: true });
        }
        laneLayer.addLayer(line);

        // Turn arrows
        if (lane) {
            const turns = lane.turns[mapDataMode];
            const frac = 0.6;
            const mLat = armFar[0] + (armNear[0]-armFar[0])*frac;
            const mLon = armFar[1] + (armNear[1]-armFar[1])*frac;
            const mid = perpOffset(mLat, mLon, bearing, off);
            const types = [...new Set(turns.map(t => t.type))];
            const arrowHtml = types.map(t => {
                const c = t==='left'?COLORS.leftArrow:t==='right'?COLORS.rightArrow:COLORS.throughArrow;
                return `<span style="color:${c};font-size:20px;font-weight:bold;text-shadow:0 0 6px rgba(0,0,0,0.9)">${TURN_ICONS[t]}</span>`;
            }).join('');
            laneLayer.addLayer(L.marker(mid, {
                icon: L.divIcon({ className: '', html: `<div style="display:flex;gap:3px;transform:rotate(${oppBearing}deg);pointer-events:none">${arrowHtml}</div>`, iconSize: [types.length*24,24], iconAnchor: [types.length*12,12] }),
                interactive: false, zIndexOffset: 100
            }));
        }
    }

    // Exit lanes
    for (let i = 0; i < arm.exitLanes; i++) {
        const off = -(i + 0.5) * LANE_WIDTH;
        const start = perpOffset(armNear[0], armNear[1], bearing, off);
        const end = perpOffset(armFar[0], armFar[1], bearing, off);
        laneLayer.addLayer(L.polyline([start, end], { color: COLORS.exit, weight: 4, opacity: 0.5, lineCap: 'butt', dashArray: '10,8' }));
    }

    // Divider
    laneLayer.addLayer(L.polyline([armNear, armFar], { color: COLORS.divider, weight: 2, opacity: 0.6, dashArray: '6,10' }));

    // Label
    const lPt = offsetLatLon(armFar[0], armFar[1], bearing, 8);
    laneLayer.addLayer(L.marker(lPt, {
        icon: L.divIcon({ className: 'arm-label', html: `<div style="transform:rotate(${bearing>180?bearing-270:bearing-90}deg)">${arm.street}</div>`, iconSize: [80,20], iconAnchor: [40,10] }),
        interactive: false
    }));
}

function selectMapLane(armIdx, laneIdx, inter) {
    clearMapSelection();
    selectedLane = { armIdx, laneIdx };
    const arm = inter.arms[armIdx];
    const lane = arm.lanes[laneIdx];
    if (!lane) return;
    const turns = lane.turns[mapDataMode];
    const center = [inter.lat, inter.lon];

    turns.forEach(turn => {
        const destArm = inter.arms[turn.toArm];
        if (!destArm) return;
        const srcOff = (laneIdx + 0.5) * LANE_WIDTH;
        const srcStart = offsetLatLon(center[0], center[1], arm.bearing, LANE_LENGTH);
        const srcPt = perpOffset(srcStart[0], srcStart[1], arm.bearing, srcOff);
        const srcMid = perpOffset(offsetLatLon(center[0], center[1], arm.bearing, 8)[0], offsetLatLon(center[0], center[1], arm.bearing, 8)[1], arm.bearing, srcOff);
        const dstOff = -(turn.toLane + 0.5) * LANE_WIDTH;
        const dstEnd = offsetLatLon(center[0], center[1], destArm.bearing, LANE_LENGTH);
        const dstPt = perpOffset(dstEnd[0], dstEnd[1], destArm.bearing, dstOff);
        const dstMid = perpOffset(offsetLatLon(center[0], center[1], destArm.bearing, 8)[0], offsetLatLon(center[0], center[1], destArm.bearing, 8)[1], destArm.bearing, dstOff);
        const pc = turn.type==='left'?COLORS.leftArrow:turn.type==='right'?COLORS.rightArrow:COLORS.throughArrow;
        turnPathLayer.addLayer(L.polyline([srcPt, srcMid, center, dstMid, dstPt], { color: pc, weight: 4, opacity: 0.9, dashArray: '10,6' }));
        turnPathLayer.addLayer(L.circleMarker(dstPt, { radius: 6, color: pc, fillColor: pc, fillOpacity: 0.9, weight: 2 }));
    });

    drawMapIntersection();

    // Show info panel
    const panel = document.getElementById('map-turn-info');
    document.getElementById('mti-title').textContent = `${arm.street} — Lane ${laneIdx+1}`;
    let html = '';
    turns.forEach(t => {
        const dest = inter.arms[t.toArm];
        html += `<div class="turn-item">
            <div class="turn-icon-box ${t.type}">${TURN_ICONS[t.type]}</div>
            <div class="turn-detail"><div class="turn-type-text">${TURN_LABELS[t.type]}</div><div class="turn-dest-text">→ ${dest?dest.street:'?'} Lane ${t.toLane+1}</div></div>
            <div class="turn-prob">${Math.round(t.prob*100)}%</div>
        </div>`;
    });
    document.getElementById('mti-body').innerHTML = html;
    panel.classList.remove('hidden');
}

// ====== SCROLL SPY ======
function updateActiveNav() {
    const sections = ['hero', 'pipeline', 'adjacency', 'map-section', 'metrics'];
    const scrollY = window.scrollY + 100;
    let activeId = 'hero';
    sections.forEach(id => {
        const el = document.getElementById(id);
        if (el && el.offsetTop <= scrollY) activeId = id;
    });
    document.querySelectorAll('.nav-link').forEach(link => {
        const href = link.getAttribute('href').slice(1);
        link.classList.toggle('active', href === activeId);
    });
}
window.addEventListener('scroll', updateActiveNav);

// ====== INIT ======
document.addEventListener('DOMContentLoaded', function() {
    buildAllMatrices();
    drawAdjMatrix();
    initMap();
});
