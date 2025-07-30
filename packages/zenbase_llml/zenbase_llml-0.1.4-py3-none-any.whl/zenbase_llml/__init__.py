"""LLML - A lightweight markup language for structured text generation."""

from .llml import LLMLOptions, llml

__version__ = "0.1.0"
__all__ = ["llml", "LLMLOptions"]

__call__ = llml
