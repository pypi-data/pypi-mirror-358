import torch
from .models import getMLP
from .data import *
from .metrics import *
from torch.utils.data import DataLoader, Dataset, Subset
import json
from datetime import datetime
from time import time
import numpy as np

def get_empty_data_dict():
    ce_data = {"acc": [], "f1": [], "loss": [], "max_singular": [], "min_singular": [], "ranks": []}
    ls_data = {"acc": [], "f1": [], "loss": [], "max_singular": [], "min_singular": [], "ranks": []}
    focal_data = {"acc": [], "f1": [], "loss": [], "max_singular": [], "min_singular": [], "ranks": []}
    scor_data = {"acc": [], "f1": [], "loss": [], "max_singular": [], "min_singular": [], "ranks": []}
    return ce_data, ls_data, focal_data, scor_data

def save_data_dicts(ce_data: dict,
                    ls_data: dict,
                    focal_data: dict,
                    scor_data: dict,
                    batch_size: int,
                    path: str = "./results"):
    timestamp = datetime.now().timestamp()

    with open(f"{path}/ce_data_{timestamp}_{batch_size}.json", "w", encoding="utf-8") as file:
        json.dump(ce_data, file, ensure_ascii=False, indent=4)

    with open(f"{path}/ls_data_{timestamp}_{batch_size}.json", "w", encoding="utf-8") as file:
        json.dump(ls_data, file, ensure_ascii=False, indent=4)

    with open(f"{path}/focal_data_{timestamp}_{batch_size}.json", "w", encoding="utf-8") as file:
        json.dump(focal_data, file, ensure_ascii=False, indent=4)

    with open(f"{path}/scor_data_{timestamp}_{batch_size}.json", "w", encoding="utf-8") as file:
        json.dump(scor_data, file, ensure_ascii=False, indent=4)

def save_dist_dicts(ce_data: dict,
                    ls_data: dict,
                    focal_data: dict,
                    scor_data: dict,
                    batch_size: int,
                    path: str = "./results"):

    timestamp = datetime.now().timestamp()

    with open(f"{path}/ce_data_{timestamp}_{batch_size}_dist.json", "w", encoding="utf-8") as file:
        json.dump(ce_data, file, ensure_ascii=False, indent=4)

    with open(f"{path}/ls_data_{timestamp}_{batch_size}_dist.json", "w", encoding="utf-8") as file:
        json.dump(ls_data, file, ensure_ascii=False, indent=4)

    with open(f"{path}/focal_data_{timestamp}_{batch_size}_dist.json", "w", encoding="utf-8") as file:
        json.dump(focal_data, file, ensure_ascii=False, indent=4)

    with open(f"{path}/scor_data_{timestamp}_{batch_size}_dist.json", "w", encoding="utf-8") as file:
        json.dump(scor_data, file, ensure_ascii=False, indent=4)

def get_empty_dist_dict():
    ce_data_dist = {"acc": [], "f1": [], "loss": [], "singulars": [], "ranks": []}
    ls_data_dist = {"acc": [], "f1": [], "loss": [], "singulars": [], "ranks": []}
    focal_data_dist = {"acc": [], "f1": [], "loss": [], "singulars": [], "ranks": []}
    scor_data_dist = {"acc": [], "f1": [], "loss": [], "singulars": [], "ranks": []}
    return ce_data_dist, ls_data_dist, focal_data_dist, scor_data_dist

def trainMLP(batch_size: int, device: str = "cuda",
             iterations: int = 1000, epochs: int = 5,
             path: str = "./results",
             *args, **kwargs):
    """
        Trains the "MLP" model class on MNIST for Cross Entropy Loss,
        Label Smoothing (p=0.1), Focal Loss and SCoR.

        MNIST is imbalanced by reducing a random class by the given
        "reducing_factor" multiplicatively. The class is selected
        randomly at each training repetition. The same dataset
        partitions are shared across all 4 models that use a different
        loss function.

        Repeats training "iterations" times. Each training takes "epochs" number
        of epochs.

        Measures accuracy, f1 score, loss, rank, max singular value and min singular value
        at the end of each training for each loss function. Saves results as a json under
        "path" directory.
    """
    ce_data, ls_data, focal_data, scor_data = get_empty_data_dict()

    train_loader: DataLoader
    test_subset: Subset
    x_test: torch.Tensor
    y_test: torch.Tensor

    _acc = 0
    _f1 = 0
    _loss = 0
    N = 0

    try:
        begin = time()
        for i in range(iterations):
            train_loader, test_subset = getUnbalancedMNIST(batch_size, *args, **kwargs)
            x_test = test_subset.dataset.dataset.data[test_subset.indices].to(device)
            y_test = test_subset.dataset.dataset.targets[test_subset.indices].to(device)

            N = len(train_loader) * batch_size
            # instead generate test_dataset and return it

            model_ce, criterion, optimizer = getMLP(device, loss="ce")
            model_ce.train()

            for epoch in range(epochs):
                _loss = model_ce.model_training(train_loader, criterion, optimizer, device)

            _acc, _f1 = model_ce.evaluate(x_test, y_test)

            ranks, max_singulars, min_singulars = perturbations(model_ce)

            ce_data["acc"].append(_acc)
            ce_data["f1"].append(_f1)
            ce_data["loss"].append(_loss / N)
            ce_data["max_singular"].append(max_singulars)
            ce_data["min_singular"].append(min_singulars)
            ce_data["ranks"].append(ranks)

            # ---- Label Smoothing ----

            model_ls, criterion, optimizer = getMLP(device, loss="ce", label_smoothing=0.1)
            model_ls.train()
            for epoch in range(epochs):
                _loss = model_ls.model_training(train_loader, criterion, optimizer, device)

            _acc, _f1 = model_ls.evaluate(x_test, y_test)
            ranks, max_singulars, min_singulars = perturbations(model_ls)

            ls_data["acc"].append(_acc)
            ls_data["f1"].append(_f1)
            ls_data["loss"].append(_loss / N)
            ls_data["max_singular"].append(max_singulars)
            ls_data["min_singular"].append(min_singulars)
            ls_data["ranks"].append(ranks)

            # ---- Focal Model ----

            model_focal, criterion, optimizer = getMLP(device, loss="focal")
            model_focal.train()
            for epoch in range(epochs):
                _loss = model_focal.model_training(train_loader, criterion, optimizer, device)

            _acc, _f1 = model_focal.evaluate(x_test, y_test)
            ranks, max_singulars, min_singulars = perturbations(model_focal)

            focal_data["acc"].append(_acc)
            focal_data["f1"].append(_f1)
            focal_data["loss"].append(_loss / N)
            focal_data["max_singular"].append(max_singulars)
            focal_data["min_singular"].append(min_singulars)
            focal_data["ranks"].append(ranks)

            # ---- scor model ----

            model_scor, criterion, optimizer = getMLP(device, loss="scor")
            model_scor.train()
            for epoch in range(epochs):
                _loss = model_scor.model_training(train_loader, criterion, optimizer, device)

            _acc, _f1 = model_scor.evaluate(x_test, y_test)
            ranks, max_singulars, min_singulars = perturbations(model_scor)

            scor_data["acc"].append(_acc)
            scor_data["f1"].append(_f1)
            scor_data["loss"].append(_loss / N)
            scor_data["max_singular"].append(max_singulars)
            scor_data["min_singular"].append(min_singulars)
            scor_data["ranks"].append(ranks)

            if device == "cuda":
                torch.cuda.empty_cache()

            if i % 1 == 0:
                end = time()
                dt = end - begin
                eta = dt * iterations / (i + 1)
                print(f"Training done %{(((i + 1) * 100) / iterations):.5f} | Batch size: {batch_size}")
                print(f"ETA: {eta:.5f}s")

        save_data_dicts(ce_data, ls_data, focal_data, scor_data, batch_size, path)

    except Exception as e:
        print(f"An exception occurred: {e}")

        save_data_dicts(ce_data, ls_data, focal_data, scor_data, batch_size, path)

def trainMLPwithAlpha(
    batch_size: int, device: str = "cuda",
    iterations: int = 1000, epochs: int = 5,
    alpha: float = 1e-04, path: str = "./results",
    *args, **kwargs
):
    """
        Trains the "MLP" model class on MNIST for SCoR with given alpha.

        Repeats training "iterations" times. Each training takes "epochs" number
        of epochs.

        Measures accuracy, f1 score, loss, rank, max singular value and min singular value
        at the end of each training. Saves results as a json under
        "path" directory.
    """
    _, _, _, scor_data = get_empty_data_dict()

    train_loader: DataLoader
    test_subset: Subset
    x_test: torch.Tensor
    y_test: torch.Tensor

    _acc = 0
    _f1 = 0
    _loss = 0
    N = 0

    try:
        begin = time()
        for i in range(iterations):
            train_loader, test_subset = getUnbalancedMNIST(batch_size, *args, **kwargs)
            x_test = test_subset.dataset.dataset.data[test_subset.indices].to(device)
            y_test = test_subset.dataset.dataset.targets[test_subset.indices].to(device)

            N = len(train_loader) * batch_size
            # instead generate test_dataset and return it

            model_scor, criterion, optimizer = getMLP(device=device, loss="scor", alpha=alpha)
            model_scor.train()

            for epoch in range(epochs):
                _loss = model_scor.model_training(train_loader, criterion, optimizer, device)

            _acc, _f1 = model_scor.evaluate(x_test, y_test)

            ranks, max_singulars, min_singulars = perturbations(model_scor)

            scor_data["acc"].append(_acc)
            scor_data["f1"].append(_f1)
            scor_data["loss"].append(_loss / N)
            scor_data["max_singular"].append(max_singulars)
            scor_data["min_singular"].append(min_singulars)
            scor_data["ranks"].append(ranks)

            if device == "cuda":
                torch.cuda.empty_cache()

            if i % 1 == 0:
                end = time()
                dt = end - begin
                eta = dt * iterations / (i + 1)
                print(f"Training done %{(((i + 1) * 100) / iterations):.5f} | Batch size: {batch_size} | Alpha: {alpha}")
                print(f"ETA: {eta:.5f}s")

        timestamp = datetime.now().timestamp()
        with open(f"{path}/scor_data_{timestamp}_{batch_size}_{np.abs(np.log10(alpha))}.json", "w", encoding="utf-8") as file:
            json.dump(scor_data, file, ensure_ascii=False, indent=4)

    except Exception as e:
        print(f"An exception occurred: {e}")
        timestamp = datetime.now().timestamp()


def trainTargetedMLP(batch_size: int, device: str = "cuda",
          iterations: int = 1000, epochs: int = 5, reducing_factor: float = 0.1,
          path: str = "./results", *args, **kwargs):

    ce_data, ls_data, focal_data, scor_data = get_empty_data_dict()
    """
        Trains the "MLP" model class on MNIST for Cross Entropy Loss,
        Label Smoothing (p=0.1), Focal Loss and SCoR.

        MNIST is imbalanced by reducing 9 random classes by the given
        "reducing_factor" multiplicatively. The classes are selected
        randomly at each training repetition. The same dataset 
        partitions are shared across all 4 models that use a different
        loss function.

        Repeats training "iterations" times. Each training takes "epochs" number
        of epochs. 

        Measures accuracy, f1 score, loss, rank, max singular value and min singular value
        at the end of each training for each loss function. Saves results as a json under
        "path" directory.
    """
    train_loader: DataLoader
    test_loader: DataLoader
    x_test: torch.Tensor
    y_test: torch.Tensor

    _acc = 0
    _f1 = 0
    _loss = 0
    N = 0

    reducingName = int(reducing_factor * 10)

    try:
        begin = time()
        for i in range(iterations):
            target_class = np.random.randint(0, 10)
            train_loader, test_loader = getUnbalancedMNIST9(batch_size, reducing_factor,
                                                            target_class=target_class, *args, **kwargs)
            x_test, y_test = loaderToData(test_loader)
            x_test = x_test.to(device)
            y_test = y_test.to(device)

            N = len(train_loader) * batch_size

            model_ce, criterion, optimizer = getMLP(device, loss="ce")
            model_ce.train()

            for epoch in range(epochs):
                _loss = model_ce.model_training(train_loader, criterion, optimizer, device)

            _acc, _f1 = model_ce.evaluateTargeted(x_test, y_test, target_class=target_class)

            ranks, max_singulars, min_singulars = perturbations(model_ce)

            ce_data["acc"].append(_acc)
            ce_data["f1"].append(_f1)
            ce_data["loss"].append(_loss / N)
            ce_data["max_singular"].append(max_singulars)
            ce_data["min_singular"].append(min_singulars)
            ce_data["ranks"].append(ranks)

            # ---- Label Smoothing ----

            model_ls, criterion, optimizer = getMLP(device, loss="ce", label_smoothing=0.1)
            model_ls.train()
            for epoch in range(epochs):
                _loss = model_ls.model_training(train_loader, criterion, optimizer, device)

            _acc, _f1 = model_ls.evaluateTargeted(x_test, y_test, target_class=target_class)
            ranks, max_singulars, min_singulars = perturbations(model_ls)

            ls_data["acc"].append(_acc)
            ls_data["f1"].append(_f1)
            ls_data["loss"].append(_loss / N)
            ls_data["max_singular"].append(max_singulars)
            ls_data["min_singular"].append(min_singulars)
            ls_data["ranks"].append(ranks)

            # ---- Focal Model ----

            model_focal, criterion, optimizer = getMLP(device, loss="focal")
            model_focal.train()
            for epoch in range(epochs):
                _loss = model_focal.model_training(train_loader, criterion, optimizer, device)

            _acc, _f1 = model_focal.evaluateTargeted(x_test, y_test, target_class=target_class)
            ranks, max_singulars, min_singulars = perturbations(model_focal)

            focal_data["acc"].append(_acc)
            focal_data["f1"].append(_f1)
            focal_data["loss"].append(_loss / N)
            focal_data["max_singular"].append(max_singulars)
            focal_data["min_singular"].append(min_singulars)
            focal_data["ranks"].append(ranks)

            # ---- scor model ----

            model_scor, criterion, optimizer = getMLP(device, loss="scor")
            model_scor.train()
            for epoch in range(epochs):
                _loss = model_scor.model_training(train_loader, criterion, optimizer, device)

            _acc, _f1 = model_scor.evaluateTargeted(x_test, y_test, target_class=target_class)
            ranks, max_singulars, min_singulars = perturbations(model_scor)

            scor_data["acc"].append(_acc)
            scor_data["f1"].append(_f1)
            scor_data["loss"].append(_loss / N)
            scor_data["max_singular"].append(max_singulars)
            scor_data["min_singular"].append(min_singulars)
            scor_data["ranks"].append(ranks)

            if device == "cuda":
                torch.cuda.empty_cache()

            if i % 1 == 0:
                end = time()
                dt = end - begin
                eta = dt * (iterations - i - 1) / (i + 1)
                print(f"Training done %{(((i + 1) * 100) / iterations):.5f} | Batch size: {batch_size}")
                print(f"ETA: {eta:.5f}s")

        timestamp = datetime.now().timestamp()

        with open(f"{path}/ce_data_{iterations}_{batch_size}_{reducingName}.json", "w", encoding="utf-8") as file:
            json.dump(ce_data, file, ensure_ascii=False, indent=4)

        with open(f"{path}/ls_data_{iterations}_{batch_size}_{reducingName}.json", "w", encoding="utf-8") as file:
            json.dump(ls_data, file, ensure_ascii=False, indent=4)

        with open(f"{path}/focal_data_{iterations}_{batch_size}_{reducingName}.json", "w", encoding="utf-8") as file:
            json.dump(focal_data, file, ensure_ascii=False, indent=4)

        with open(f"{path}/scor_data_{iterations}_{batch_size}_{reducingName}.json", "w", encoding="utf-8") as file:
            json.dump(scor_data, file, ensure_ascii=False, indent=4)
    except Exception as e:
        print(f"An exception occurred: {e}")

        timestamp = datetime.now().timestamp()

        with open(f"{path}/ce_data_{timestamp}_{batch_size}_{reducingName}.json", "w", encoding="utf-8") as file:
            json.dump(ce_data, file, ensure_ascii=False, indent=4)

        with open(f"{path}/ls_data_{timestamp}_{batch_size}_{reducingName}.json", "w", encoding="utf-8") as file:
            json.dump(ls_data, file, ensure_ascii=False, indent=4)

        with open(f"{path}/focal_data_{timestamp}_{batch_size}_{reducingName}.json", "w", encoding="utf-8") as file:
            json.dump(focal_data, file, ensure_ascii=False, indent=4)

        with open(f"{path}/scor_data_{timestamp}_{batch_size}_{reducingName}.json", "w", encoding="utf-8") as file:
            json.dump(scor_data, file, ensure_ascii=False, indent=4)

def trainMLPwithdist(batch_size: int, device: str = "cuda",
          iterations: int = 1000, epochs: int = 5, path: str = "./results",
          *args, **kwargs):
    """
        Trains the "MLP" model class on MNIST for Cross Entropy Loss,
        Label Smoothing (p=0.1), Focal Loss and SCoR.

        MNIST is imbalanced by reducing a random class by the given
        "reducing_factor" multiplicatively. The class is selected
        randomly at each training repetition. The same dataset
        partitions are shared across all 4 models that use a different
        loss function.

        Repeats training "iterations" times. Each training takes "epochs" number
        of epochs.

        Measures accuracy, f1 score, loss, rank, singular value distribution
        at the end of each training for each loss function. Saves results as a json under
        "path" directory.
    """
    ce_data_dist, ls_data_dist, focal_data_dist, scor_data_dist = get_empty_dist_dict()

    train_loader: DataLoader
    test_subset: Subset
    x_test: torch.Tensor
    y_test: torch.Tensor

    _acc = 0
    _f1 = 0
    _loss = 0
    N = 0

    try:
        begin = time()
        for i in range(iterations):
            train_loader, test_subset = getUnbalancedMNIST(batch_size, *args, **kwargs)
            x_test = test_subset.dataset.dataset.data[test_subset.indices].to(device)
            y_test = test_subset.dataset.dataset.targets[test_subset.indices].to(device)

            N = len(train_loader) * batch_size
            # instead generate test_dataset and return it

            model_ce, criterion, optimizer = getMLP(device, loss="ce")
            model_ce.train()

            for epoch in range(epochs):
                _loss = model_ce.model_training(train_loader, criterion, optimizer, device)

            _acc, _f1 = model_ce.evaluate(x_test, y_test)

            ranks, singulars = spectralDist(model_ce)

            ce_data_dist["acc"].append(_acc)
            ce_data_dist["f1"].append(_f1)
            ce_data_dist["loss"].append(_loss / N)
            ce_data_dist["singulars"].append(singulars)
            ce_data_dist["ranks"].append(ranks)

            # ---- Label Smoothing ----

            model_ls, criterion, optimizer = getMLP(device, loss="ce", label_smoothing=0.1)
            model_ls.train()
            for epoch in range(epochs):
                _loss = model_ls.model_training(train_loader, criterion, optimizer, device)

            _acc, _f1 = model_ls.evaluate(x_test, y_test)
            ranks, singulars = spectralDist(model_ls)

            ls_data_dist["acc"].append(_acc)
            ls_data_dist["f1"].append(_f1)
            ls_data_dist["loss"].append(_loss / N)
            ls_data_dist["singulars"].append(singulars)
            ls_data_dist["ranks"].append(ranks)

            # ---- Focal Model ----

            model_focal, criterion, optimizer = getMLP(device, loss="focal")
            model_focal.train()
            for epoch in range(epochs):
                _loss = model_focal.model_training(train_loader, criterion, optimizer, device)

            _acc, _f1 = model_focal.evaluate(x_test, y_test)
            ranks, singulars = spectralDist(model_focal)

            focal_data_dist["acc"].append(_acc)
            focal_data_dist["f1"].append(_f1)
            focal_data_dist["loss"].append(_loss / N)
            focal_data_dist["singulars"].append(singulars)
            focal_data_dist["ranks"].append(ranks)

            # ---- scor model ----

            model_scor, criterion, optimizer = getMLP(device, loss="scor")
            model_scor.train()
            for epoch in range(epochs):
                _loss = model_scor.model_training(train_loader, criterion, optimizer, device)

            _acc, _f1 = model_scor.evaluate(x_test, y_test)
            ranks, singulars = spectralDist(model_scor)

            scor_data_dist["acc"].append(_acc)
            scor_data_dist["f1"].append(_f1)
            scor_data_dist["loss"].append(_loss / N)
            scor_data_dist["singulars"].append(singulars)
            scor_data_dist["ranks"].append(ranks)

            if device == "cuda":
                torch.cuda.empty_cache()

            if i % 1 == 0:
                end = time()
                dt = end - begin
                eta = dt * iterations / (i + 1)
                print(f"Training done %{(((i + 1) * 100) / iterations):.5f} | Batch size: {batch_size}")
                print(f"ETA: {eta:.5f}s")

        save_dist_dicts(ce_data_dist, ls_data_dist, focal_data_dist, scor_data_dist, batch_size, path)

    except Exception as e:
        print(f"An exception occurred: {e}")

        save_dist_dicts(ce_data_dist, ls_data_dist, focal_data_dist, scor_data_dist, batch_size, path)

def trainTargetedMLPwithdist(batch_size: int, device: str = "cuda",
          iterations: int = 1000, epochs: int = 5, reducing_factor: float = 0.1,
          path: str = "./results", *args, **kwargs):
    ce_data_dist, ls_data_dist, focal_data_dist, scor_data_dist = get_empty_dist_dict()
    """
        Trains the "MLP" model class on MNIST for Cross Entropy Loss,
        Label Smoothing (p=0.1), Focal Loss and SCoR.

        MNIST is imbalanced by reducing 9 random classes by the given
        "reducing_factor" multiplicatively. The classes are selected
        randomly at each training repetition. The same dataset 
        partitions are shared across all 4 models that use a different
        loss function.

        Repeats training "iterations" times. Each training takes "epochs" number
        of epochs. 

        Measures accuracy, f1 score, loss, rank, singular value distribution
        at the end of each training for each loss function. Saves results as a json under
        "path" directory.
    """
    train_loader: DataLoader
    test_loader: DataLoader
    x_test: torch.Tensor
    y_test: torch.Tensor

    _acc = 0
    _f1 = 0
    _loss = 0
    N = 0

    reducingName = int(reducing_factor * 10)

    try:
        begin = time()
        for i in range(iterations):
            target_class = np.random.randint(0, 10)
            train_loader, test_loader = getUnbalancedMNIST9(batch_size, reducing_factor,
                                                            target_class=target_class, *args, **kwargs)
            x_test, y_test = loaderToData(test_loader)
            x_test = x_test.to(device)
            y_test = y_test.to(device)

            N = len(train_loader) * batch_size

            model_ce, criterion, optimizer = getMLP(device, loss="ce")
            model_ce.train()

            for epoch in range(epochs):
                _loss = model_ce.model_training(train_loader, criterion, optimizer, device)

            _acc, _f1 = model_ce.evaluateTargeted(x_test, y_test, target_class=target_class)

            ranks, singulars = spectralDist(model_ce)

            ce_data_dist["acc"].append(_acc)
            ce_data_dist["f1"].append(_f1)
            ce_data_dist["loss"].append(_loss / N)
            ce_data_dist["singulars"].append(singulars)
            ce_data_dist["ranks"].append(ranks)

            # ---- Label Smoothing ----

            model_ls, criterion, optimizer = getMLP(device, loss="ce", label_smoothing=0.1)
            model_ls.train()
            for epoch in range(epochs):
                _loss = model_ls.model_training(train_loader, criterion, optimizer, device)

            _acc, _f1 = model_ls.evaluateTargeted(x_test, y_test, target_class=target_class)
            ranks, singulars = spectralDist(model_ls)

            ls_data_dist["acc"].append(_acc)
            ls_data_dist["f1"].append(_f1)
            ls_data_dist["loss"].append(_loss / N)
            ls_data_dist["singulars"].append(singulars)
            ls_data_dist["ranks"].append(ranks)

            # ---- Focal Model ----

            model_focal, criterion, optimizer = getMLP(device, loss="focal")
            model_focal.train()
            for epoch in range(epochs):
                _loss = model_focal.model_training(train_loader, criterion, optimizer, device)

            _acc, _f1 = model_focal.evaluateTargeted(x_test, y_test, target_class=target_class)
            ranks, singulars = spectralDist(model_focal)

            focal_data_dist["acc"].append(_acc)
            focal_data_dist["f1"].append(_f1)
            focal_data_dist["loss"].append(_loss / N)
            focal_data_dist["singulars"].append(singulars)
            focal_data_dist["ranks"].append(ranks)

            # ---- scor model ----

            model_scor, criterion, optimizer = getMLP(device, loss="scor")
            model_scor.train()
            for epoch in range(epochs):
                _loss = model_scor.model_training(train_loader, criterion, optimizer, device)

            _acc, _f1 = model_scor.evaluateTargeted(x_test, y_test, target_class=target_class)
            ranks, singulars = spectralDist(model_scor)

            scor_data_dist["acc"].append(_acc)
            scor_data_dist["f1"].append(_f1)
            scor_data_dist["loss"].append(_loss / N)
            scor_data_dist["singulars"].append(singulars)
            scor_data_dist["ranks"].append(ranks)

            if device == "cuda":
                torch.cuda.empty_cache()

            if i % 1 == 0:
                end = time()
                dt = end - begin
                eta = dt * (iterations - i - 1) / (i + 1)
                print(f"Training done %{(((i + 1) * 100) / iterations):.5f} | Batch size: {batch_size}")
                print(f"ETA: {eta:.5f}s")

        timestamp = datetime.now().timestamp()

        with open(f"{path}/ce_data_{iterations}_{batch_size}_{reducingName}_dist.json", "w", encoding="utf-8") as file:
            json.dump(ce_data_dist, file, ensure_ascii=False, indent=4)

        with open(f"{path}/ls_data_{iterations}_{batch_size}_{reducingName}_dist.json", "w", encoding="utf-8") as file:
            json.dump(ls_data_dist, file, ensure_ascii=False, indent=4)

        with open(f"{path}/focal_data_{iterations}_{batch_size}_{reducingName}_dist.json", "w", encoding="utf-8") as file:
            json.dump(focal_data_dist, file, ensure_ascii=False, indent=4)

        with open(f"{path}/scor_data_{iterations}_{batch_size}_{reducingName}_dist.json", "w", encoding="utf-8") as file:
            json.dump(scor_data_dist, file, ensure_ascii=False, indent=4)
    except Exception as e:
        print(f"An exception occurred: {e}")

        timestamp = datetime.now().timestamp()

        with open(f"{path}/ce_data_{timestamp}_{batch_size}_{reducingName}_dist.json", "w", encoding="utf-8") as file:
            json.dump(ce_data_dist, file, ensure_ascii=False, indent=4)

        with open(f"{path}/ls_data_{timestamp}_{batch_size}_{reducingName}_dist.json", "w", encoding="utf-8") as file:
            json.dump(ls_data_dist, file, ensure_ascii=False, indent=4)

        with open(f"{path}/focal_data_{timestamp}_{batch_size}_{reducingName}_dist.json", "w", encoding="utf-8") as file:
            json.dump(focal_data_dist, file, ensure_ascii=False, indent=4)

        with open(f"{path}/scor_data_{timestamp}_{batch_size}_{reducingName}_dist.json", "w", encoding="utf-8") as file:
            json.dump(scor_data_dist, file, ensure_ascii=False, indent=4)


