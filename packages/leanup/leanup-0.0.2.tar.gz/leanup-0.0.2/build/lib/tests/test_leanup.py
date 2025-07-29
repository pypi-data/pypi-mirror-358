#!/usr/bin/env python

"""Tests for `leanup` package."""

import pytest

def test_leanup_import():
    """Test if the package can be imported."""
    from leanup import __version__
    print(f"LeanUp version: {__version__}")