"""Module for the command line interface.

Import here all groups that directly inherit from root.
"""
from .root import cmd_root
from .tenant import cmd_tenant
from .test import cmd_test

__all__ = [
    'cmd_tenant',
    'cmd_root',
    'cmd_test',
]
