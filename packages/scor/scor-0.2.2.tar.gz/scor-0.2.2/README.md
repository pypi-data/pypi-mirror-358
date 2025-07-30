# Stochastic Covariance Regularization for Imbalanced Datasets - ICANN 2025 

The repository of the paper "Stochastic Covariance Regularization for Imbalanced Datasets",
accepted into [ICANN 2025](https://e-nns.org/icann2025/). Conference papers are not yet
published. When published, a link to the Springer page of the paper will be provided here.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

[PyPi page](https://pypi.org/project/scor/)

[Github page](https://github.com/ahmeterdem1/scor)

_pip install scor_

## "scor" package

The "scor" package is organized as a library that could easily be imported
and used in applications. It includes all utility functions, measurement
functions, model classes and data loaders used in the paper, organized
into modules.

### scor.data

This module includes data utilities and data loader functions for datasets
that were used in the paper. Data loading functions for MNIST, CIFAR-10,
Flower102, Oxford IIIT Pets, DTD, STL-10 and LFW People are given. For
LFW People, you need to [download](https://www.kaggle.com/datasets/jessicali9530/lfw-dataset) 
it then extract it first, because the link that PyTorch provides within its own data loader
is broken.

### scor.losses

This module includes the SCoR loss function alongside other that were used in the paper.

### scor.metrics

This module has utility functions that calculate ranks and singular values of weight matrices
of models, that were interpreted as indicators of matrix perturbations in the paper.

### scor.models

This module hosts model classes used in tests. It does not include ResNet32 and ResNet50 classes,
because respective tests in the paper were adopted from other sources. Several options for ConvNeXt
is supported, but in the paper only ConvNeXt-Tiny is used.

### scor.training

This module hosts several training functions for several tests in the paper. These functions cover
first phase of experiments in the paper, where MNIST and CIFAR-10 is artificially imbalanced by
imbalancing a random class, or 9 random classes multiplicatively by a reduction factor.

## Examples

Example notebooks that use the "scor" package for training on given datasets are provided under
the "examples" directory.

## imagenet.py

This file is for training models with various loss functions on the ImageNet dataset.
Code from [here](https://github.com/pytorch/examples/tree/main/imagenet) is adapted 
to be used with loss functions defined in this repository.

A "loss" option is included to the adapted code. Run ```python imagenet.py --help```
for a proper description.
