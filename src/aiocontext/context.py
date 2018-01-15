"""Context information storage for asyncio."""

import asyncio
from collections import ChainMap
from collections.abc import MutableMapping
from contextlib import suppress
from uuid import uuid4

from .__about__ import __title__
from .errors import EventLoopError, TaskContextError, TaskFactoryError
from .task_factory import get_task_factory_attr


class Context(MutableMapping):
    """Create an empty, asynchronous execution context.

    The context must be attached to an event loop. It behaves like a
    dictionnary::

        >>> context = Context()
        >>> context.attach(loop)
        >>> context['key1'] = 'value'
        >>> context['key1']
        'value'
        >>> context.get('key2', 'defaut')
        'default'

    Upon initialization, an optional argument *copy_func* can be passed to
    specify how context data are copied between tasks. Relevant values are:

    * :class:`dict` or :func:`copy.copy` to create a shallow copy.
    * :func:`copy.deepcopy` to create a deep copy. All values should support
      the deepcopy protocol.
    * :func:`chainmap_copy` to use a :class:`collections.ChainMap`, with child
      task data stored in the front map and parent data stored in nested maps.
    """

    __slots__ = (
        '_copy_func',
        '_data_attr',
    )

    def __init__(self, copy_func=dict):
        self._copy_func = copy_func
        self._data_attr = '_{prefix}_{suffix}'.format(
            prefix=__title__,
            suffix=str(uuid4()).replace('-', ''),
        )

    @property
    def copy_func(self):
        """Copy function, called when a new task is spawned."""
        return self._copy_func

    def get_data(self, task=None):
        """Return the :class:`dict` of *task* data.

        If *task* is omitted or ``None``, return data of the task being
        currently executed. If no task is running, an :exc:`EventLoopError` is
        raised.

        This method raises :exc:`TaskContextError` if no context data is stored
        in *task*. This usually indicates that the context task factory was not
        set in the event loop.

        ::

            >>> context['key'] = 'value'
            >>> context.get_data()
            {'key': 'value'}
        """
        if task is None:
            task = asyncio.Task.current_task()
            if task is None:
                raise EventLoopError("No event loop found")
        data = getattr(task, self._data_attr, None)
        if data is None:
            raise TaskContextError("No task context found")
        return data

    def __getitem__(self, key):
        data = self.get_data()
        return data[key]

    def __setitem__(self, key, value):
        data = self.get_data()
        data[key] = value

    def __delitem__(self, key):
        data = self.get_data()
        del data[key]

    def __iter__(self):
        data = self.get_data()
        return iter(data)

    def __len__(self):
        data = self.get_data()
        return len(data)

    def attach(self, loop):
        """Attach the execution context to *loop*.

        When new tasks are spawned by the loop, they will inherit context data
        from the parent task. The loop must use a context-aware task factory;
        if not, a :exc:`TaskFactoryError` is raised.

        This method has no effect if the context is already attached to *loop*.
        """
        get_task_factory_attr(loop)[self._data_attr] = self

    def detach(self, loop):
        """Detach the execution context from *loop*.

        This method has no effect if the context is not attached to *loop*.
        """
        with suppress(KeyError, TaskFactoryError):
            del get_task_factory_attr(loop)[self._data_attr]


def chainmap_copy(data):
    """Context copy function based on :class:`collections.ChainMap`.

    ::

        context = Context(copy_func=chainmap_copy)

    On nested copies, :class:`collections.ChainMap` instances are flattened
    for efficiency purposes.
    """
    if isinstance(data, ChainMap):
        return data.new_child()
    else:
        return ChainMap({}, data)


def get_loop_contexts(loop):
    """Return the list of contexts attached to *loop*.

    ::

        >>> context1 = Context()
        >>> context1.attach(loop)
        >>> context2 = Context()
        >>> context2.attach(loop)
        >>> get_loop_contexts(loop)
        [<Context object at 0x10>, <Context object at 0x20>]
        >>> context2.detach(loop)
        [<Context object at 0x10>]

    Raises :exc:`TaskFactoryError` if the loop is not context-aware, i.e. the
    task factory was not set.
    """
    return list(get_task_factory_attr(loop).values())
