"""
Analysis of waveguide data.

This module provides functions to analyze waveguide data, including
calculating effective index, group index, and dispersion and losses.
"""

from .Data_class import Data
import scipy.signal as signal
import matplotlib.pyplot as plt
import numpy as np


def find_data_peaks(
    my_data: Data,
    data_key: str = "Optical power TE, W",
    reverse: bool = False,
    **kwargs,
) -> Data:
    """
    Find peaks in the optical power data and return a Data object with the peaks.

    Args:
        my_data (Data): The Data object containing optical power data.
        data_key(str): The key for the optical power data in the Data object.
        reverse (bool): If True, find valleys instead of peaks. Default is False.
        **kwargs: Additional keyword arguments for peak finding.

    Returns:
        Data: A new Data object containing the peaks found in the optical power data.

    """
    # Extract the optical power data
    optical_power = my_data.get_data(data_key)
    wavelengths = my_data.get_data("Wavelength, nm")

    if optical_power is None or wavelengths is None:
        raise ValueError(
            "Optical power and wavelength data are required for peak finding."
        )

    # Find peaks
    if reverse:
        peaks, _ = signal.find_peaks(-optical_power, **kwargs)
    else:
        peaks, _ = signal.find_peaks(optical_power, **kwargs)

    # Create a new Data object with the peaks
    metadata = {"Measurement": "Peak Finding"}
    data_out = {
        "Wavelength, nm": wavelengths[peaks],
        data_key: optical_power[peaks],
        "peaks": peaks,
    }

    return Data(data=data_out, metadata=metadata)


def calculate_group_index(
    my_data: Data,
    data_key: str = "Optical power TE, W",
    length_wg: float = 4.6e6,
    N_average=10,
) -> Data:
    """
    Calculate the group index from the fabry perot interferences.

    Args:
        my_data (Data): The Data object containing optical power data.
        data_key (str): The key for the optical power data in the Data object.
        length_wg (float): The length of the waveguide in nanometers. Default is 4.6e6.
        N_average (int): The number of points to average for the group index
            calculation. Default is 10.

    Returns:
        Data: A new Data object with the group index.

    """
    # Extract the optical power data
    optical_power = my_data.get_data(data_key)
    wavelengths = my_data.get_data("Wavelength, nm")

    if optical_power is None or wavelengths is None:
        raise ValueError(
            "Optical power and wavelength data are required for peak finding."
        )

    # Find peaks using the find_data_peaks function
    prominence = (np.max(optical_power) - np.min(optical_power)) * 0.1
    peaks = find_data_peaks(my_data, data_key=data_key, prominence=prominence)
    peaks = peaks.get_data("peaks")

    # calculate the group index from the distances between the peaks
    ng = (
        N_average
        * 0.5
        * wavelengths[peaks[N_average:]]
        * wavelengths[peaks[:-N_average]]
        / (
            length_wg
            * (wavelengths[peaks[N_average:]] - wavelengths[peaks[:-N_average]])
        )
    )

    # Calculate the average wavelength for the group index calculation
    wl = 0.5 * (wavelengths[peaks[N_average:]] + wavelengths[peaks[:-N_average]])

    # Create a new Data object with the group index
    metadata = {"Measurement": "Group Index Calculation"}
    data_out = {
        "Wavelength, nm": wl,
        "Group index": ng,
    }

    return Data(data=data_out, metadata=metadata)


def calculate_waveguide_losses(
    my_data: Data, data_key: str = "Optical power TE, W", reflection_coeff: float = 0.32
) -> Data:
    """
    Calculate the waveguide losses in dB.

    Calculate the waveguide losses from the optical power data using Fabry-Perot
    interference, using all intervals at once.

    Args:
        my_data (Data): The Data object containing optical power data.
        data_key (str): The key for the optical power data in the Data object.
        reflection_coeff (float): Reflection coefficient at the facets.

    Returns:
        Data: A new Data object with the waveguide losses (wavelength, loss).

    """
    optical_power = my_data.get_data(data_key)
    wavelengths = my_data.get_data("Wavelength, nm")
    if optical_power is None or wavelengths is None:
        raise ValueError(
            "Optical power and wavelength data are required for loss calculation."
        )

    # Find peaks and valleys (dips)
    prominence = (np.max(optical_power) - np.min(optical_power)) * 0.1
    peaks = find_data_peaks(my_data, data_key=data_key, prominence=prominence).get_data(
        "peaks"
    )
    dips = find_data_peaks(
        my_data, data_key=data_key, reverse=True, prominence=prominence
    ).get_data("peaks")

    # Sort peaks and dips
    peaks = np.sort(peaks)
    dips = np.sort(dips)

    # Use all valid intervals: for each dip, find the closest left and right peaks
    left_peaks = np.searchsorted(peaks, dips, side="right") - 1
    right_peaks = left_peaks + 1
    valid = (left_peaks >= 0) & (right_peaks < len(peaks))
    left_peaks = peaks[left_peaks[valid]]
    right_peaks = peaks[right_peaks[valid]]
    dips = dips[valid]

    # Calculate contrast and loss for all intervals at once
    peak_avg = 0.5 * (optical_power[left_peaks] + optical_power[right_peaks])
    dip_intensity = optical_power[dips]
    contrast = peak_avg / dip_intensity
    sqrt_contrast = np.sqrt(contrast)
    wl = 0.5 * (wavelengths[left_peaks] + wavelengths[right_peaks])

    # Only keep intervals where sqrt_contrast > 1 and dip_intensity > 0
    mask = (sqrt_contrast > 1) & (dip_intensity > 0)
    loss_array = np.log(
        1 / reflection_coeff * (sqrt_contrast[mask] - 1) / (sqrt_contrast[mask] + 1)
    ) * (-4.3429)
    wl_array = wl[mask]

    data_out = {
        "Wavelength, nm": wl_array,
        "Loss, dB": loss_array,
    }
    metadata = {"Measurement": "Propagation Loss, dB"}
    return Data(data=data_out, metadata=metadata)


def calculate_peak_height_waveguide_loss(
    my_data: Data,
    data_key: str = "Optical power TE, W",
    reflection_coeff: float = 0.32,
) -> Data:
    """
    Calculate waveguide losses and peak height with detailed metadata.

    Waveguide losses are calculated by finding the maximum loss (peak),
    estimating the noise floor as the given percentile
    of the loss distribution, and returning the difference (peak height)
    along with the loss spectrum.

    Args:
        my_data (Data): The Data object containing optical power data.
        data_key (str): The key for the optical power data in the Data object.
        reflection_coeff (float): Reflection coefficient at the facets.

    Returns:
        Data: A new Data object with wavelength, loss, and detailed peak/noise metadata.

    """
    # Use the existing loss calculation function
    loss_data = calculate_waveguide_losses(
        my_data, data_key=data_key, reflection_coeff=reflection_coeff
    )
    wl_array = loss_data.get_data("Wavelength, nm")
    loss_array = loss_data.get_data("Loss, dB")

    if wl_array is None or loss_array is None:
        raise ValueError(
            "Optical power and wavelength data are required for loss calculation."
        )

    # Find the maximum loss (peak) and estimate the noise floor (percentile)
    if loss_array is not None and len(loss_array) > 0:
        max_idx = int(np.argmax(loss_array))
        max_loss = loss_array[max_idx]
        max_wl = wl_array[max_idx]
        noise_floor = np.percentile(loss_array, 30)
        # Find the closest wavelength to the peak with value near the noise floor
        noise_idx = int(np.argmin(np.abs(loss_array - noise_floor)))
        noise_wl = wl_array[noise_idx]
        peak_height = max_loss - noise_floor
        pos_end_highpeak = [float(max_wl), float(max_loss)]
        pos_start_lowpeak = [float(noise_wl), float(noise_floor)]
    else:
        peak_height = 0
        pos_end_highpeak = [None, None]
        pos_start_lowpeak = [None, None]

    data_out = {
        "Wavelength, nm": wl_array,
        "Loss, dB": loss_array,
    }
    metadata = {
        "Measurement": "Peak height waveguide loss, dB",
    }
    extraction_points = {
        "pos_start_lowpeak": [pos_start_lowpeak, noise_floor],
        "pos_end_highpeak": [pos_end_highpeak, max_loss]
    }
    extraction_value = {
        "peak_height": peak_height,
    }

    return Data(data=data_out,
                metadata=metadata,
                extraction_point=extraction_points,
                extraction_value=extraction_value)


def find_peaks_plot(my_data: Data, figure=None) -> object:
    """
    Find peaks in the optical power data and plot them.

    Args:
        my_data (Data): The Data object containing optical power data.
        figure: matplotlib Figure object to plot on. If None, create new figure.

    Returns:
        The matplotlib Figure object used for plotting.

    """
    # Extract the optical power data
    optical_power = my_data.get_data("Optical power TE, W")
    wavelengths = my_data.get_data("Wavelength, nm")

    if optical_power is None or wavelengths is None:
        raise ValueError(
            "Optical power and wavelength data are required for peak finding."
        )

    # Find peaks
    peaks, _ = signal.find_peaks(optical_power, distance=10, width=5)

    fig = figure
    if fig is None:
        fig = plt.figure(figsize=(10, 6))
    ax = fig.gca()
    ax.plot(wavelengths, optical_power, label="Optical Power TE")
    ax.plot(wavelengths[peaks], optical_power[peaks], "x", label="Peaks")
    ax.set_xlabel("Wavelength (nm)")
    ax.set_ylabel("Optical Power (W)")
    ax.set_title("Peak Finding in Optical Power Data")
    ax.legend()
    ax.grid()
    return fig
