from torch import nn


def freeze(module: nn.Module, mode: bool = True):
    if mode:
        for parameter in module.parameters():
            if parameter.requires_grad:
                parameter.requires_grad = False


def unfreeze(module: nn.Module, mode: bool = True):
    if mode:
        for parameter in module.parameters():
            if not parameter.requires_grad:
                parameter.requires_grad = True