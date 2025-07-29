from typing import Optional, Any
import torch
from torch import nn


def load_weights(
    module: nn.Module,
    path: str,
    key: Optional[str] = None,
    pickle_module: Any = None,
    weights_only: Optional[bool] = None,
    mmap: Optional[bool] = None,
    **pickle_load_args: Any
) -> nn.Module:
    state_dict = torch.load(
        path,
        next(module.parameters()).device,
        pickle_module,
        weights_only=weights_only,
        mmap=mmap,
        **pickle_load_args
    )
    if key is not None:
        state_dict = state_dict[key]
    module.load_state_dict(state_dict)
    return module