from typing import overload
from abc import abstractmethod


def _function(function):
    return function


globals()['overload'] = _function
globals()['abstractmethod'] = _function