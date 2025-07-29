from .. import Point
from ..mapper import Mapper
from .utils.defaults import DefaultInitBundle
from .loader import EnvVarLoader
from .interface import Bot
from .client import RawTurnProcessor, NewClientFromConfig
from concurrent.futures import ThreadPoolExecutor
from typing import Callable
import signal
import sys

def NewDefaultStarter():
    defaultConfig, defaultMapper, defaultInitialPosition = DefaultInitBundle()
    return Starter(defaultInitialPosition, defaultConfig, defaultMapper)

class Starter:
    def __init__(self, initial_position: Point, config: EnvVarLoader, mapper: Mapper):
        self.initial_position = initial_position
        self.config = config
        self.mapper = mapper

    def get_mapper(self):
        return self.mapper

    def set_mapper(self, mapper: Mapper):
        self.mapper = mapper

    def get_initial_position(self):
        return self.initial_position

    def set_initial_position(self, initial_position: Point):
        self.initial_position = initial_position

    def get_config(self):
        return self.config

    def set_config(self, config: EnvVarLoader):
        self.config = config

    def run(self, bot: Bot, on_join: Callable[[], None]):
        lugoClient = NewClientFromConfig(self.config, self.initial_position)
        executor = ThreadPoolExecutor()
        lugoClient.play_as_bot(executor, bot, on_join)
        
        print("We are playing!")
        def signal_handler(_, __):
            print("Stop requested\n")
            lugoClient.stop()
            sys.exit(0)

        signal.signal(signal.SIGINT, signal_handler)
        lugoClient.wait()
        print("bye!")

    def run_just_turn_handler(self, raw_processor: RawTurnProcessor, on_join: Callable[[], None]):
        lugoClient = NewClientFromConfig(self.config, self.initial_position)
        lugoClient.play(raw_processor, on_join).then(lambda: print("all done")).catch(lambda e: print(e))
