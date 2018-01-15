Introcution
===========

Prerequistes
------------

AioContext works with Python 3.4 and greater. It is compatible with both
asyncio and uvloop event loops and does not depend on external libraries.

Installation
------------

The recommended way to install packages is to use ``pip`` inside a virtual
environment:

.. code-block:: bash

    $ pip install aiocontext

To install a development version:

.. code-block:: bash

    $ git clone https://github.com/sqreen/AioContext.git
    $ cd aiocontext
    $ pip install -r requirements.txt
    $ pip install -e .

Basic API usage
---------------

This section is a brief introduction to AioContext API.

AioContext allows to store context information inside the asyncio.Task object.
A typical use case for it is to pass information between coroutine calls
without the need to do it explicitly using the called coroutine args.

To create a new context store, instanciate a :class:`aiocontext.Context`
instance::

    from aiocontext import Context
    context = Context()

A context object is a :class:`dict` so you can store any value you want inside.
For example, in a web application, you can share a ``request_id`` between
asynchronous calls with the following code::

    async def print_request():
        print("Request ID:", context.get('request_id', 'unknown'))

    async def handle_request():
        context['request_id'] = 42
        await print_request()

To enable context propagation between tasks (i.e. between calls like
:func:`asyncio.ensure_future`, :func:`asyncio.wait_for`,
:func:`asyncio.gather`, etc.), the task factory of the event loop must be
changed to be made context-aware. This is done by calling
:func:`aiocontext.wrap_task_factory`::

    from aiocontext import wrap_task_factory
    loop = asyncio.get_event_loop()
    wrap_task_factory(loop)

If a custom task factory is already set, this function will "wrap" it with
context management code, so it must be called after
:meth:`asyncio.Loop.set_task_factory`.

Finally, the context must be attached to the event loop::

    context.attach(loop)

The full code looks like::

    import asyncio
    import aiocontext

    context = aiocontext.Context()

    async def print_request():
        print("Request ID:", context.get('request_id', 'unknown'))

    async def handle_request():
        context['request_id'] = 42
        await print_request()

    if __name__ == '__main__':
        loop = asyncio.get_event_loop()
        aiocontext.wrap_task_factory(loop)
        context.attach(loop)
        loop.run_until_complete(handle_request())

Comparison with other solutions
-------------------------------

`aiotask-context`_ was an important source of inspiration and is a more
battle-tested library. It provides a simpler API with a global, unique context.
It does not support overloading custom task factories at the moment.

`aiolocals`_ is another library to track task-local states. It comes with
`aiohttp`_ integration to track HTTP requests. New tasks must be explicitly
spawned with a ``wrap_async`` function to share contexts, which may be
problematic when using libraries.

`tasklocals`_ strives to provide an interface similar to
:func:`threading.local`. It provides no mechanism of context sharing when a
child task is spawned. The project looks abandoned.

In the future, asynchronous context storage could be supported natively in the
Python language. This is discussed in `PEP 550`_ and `PEP 567`_.

.. _aiohttp: https://aiohttp.readthedocs.io/
.. _aiolocals: https://docs.atlassian.com/aiolocals/
.. _aiotask-context: https://github.com/Skyscanner/aiotask-context
.. _tasklocals: https://github.com/vkryachko/tasklocals
.. _PEP 550: https://www.python.org/dev/peps/pep-0550/
.. _PEP 567: https://www.python.org/dev/peps/pep-0567/
