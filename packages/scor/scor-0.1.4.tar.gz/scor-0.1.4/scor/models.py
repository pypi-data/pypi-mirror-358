import torch.nn as nn
import torch
from torch.utils.data import DataLoader
import torch.optim as optim
from torchvision.models.convnext import (
    convnext_tiny,
    convnext_small,
    convnext_base,
    convnext_large,
    ConvNeXt_Tiny_Weights,
    ConvNeXt_Small_Weights,
    ConvNeXt_Base_Weights,
    ConvNeXt_Large_Weights,
)

from .losses import *

from tqdm import tqdm
from sklearn.metrics import f1_score

class MLP(nn.Module):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.sequence = nn.Sequential(
            nn.Linear(784, 128),
            nn.ReLU(),
            nn.Linear(128, 10)
        )

        self.softmax = nn.Softmax(dim=-1)

    def forward(self, x):
        x = x.view(-1, 784)
        return self.sequence(x)

    def predict(self, x):
        x = x.view(-1, 784)
        return torch.argmax(self.softmax(self.sequence(x)), dim=-1)

    def model_training(self, train_loader: DataLoader,
                       criterion: nn.Module, optimizer: optim.Optimizer,
                       device: str = "cuda"):

        _loss = 0

        N: int = next(iter(train_loader))[0].shape[0]
        pbar = tqdm(train_loader, total=len(train_loader), desc=f"Training")

        for i, (x, y) in enumerate(pbar):
            optimizer.zero_grad()
            x = x.to(device)
            y = y.to(device)
            out = self(x)
            loss = criterion(out, y)
            _loss += loss.item()
            loss.backward()
            optimizer.step()
            pbar.set_postfix({"Loss": _loss / ((i + 1) * N)})

        if device == "cuda":
            torch.cuda.empty_cache()
        return _loss


    @torch.no_grad()
    def evaluate(self, test_data: torch.Tensor, test_labels: torch.Tensor,
                 n_parts: int = 5, empty_cache: bool = True):

        N = test_data.shape[0] // n_parts
        temp_out: torch.Tensor
        acc = 0
        f1_scores = 0

        for i in range(n_parts):
            temp_out = self.predict(test_data[N * i:N * (i + 1)].type(torch.float32))
            acc += (torch.count_nonzero(temp_out == test_labels[N * i:N * (i + 1)]) / N).item()

            f1_scores += f1_score(test_labels[N * i:N * (i + 1)].type(torch.uint8).cpu().numpy().ravel(),
                                  temp_out.type(torch.uint8).cpu().numpy().ravel(),
                                  average="macro", zero_division=0)

            if empty_cache:
                torch.cuda.empty_cache()

        return acc / n_parts, f1_scores / n_parts

    @torch.no_grad()
    def evaluateTargeted(self, test_data: torch.Tensor, test_labels: torch.Tensor,
                         n_parts: int = 5, empty_cache: bool = True, target_class: int = 0):

        N = test_data.shape[0] // n_parts
        temp_out: torch.Tensor
        acc = 0
        f1_scores = 0

        for i in range(n_parts):
            mask = (test_labels[N * i:N * (i + 1)].type(torch.uint8) != target_class)
            temp_out = self.predict(test_data[N * i:N * (i + 1)][mask].type(torch.float32))
            tests = test_labels[N * i:N * (i + 1)][mask]

            acc += (torch.count_nonzero(temp_out == tests) / N).item()

            f1_scores += f1_score(tests.type(torch.uint8).cpu().numpy().ravel(),
                                  temp_out.type(torch.uint8).cpu().numpy().ravel(),
                                  average="macro", zero_division=0)

            if empty_cache:
                torch.cuda.empty_cache()

        return acc / n_parts, f1_scores / n_parts

class ResidualBlock(nn.Module):

    def __init__(self, in_channels: int, out_channels: int, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.in_channels = in_channels
        self.out_channels = out_channels

        self.sequence = nn.Sequential(
            nn.Conv2d(self.in_channels, self.out_channels, kernel_size=3, stride=1, padding=1, bias=False),
            nn.BatchNorm2d(self.out_channels),
            nn.ReLU(),
            nn.Conv2d(self.out_channels, self.out_channels, kernel_size=3, stride=1, padding=1, bias=False),
            nn.BatchNorm2d(self.out_channels),
            nn.ReLU(),
            nn.Conv2d(self.out_channels, self.out_channels, kernel_size=3, stride=1, padding=1, bias=False),
            nn.BatchNorm2d(self.out_channels),
            nn.ReLU(),
            nn.Conv2d(self.out_channels, self.out_channels, kernel_size=3, stride=1, padding=1, bias=False),
            nn.BatchNorm2d(self.out_channels),
        )

    def forward(self, x):
        return self.sequence(x) + x

class ResNet(nn.Module):

    """
        This is the basic ResNet structure used for CIFAR-10 tests.
        This excludes CIFAR-10-LT.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.sequence = nn.Sequential(
            nn.Conv2d(3, 32, kernel_size=3, stride=1, padding=1),
            nn.ReLU(),
            ResidualBlock(32, 32),
            nn.ReLU(),
            ResidualBlock(32, 32),
            nn.ReLU(),
            ResidualBlock(32, 32),
            nn.ReLU(),
            ResidualBlock(32, 32),
            nn.ReLU(),
            nn.Conv2d(32, 64, kernel_size=3, stride=1, padding=1),
            nn.ReLU(),
            nn.Flatten(),
            nn.Linear(64 * 32 * 32, 64 * 32),
            nn.Dropout(0.5),
            nn.ReLU(),
            nn.Linear(64 * 32, 10)
        )

        self.softmax = nn.Softmax(dim=-1)

    def forward(self, x):
        out = self.sequence(x)
        return out

    def predict(self, x):
        x = x.reshape(-1, 3, 32, 32)
        out = self.softmax(self.sequence(x))
        return torch.argmax(out, dim=-1)

    def model_training(self, train_loader: DataLoader,
                       criterion: nn.Module, optimizer: optim.Optimizer,
                       device: str = "cuda", N=64):

        _loss = 0
        pbar = tqdm(train_loader, total=len(train_loader), desc=f"Training")

        for i, (x, y) in enumerate(pbar):
            optimizer.zero_grad()
            x = x.to(device)
            y = y.to(device)
            out = self(x)
            #print(out.shape, y.shape)
            loss = criterion(out, y)
            loss.backward()
            _loss += loss.item()
            optimizer.step()

            pbar.set_postfix({"Loss": _loss / ((i + 1) * N)})

        if device == "cuda":
            torch.cuda.empty_cache()
        return _loss

    @torch.no_grad()
    def evaluate(self, test_data: torch.Tensor, test_labels: torch.Tensor,
                 n_parts: int = 1, empty_cache: bool = True):

        N = test_data.shape[0] // n_parts
        temp_out: torch.Tensor
        acc = 0
        f1_scores = 0

        for i in range(n_parts):
            temp_out = self.predict(test_data[N * i:N * (i + 1)].type(torch.float32))
            acc += (torch.count_nonzero(temp_out == test_labels[N * i:N * (i + 1)]) / N).item()

            f1_scores += f1_score(test_labels[N * i:N * (i + 1)].type(torch.uint8).cpu().numpy().ravel(),
                                  temp_out.type(torch.uint8).cpu().numpy().ravel(),
                                  average="macro", zero_division=0)

            if empty_cache:
                torch.cuda.empty_cache()

        return acc / n_parts, f1_scores / n_parts

    @torch.no_grad()
    def evaluateTargeted(self, test_data: torch.Tensor, test_labels: torch.Tensor,
                 n_parts: int = 1, empty_cache: bool = True, target_class: int = 0):

        N = test_data.shape[0] // n_parts
        temp_out: torch.Tensor
        acc = 0
        f1_scores = 0

        for i in range(n_parts):
            mask = (test_labels[N * i:N * (i + 1)].type(torch.uint8) != target_class)
            temp_out = self.predict(test_data[N * i:N * (i + 1)][mask].type(torch.float32))
            tests = test_labels[N * i:N * (i + 1)][mask]

            acc += (torch.count_nonzero(temp_out == tests) / N).item()

            f1_scores += f1_score(tests.type(torch.uint8).cpu().numpy().ravel(),
                                  temp_out.type(torch.uint8).cpu().numpy().ravel(),
                                  average="macro", zero_division=0)

            if empty_cache:
                torch.cuda.empty_cache()

        return acc / n_parts, f1_scores / n_parts

class ConvNeXtBase(nn.Module):

    def __init__(self, size: str = "tiny", *args, **kwargs):
        """
            This is the base class for ConvNeXt applications,
            where ConvNeXt is needed as the feature extractor.

            This class, under its "feature_extractor" attribute,
            has the vector outputs of selected model size.

            Args:
                size (str): The size of the ConvNeXt to be used.
                    Must be one of ['tiny', 'small', 'base', 'large'].
        """

        super().__init__(*args, **kwargs)
        self.size = size.lower()
        self.channels = None

        if self.size == "tiny":
            weights = ConvNeXt_Tiny_Weights.DEFAULT
            backbone = convnext_tiny(weights=weights)
        elif self.size == "small":
            weights = ConvNeXt_Small_Weights.DEFAULT
            backbone = convnext_small(weights=weights)
        elif self.size == "base":
            weights = ConvNeXt_Base_Weights.DEFAULT
            backbone = convnext_base(weights=weights)
        elif self.size == "large":
            weights = ConvNeXt_Large_Weights.DEFAULT
            backbone = convnext_large(weights=weights)
        else:
            raise ValueError(f"size argument must be one of ['tiny', 'small', 'base', 'large']")

        self.feature_extractor = nn.Sequential(*list(backbone.children())[:-1])

    def forward(self, x):
        return self.feature_extractor(x)

class ConvNeXtClassification(ConvNeXtBase):

    def __init__(self, size: str = "tiny", num_classes: int = 1000, *args, **kwargs):
        """
            The classification oriented extension of ConvNeXtBase class. This class,
            adds a single hidden layer classification head with "num_classes" outputs.

            Args:
                size (str): The size of the ConvNeXt base to be used.
                    Must be one of ['tiny', 'small', 'base', 'large'].
                    Defaults to 'tiny'.

                num_classes (int): Number of classes to predict. Defaults
                    to 1000 for ImageNet.
        """

        super().__init__(size=size, *args, **kwargs)

        self.input_dims = 768 if self.size == "tiny" or self.size == "small" else \
            1024 if self.size == "base" else 1536

        self.num_classes = num_classes

        self.head = nn.Sequential(
            nn.Linear(self.input_dims, 512),
            nn.ReLU(),
            nn.Linear(512, self.num_classes)
        )

    def forward(self, x, opl: bool = False):
        features = super().forward(x)
        features = features.view(features.size(0), -1)
        if opl:
            return self.head(features), features
        return self.head(features)  # This will still be returned as a tuple? Because Python?

class FaceVerificationModel(nn.Module):
    def __init__(self, num_classes=10):
        super().__init__()

        weights = ConvNeXt_Tiny_Weights.DEFAULT
        backbone = convnext_tiny(weights=weights)

        self.feature_extractor = nn.Sequential(*list(backbone.children())[:-1])

        self.fc = nn.Sequential(
            nn.Linear(768, 512),
            nn.ReLU(),
            nn.Linear(512, num_classes)
        )

    def forward(self, img1):
        f1 = self.feature_extractor(img1)

        f1 = f1.view(f1.shape[0], -1)  # Flatten
        out = self.fc(f1)  # Pass through classification head
        return out, f1

def getMLP(device: str = "cuda", loss: str = "ce", *args, **kwargs):

    """

        Generate an MLP, with a dedicated loss function and a fresh optimizer.

    """

    model = MLP().to(device)
    if loss == "ce":  # Label smoothing is included here
        _loss = nn.CrossEntropyLoss(*args, **kwargs)
    elif loss == "scor":
        _loss = SCoR(*args, **kwargs)
    elif loss == "focal":
        _loss = FocalLoss(*args, **kwargs)
    else:
        raise

    return model, _loss, optim.Adam(model.parameters())

def getResNet(device: str, loss: str = "ce", *args, **kwargs):

    """

        Generate a ResNet, with a dedicated loss function and a fresh optimizer.

    """

    model = ResNet().to(device)

    if loss == "ce":  # Label smoothing is included here
        _loss = nn.CrossEntropyLoss(*args, **kwargs)
    elif loss == "scor":
        _loss = SCoR(*args, **kwargs)
    elif loss == "focal":
        _loss = FocalLoss(*args, **kwargs)
    else:
        raise

    return model, _loss, optim.Adam(model.parameters())
