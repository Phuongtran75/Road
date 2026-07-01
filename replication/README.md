# Lane-Level Intersection Topology Replication Codebase

This repository contains a complete, research-grade Python/PyTorch replication codebase for Hugo Nilsson's 2024 and 2026 publications on signalized intersection lane-level topology inference.

## Pipeline Architecture

The pipeline consists of a **staged modeling architecture** with **post-processing rules**:

1. **Stage 1 (Oriented Object Detector)**: Predicts 32 detailed classes of lane markings and vehicles in rotated arm images.
2. **Stage 2 (Lane Detector)**: A CNN + MLP architecture that takes rotated arm images, bearing offsets, and Stage 1 projected object detections (220-dim feature vector) as input and outputs slot-wise lane presence, type, and allowed turn directions for 22 slots.
3. **Stage 3 (Turn Detector)**: Stacked attributes from all arms and absolute arm bearings are passed along with intersection imagery to output a $4 \times 22 \times 66$ turn adjacency matrix (4 approach arms × 22 lane slots × 66 exit columns).
4. **Stage 4 (Post-Processing Heuristic)**: A rule-based heuristic that processes probabilities in descending order to enforce topological consistency.

## Project Structure

```
f:\Road\replication\
├── README.md               <-- This documentation
├── data_encoding.py        <-- Lane slot mapping and adjacency matrix construction
├── models.py               <-- PyTorch model definitions for LaneDetector & TurnDetector
├── losses.py               <-- Weighted CE and Soft Dice loss formulations
├── post_processing.py      <-- Post-Processing Heuristic (PPH) rules
├── train.py                <-- Data loading pipelines and PyTorch training loops
├── optuna_tune.py          <-- Hyperparameter optimization using Optuna (TPE)
└── evaluation.py           <-- Turn-level, slot-level, and arm-level evaluation & baseline
```

## Setup & Dependencies

Ensure you have PyTorch, torchvision, and Optuna installed:
```bash
pip install torch torchvision optuna numpy pillow scipy scikit-learn
```

## Running the Codebase

### 1. Model Training

To train the models on the complete dataset:
```bash
# Train both Lane Detector (Stage 2) and Turn Detector (Stage 3)
python replication/train.py --stage both --epochs 20 --batch_size 16

# Train only the Turn Detector
python replication/train.py --stage 3 --epochs 20 --batch_size 16
```

### 2. Hyperparameter Tuning

To run hyperparameter optimization using Optuna's Tree-structured Parzen Estimator (TPE):
```bash
# Tune the Turn Detector (Stage 3) for 10 trials
python replication/optuna_tune.py --stage 3 --trials 10 --epochs 3
```

### 3. Evaluation

To run evaluations on pre-computed or saved prediction checkpoints:
```bash
# Verify evaluation on test split excluding virtual/exit-only arms
python scratch/verify_eval_no_virtual.py
```

## Key Findings & Reproductions
* **Adjacency Matrix dimensions**: $4 \times 22 \times 66$.
* **Soft Dice + Weighted CE loss** with class imbalance caps (at 30) and "almost impossible" area masking (for cell N/P ratios $\ge 1000$) are fully implemented in `losses.py`.
* The **Post-Processing Heuristic (PPH)** is implemented in `post_processing.py`.
