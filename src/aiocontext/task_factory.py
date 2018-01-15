"""Task factory."""

import asyncio
from functools import wraps

from .__about__ import __title__
from .errors import TaskFactoryError


_TASK_FACTORY_ATTR = '_{}_contexts'.format(__title__)


def get_task_factory_attr(loop):
    """Return the dict of contexts registered in *loop*.

    Raises :exc:`TaskFactoryError` if the loop is not context-aware.
    """
    task_factory = loop.get_task_factory()
    if not hasattr(task_factory, _TASK_FACTORY_ATTR):
        raise TaskFactoryError("Task factory is not context-aware")
    return getattr(task_factory, _TASK_FACTORY_ATTR)


def _default_task_factory(loop, coro):
    return asyncio.Task(coro, loop=loop)


def wrap_task_factory(loop):
    """Wrap the *loop* task factory to make it context-aware.

    Internally, this replaces the loop task factory by a wrapper function that
    manages context sharing between tasks. When a new task is spawned, the
    original task factory is called, then for each attached context, data is
    copied from the parent task to the child one. How copy is performed is
    specified in :meth:`Context.copy_func`.

    If *loop* uses a custom task factory, this function must be called after
    setting it::

        class CustomTask(asyncio.Task):
            pass

        def custom_task_factory(loop, coro):
            return CustomTask(coro, loop=loop)

        loop.set_task_factory(custom_task_factory)
        wrap_task_factory(loop)

    This function has no effect if the task factory is already context-aware.
    """
    task_factory = loop.get_task_factory()
    if hasattr(task_factory, _TASK_FACTORY_ATTR):
        return
    if task_factory is None:
        task_factory = _default_task_factory

    @wraps(task_factory)
    def wrapper(loop, coro):
        parent_task = asyncio.Task.current_task(loop=loop)
        child_task = task_factory(loop, coro)
        if child_task._source_traceback:
            del child_task._source_traceback[-1]
        for context in getattr(wrapper, _TASK_FACTORY_ATTR).values():
            parent_data = getattr(parent_task, context._data_attr, None)
            if parent_data is None:
                child_data = {}
            else:
                child_data = context.copy_func(parent_data)
            setattr(child_task, context._data_attr, child_data)
        return child_task

    setattr(wrapper, _TASK_FACTORY_ATTR, {})
    loop.set_task_factory(wrapper)


def unwrap_task_factory(loop):
    """Restore the original task factory of *loop*.

    This function cancels the effect of :func:`wrap_task_factory`. After
    calling it, the loop task factory is no longer context-aware. Context
    registration is lost.

    This function has no effect if the task factory is not context-aware.
    """
    task_factory = loop.get_task_factory()
    if not hasattr(task_factory, _TASK_FACTORY_ATTR):
        return
    loop.set_task_factory(task_factory.__wrapped__)
