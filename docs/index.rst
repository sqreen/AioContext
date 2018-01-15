Welcome to AioContext
=====================

AioContext is a Python library to store context information within the
:class:`asyncio.Task` object::

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

Features:

* Support both asyncio and uvloop event loops.
* Support custom loop task factories.
* Manage several execution contexts.

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   introduction
   api
   changelog

If you can’t find the information you’re looking for, have a look at the index
or try to find it using the search function:

* :ref:`genindex`
* :ref:`search`
