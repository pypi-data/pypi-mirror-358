import torch
import torch.nn as nn
from itertools import chain

def perturbations(model: nn.Module, epsilon: float = 1e-07):

    """

        Calculates ranks, maximum singular values and minimum singular values
        as "measures" of matrix perturbations.
    """

    ranks = []
    max_singulars = []
    min_singulars = []
    s: torch.Tensor

    # Model must have all layers in self.sequence
    for name, param in model.sequence.named_parameters():
        if "bias" in name:
            continue

        s = torch.linalg.svdvals(param)
        ranks.append(torch.sum(s > epsilon).item())
        max_singulars.append(s[0].item())
        min_singulars.append(s[-1].item())

    return ranks, max_singulars, min_singulars

def spectralDist(model: nn.Module, epsilon: float = 1e-07):

    """
        Calculates ranks and all singular values of all weight matrix of the
        give model, for the evaluation of spectral distributions.
    """

    ranks = []
    singulars = []
    s: torch.Tensor

    for name, param in model.sequence.named_parameters():
        if "bias" in name:
            continue

        s = torch.linalg.svdvals(param)
        ranks.append(torch.sum(s > epsilon).item())
        singulars.append(s.tolist())

    return ranks, list(chain(*singulars))

def perturbationsMultiple(model: nn.Module, epsilon: float = 1e-07):
    ranks = []
    max_singulars = []
    min_singulars = []
    s: torch.Tensor

    # Model must have all layers in self.sequence
    for name, param in model.sequence.named_parameters():
        if "bias" in name or param.ndim < 2:
            continue

        s = torch.linalg.svdvals(param)
        ranks.append(torch.sum(s > epsilon).item())
        max_singulars.append(torch.mean(s[0]).item())
        min_singulars.append(torch.mean(s[-1]).item())

    return ranks, max_singulars, min_singulars
