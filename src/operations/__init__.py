"""
Operations package for CodeFlux.
Contains implementations of various file transformation and analysis operations.
"""

# First import the base classes to avoid circular dependencies
from operations.base import Operation, OperationStats

# Import specific operations
# These imports will happen after base is already loaded
from operations.flatten import FlattenOperation
from operations.deflatten import DeflattenOperation
from operations.minify import MinifyOperation
from operations.bundle import BundleOperation
from operations.autocomment import AutoCommentOperation
from operations.linebreak import LinebreakOperation

__all__ = [
    'Operation',
    'OperationStats',
    'FlattenOperation',
    'DeflattenOperation',
    'MinifyOperation',
    'BundleOperation',
    'AutoCommentOperation',
    'LinebreakOperation',
]
