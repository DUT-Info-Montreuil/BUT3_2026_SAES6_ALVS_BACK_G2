# src/application/use_cases/letter/__init__.py
"""Use Cases Letter."""

from src.application.use_cases.letter.create_letter import (
    CreateTextLetterUseCase,
    CreateFileLetterUseCase
)
from src.application.use_cases.letter.get_letters import (
    GetLettersForColliUseCase,
    GetLetterByIdUseCase
)
from src.application.use_cases.letter.delete_letter import DeleteLetterUseCase

__all__ = [
    'CreateTextLetterUseCase',
    'CreateFileLetterUseCase',
    'GetLettersForColliUseCase',
    'GetLetterByIdUseCase',
    'DeleteLetterUseCase'
]
