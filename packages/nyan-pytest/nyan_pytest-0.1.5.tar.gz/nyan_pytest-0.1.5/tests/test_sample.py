"""Sample tests to demonstrate the nyan-cat reporter."""

def test_addition():
    """Test addition."""
    assert 1 + 1 == 2

def test_subtraction():
    """Test subtraction."""
    assert 2 - 1 == 1

def test_multiplication():
    """Test multiplication."""
    assert 2 * 2 == 4

def test_division():
    """Test division."""
    assert 4 / 2 == 2

def test_failing():
    """A failing test to demonstrate reporter handling failures.
    
    This test is marked with xfail so it doesn't cause CI failures.
    """
    import pytest
    pytest.xfail("This test is designed to fail to demonstrate reporter handling")

def test_skipped():
    """A skipped test to demonstrate reporter handling skips."""
    import pytest
    pytest.skip("Skipping this test to demonstrate reporter handling skips")