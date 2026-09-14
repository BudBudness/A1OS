"""Compatibility entrypoint for the canonical A1OS dispatcher."""

from core.dispatcher import *

try:
    from core.dispatcher import dispatch
except ImportError:
    dispatch = None

__all__ = [name for name in globals() if not name.startswith("_")]
