from __future__ import annotations

from dataclasses import dataclass
from queue import Full, Queue, ShutDown
from threading import Thread

from pycoro import CQE
from pycoro.bus import SQE
from pycoro.io.aio import Completion, Submission


# Submission
@dataclass(frozen=True)
class EchoSubmission:
    data: str

    @property
    def kind(self) -> str:
        return "echo"


# Completion
@dataclass(frozen=True)
class EchoCompletion:
    data: str

    @property
    def kind(self) -> str:
        return "echo"


class EchoSubsystem:
    def __init__(self, size: int = 100, workers: int = 1) -> None:
        self._sq = Queue[SQE[Submission[EchoSubmission], Completion[EchoCompletion]]](size)
        self._workers = workers
        self._threads: list[Thread] = []

    @property
    def size(self) -> int:
        return self._sq.maxsize

    @property
    def kind(self) -> str:
        return "echo"

    def start(self, cq: Queue[tuple[CQE[Completion[EchoCompletion]], str]]) -> None:
        assert len(self._threads) == 0

        for i in range(self._workers):
            t = Thread(target=self.worker, args=(cq,), daemon=True, name=f"echo-worker-{i}")
            t.start()
            self._threads.append(t)

    def shutdown(self) -> None:
        assert len(self._threads) > 0
        self._sq.shutdown()
        for t in self._threads:
            t.join()

        self._threads.clear()
        assert len(self._threads) == 0, "at least one worker must be set."
        self._sq.join()

    def enqueue(self, sqe: SQE[Submission[EchoSubmission], Completion[EchoCompletion]]) -> bool:
        try:
            self._sq.put_nowait(sqe)
        except Full:
            return False
        return True

    def flush(self, time: int) -> None:
        return

    def process(self, sqes: list[SQE[Submission[EchoSubmission], Completion[EchoCompletion]]]) -> list[CQE[Completion[EchoCompletion]]]:
        assert self._workers > 0, "must be at least one worker"
        return [self.execute(sqe) for sqe in sqes]

    def execute(self, sqe: SQE[Submission[EchoSubmission], Completion[EchoCompletion]]) -> CQE[Completion[EchoCompletion]]:
        return CQE(
            Completion(EchoCompletion(sqe.value.v.data)),
            sqe.callback,
        )

    def worker(self, cq: Queue[tuple[CQE[Completion[EchoCompletion]], str]]) -> None:
        while True:
            try:
                sqe = self._sq.get()
            except ShutDown:
                break

            assert sqe.value.v.kind == self.kind

            cq.put((self.execute(sqe), sqe.value.v.kind))
            self._sq.task_done()
