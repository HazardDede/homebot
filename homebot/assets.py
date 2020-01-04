"""Utility methods related to asset management."""

import os
from pathlib import Path
from typing import List, Optional

from homebot.utils import Singleton, AutoStrMixin, LogMixin

ASSETS_DIR_ENV_OVERRIDE = 'ASSETS_DIR'
TEMPLATES_DIR_ENV_OVERRIDE = 'TEMPLATES_DIR'


class AssetDirectoryNotFoundError(NotADirectoryError):
    """Is raised when no assets directory could not be resolved."""

    DEFAULT_MESSAGE = "The asset directory could not be resolved. Probed:\n{}"

    def __init__(self, probe_list: List[str]):
        super().__init__(self.DEFAULT_MESSAGE.format(probe_list))


class TemplateDirectoryNotFoundError(AssetDirectoryNotFoundError):
    """Is raised when the template directory could not be resolved."""

    DEFAULT_MESSAGE = "The template directory could not be resolved. Probed:\n{}"


class AssetManager(AutoStrMixin, LogMixin, metaclass=Singleton):
    """Asset and template manager."""
    def __init__(self) -> None:
        self.base_path: Optional[str] = None

    def assets_dir(self) -> Path:
        """
        Return the absolute path to the asset directory.
        1.  Check if the assets environment variable is set; if yes -> take this dir
        2.1 Check the path where the config is located for an assets directory
        2.2 Check the current working directory for an assets directory
        """
        probe_list = []
        if ASSETS_DIR_ENV_OVERRIDE in os.environ:
            probe_list.append(os.environ[ASSETS_DIR_ENV_OVERRIDE])
        else:
            if self.base_path:
                probe_list.append(os.path.join(self.base_path, 'assets'))
            probe_list.append(os.path.join(os.getcwd(), 'assets'))

        probe_list = [os.path.abspath(probe) for probe in probe_list]
        self.logger.debug("Probing for assets directory: %s", str(probe_list))

        for probe in probe_list:
            if os.path.isdir(probe):
                self.logger.debug("Asset directory is: %s", str(probe))
                return Path(probe)

        raise AssetDirectoryNotFoundError(probe_list)

    def templates_dir(self) -> Path:
        """
        Return the absolute path to the template directory.
        1.  Check if the template directory environment variable is set; if yes -> take it
        2.1 Check if the assets directory does contain a templates directory
        2.2 Check if the path where the config is located does contain a templates directory
        2.3 Check if the current working directory does contain a templates directory
        """
        probe_list = []
        if TEMPLATES_DIR_ENV_OVERRIDE in os.environ:
            probe_list.append(os.environ[TEMPLATES_DIR_ENV_OVERRIDE])
        else:
            probe_list.append(os.path.join(str(self.assets_dir()), 'templates'))
            if self.base_path:
                probe_list.append(os.path.join(self.base_path, 'templates'))
            probe_list.append(os.path.join(os.getcwd(), 'templates'))

        probe_list = [os.path.abspath(probe) for probe in probe_list]
        self.logger.debug("Probing for template directory: %s", str(probe_list))

        for probe in probe_list:
            if os.path.isdir(probe):
                self.logger.debug("Template directory is: %s", str(probe))
                return Path(probe)

        raise TemplateDirectoryNotFoundError(probe_list)

    def template_path(self, template_name: str) -> Path:
        """Return the absolute path to the passed template name."""
        file_path = self.templates_dir().joinpath(template_name)
        if not file_path.is_file():
            raise FileNotFoundError("Template '{}' is not a file".format(str(file_path)))

        self.logger.debug("Template file is: %s", str(file_path))
        return file_path
