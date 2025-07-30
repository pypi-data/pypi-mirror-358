"""
type_extension - Extended typing support with additional features
"""

# Импортируем всё из typing_extensions
from .typing_extensions import *

# Экспортируем основные типы из typing
from typing import (
    Any, Dict, List, Optional, Union, Tuple, Set, FrozenSet,
    Callable, Iterator, Iterable, Generator, Coroutine,
    Type, TypeVar, Generic, ClassVar, Final, Literal,
    overload, cast, no_type_check, no_type_check_decorator
)

# Дополнительные типы для совместимости
try:
    from typing import Annotated
except ImportError:
    # Для старых версий Python
    class _AnnotatedAlias:
        def __getitem__(self, item):
            return item[0] if isinstance(item, tuple) else item
    
    Annotated = _AnnotatedAlias()

__version__ = "3.1.2"
__all__ = [
    'Any', 'Dict', 'List', 'Optional', 'Union', 'Tuple', 'Set',
    'FrozenSet', 'Callable', 'Iterator', 'Iterable', 'Generator',
    'Coroutine', 'Type', 'TypeVar', 'Generic', 'ClassVar', 'Final',
    'Literal', 'Annotated', 'overload', 'cast', 'no_type_check',
    'no_type_check_decorator'
] 