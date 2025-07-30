from __future__ import annotations

import random
from dataclasses import dataclass
from queue import Full

from pycoro import Computation, Promise, Pycoro
from pycoro.io import AIO
from pycoro.io.aio import Completion, Submission
from pycoro.io.subsystems.echo import EchoCompletion, EchoSubmission, EchoSubsystem
from pycoro.io.subsystems.store import StoreCompletion, StoreSubmission, Transaction
from pycoro.io.subsystems.store.sqlite import StoreSqliteSubsystem

type Command = ReadCommand


@dataclass(frozen=True)
class ReadCommand:
    id: int


def read_handler(cmd: ReadCommand) -> ReadResult:
    return ReadResult(cmd.id)


type Result = ReadResult


@dataclass(frozen=True)
class ReadResult:
    id: int


def foo(n: int) -> Computation[Submission[EchoSubmission | StoreSubmission[Command]], Completion[EchoCompletion | StoreCompletion[Result]]]:
    p: Promise | None = None
    for _ in range(n):
        p = yield Submission(StoreSubmission(Transaction([ReadCommand(n) for _ in range(n)])))

    assert p is not None
    v: Completion = yield p
    assert isinstance(v, StoreCompletion)
    assert len(v.results) == n
    return v


def bar(n: int, data: str) -> Computation[Submission[EchoSubmission | StoreSubmission[Command]], Completion[EchoCompletion | StoreCompletion[Result]]]:
    p: Promise | None = None
    for _ in range(n):
        p = yield Submission(EchoSubmission(data))

    assert p is not None
    v = yield p
    return Completion(EchoCompletion(v))


def _run(seed: int) -> None:
    r = random.Random(seed)

    echo_subsystem_size = r.randint(1, 100)
    store_sqlite_subsystem_size = r.randint(1, 100)
    io_size = r.randint(1, 100)

    if store_sqlite_subsystem_size > io_size:
        return

    if echo_subsystem_size > io_size:
        return

    echo_subsystem = EchoSubsystem(echo_subsystem_size, r.randint(1, 3))
    store_sqlite_subsystem = StoreSqliteSubsystem(store_sqlite_subsystem_size, r.randint(1, 100))
    store_sqlite_subsystem.add_command_handler(ReadCommand, read_handler)

    io = AIO[EchoSubmission | StoreSubmission[Command], EchoCompletion | StoreCompletion[Result]](io_size)

    io.attach_subsystem(echo_subsystem)
    io.attach_subsystem(store_sqlite_subsystem)
    s = Pycoro(io, r.randint(1, 100), r.randint(1, 100))

    n_coros = r.randint(1, 100)
    try:
        for _ in range(n_coros):
            match r.randint(0, 1):
                case 0:
                    s.add(bar(r.randint(1, 100), "hi"))
                case 1:
                    s.add(foo(r.randint(1, 100)))
                case _:
                    raise NotImplementedError
    except Full:
        return

    s.start()
    s.loop()
    assert s.done()
    return


def test_fuzz() -> None:
    for _ in range(100):
        seed = random.randint(1, 100)
        _run(seed)
