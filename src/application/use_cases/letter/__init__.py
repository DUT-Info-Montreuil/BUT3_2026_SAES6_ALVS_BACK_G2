# src/application/use_cases/letter/__init__.py
"""Use Cases Letter."""

from src.application.use_cases.letter.create_letter import (
    CreateFileLetterUseCase,
    CreateTextLetterUseCase,
)
from src.application.use_cases.letter.delete_letter import DeleteLetterUseCase
from src.application.use_cases.letter.get_letters import (
    GetLetterByIdUseCase,
    GetLettersForColliUseCase,
)

__all__ = [
    'CreateTextLetterUseCase',
    'CreateFileLetterUseCase',
    'GetLettersForColliUseCase',
    'GetLetterByIdUseCase',
    'DeleteLetterUseCase'
]
