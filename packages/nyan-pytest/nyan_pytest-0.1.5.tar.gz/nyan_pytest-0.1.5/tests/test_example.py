"""Example tests to demonstrate the nyan-pytest plugin."""

import time
import pytest


def test_passing():
    """A passing test."""
    assert True


def test_another_passing():
    """Another passing test."""
    time.sleep(0.1)  # Small delay to see the animation
    assert 1 + 1 == 2


def test_slow_passing():
    """A slow passing test to see the animation."""
    time.sleep(0.2)  # Longer delay
    assert "nyan" in "nyan-cat"


def test_skipped():
    """A skipped test."""
    import pytest
    pytest.skip("This test is skipped")


@pytest.mark.xfail
def test_expected_failure():
    """A test expected to fail."""
    assert False