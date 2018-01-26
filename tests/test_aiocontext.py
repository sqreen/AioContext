import asyncio
import traceback

import pytest

from aiocontext import (Context, EventLoopError, TaskContextError,
                        TaskFactoryError, chainmap_copy, get_loop_contexts,
                        unwrap_task_factory, wrap_task_factory)


def _wrapped_task_factory(event_loop):
    try:
        get_loop_contexts(event_loop)
    except TaskFactoryError:
        return False
    else:
        return True


class CustomTask(asyncio.Task):
    pass


def custom_task_factory(loop, coro):
    return CustomTask(coro, loop=loop)


def test_wrap_task_factory(event_loop):
    assert not _wrapped_task_factory(event_loop)
    wrap_task_factory(event_loop)
    assert _wrapped_task_factory(event_loop)


def test_wrap_task_factory_many(event_loop):
    assert not _wrapped_task_factory(event_loop)
    for _ in range(3):
        wrap_task_factory(event_loop)
    assert _wrapped_task_factory(event_loop)


def test_wrap_task_factory_custom(event_loop):
    event_loop.set_task_factory(custom_task_factory)
    assert not _wrapped_task_factory(event_loop)
    wrap_task_factory(event_loop)
    assert _wrapped_task_factory(event_loop)
    task = event_loop.create_task(asyncio.sleep(1))
    task.cancel()
    assert isinstance(task, CustomTask)


def test_unwrap_task_factory(event_loop):
    wrap_task_factory(event_loop)
    assert _wrapped_task_factory(event_loop)
    unwrap_task_factory(event_loop)
    assert not _wrapped_task_factory(event_loop)


def test_unwrap_task_factory_many(event_loop):
    wrap_task_factory(event_loop)
    assert _wrapped_task_factory(event_loop)
    for _ in range(3):
        unwrap_task_factory(event_loop)
        assert not _wrapped_task_factory(event_loop)


def test_unwrap_task_factory_custom(event_loop):
    event_loop.set_task_factory(custom_task_factory)
    wrap_task_factory(event_loop)
    assert _wrapped_task_factory(event_loop)
    unwrap_task_factory(event_loop)
    assert not _wrapped_task_factory(event_loop)
    assert event_loop.get_task_factory() is custom_task_factory


@pytest.mark.asyncio
@asyncio.coroutine
def test_wrap_task_factory_traceback(context, context_loop):
    context_loop.set_debug(True)
    task = context_loop.create_task(asyncio.sleep(1))
    task.cancel()
    assert isinstance(task._source_traceback, traceback.StackSummary)


class TestContext:

    def test_copy_func(self):
        context = Context()
        assert context.copy_func is dict
        context = Context(copy_func=chainmap_copy)
        assert context.copy_func is chainmap_copy

    @pytest.mark.asyncio
    @asyncio.coroutine
    def test_get_data(self, context, context_loop):
        context['key1'] = 'value1'
        assert context.get_data() == {'key1': 'value1'}

        @asyncio.coroutine
        def coro():
            context['key2'] = 'value2'

        task = context_loop.create_task(coro())
        yield from task
        assert context.get_data(task) == {'key1': 'value1', 'key2': 'value2'}
        assert context.get_data() == {'key1': 'value1'}

    @pytest.mark.asyncio
    @asyncio.coroutine
    def test_getitem(self, context, context_loop):
        context['key1'] = 'value'
        assert context['key1'] == 'value'
        with pytest.raises(KeyError):
            context['key2']

    @pytest.mark.asyncio
    @asyncio.coroutine
    def test_setitem(self, context, context_loop):
        context['key'] = 'value1'
        assert context['key'] == 'value1'
        context['key'] = 'value2'
        assert context['key'] == 'value2'

    @pytest.mark.asyncio
    @asyncio.coroutine
    def test_delitem(self, context, context_loop):
        with pytest.raises(KeyError):
            del context['key']
        context['key'] = 'value'
        del context['key']
        assert 'key' not in context

    @pytest.mark.asyncio
    @asyncio.coroutine
    def test_iter(self, context, context_loop):
        context['key1'] = 'value1'
        context['key2'] = 'value2'
        assert list(sorted(context)) == ['key1', 'key2']

    @pytest.mark.asyncio
    @asyncio.coroutine
    def test_len(self, context, context_loop):
        context['key1'] = 'value1'
        context['key2'] = 'value2'
        assert len(context) == 2

    def test_missing_event_loop(self, context):
        with pytest.raises(EventLoopError):
            context.get_data()
        with pytest.raises(EventLoopError):
            context['key']
        with pytest.raises(EventLoopError):
            context['key'] = 'value'
        with pytest.raises(EventLoopError):
            del context['key']
        with pytest.raises(EventLoopError):
            list(context)
        with pytest.raises(EventLoopError):
            len(context)

    @pytest.mark.asyncio
    @asyncio.coroutine
    def test_missing_task_context(self, context, event_loop):
        with pytest.raises(TaskContextError):
            context.get_data()
        with pytest.raises(TaskContextError):
            context['key']
        with pytest.raises(TaskContextError):
            context['key'] = 'value'
        with pytest.raises(TaskContextError):
            del context['key']
        with pytest.raises(TaskContextError):
            list(context)
        with pytest.raises(TaskContextError):
            len(context)

    def test_attach(self, event_loop):
        wrap_task_factory(event_loop)
        assert len(get_loop_contexts(event_loop)) == 0
        context1 = Context()
        context1.attach(event_loop)
        assert len(get_loop_contexts(event_loop)) == 1
        context2 = Context()
        context2.attach(event_loop)
        assert len(get_loop_contexts(event_loop)) == 2
        context2.attach(event_loop)
        assert len(get_loop_contexts(event_loop)) == 2

    def test_detach(self, event_loop):
        wrap_task_factory(event_loop)
        context1 = Context()
        context1.attach(event_loop)
        context2 = Context()
        context2.attach(event_loop)
        assert len(get_loop_contexts(event_loop)) == 2
        context2.detach(event_loop)
        assert len(get_loop_contexts(event_loop)) == 1
        context2.detach(event_loop)
        assert len(get_loop_contexts(event_loop)) == 1


def test_chainmap_copy():
    data1 = {'key1': 'value1'}
    data2 = chainmap_copy(data1)
    data2['key2'] = 'value2'
    data3 = chainmap_copy(data2)
    data3['key3'] = 'value3'
    assert data1 == {'key1': 'value1'}
    assert data2 == {'key1': 'value1', 'key2': 'value2'}
    assert data3 == {'key1': 'value1', 'key2': 'value2', 'key3': 'value3'}
    assert len(data3.maps) == 3


def test_get_loop_contexts(context, event_loop):
    with pytest.raises(TaskFactoryError):
        get_loop_contexts(event_loop)
    wrap_task_factory(event_loop)
    assert get_loop_contexts(event_loop) == []
    context.attach(event_loop)
    assert get_loop_contexts(event_loop) == [context]
