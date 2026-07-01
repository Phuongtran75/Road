import torch
import torch.nn as nn
import torch.nn.functional as F

class SoftDiceLoss(nn.Module):
    """
    Soft Dice Loss for binary classification tasks.
    """
    def __init__(self, epsilon=1e-6):
        super(SoftDiceLoss, self).__init__()
        self.epsilon = epsilon
        
    def forward(self, pred, target):
        """
        pred: Tensor of shape (B, ...) containing probabilities in [0, 1].
        target: Binary ground truth tensor of the same shape.
        """
        # Flatten tensors
        pred = pred.view(-1)
        target = target.view(-1)
        
        intersection = torch.sum(pred * target)
        union = torch.sum(pred) + torch.sum(target)
        
        dice = (2. * intersection + self.epsilon) / (union + self.epsilon)
        return 1. - dice

class MultiClassSoftDiceLoss(nn.Module):
    """
    Soft Dice Loss for multi-class classification tasks.
    """
    def __init__(self, num_classes, epsilon=1e-6):
        super(MultiClassSoftDiceLoss, self).__init__()
        self.num_classes = num_classes
        self.epsilon = epsilon
        
    def forward(self, pred, target):
        """
        pred: Tensor of shape (B, C, L) containing class probabilities.
        target: Integer tensor of shape (B, L) containing class indices (0 to C-1).
        """
        B, C, L = pred.shape
        # Convert target to one-hot: shape (B, C, L)
        target_one_hot = F.one_hot(target, num_classes=self.num_classes).permute(0, 2, 1).float()
        
        loss = 0.0
        for c in range(self.num_classes):
            p = pred[:, c, :].contiguous().view(-1)
            t = target_one_hot[:, c, :].contiguous().view(-1)
            
            intersection = torch.sum(p * t)
            union = torch.sum(p) + torch.sum(t)
            dice_c = (2. * intersection + self.epsilon) / (union + self.epsilon)
            loss += (1. - dice_c)
            
        return loss / self.num_classes

class LaneLoss(nn.Module):
    """
    Combined loss for Lane Detection model.
    Includes BCE and Soft Dice loss terms for multiple attributes.
    """
    def __init__(self, pos_weights=None, class_weights=None, loss_weights=None):
        super(LaneLoss, self).__init__()
        # Table 4 and 5 defaults
        self.pos_weights = pos_weights if pos_weights is not None else {
            'lane': 4.80,
            'slip': 30.0,  # Cap at 30 (raw 2118.81)
            'left': 26.29,
            'through': 13.72,
            'right': 27.57
        }
        self.class_weights = class_weights if class_weights is not None else torch.tensor([0.21, 10.07, 11.18])
        self.loss_weights = loss_weights if loss_weights is not None else {
            'lane_ce': 0.20, 'lane_dice': 0.20,
            'type_ce': 0.15, 'type_dice': 0.15,
            'turn_ce': 0.10, 'turn_dice': 0.10,
            'slip_ce': 0.05, 'slip_dice': 0.05
        }
        
        self.dice_binary = SoftDiceLoss()
        self.dice_multiclass = MultiClassSoftDiceLoss(num_classes=3)
        
    def forward(self, preds, targets):
        """
        preds: dict of output tensors:
            - 'lane': (B, 22) logits
            - 'lane_type': (B, 3, 22) logits
            - 'left': (B, 22) logits
            - 'through': (B, 22) logits
            - 'right': (B, 22) logits
            - 'slip': (B, 22) logits
        targets: dict of target tensors of same shapes (except lane_type which is (B, 22) integers)
        """
        # Move class_weights to correct device
        class_weights = self.class_weights.to(preds['lane'].device)
        
        # 1. Lane presence loss (binary)
        weight_lane = torch.tensor([self.pos_weights['lane']], device=preds['lane'].device)
        ce_lane = F.binary_cross_entropy_with_logits(preds['lane'], targets['lane'], pos_weight=weight_lane)
        dice_lane = self.dice_binary(torch.sigmoid(preds['lane']), targets['lane'])
        
        # 2. Lane type loss (multi-class: no_lane, approach, exit)
        ce_type = F.cross_entropy(preds['lane_type'], targets['lane_type'].long(), weight=class_weights)
        dice_type = self.dice_multiclass(F.softmax(preds['lane_type'], dim=1), targets['lane_type'].long())
        
        # 3. Turn directions loss (binary)
        ce_left = F.binary_cross_entropy_with_logits(preds['left'], targets['left'], 
                                                     pos_weight=torch.tensor([self.pos_weights['left']], device=preds['left'].device))
        ce_through = F.binary_cross_entropy_with_logits(preds['through'], targets['through'], 
                                                        pos_weight=torch.tensor([self.pos_weights['through']], device=preds['through'].device))
        ce_right = F.binary_cross_entropy_with_logits(preds['right'], targets['right'], 
                                                      pos_weight=torch.tensor([self.pos_weights['right']], device=preds['right'].device))
        ce_turn = ce_left + ce_through + ce_right
        
        dice_left = self.dice_binary(torch.sigmoid(preds['left']), targets['left'])
        dice_through = self.dice_binary(torch.sigmoid(preds['through']), targets['through'])
        dice_right = self.dice_binary(torch.sigmoid(preds['right']), targets['right'])
        dice_turn = dice_left + dice_through + dice_right
        
        # 4. Slip lane loss (binary)
        weight_slip = torch.tensor([self.pos_weights['slip']], device=preds['slip'].device)
        ce_slip = F.binary_cross_entropy_with_logits(preds['slip'], targets['slip'], pos_weight=weight_slip)
        dice_slip = self.dice_binary(torch.sigmoid(preds['slip']), targets['slip'])
        
        # Aggregate
        total_loss = (
            self.loss_weights['lane_ce'] * ce_lane + self.loss_weights['lane_dice'] * dice_lane +
            self.loss_weights['type_ce'] * ce_type + self.loss_weights['type_dice'] * dice_type +
            self.loss_weights['turn_ce'] * ce_turn + self.loss_weights['turn_dice'] * dice_turn +
            self.loss_weights['slip_ce'] * ce_slip + self.loss_weights['slip_dice'] * dice_slip
        )
        
        return total_loss

class TurnLoss(nn.Module):
    """
    Combined loss for Turn Detection model.
    Includes custom area of interest and almost impossible area weightings.
    """
    def __init__(self, np_ratios, ce_weight_interest=0.40, ce_weight_impossible=0.20, dice_weight=0.40, weight_cap=30.0, np_threshold=1000.0):
        super(TurnLoss, self).__init__()
        # np_ratios is a tensor of shape (4, 22, 66)
        self.register_buffer('np_ratios', torch.tensor(np_ratios, dtype=torch.float32))
        self.ce_weight_interest = ce_weight_interest
        self.ce_weight_impossible = ce_weight_impossible
        self.dice_weight = dice_weight
        self.weight_cap = weight_cap
        self.np_threshold = np_threshold
        
        # Identify almost impossible mask (N/P ratio >= np_threshold)
        # Per 2026 paper Section 3.7, this threshold is a tunable hyperparameter.
        self.register_buffer('almost_impossible_mask', (self.np_ratios >= np_threshold))
        
        # Compute cell-wise positive weights (capped)
        pos_weights = torch.clamp(self.np_ratios, max=weight_cap)
        self.register_buffer('pos_weights', pos_weights)
        
        self.dice_loss = SoftDiceLoss()
        
    def forward(self, pred_logits, targets):
        """
        pred_logits: predicted logits of shape (B, 4, 22, 66)
        targets: binary target of shape (B, 4, 22, 66)
        """
        # Calculate cell-wise binary cross entropy manually to apply individual pos_weights and area weights
        probs = torch.sigmoid(pred_logits)
        
        # Clamp probs to avoid log(0)
        probs_clamped = torch.clamp(probs, min=1e-7, max=1.0 - 1e-7)
        
        # BCE with individual pos_weight:
        # loss = - [pos_weight * target * log(prob) + (1 - target) * log(1 - prob)]
        # Shape: (B, 4, 22, 66)
        bce_loss_cell = - (self.pos_weights * targets * torch.log(probs_clamped) + 
                           (1.0 - targets) * torch.log(1.0 - probs_clamped))
        
        # Apply area weighting (0.40 for interest, 0.20 for impossible)
        # Use broadcasting to apply the mask over the batch dimension
        area_weights = torch.where(self.almost_impossible_mask, 
                                   self.ce_weight_impossible, 
                                   self.ce_weight_interest)
        
        weighted_ce_cell = bce_loss_cell * area_weights
        ce_loss = torch.mean(weighted_ce_cell)
        
        # Dice loss over the total area
        dice = self.dice_loss(probs, targets)
        
        # Combined Loss
        total_loss = ce_loss + self.dice_weight * dice
        
        return total_loss
