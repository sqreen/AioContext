"""Errors and exceptions."""


class AioContextError(Exception):
    """Base class for aiocontext errors."""


class EventLoopError(AioContextError):
    """Raised when the current running task cannot be determined.

    This generally means that the context is manipulated with no event loop
    running, e.g. in synchronous code.
    """


class TaskFactoryError(AioContextError):
    """Raised when no context-aware task factory was set for the current loop.

    This generally means the following code was not executed::

        wrap_task_factory(loop)
    """


class TaskContextError(AioContextError):
    """Raised when no context data is stored in the current task.

    This generally means the context is not registered in the current loop,
    i.e. the following code was not executed::

        context.attach(loop)
    """
