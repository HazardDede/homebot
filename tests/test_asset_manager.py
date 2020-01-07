import os

import pytest
from argresolver.utils import modified_environ

from homebot import AssetManager
from homebot.assets import AssetDirectoryNotFoundError, TemplateDirectoryNotFoundError, SecretNotFoundError


def test_singleton_instance():
    dut1 = AssetManager()
    dut2 = AssetManager()

    assert dut1 == dut2
    dut2.base_path = "foo"
    assert dut1.base_path == 'foo'


def test_asset_dir():
    dut = AssetManager()
    base_path = os.path.join(os.path.dirname(__file__), 'resources')
    dut.base_path = base_path
    assert str(dut.assets_dir()) == os.path.join(base_path, 'assets')

    with modified_environ(ASSETS_DIR=base_path):
        dut.base_path = None
        assert str(dut.assets_dir()) == os.path.join(base_path)

    with modified_environ(ASSETS_DIR="i do not exist"):
        with pytest.raises(AssetDirectoryNotFoundError):
            dut.assets_dir()


def test_secret():
    dut = AssetManager()
    with modified_environ('token', 'not_here', TOKEN='the_token'):
        assert dut.secret('token') == 'the_token'
        assert dut.secret('TOKEN') == 'the_token'
        with pytest.raises(SecretNotFoundError, match="The secret 'not_here' could not be resolved."):
            dut.secret('not_here')


def test_template_dir():
    dut = AssetManager()
    base_path = os.path.join(os.path.dirname(__file__), 'resources')
    dut.base_path = base_path
    assert str(dut.templates_dir()) == os.path.join(base_path, 'assets/templates')

    with modified_environ(TEMPLATES_DIR=base_path):
        dut.base_path = None
        assert str(dut.templates_dir()) == os.path.join(base_path)

    with modified_environ(TEMPLATES_DIR="i do not exist"):
        with pytest.raises(TemplateDirectoryNotFoundError):
            dut.templates_dir()


def test_template_path():
    dut = AssetManager()
    dut.base_path = os.path.join(os.path.dirname(__file__), 'resources')
    assert str(dut.template_path('tpl.json')) == os.path.join(dut.base_path, 'assets/templates/tpl.json')

    with pytest.raises(FileNotFoundError):
        dut.template_path('not_there.json')
