"""Tests for command line interface."""
from click.testing import CliRunner

from aiida_finales.cli import cmd_root


def test_cli():
    """Initial test function."""
    runner = CliRunner()
    runner.invoke(cmd_root, '--help', catch_exceptions=False)
