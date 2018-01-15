import asyncio

import pytest
import uvloop

import aiocontext


@pytest.fixture()
def asyncio_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture()
def uvloop_loop():
    loop = uvloop.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(params=['asyncio_loop', 'uvloop_loop'])
def event_loop(request):
    return request.getfuncargvalue(request.param)


@pytest.fixture()
def context():
    return aiocontext.Context()


@pytest.fixture()
def context_loop(context, event_loop):
    aiocontext.wrap_task_factory(event_loop)
    context.attach(event_loop)
    return event_loop
