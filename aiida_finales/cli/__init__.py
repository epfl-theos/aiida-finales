"""Module for the command line interface.

Import here all groups that directly inherit from root.
"""
from .client import cmd_client
from .root import cmd_root
from .test import cmd_test

__all__ = [
    'cmd_client',
    'cmd_root',
    'cmd_test',
]
