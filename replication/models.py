import torch
import torch.nn as nn
from torchvision.models import resnet18, ResNet18_Weights

class ImageBackbone(nn.Module):
    """
    ResNet-18 image feature extractor with frozen weights.
    """
    def __init__(self, frozen=True):
        super(ImageBackbone, self).__init__()
        # Load pre-trained ResNet-18 with default weights
        self.resnet = resnet18(weights=ResNet18_Weights.DEFAULT)
        # Replace classification head with Identity to extract raw 512-dim features
        self.feature_dim = self.resnet.fc.in_features
        self.resnet.fc = nn.Identity()
        
        if frozen:
            for param in self.resnet.parameters():
                param.requires_grad = False
                
    def forward(self, x):
        # Input shape: (B, 3, H, W)
        features = self.resnet(x)  # Output shape: (B, 512)
        return features

class LaneDetector(nn.Module):
    """
    Stage 2: Lane Detector.
    Combines ResNet image backbone (for arm image) and MLP (for projections + bearings).
    """
    def __init__(self, num_slots=22, num_attrs=8, proj_dim=220, bearing_dim=3, frozen_resnet=True):
        super(LaneDetector, self).__init__()
        self.num_slots = num_slots
        self.num_attrs = num_attrs
        
        # 1. Image backbone
        self.img_backbone = ImageBackbone(frozen=frozen_resnet)
        
        # 2. MLP for projections and bearing offsets
        non_img_in_dim = proj_dim + bearing_dim  # 220 + 3 = 223
        self.mlp_non_img = nn.Sequential(
            nn.Linear(non_img_in_dim, 128),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(128, 64),
            nn.ReLU()
        )
        
        # 3. Combined MLP to project features to slots
        combined_in_dim = 512 + 64
        self.mlp_combined = nn.Sequential(
            nn.Linear(combined_in_dim, 256),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(256, num_slots * num_attrs)  # 22 * 8 = 176
        )
        
    def forward(self, img, non_img_features):
        """
        img: (B, 3, 224, 224) arm image. If None, dummy zero tensor is used.
        non_img_features: (B, 223) projection scores + bearing offsets
        """
        if img is None:
            img = torch.zeros((non_img_features.shape[0], 3, 224, 224), device=non_img_features.device)
            
        img_feats = self.img_backbone(img)                 # (B, 512)
        non_img_feats = self.mlp_non_img(non_img_features) # (B, 64)
        
        combined = torch.cat([img_feats, non_img_feats], dim=1) # (B, 576)
        logits = self.mlp_combined(combined)                    # (B, 176)
        
        # Reshape to (B, 22, 8)
        logits = logits.view(-1, self.num_slots, self.num_attrs)
        
        # Extract attribute categories:
        # Attributes indices:
        # 0: lane presence (B, 22)
        # 1:3: lane_type classes (B, 3, 22) after permutation
        # 4: left turn (B, 22)
        # 5: through turn (B, 22)
        # 6: right turn (B, 22)
        # 7: slip lane (B, 22)
        lane_logit = logits[:, :, 0]
        lane_type_logits = logits[:, :, 1:4].permute(0, 2, 1)  # (B, 3, 22) for cross-entropy
        left_logit = logits[:, :, 4]
        through_logit = logits[:, :, 5]
        right_logit = logits[:, :, 6]
        slip_logit = logits[:, :, 7]
        
        return {
            'lane': lane_logit,
            'lane_type': lane_type_logits,
            'left': left_logit,
            'through': through_logit,
            'right': right_logit,
            'slip': slip_logit
        }

class TurnDetector(nn.Module):
    """
    Stage 3: Turn Detector.
    Combines ResNet image backbone (for intersection image) and MLP (for stacked lane slot attributes + bearings).
    """
    def __init__(self, num_arms=4, num_slots=22, num_attrs=8, bearing_dim=4, frozen_resnet=True):
        super(TurnDetector, self).__init__()
        self.num_arms = num_arms
        self.num_slots = num_slots
        self.num_attrs = num_attrs
        
        # 1. Image backbone
        self.img_backbone = ImageBackbone(frozen=frozen_resnet)
        
        # 2. MLP for stacked slot attribute predictions and absolute bearings
        non_img_in_dim = num_arms * num_slots * num_attrs + bearing_dim  # 4 * 22 * 8 + 4 = 708
        self.mlp_non_img = nn.Sequential(
            nn.Linear(non_img_in_dim, 256),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(256, 128),
            nn.ReLU()
        )
        
        # 3. Combined MLP to output the adjacency matrix logits
        combined_in_dim = 512 + 128
        self.mlp_combined = nn.Sequential(
            nn.Linear(combined_in_dim, 512),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(512, num_arms * num_slots * 66)  # 4 * 22 * 66 = 5808
        )
        
    def forward(self, img, non_img_features):
        """
        img: (B, 3, 224, 224) intersection image. If None, dummy zero tensor is used.
        non_img_features: (B, 708) stacked lane attributes + bearings
        """
        if img is None:
            img = torch.zeros((non_img_features.shape[0], 3, 224, 224), device=non_img_features.device)
            
        img_feats = self.img_backbone(img)                 # (B, 512)
        non_img_feats = self.mlp_non_img(non_img_features) # (B, 128)
        
        combined = torch.cat([img_feats, non_img_feats], dim=1) # (B, 640)
        logits = self.mlp_combined(combined)                    # (B, 5808)
        
        # Reshape to (B, 4, 22, 66) representing adjacency matrix
        logits = logits.view(-1, self.num_arms, self.num_slots, 66)
        return logits
