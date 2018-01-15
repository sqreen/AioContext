"""Context information storage for asyncio."""

from .__about__ import (__author__, __copyright__, __email__, __license__,
                        __summary__, __title__, __uri__, __version__)
from .context import Context, chainmap_copy, get_loop_contexts
from .errors import (AioContextError, EventLoopError, TaskContextError,
                     TaskFactoryError)
from .task_factory import unwrap_task_factory, wrap_task_factory


__all__ = [
    '__author__',
    '__copyright__',
    '__email__',
    '__license__',
    '__summary__',
    '__title__',
    '__uri__',
    '__version__',
    'wrap_task_factory',
    'unwrap_task_factory',
    'Context',
    'chainmap_copy',
    'get_loop_contexts',
    'AioContextError',
    'EventLoopError',
    'TaskFactoryError',
    'TaskContextError',
]
