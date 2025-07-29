import asyncio

from engin import Engin, Invoke, Supervisor


async def delayed_error_task():
    raise RuntimeError("Process errored")


def supervise(supervisor: Supervisor) -> None:
    supervisor.supervise(delayed_error_task)


async def test_error_in_supervised_task_handled_when_run(caplog):
    engin = Engin(Invoke(supervise))
    await asyncio.wait_for(engin.run(), timeout=0.5)


async def test_error_in_supervised_task_handled_when_start(caplog):
    engin = Engin(Invoke(supervise))
    await asyncio.wait_for(engin.start(), timeout=0.5)
