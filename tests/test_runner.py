import os

from homebot.__main__ import Runner

DUMMY_CONFIG = os.path.join(os.path.dirname(__file__), 'resources/config.py')


def test_validate():
    dut = Runner()
    dut.validate(DUMMY_CONFIG)


def test_run():
    dut = Runner()
    dut.run(DUMMY_CONFIG)
