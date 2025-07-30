"""DreiPC Python CLI - A tool for creating FastAPI projects with best practices."""

__version__ = "1.0.0"
__author__ = "Your Name"
__email__ = "your.email@example.com"
__description__ = "A CLI tool for creating FastAPI projects"

from .generator import FastAPIProjectGenerator
from .cli import main

__all__ = ["FastAPIProjectGenerator", "main"]