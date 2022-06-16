# -*- coding: utf-8 -*-
"""Topmost command line, kept separate to prevent import cycles."""

import click


@click.group('aiida-finale')
def cmd_root():
    """Command line interface for aiida-finale."""
