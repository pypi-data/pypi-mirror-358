# note: normally we want to import from src BUT in this case we need the installed version to properly test it!!
import os
import subprocess

from sassquatch.__about__ import __version__
from sassquatch.core import sass_binary, show_versions


def test_binary_exists(capsys):
    path = sass_binary()

    assert path.exists()

    sass_version: str = subprocess.check_output(
        f"{path} --version", shell=True, text=True
    ).strip()

    show_versions()
    stdout = capsys.readouterr().out

    assert __version__ in stdout
    assert sass_version in stdout
