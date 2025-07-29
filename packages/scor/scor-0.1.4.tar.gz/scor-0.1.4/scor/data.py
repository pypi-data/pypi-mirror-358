from torchvision import transforms
from torchvision import datasets
from torchvision.datasets import MNIST, CIFAR10, Flowers102, OxfordIIITPet, DTD, STL10, ImageFolder
from torch.utils.data import DataLoader, random_split, Subset
import torch

import numpy as np
import os
import shutil

transform_ = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.RandomHorizontalFlip(),
    transforms.RandomRotation(15),
    transforms.ColorJitter(brightness=0.2, contrast=0.2, saturation=0.2),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
])

normalTransform = transforms.Compose([
    transforms.ToTensor(),
    transforms.Normalize((0.,), (1.,))
])

uniformTransform = transforms.Compose([
    transforms.RandomHorizontalFlip(),
    transforms.RandomCrop(32, padding=4),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.4914, 0.4822, 0.4465], std=[0.2470, 0.2435, 0.2616]),
])

def get_cifar10(transform=None,
                batch_size: int = 64,
                shuffle: bool = True,
                num_workers: int = 0,
                drop_last: bool = False):

    train_set = CIFAR10(root='./data', train=True, download=True, transform=transform)
    test_set = CIFAR10(root='./data', train=False, download=True, transform=transform)

    train_loader = DataLoader(train_set, batch_size=batch_size, shuffle=shuffle, num_workers=num_workers, drop_last=drop_last)
    test_loader = DataLoader(test_set, batch_size=batch_size, shuffle=shuffle, num_workers=num_workers, drop_last=drop_last)

    return train_loader, test_loader

def get_mnist(transform=None,
              batch_size: int = 64,
              shuffle: bool = True,
              num_workers: int = 0,
              drop_last: bool = False):

    train_set = MNIST(root='./data', train=True, download=True, transform=transform)
    test_set = MNIST(root='./data', train=False, download=True, transform=transform)

    train_loader = DataLoader(train_set, batch_size=batch_size, shuffle=shuffle, num_workers=num_workers, drop_last=drop_last)
    test_loader = DataLoader(test_set, batch_size=batch_size, shuffle=shuffle, num_workers=num_workers, drop_last=drop_last)

    return train_loader, test_loader

def get_flowers102(transform=transform_,
                   batch_size: int = 32,
                   shuffle: bool = True,
                   num_workers: int = 0,
                   drop_last: bool = False):

    train_set = Flowers102(root="./data", split="train", download=True, transform=transform)
    test_set = Flowers102(root="./data", split="test", download=True, transform=transform)

    train_loader = DataLoader(train_set, batch_size=batch_size, shuffle=shuffle, num_workers=num_workers, drop_last=drop_last)
    test_loader = DataLoader(test_set, batch_size=batch_size, shuffle=shuffle, num_workers=num_workers, drop_last=drop_last)

    return train_loader, test_loader

def get_oxfordpets(transform=transform_,
                   batch_size: int = 32,
                   shuffle: bool = True,
                   num_workers: int = 0,
                   drop_last: bool = False):
    train_set = OxfordIIITPet(root="./data", split="trainval", download=True, transform=transform)
    test_set = OxfordIIITPet(root="./data", split="test", download=True, transform=transform)

    train_loader = DataLoader(train_set, batch_size=batch_size, shuffle=shuffle, num_workers=num_workers,
                              drop_last=drop_last)
    test_loader = DataLoader(test_set, batch_size=batch_size, shuffle=shuffle, num_workers=num_workers,
                             drop_last=drop_last)

    return train_loader, test_loader

def get_stl10(transform=transform_,
              batch_size: int = 128,
              shuffle: bool = True,
              num_workers: int = 0,
              drop_last: bool = False):

    train_set = STL10(root="./data", split="train", download=True, transform=transform)
    test_set = STL10(root="./data", split="test", download=True, transform=transform)

    train_loader = DataLoader(train_set, batch_size=batch_size, shuffle=shuffle, num_workers=num_workers,
                              drop_last=drop_last)
    test_loader = DataLoader(test_set, batch_size=batch_size, shuffle=shuffle, num_workers=num_workers,
                             drop_last=drop_last)

    return train_loader, test_loader

def get_dtd(transform=transform_,
            batch_size: int = 32,
            shuffle: bool = True,
            num_workers: int = 0,
            drop_last: bool = False):

    train_set = DTD(root="./data", split="train", download=True, transform=transform)
    test_set = DTD(root="./data", split="test", download=True, transform=transform)

    train_loader = DataLoader(train_set, batch_size=batch_size, shuffle=shuffle, num_workers=num_workers,
                              drop_last=drop_last)
    test_loader = DataLoader(test_set, batch_size=batch_size, shuffle=shuffle, num_workers=num_workers,
                             drop_last=drop_last)

    return train_loader, test_loader

def get_lfw(lfw_root: str,
            transform=transform_,
            batch_size: int = 128,
            trainset_size: float = 0.8,
            shuffle: bool = True,
            num_workers: int = 0,
            drop_last: bool = False,
            exclude: int = 5):

    for folder in os.listdir(lfw_root):
        folder_path = os.path.join(lfw_root, folder)
        if os.path.isdir(folder_path):  # Check if it's a directory
            num_images = len(os.listdir(folder_path))  # Count images
            if num_images < exclude:
                shutil.rmtree(folder_path)  # Delete the folder
                print(f"Deleted: {folder_path} (Had {num_images} images)")

    dataset = ImageFolder(lfw_root, transform=transform)
    train_size = int(trainset_size * len(dataset))
    test_size = len(dataset) - train_size

    train_dataset, test_dataset = random_split(dataset, [train_size, test_size])
    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=shuffle, num_workers=num_workers, drop_last=drop_last)
    test_loader = DataLoader(test_dataset, batch_size=batch_size, shuffle=shuffle, num_workers=num_workers, drop_last=drop_last)
    return train_loader, test_loader

def loadMNIST(transform: transforms.Compose = normalTransform, batch_size: int = 64):
    train_dataset = datasets.MNIST(root="data", train=True, transform=transform, download=True)
    test_dataset = datasets.MNIST(root="data", train=False, transform=transform, download=True)

    train_loader = DataLoader(dataset=train_dataset, batch_size=batch_size, shuffle=True)
    test_loader = DataLoader(dataset=test_dataset, shuffle=True)

    return train_loader, test_loader

def getUnbalancedMNIST(batch_size: int, split: float = 0.8, transform: transforms.Compose = normalTransform,
                       reducing_factor: float = 0.05, target_class: int = None):

    if target_class is None:
        target_class = np.random.randint(0, 10)

    train_dataset = datasets.MNIST(root="data", train=True, transform=transform, download=True)
    class_indices = {i: (train_dataset.targets == i).nonzero(as_tuple=True)[0] for i in range(10)}

    # randomize the order of data for each class
    for key, value in class_indices.items():
        perm = torch.randperm(len(value))
        class_indices[key] = value[perm]

    num_samples = len(class_indices[target_class])
    reduced_indices = class_indices[target_class][:int(reducing_factor * num_samples)]

    unbalanced_indices = reduced_indices.tolist()
    for i in range(10):
        if target_class == i:
            continue
        unbalanced_indices.extend(class_indices[i].tolist())

    unbalanced_dataset = Subset(train_dataset, unbalanced_indices)

    train_size = int(split * len(unbalanced_dataset))
    test_size = len(unbalanced_dataset) - train_size

    train_dataset, test_dataset = random_split(unbalanced_dataset, [train_size, test_size])

    train_loader = DataLoader(dataset=train_dataset, batch_size=batch_size, shuffle=True)

    return train_loader, test_dataset


def getUnbalancedMNIST9(
        batch_size: int,
        split: float = 0.8,
        transform: transforms.Compose = normalTransform,
        reducing_factor: float = 0.1,
        target_class: int = None
):

    if target_class is None:
        target_class = np.random.randint(0, 10)

    train_dataset = datasets.MNIST(root="data", train=True, transform=transform, download=True)
    class_indices = {i: (train_dataset.targets == i).nonzero(as_tuple=True)[0] for i in range(10)}

    for key in class_indices:
        class_indices[key] = class_indices[key][torch.randperm(len(class_indices[key]))]

    unbalanced_indices = []
    for i in range(10):
        if target_class == i:
            unbalanced_indices.extend(class_indices[i].tolist())
        else:
            num_samples = len(class_indices[i])
            unbalanced_indices.extend(class_indices[i][:int(reducing_factor * num_samples)].tolist())

    unbalanced_dataset = Subset(train_dataset, unbalanced_indices)

    train_size = int(split * len(unbalanced_dataset))
    test_size = len(unbalanced_dataset) - train_size
    train_dataset, test_dataset = random_split(unbalanced_dataset, [train_size, test_size])

    # Create DataLoader instances
    train_loader = DataLoader(dataset=train_dataset, batch_size=batch_size, shuffle=True)
    test_loader = DataLoader(test_dataset, batch_size=batch_size, shuffle=False)

    return train_loader, test_loader

def loadCIFAR10(transform: transforms.Compose = uniformTransform, batch_size: int = 64):

    train_dataset = datasets.CIFAR10(
        root='./data',
        train=True,
        download=True,
        transform=transform
    )

    test_dataset = datasets.CIFAR10(
        root='./data',
        train=False,
        download=True,
        transform=transform
    )

    train_loader = DataLoader(
        dataset=train_dataset,
        batch_size=batch_size,
        shuffle=True
    )

    test_loader = DataLoader(
        dataset=test_dataset,
        shuffle=True
    )

    return train_loader, test_loader


def getUnbalancedCIFAR(
        batch_size: int,
        split: float = 0.8,
        transform: transforms.Compose = uniformTransform,
        reducing_factor: float = 0.05,
        target_class: int = None
):

    if target_class is None:
        target_class = np.random.randint(0, 10)


    train_dataset = datasets.CIFAR10(root="data", train=True, transform=transform, download=True)

    class_indices = {i: (torch.tensor(train_dataset.targets) == i).nonzero(as_tuple=True)[0] for i in range(10)}


    for key in class_indices:
        class_indices[key] = class_indices[key][torch.randperm(len(class_indices[key]))]


    num_samples = len(class_indices[target_class])
    reduced_indices = class_indices[target_class][:int(reducing_factor * num_samples)]


    unbalanced_indices = reduced_indices.tolist()
    for i in range(10):
        if target_class == i:
            continue
        unbalanced_indices.extend(class_indices[i].tolist())


    unbalanced_dataset = Subset(train_dataset, unbalanced_indices)


    train_size = int(split * len(unbalanced_dataset))
    test_size = len(unbalanced_dataset) - train_size
    train_dataset, test_dataset = random_split(unbalanced_dataset, [train_size, test_size])

    train_loader = DataLoader(dataset=train_dataset, batch_size=batch_size, shuffle=True)
    test_loader = DataLoader(test_dataset, shuffle=False)
    return train_loader, test_loader

def getUnbalancedCIFAR9(
        batch_size: int,
        split: float = 0.8,
        transform: transforms.Compose = uniformTransform,
        reducing_factor: float = 0.05,
        target_class: int = None
):

    if target_class is None:
        target_class = np.random.randint(0, 10)


    train_dataset = datasets.CIFAR10(root="./data", train=True, transform=transform, download=True)

    class_indices = {i: (torch.tensor(train_dataset.targets) == i).nonzero(as_tuple=True)[0] for i in range(10)}

    for key in class_indices:
        class_indices[key] = class_indices[key][torch.randperm(len(class_indices[key]))]

    unbalanced_indices = []
    for i in range(10):
        if target_class == i:
            unbalanced_indices.extend(class_indices[i].tolist())
        else:
            num_samples = len(class_indices[i])
            unbalanced_indices.extend(class_indices[i][:int(reducing_factor * num_samples)].tolist())

    unbalanced_dataset = Subset(train_dataset, unbalanced_indices)

    train_size = int(split * len(unbalanced_dataset))
    test_size = len(unbalanced_dataset) - train_size
    train_dataset, test_dataset = random_split(unbalanced_dataset, [train_size, test_size])

    # Create DataLoader instances
    train_loader = DataLoader(dataset=train_dataset, batch_size=batch_size, shuffle=True)
    test_loader = DataLoader(test_dataset, batch_size=batch_size, shuffle=False)

    return train_loader, test_loader

def loaderToData(dataloader: DataLoader):
    x_list = []
    y_list = []

    for x_batch, y_batch in dataloader:
        x_list.append(x_batch)
        y_list.append(y_batch)

    return torch.cat(x_list, dim=0), torch.cat(y_list, dim=0)
