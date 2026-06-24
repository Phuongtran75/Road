import os
import sys
import json
import argparse
import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader
from PIL import Image

# Setup path to import replication modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from replication.data_encoding import DatasetEncoder, get_3way_transform_mapping
from replication.models import LaneDetector, TurnDetector
from replication.losses import LaneLoss, TurnLoss
from replication.evaluation import evaluate_predictions

# Detailed to 10-class aggregation mapping
DETAILED_TO_10_CLASSES = {
    0: 0,  # Arrow left -> Left arrow
    1: 1,  # Arrow right -> Right arrow
    2: 0,  # Arrow right left -> Left arrow
    3: 1,  # Arrow right through -> Right arrow
    4: 2,  # Arrow right through left -> Through arrow
    5: 2,  # Arrow through -> Through arrow
    6: 0,  # Arrow through left -> Left arrow
    7: 9,  # Bus lane -> Other
    8: 4,  # Car backward -> Cars backward
    9: 3,  # Car forward -> Cars forward
    10: 5, # Car other -> Cars other
    11: 9, # Cycle lane -> Other
    12: 4, # Large vehicle backward -> Cars backward
    13: 3, # Large vehicle forward -> Cars forward
    14: 5, # Large vehicle other -> Cars other
    15: 9, # Line horizontal other -> Other
    16: 8, # Line vertical give way -> Stop line
    17: 7, # Line vertical lane -> Dashed line
    18: 6, # Line vertical lane solid -> Solid line
    19: 6, # Line vertical median -> Solid line
    20: 9, # Line vertical other -> Other
    21: 7, # Line vertical parking -> Dashed line
    22: 6, # Line vertical verge -> Solid line
    23: 9, # Median painted -> Other
    24: 6, # Median physical -> Solid line
    25: 9, # Other road marking -> Other
    26: 9, # Pedestrian crossing signalised -> Other
    27: 9, # Pedestrian crossing zebra -> Other
    28: 9, # Speed marking -> Other
    29: 6, # Split island -> Solid line
    30: 8, # Stop line -> Stop line
    31: 9, # Verge painted -> Other
}

def apply_lane_slot_shift_augmentation(projections, targets, max_shift=1):
    """
    Randomly shifts single arm projection features and corresponding target attributes.
    projections: 220-dim numpy array (22 slots x 10 classes)
    targets: dict containing target tensors of shape (22,)
    """
    shift = np.random.randint(-max_shift, max_shift + 1)
    if shift == 0:
        return projections, targets
        
    # Shift projections
    proj_reshaped = projections.reshape(22, 10)
    shifted_proj = np.zeros_like(proj_reshaped)
    if shift > 0:
        shifted_proj[shift:] = proj_reshaped[:-shift]
    else:
        shifted_proj[:shift] = proj_reshaped[-shift:]
    new_projections = shifted_proj.flatten()
    
    # Shift targets
    new_targets = {}
    for k, v in targets.items():
        shifted_v = torch.zeros_like(v)
        if shift > 0:
            shifted_v[shift:] = v[:-shift]
        else:
            shifted_v[:shift] = v[-shift:]
        new_targets[k] = shifted_v
        
    return new_projections, new_targets

class LaneDataset(Dataset):
    """
    Dataset for training/evaluating the Stage 2 Lane Detector.
    """
    def __init__(self, data_dir, split_ids, encoder, transform=None, augment=False):
        self.data_dir = data_dir
        self.split_ids = split_ids
        self.encoder = encoder
        self.transform = transform
        self.augment = augment
        
        # Load detailed COCO results to build projections
        self.detections_by_image = {}
        self.image_id_to_filename = {}
        
        # Load COCO template detailed to map image_id to filename
        tmpl_path = os.path.join(data_dir, "predictions", "lane_objects", "coco_template_detailed.json")
        if not os.path.exists(tmpl_path):
            tmpl_path = os.path.join(data_dir, "coco_template_detailed.json")
            
        if os.path.exists(tmpl_path):
            with open(tmpl_path, "r", encoding="utf-8") as f:
                tmpl = json.load(f)
                for img in tmpl.get('images', []):
                    self.image_id_to_filename[img['id']] = img['file_name']
                    
        # Load detections
        det_path = os.path.join(data_dir, "predictions", "lane_objects", "version_14", "coco_instances_results_detailed.json")
        if not os.path.exists(det_path):
            det_path = os.path.join(data_dir, "coco_instances_results_detailed.json")
            
        if os.path.exists(det_path):
            with open(det_path, "r", encoding="utf-8") as f:
                detections = json.load(f)
                for d in detections:
                    img_id = d['image_id']
                    if img_id not in self.detections_by_image:
                        self.detections_by_image[img_id] = []
                    self.detections_by_image[img_id].append(d)
                    
        # Map filename back to detections
        self.filename_to_detections = {}
        for img_id, det_list in self.detections_by_image.items():
            fname = self.image_id_to_filename.get(img_id)
            if fname:
                self.filename_to_detections[fname] = det_list
                
        # Build samples list: for each intersection in split, gather physical arms
        self.samples = []
        for inter_id in self.split_ids:
            info = encoder.get_intersection_info(inter_id)
            if not info:
                continue
                
            arms = info['arms']
            is_3way = len(arms) == 3
            if is_3way:
                new_arms, arm_mapping = get_3way_transform_mapping(arms)
            else:
                new_arms = sorted(arms, key=lambda x: x['bearing'] % 360)
                arm_mapping = {arm['label']: idx + 1 for idx, arm in enumerate(new_arms)}
                
            for idx, arm in enumerate(new_arms):
                if arm.get('is_virtual'):
                    continue
                # Construct sample
                self.samples.append({
                    'intersection_id': inter_id,
                    'arm_info': arm,
                    'all_arms': new_arms,
                    'arm_idx': idx
                })

    def __len__(self):
        return len(self.samples)

    def __getitem__(self, idx):
        sample = self.samples[idx]
        arm_info = sample['arm_info']
        all_arms = sample['all_arms']
        arm_idx = sample['arm_idx']
        
        # 1. Load image
        img_name = arm_info.get('file_name')
        img_path = os.path.join(self.data_dir, img_name) if img_name else None
        
        img_tensor = torch.zeros((3, 224, 224), dtype=torch.float32)
        if img_path and os.path.exists(img_path):
            try:
                with Image.open(img_path) as img:
                    img = img.convert('RGB').resize((224, 224))
                    # Normalization values
                    arr = np.array(img, dtype=np.float32) / 255.0
                    mean = np.array([0.485, 0.456, 0.406], dtype=np.float32)
                    std = np.array([0.229, 0.224, 0.225], dtype=np.float32)
                    arr = (arr - mean) / std
                    img_tensor = torch.from_numpy(arr.transpose(2, 0, 1))
            except Exception as e:
                pass
                
        # 2. Compute 220-dimensional projections
        projections = np.zeros(220, dtype=np.float32)
        detections = self.filename_to_detections.get(img_name, [])
        for det in detections:
            cat_id = det['category_id']
            if cat_id not in DETAILED_TO_10_CLASSES:
                continue
            cls_10 = DETAILED_TO_10_CLASSES[cat_id]
            
            bbox = det['bbox'] # [x, y, w, h]
            cx = bbox[0] + bbox[2] / 2.0
            
            # Map cx (0 to 1000) to slot (0 to 21)
            slot_idx = int(cx / (1000.0 / 22.0))
            slot_idx = max(0, min(21, slot_idx))
            
            # Add score to projection feature
            projections[slot_idx * 10 + cls_10] += det['score']
            
        # 3. Compute bearing offsets (angular distance from current arm to others)
        bearing_offsets = np.zeros(3, dtype=np.float32)
        ref_bearing = arm_info['bearing']
        
        # Relative clockwise offsets to remaining 3 arms
        offset_idx = 0
        for i in range(1, 4):
            other_arm = all_arms[(arm_idx + i) % 4]
            diff = (other_arm['bearing'] - ref_bearing) % 360
            bearing_offsets[offset_idx] = diff / 360.0
            offset_idx += 1
            
        # 4. Get ground-truth lane slot attributes
        # label matrix shape: (22, 8)
        arm_id = arm_info['id']
        targets_matrix = self.encoder.encode_lane_attributes(arm_id)
        
        # Split target matrix into target dict
        targets = {
            'lane': torch.tensor(targets_matrix[:, 0], dtype=torch.float32),
            'lane_type': torch.tensor(targets_matrix[:, 1], dtype=torch.long),
            'slip': torch.tensor(targets_matrix[:, 2], dtype=torch.float32),
            'left': torch.tensor(targets_matrix[:, 3], dtype=torch.float32),
            'through': torch.tensor(targets_matrix[:, 4], dtype=torch.float32),
            'right': torch.tensor(targets_matrix[:, 5], dtype=torch.float32)
        }
        
        if self.augment:
            projections, targets = apply_lane_slot_shift_augmentation(projections, targets)
            
        non_img_features = np.concatenate([projections, bearing_offsets])
        
        return img_tensor, torch.from_numpy(non_img_features), targets

class TurnDataset(Dataset):
    """
    Dataset for training/evaluating the Stage 3 Turn Detector.
    """
    def __init__(self, data_dir, split_ids, encoder, use_gt_lane_attrs=True, augment=False):
        self.data_dir = data_dir
        self.split_ids = split_ids
        self.encoder = encoder
        self.use_gt_lane_attrs = use_gt_lane_attrs
        self.augment = augment
        
        # Load lane predictions if using predicted attributes
        self.lane_predictions = {}
        if not use_gt_lane_attrs:
            pred_path = os.path.join(data_dir, "predictions", "lanes", "version_73", "lane_predictions.json")
            if not os.path.exists(pred_path):
                pred_path = os.path.join(data_dir, "lane_predictions.json")
                
            if os.path.exists(pred_path):
                with open(pred_path, "r", encoding="utf-8") as f:
                    preds_raw = json.load(f)
                    
                # Group predictions by arm_id and slot
                for idx_str, arm_id in preds_raw['arm_id'].items():
                    slot = preds_raw['lane_slot'][idx_str]
                    if arm_id not in self.lane_predictions:
                        self.lane_predictions[arm_id] = {}
                        
                    # Extract attributes
                    l_type = 0
                    if preds_raw['approach'][idx_str] > 0.5:
                        l_type = 1
                    elif preds_raw['exit'][idx_str] > 0.5:
                        l_type = 2
                        
                    self.lane_predictions[arm_id][slot] = {
                        'lane': preds_raw['lane'][idx_str],
                        'l_type': l_type,
                        'slip': preds_raw['slip'][idx_str],
                        'left': preds_raw['left'][idx_str],
                        'through': preds_raw['through'][idx_str],
                        'right': preds_raw['right'][idx_str],
                        'approach': preds_raw['approach'][idx_str],
                        'exit': preds_raw['exit'][idx_str]
                    }

    def __len__(self):
        return len(self.split_ids)

    def __getitem__(self, idx):
        inter_id = self.split_ids[idx]
        info = self.encoder.get_intersection_info(inter_id)
        
        # 1. Load intersection-centered image (zeros as fallback since i_*.png missing)
        img_name = info.get('file_name')
        img_path = os.path.join(self.data_dir, img_name) if img_name else None
        
        img_tensor = torch.zeros((3, 224, 224), dtype=torch.float32)
        if img_path and os.path.exists(img_path):
            try:
                with Image.open(img_path) as img:
                    img = img.convert('RGB').resize((224, 224))
                    arr = np.array(img, dtype=np.float32) / 255.0
                    mean = np.array([0.485, 0.456, 0.406], dtype=np.float32)
                    std = np.array([0.229, 0.224, 0.225], dtype=np.float32)
                    arr = (arr - mean) / std
                    img_tensor = torch.from_numpy(arr.transpose(2, 0, 1))
            except Exception as e:
                pass
                
        # 2. Get stacked lane slot attributes (4 arms x 22 slots x 8 attributes)
        arms = info['arms']
        is_3way = len(arms) == 3
        if is_3way:
            new_arms, arm_mapping = get_3way_transform_mapping(arms)
        else:
            new_arms = sorted(arms, key=lambda x: x['bearing'] % 360)
            
        lane_attrs = np.zeros((4, 22, 8), dtype=np.float32)
        for idx, arm in enumerate(new_arms):
            if arm.get('is_virtual'):
                continue
                
            arm_id = arm['id']
            if self.use_gt_lane_attrs:
                # Use ground-truth attributes
                lane_attrs[idx] = self.encoder.encode_lane_attributes(arm_id)
            else:
                # Use predictions from Stage 2
                if arm_id in self.lane_predictions:
                    arm_preds = self.lane_predictions[arm_id]
                    for slot in range(1, 23):
                        row = slot - 1
                        if slot in arm_preds:
                            s = arm_preds[slot]
                            lane_attrs[idx, row, 0] = s['lane']
                            lane_attrs[idx, row, 1] = s['l_type']
                            lane_attrs[idx, row, 2] = s['slip']
                            lane_attrs[idx, row, 3] = s['left']
                            lane_attrs[idx, row, 4] = s['through']
                            lane_attrs[idx, row, 5] = s['right']
                            lane_attrs[idx, row, 6] = s['approach']
                            lane_attrs[idx, row, 7] = s['exit']
                            
        # 3. Get normalized absolute bearings
        bearings = np.zeros(4, dtype=np.float32)
        for idx, arm in enumerate(new_arms):
            bearings[idx] = arm['bearing'] / 360.0
            
        # 4. Get ground-truth adjacency matrix
        adj_matrix = self.encoder.encode_intersection_turns(inter_id)
        
        # Apply augmentation if augment is True
        if self.augment:
            from replication.data_encoding import apply_rotation_augmentation, apply_slot_shift_augmentation
            # Rotate
            lane_attrs, adj_matrix, img_tensor, k = apply_rotation_augmentation(lane_attrs, adj_matrix, img_tensor)
            # Roll bearings by k
            bearings = np.roll(bearings, k)
            # Slot shift
            lane_attrs, adj_matrix = apply_slot_shift_augmentation(lane_attrs, adj_matrix)
            
        stacked_lane_features = lane_attrs.flatten() # 4 * 22 * 8 = 704
        non_img_features = np.concatenate([stacked_lane_features, bearings])
        
        return img_tensor, torch.from_numpy(non_img_features), torch.from_numpy(adj_matrix)

def train_lane_detector(args, encoder):
    print("--- STARTING STAGE 2: LANE DETECTOR TRAINING ---")
    
    # Load splits
    split_path = os.path.join(args.data_dir, "labels", "turns", "data_split.json")
    with open(split_path, "r", encoding="utf-8") as f:
        splits = json.load(f)
        
    train_ids = splits['train']
    val_ids = splits['val']
    
    if args.subset:
        train_ids = train_ids[:args.subset]
        val_ids = val_ids[:max(1, args.subset // 4)]
        
    print(f"Training on {len(train_ids)} intersections, validating on {len(val_ids)} intersections.")
    
    # Datasets
    train_dataset = LaneDataset(args.data_dir, train_ids, encoder, augment=True)
    val_dataset = LaneDataset(args.data_dir, val_ids, encoder, augment=False)
    
    # Dataloaders
    drop_last = len(train_dataset) >= args.batch_size
    train_loader = DataLoader(train_dataset, batch_size=args.batch_size, shuffle=True, drop_last=drop_last)
    val_loader = DataLoader(val_dataset, batch_size=args.batch_size, shuffle=False)
    
    # Model
    model = LaneDetector(frozen_resnet=args.frozen_resnet)
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    model.to(device)
    
    # Optim & Loss
    optimizer = torch.optim.Adam(model.parameters(), lr=args.lr)
    criterion = LaneLoss()
    
    best_val_loss = float('inf')
    epochs_no_improve = 0
    patience = 5
    
    for epoch in range(args.epochs):
        model.train()
        train_loss = 0.0
        for img, non_img, targets in train_loader:
            img = img.to(device)
            non_img = non_img.to(device)
            
            optimizer.zero_grad()
            preds = model(img, non_img)
            
            # Move targets to device
            targets_dev = {k: v.to(device) for k, v in targets.items()}
            
            loss = criterion(preds, targets_dev)
            loss.backward()
            optimizer.step()
            
            train_loss += loss.item()
            
        # Eval
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
                
        if len(train_loader) > 0:
            train_loss /= len(train_loader)
        if len(val_loader) > 0:
            val_loss /= len(val_loader)
        
        print(f"Epoch {epoch+1:02d}/{args.epochs} | Train Loss: {train_loss:.4f} | Val Loss: {val_loss:.4f}")
        
        # Save best & Early stopping
        if val_loss < best_val_loss:
            best_val_loss = val_loss
            epochs_no_improve = 0
            torch.save(model.state_dict(), os.path.join(args.save_dir, "lane_detector_best.pt"))
            print("  --> Saved new best model checkpoint.")
        else:
            epochs_no_improve += 1
            if epochs_no_improve >= patience:
                print(f"Early stopping triggered after {epoch+1} epochs.")
                break

def train_turn_detector(args, encoder):
    print("\n--- STARTING STAGE 3: TURN DETECTOR TRAINING ---")
    
    # Load splits
    split_path = os.path.join(args.data_dir, "labels", "turns", "data_split.json")
    with open(split_path, "r", encoding="utf-8") as f:
        splits = json.load(f)
        
    train_ids = splits['train']
    val_ids = splits['val']
    
    if args.subset:
        train_ids = train_ids[:args.subset]
        val_ids = val_ids[:max(1, args.subset // 4)]
        
    print(f"Training on {len(train_ids)} intersections, validating on {len(val_ids)} intersections.")
    
    # 1. Compute cell-wise positive weights (N/P ratio) from the training split
    print("Computing cell-wise negative-to-positive (N/P) ratios from training split...")
    y_train_list = []
    for inter_id in train_ids:
        y_train_list.append(encoder.encode_intersection_turns(inter_id))
    y_train_arr = np.stack(y_train_list) # shape (N, 4, 22, 66)
    
    positives = np.sum(y_train_arr, axis=0)
    negatives = len(train_ids) - positives
    
    # Handle zeros: if positive count is 0, set ratio to 1000.0 (almost impossible)
    np_ratios = np.zeros_like(positives)
    for a in range(4):
        for s in range(22):
            for c in range(66):
                p = positives[a, s, c]
                n = negatives[a, s, c]
                if p == 0:
                    np_ratios[a, s, c] = 1000.0
                else:
                    np_ratios[a, s, c] = n / p
                    
    # Datasets
    train_dataset = TurnDataset(args.data_dir, train_ids, encoder, use_gt_lane_attrs=True, augment=True)
    val_dataset = TurnDataset(args.data_dir, val_ids, encoder, use_gt_lane_attrs=True, augment=False)
    
    # Dataloaders
    drop_last = len(train_dataset) >= args.batch_size
    train_loader = DataLoader(train_dataset, batch_size=args.batch_size, shuffle=True, drop_last=drop_last)
    val_loader = DataLoader(val_dataset, batch_size=args.batch_size, shuffle=False)
    
    # Model
    model = TurnDetector(frozen_resnet=args.frozen_resnet)
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    model.to(device)
    
    # Optim & Loss
    optimizer = torch.optim.Adam(model.parameters(), lr=args.lr)
    criterion = TurnLoss(np_ratios=np_ratios)
    
    best_val_loss = float('inf')
    epochs_no_improve = 0
    patience = 5
    
    for epoch in range(args.epochs):
        model.train()
        train_loss = 0.0
        for img, non_img, targets in train_loader:
            img = img.to(device)
            non_img = non_img.to(device)
            targets = targets.to(device)
            
            optimizer.zero_grad()
            preds = model(img, non_img)
            
            loss = criterion(preds, targets)
            loss.backward()
            optimizer.step()
            
            train_loss += loss.item()
            
        # Eval
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
                
        if len(train_loader) > 0:
            train_loss /= len(train_loader)
        if len(val_loader) > 0:
            val_loss /= len(val_loader)
        
        print(f"Epoch {epoch+1:02d}/{args.epochs} | Train Loss: {train_loss:.4f} | Val Loss: {val_loss:.4f}")
        
        # Save best & Early stopping
        if val_loss < best_val_loss:
            best_val_loss = val_loss
            epochs_no_improve = 0
            torch.save(model.state_dict(), os.path.join(args.save_dir, "turn_detector_best.pt"))
            print("  --> Saved new best model checkpoint.")
        else:
            epochs_no_improve += 1
            if epochs_no_improve >= patience:
                print(f"Early stopping triggered after {epoch+1} epochs.")
                break

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Train Lane and Turn Detectors")
    parser.add_argument("--stage", type=str, default="both", choices=["2", "3", "both"], help="Pipeline stage to train")
    parser.add_argument("--epochs", type=int, default=20, help="Number of training epochs")
    parser.add_argument("--batch_size", type=int, default=16, help="Training batch size")
    parser.add_argument("--lr", type=float, default=1e-4, help="Learning rate")
    parser.add_argument("--data_dir", type=str, default=r"f:\Road\main_task\data", help="Dataset directory")
    parser.add_argument("--save_dir", type=str, default=r"f:\Road\replication", help="Directory to save weights")
    parser.add_argument("--subset", type=int, default=None, help="Run on subset of intersections for quick sanity check")
    parser.add_argument("--frozen_resnet", action="store_true", default=True, help="Whether to freeze ResNet backbone weights")
    
    args = parser.parse_args()
    
    # Initialize dataset encoder
    encoder = DatasetEncoder(args.data_dir)
    
    if args.stage in ["2", "both"]:
        train_lane_detector(args, encoder)
        
    if args.stage in ["3", "both"]:
        train_turn_detector(args, encoder)
