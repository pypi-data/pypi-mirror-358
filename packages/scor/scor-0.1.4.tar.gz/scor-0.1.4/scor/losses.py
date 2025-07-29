import torch
import torch.nn as nn
import torch.nn.functional as F

class SCoR(nn.Module):

    def __init__(self, alpha: float = 1e-04):
        """
            Stochastic Covariance Regularisation. Default alpha is 1e-04.

        """
        super().__init__()
        self.alpha = alpha
        self.crossEntropy = nn.CrossEntropyLoss()

    def forward(self, y_pred, y_true):
        _loss = self.crossEntropy(y_pred, y_true)

        if y_pred.shape[0] % 2 == 0:
            perm = torch.randperm(y_pred.shape[0]).to(y_pred.device)
            randomized = y_pred.index_select(0, perm)
            first_half = randomized[y_pred.shape[0] // 2:, :]  # Indeed this is the second half
            second_half = randomized[:y_pred.shape[0] // 2, :]  # and this is the first half
            _loss_svr = self.alpha * torch.norm(first_half.T @ second_half, p="fro")
        else:
            _loss_svr = self.alpha * torch.norm(y_pred.T @ y_pred, p="fro")

        return _loss + _loss_svr

class SCoRandLS(nn.Module):

    def __init__(self, alpha: float = 1e-04):
        """
            Combination of SCoR with Label Smoothing (LS). LS uses p=0.1, SCoR uses
            the default alpha value of 1e-04.
        """
        super().__init__()
        self.alpha = alpha
        self.crossEntropy = nn.CrossEntropyLoss(label_smoothing=0.1)

    def forward(self, y_pred, y_true):
        _loss = self.crossEntropy(y_pred, y_true)

        if y_pred.shape[0] % 2 == 0:
            perm = torch.randperm(y_pred.shape[0]).to(y_pred.device)
            randomized = y_pred.index_select(0, perm)
            first_half = randomized[y_pred.shape[0] // 2:, :]  # Indeed this is the second half
            second_half = randomized[:y_pred.shape[0] // 2, :]  # and this is the first half
            _loss_svr = self.alpha * torch.norm(first_half.T @ second_half, p="fro")
        else:
            _loss_svr = self.alpha * torch.norm(y_pred.T @ y_pred, p="fro")

        return _loss + _loss_svr

class OPL(nn.Module):
    def __init__(self, epsilon=1e-6, alpha: float = 1, gamma: float = 0.5):
        """
            Orthogonal Projection Los, directly implemented from the Torch
            pseudocode of the paper.

            The default configuration is the best hyperparameter configuration
            reported within the paper.
        """
        super().__init__()
        self.alpha = alpha
        self.gamma = gamma
        self.cross_entropy = nn.CrossEntropyLoss()
        self.epsilon = epsilon

    def forward(self, logits, labels, features):
        batch_size, feature_dim = features.shape
        ce_loss_ = self.cross_entropy(logits, labels)

        features = F.normalize(features, p=2, dim=1)

        mask = torch.eq(labels, labels.t())
        eye = torch.eye(mask.shape[0], device=features.device)
        mask_pos = mask.masked_fill(eye.type(torch.bool), 0)
        mask_neg = ~mask

        dot_prod = torch.matmul(features, features.t())
        pos_total = (mask_pos * dot_prod).sum()
        neg_total = torch.abs(mask_neg * dot_prod).sum()
        pos_mean = pos_total / (mask_pos.sum() + self.epsilon)
        neg_mean = neg_total / (mask_neg.sum() + self.epsilon)

        loss = (1.0 - pos_mean) + self.gamma * neg_mean

        return ce_loss_ + self.alpha * loss / batch_size

class FocalLoss(nn.Module):

    def __init__(self, gamma: float = 2):
        super().__init__()
        self.gamma = gamma

    def forward(self, y_pred, y_true):
        probs = F.softmax(y_pred, dim=-1)
        targets_one_hot = F.one_hot(y_true, num_classes=y_pred.shape[-1]).float()
        pt = torch.sum(targets_one_hot * probs, dim=-1)
        focal_weight = (1 - pt) ** self.gamma
        log_pt = F.log_softmax(y_pred, dim=-1)
        log_pt = torch.sum(targets_one_hot * log_pt, dim=-1)
        return -torch.sum(focal_weight * log_pt)  # Sum over batches
        #return - torch.sum(((y_true - y_pred) ** self.gamma) * torch.log(y_pred))

# Use nn.CrossEntropyLoss(label_smoothing=0.1) for label smoothing
