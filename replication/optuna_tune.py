import os
import sys
import json
import argparse
import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import DataLoader
import optuna

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from replication.data_encoding import DatasetEncoder
from replication.train import LaneDataset, TurnDataset
from replication.models import LaneDetector, TurnDetector
from replication.losses import LaneLoss, TurnLoss

def objective_lane(trial, args, encoder):
    # Suggest hyperparameters
    lr = trial.suggest_float("lr", 1e-5, 1e-2, log=True)
    batch_size = trial.suggest_categorical("batch_size", [8, 16, 32])
    
    lane_ce = trial.suggest_float("lane_ce", 0.05, 0.40)
    lane_dice = trial.suggest_float("lane_dice", 0.05, 0.40)
    type_ce = trial.suggest_float("type_ce", 0.05, 0.30)
    type_dice = trial.suggest_float("type_dice", 0.05, 0.30)
    turn_ce = trial.suggest_float("turn_ce", 0.05, 0.20)
    turn_dice = trial.suggest_float("turn_dice", 0.05, 0.20)
    slip_ce = trial.suggest_float("slip_ce", 0.01, 0.10)
    slip_dice = trial.suggest_float("slip_dice", 0.01, 0.10)
    
    loss_weights = {
        'lane_ce': lane_ce, 'lane_dice': lane_dice,
        'type_ce': type_ce, 'type_dice': type_dice,
        'turn_ce': turn_ce, 'turn_dice': turn_dice,
        'slip_ce': slip_ce, 'slip_dice': slip_dice
    }
    
    # Load splits
    split_path = os.path.join(args.data_dir, "labels", "turns", "data_split.json")
    with open(split_path, "r", encoding="utf-8") as f:
        splits = json.load(f)
        
    train_ids = splits['train']
    val_ids = splits['val']
    
    if args.subset:
        train_ids = train_ids[:args.subset]
        val_ids = val_ids[:max(1, args.subset // 4)]
        
    # Datasets & Dataloaders
    train_dataset = LaneDataset(args.data_dir, train_ids, encoder, augment=True)
    val_dataset = LaneDataset(args.data_dir, val_ids, encoder, augment=False)
    
    drop_last = len(train_dataset) >= batch_size
    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True, drop_last=drop_last)
    val_loader = DataLoader(val_dataset, batch_size=batch_size, shuffle=False)
    
    # Model
    model = LaneDetector(frozen_resnet=True)
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    model.to(device)
    
    # Loss & Optim
    optimizer = torch.optim.Adam(model.parameters(), lr=lr)
    criterion = LaneLoss(loss_weights=loss_weights)
    
    # Train for a few epochs to evaluate performance
    epochs = args.epochs
    for epoch in range(epochs):
        model.train()
        for img, non_img, targets in train_loader:
            img = img.to(device)
            non_img = non_img.to(device)
            targets_dev = {k: v.to(device) for k, v in targets.items()}
            
            optimizer.zero_grad()
            preds = model(img, non_img)
            loss = criterion(preds, targets_dev)
            loss.backward()
            optimizer.step()
            
    # Evaluation
    model.eval()
    val_loss = 0.0
    with torch.no_grad():
        for img, non_img, targets in val_loader:
            img = img.to(device)
            non_img = non_img.to(device)
            targets_dev = {k: v.to(device) for k, v in targets.items()}
            preds = model(img, non_img)
            loss = criterion(preds, targets_dev)
            val_loss += loss.item()
            
    return val_loss / len(val_loader) if len(val_loader) > 0 else float('inf')

def objective_turn(trial, args, encoder, np_ratios):
    # Suggest hyperparameters
    lr = trial.suggest_float("lr", 1e-5, 1e-2, log=True)
    batch_size = trial.suggest_categorical("batch_size", [8, 16, 32])
    
    ce_weight_interest = trial.suggest_float("ce_weight_interest", 0.1, 0.8)
    ce_weight_impossible = trial.suggest_float("ce_weight_impossible", 0.05, 0.5)
    dice_weight = trial.suggest_float("dice_weight", 0.1, 0.9)
    weight_cap = trial.suggest_float("weight_cap", 10.0, 50.0)
    np_threshold = trial.suggest_float("np_threshold", 100.0, 5000.0, log=True)
    
    # Load splits
    split_path = os.path.join(args.data_dir, "labels", "turns", "data_split.json")
    with open(split_path, "r", encoding="utf-8") as f:
        splits = json.load(f)
        
    train_ids = splits['train']
    val_ids = splits['val']
    
    if args.subset:
        train_ids = train_ids[:args.subset]
        val_ids = val_ids[:max(1, args.subset // 4)]
        
    # Datasets & Dataloaders
    train_dataset = TurnDataset(args.data_dir, train_ids, encoder, use_gt_lane_attrs=True, augment=True)
    val_dataset = TurnDataset(args.data_dir, val_ids, encoder, use_gt_lane_attrs=True, augment=False)
    
    drop_last = len(train_dataset) >= batch_size
    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True, drop_last=drop_last)
    val_loader = DataLoader(val_dataset, batch_size=batch_size, shuffle=False)
    
    # Model
    model = TurnDetector(frozen_resnet=True)
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    model.to(device)
    
    # Loss & Optim
    optimizer = torch.optim.Adam(model.parameters(), lr=lr)
    criterion = TurnLoss(np_ratios=np_ratios, ce_weight_interest=ce_weight_interest,
                          ce_weight_impossible=ce_weight_impossible, dice_weight=dice_weight,
                          weight_cap=weight_cap, np_threshold=np_threshold)
    criterion.to(device)  # Move TurnLoss buffers to GPU
    
    # Train for a few epochs
    epochs = args.epochs
    for epoch in range(epochs):
        model.train()
        for img, non_img, targets in train_loader:
            img = img.to(device)
            non_img = non_img.to(device)
            targets = targets.to(device)
            
            optimizer.zero_grad()
            preds = model(img, non_img)
            loss = criterion(preds, targets)
            loss.backward()
            optimizer.step()
            
    # Evaluation
    model.eval()
    val_loss = 0.0
    with torch.no_grad():
        for img, non_img, targets in val_loader:
            img = img.to(device)
            non_img = non_img.to(device)
            targets = targets.to(device)
            preds = model(img, non_img)
            loss = criterion(preds, targets)
            val_loss += loss.item()
            
    return val_loss / len(val_loader) if len(val_loader) > 0 else float('inf')

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Tune Lane or Turn Detectors using Optuna")
    parser.add_argument("--stage", type=str, default="3", choices=["2", "3"], help="Stage to tune (2 for Lane, 3 for Turn)")
    parser.add_argument("--trials", type=int, default=10, help="Number of Optuna trials")
    parser.add_argument("--epochs", type=int, default=3, help="Number of training epochs per trial")
    parser.add_argument("--data_dir", type=str, default=r"f:\Road\main_task\data", help="Dataset directory")
    parser.add_argument("--subset", type=int, default=10, help="Subset size for quick evaluation")
    
    args = parser.parse_args()
    
    encoder = DatasetEncoder(args.data_dir)
    
    optuna.logging.set_verbosity(optuna.logging.INFO)
    study = optuna.create_study(direction="minimize")
    
    if args.stage == "2":
        print(f"--- STARTING OPTUNA STUDY FOR LANE DETECTOR ({args.trials} trials) ---")
        study.optimize(lambda trial: objective_lane(trial, args, encoder), n_trials=args.trials)
    else:
        print(f"--- STARTING OPTUNA STUDY FOR TURN DETECTOR ({args.trials} trials) ---")
        # Precompute N/P ratios for training subset
        split_path = os.path.join(args.data_dir, "labels", "turns", "data_split.json")
        with open(split_path, "r", encoding="utf-8") as f:
            splits = json.load(f)
        train_ids = splits['train']
        if args.subset:
            train_ids = train_ids[:args.subset]
            
        y_train_list = []
        for inter_id in train_ids:
            y_train_list.append(encoder.encode_intersection_turns(inter_id))
        y_train_arr = np.stack(y_train_list)
        positives = np.sum(y_train_arr, axis=0)
        negatives = len(train_ids) - positives
        np_ratios = np.zeros_like(positives)
        for a in range(4):
            for s in range(22):
                for c in range(66):
                    p = positives[a, s, c]
                    n = negatives[a, s, c]
                    np_ratios[a, s, c] = 1000.0 if p == 0 else n / p
                    
        study.optimize(lambda trial: objective_turn(trial, args, encoder, np_ratios), n_trials=args.trials)
        
    print("\n--- OPTUNA TUNING COMPLETED ---")
    print(f"Best Trial value (Val Loss): {study.best_trial.value:.4f}")
    print("Best hyperparameters:")
    for k, v in study.best_trial.params.items():
        print(f"  {k}: {v}")
