import contextlib
import traceback
from concurrent.futures import ThreadPoolExecutor

import grpc
import time
from typing import Any, Iterator

from ... import GameSnapshot, Remote, RemoteStub, log_with_time
from src.lugo4py.protos.rl_assistant_pb2 import RLSessionConfig
from src.lugo4py.protos.rl_assistant_pb2_grpc import RLAssistantStub
from src.lugo4py.rl.src.training_controller import TrainingCrl
from src.lugo4py.rl.src.contracts import BotTrainer, TrainingFunction

class Gym:

    def __init__(self, executor: ThreadPoolExecutor,  grpc_address):

        channel = grpc.insecure_channel(grpc_address)

        # Block until channel is ready (or timeout)
        grpc.channel_ready_future(channel).result(timeout=5)

        self.remote = RemoteStub(channel)
        self.assistant = RLAssistantStub(channel)
        self.executor = executor


    def start(self, trainer: BotTrainer, training_function: TrainingFunction) -> None:

        training_ctrl = TrainingCrl(trainer, self.remote, self.assistant)

        response_iterator = self.assistant.StartSession(request=RLSessionConfig())


        self._training_routine = self.executor.submit(self._response_watcher, response_iterator)


        time.sleep(2)
        training_function(training_ctrl)

    def _response_watcher(
        self,
        response_iterator: Iterator[GameSnapshot],
        ) -> None:
        try:
            for snapshot in response_iterator:
                log_with_time(f"still alive")

            # self._play_finished.set()
        except grpc.RpcError as e:
            if grpc.StatusCode.INVALID_ARGUMENT == e.code():
                log_with_time(f"did not connect to RL session {e.details()}")
        except Exception as e:
            log_with_time(f"internal error processing RL session: {e}")
            traceback.print_exc()
