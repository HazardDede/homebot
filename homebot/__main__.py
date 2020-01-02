"""Main application entrypoint."""
import asyncio
import importlib
import logging
import os
import pathlib
import py_compile
import sys

import fire  # type: ignore

from homebot import Orchestrator


logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)


def _assert_config_file(config: str) -> None:
    if not os.path.isfile(config):
        raise FileNotFoundError(f"Configuration '{str(config)}' does not exist.")


class Runner:
    """Homebot app."""

    @staticmethod
    def run(config: str) -> None:
        """
        Runs the homebot with the specified configuration.

        Args:
            config (str): The config to load.
        """
        _assert_config_file(config)
        module_path = os.path.dirname(config)
        sys.path.insert(0, module_path)
        file_name = pathlib.Path(config).stem
        module = importlib.import_module(file_name)

        orchestra = None
        for var in dir(module):
            val = getattr(module, var)
            if isinstance(val, Orchestrator):
                orchestra = val
                break

        if not orchestra:
            raise RuntimeError(f"Configuration '{str(config)}' does not include a "
                               f"Orchestrator.")

        loop = asyncio.get_event_loop()
        loop.run_until_complete(orchestra.run())

    @staticmethod
    def validate(config: str) -> None:
        """
        Validates the specified configuration.
        If the config is valid the validation will be quiet; if the config is broken it
        will complaint.

        Args:
            config (str): The config to validate.
        """
        _assert_config_file(config)

        py_compile.compile(config)


if __name__ == '__main__':
    fire.Fire(Runner)  # pragma: no cover
