"""
Unit tests for the math_utils module.

This module contains tests for the mathematical utilities provided by.
"""

import re

import pytest

import sp_brew.utils_math as math_utils


def test_bisection_method():
    """Test the bisection_method function."""

    # Define a simple function with a root
    def f(x):
        return x**2 - 4  # Root at x = 2

    # Test the bisection method
    root = math_utils.bisection_method(f, 0, 3)
    assert abs(root - 2) < 1e-6, f"Expected root close to 2, got {root}"


def test_bisection_method_no_root():
    """Test the bisection_method function with no root in the interval."""

    # Define a function with no root in the interval
    def f(x):
        return x**2 + 1  # No real roots

    # Expect a ValueError when trying to find a root
    with pytest.raises(
        ValueError, match=re.escape("f(a) and f(b) must have opposite signs")
    ):
        math_utils.bisection_method(f, 0, 1)


def test_bisection_method_max_iter():
    """Test the bisection_method function with maximum iterations reached."""

    # Define a function that converges slowly
    def f(x):
        return x - 1  # Root at x = 1

    # Expect a ValueError when maximum iterations are reached
    with pytest.raises(
        ValueError,
        match=re.escape("Maximum number of iterations reached no convergence"),
    ):
        math_utils.bisection_method(f, 0, 6, max_iter=2)
