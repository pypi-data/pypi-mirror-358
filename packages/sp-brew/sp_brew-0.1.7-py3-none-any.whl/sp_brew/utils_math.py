"""
Define functions used for mathematical operations and data processing in.

This module contains mathematical utilities such as root finding and signal
processing for use throughout the package.
"""

import numpy as np
from scipy.constants import c

######################################################################
#  ############################### MATH FUNCTION #####################
######################################################################


def bisection_method(f, a, b, tol=1e-6, max_iter=100) -> float:
    """
    Find a root of the function f(x) using the bisection method.

    Args:
        f: The function to find the root of.
        a: The left endpoint of the interval.
        b: The right endpoint of the interval.
        tol: The desired tolerance for the root.
        max_iter: The maximum number of iterations to perform.

    Returns:
        The approximate root of the function.

    Raises:
        ValueError: If f(a) and f(b) do not have opposite signs, or if the
            maximum number of iterations is reached without convergence.

    """
    if f(a) * f(b) >= 0:
        raise ValueError("f(a) and f(b) must have opposite signs")

    for i in range(max_iter):
        c = (a + b) / 2
        if abs(f(c)) < tol:
            return c
        elif f(a) * f(c) < 0:
            b = c
        else:
            a = c
    raise ValueError("Maximum number of iterations reached no convergence")


def OFDR_fft(signal, wl_arr, ng):
    """
    Perform Optical Frequency-Domain Reflectometry (OFDR) FFT.

    OFDR is a technique used for characterization of small on-chip reflections
    from waveguide crossings, transitions, and butt-joints. It is used to map
    the distribution of reflections in the spatial domain.
    OFDR can be conducted in transmission or reflection.

    The output signals are recorded by a power meter (detector) when sweeping
    the tunable laser. The script takes the raw data and performs a Fourier
    transform to return:
        1. a plot of the raw data
        2. FFT spectrum over relative intensity against cavity length

    Args:
        signal: The input signal as a NumPy array.
        wl_arr: Wavelength sweep (nm) as a NumPy array.
        ng: Group index of the waveguide.

    Returns:
        tuple: (L, rel_pwr)
            L (np.ndarray): Cavity length [mm].
            rel_pwr (np.ndarray): Relative power [dB].

    """
    # Fourier transform of power
    wl_arr = wl_arr * 1e-06  # units mm (scale of the PIC)
    signal_fr = np.abs(np.fft.fft(signal))
    signal_fr = np.fft.fftshift(signal_fr)

    # Normalize and convert to dB scale
    maxP = np.max(signal_fr)
    rel_pwr = 10 * np.log10(signal_fr / maxP)

    nX = len(wl_arr)
    print(nX)
    f_max = c / (wl_arr[nX - 1])
    f_min = c / wl_arr[0]
    freq = np.linspace(f_max, f_min, nX)

    # Calculate cavity length[mm]
    df = np.abs(freq[0] - freq[1])  # Calculate frequency difference
    sfreq = 1 / df
    L = c / ng * (sfreq / 2) * np.linspace(0, 1, nX)
    L = L - (np.max(L / 2.0))

    return (L, rel_pwr)
