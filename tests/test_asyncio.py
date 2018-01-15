import asyncio

import pytest


@asyncio.coroutine
def _check_update_context(context):
    assert context == {'key1': 'value1'}
    context['key1'] = 'value2'
    context['key2'] = 'value2'
    assert context == {'key1': 'value2', 'key2': 'value2'}


@pytest.mark.asyncio
@asyncio.coroutine
def test_ensure_future(context, context_loop):
    context['key1'] = 'value1'
    yield from asyncio.ensure_future(_check_update_context(context))
    assert context == {'key1': 'value1'}


@pytest.mark.asyncio
@asyncio.coroutine
def test_wait_for(context, context_loop):
    context['key1'] = 'value1'
    yield from asyncio.wait_for(_check_update_context(context), 1)
    assert context == {'key1': 'value1'}


@pytest.mark.asyncio
@asyncio.coroutine
def test_gather(context, context_loop):
    context['key1'] = 'value1'
    yield from asyncio.gather(_check_update_context(context))
    assert context == {'key1': 'value1'}
