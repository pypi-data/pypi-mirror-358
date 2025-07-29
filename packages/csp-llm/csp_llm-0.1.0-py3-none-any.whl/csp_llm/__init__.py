"""
csp_llm

I'll put a description here later
"""

__version__ = "0.1.0"
__author__ = "Votre Nom"
__email__ = "votre.email@example.com"

from .ai_client import AIClient
from .csp_solver import CSPSolver
from .main import main_function

__all__ = [
    "main_function",
    "CSPSolver",
    "AIClient",
    "__version__",
]
