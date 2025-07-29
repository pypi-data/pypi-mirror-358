"""
Analysis of waveguide data.

This module provides functions to analyze waveguide data, including
calculating effective index, group index, and dispersion and losses.
"""

from .Data_class import Data
import scipy.signal as signal
import matplotlib.pyplot as plt


def find_data_peaks(my_data : Data,data_key:str="Optical power TE, W",**kwargs)-> Data:
    """
    Find peaks in the optical power data and return a Data object with the peaks.

    Args:
        my_data (Data): The Data object containing optical power data.
        data_key(str): The key for the optical power data in the Data object.
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
    peaks, _ = signal.find_peaks(optical_power, **kwargs)

    # Create a new Data object with the peaks
    metadata = {"Measurement": "Peak Finding"}
    data_out = {
        "Wavelength, nm": wavelengths[peaks],
        "Optical Power TE, W": optical_power[peaks],
    }

    results=Data(data=data_out, metadata=metadata)

    my_data.add_analysis(key="peaks", value=results)

    return my_data

def calculate_group_index(my_data: Data, length_wg:float=4.6e6, N_average=10) -> Data:
    """
    Calculate the group index from the fabry perot interferences.

    Args:
        my_data (Data): The Data object containing effective index data.
        length_wg (float): The length of the waveguide in nanometers. Default is 4.6e6.
        N_average (int): The number of points to average for the group index
            calculation. Default is 100.

    Returns:
        Data: A new Data object with the group index.

    """
    # Placeholder for actual implementation
    metadata = {"Measurement": "Group Index Calculation"}

    # TODO check that the data contains the necessary keys
    # ( or is the right type of measurement)
    # step one find peaks and their positions let's use the scipy function
    peaks, _ = signal.find_peaks(
        my_data.get_data("Optical power TE, W"),
        distance=10,
        width=5
    )
    wavelengths= my_data.get_data("Wavelength, nm")
    if wavelengths is None:
        raise ValueError("Wavelength data is required for group index calculation.")
    # from the distances between the peaks
    # calculate the group index
    ng = (
        N_average *0.5
        * wavelengths[peaks[N_average:]]
        * wavelengths[peaks[:-N_average]]
        / (
            length_wg
            * (wavelengths[peaks[N_average:]] - wavelengths[peaks[:-N_average]])
        )
    )
    wl=0.5* (
        wavelengths[peaks[N_average:]] + wavelengths[peaks[:-N_average]]
    )
    data_out= {
        "Wavelength, nm": wl,
        "Group index": ng,
    }

    return Data(data=data_out, metadata=metadata)

def find_peaks_plot(my_data:Data)->None:
    """
    Find peaks in the optical power data and plot them.

    Args:
        my_data (Data): The Data object containing optical power data.

    """
    # Extract the optical power data
    optical_power = my_data.get_data("Optical power TE, W")
    wavelengths = my_data.get_data("Wavelength, nm")

    if optical_power is None or wavelengths is None:
        raise ValueError(
            "Optical power and wavelength data are required for peak finding."
        )

    # Find peaks
    peaks, _ = signal.find_peaks(optical_power,distance=10,width=5)

    # Plot the data and the peaks
    plt.figure(figsize=(10, 6))
    plt.plot(wavelengths, optical_power, label="Optical Power TE")
    plt.plot(wavelengths[peaks], optical_power[peaks], "x", label="Peaks")
    plt.xlabel("Wavelength (nm)")
    plt.ylabel("Optical Power (W)")
    plt.title("Peak Finding in Optical Power Data")
    plt.legend()
    plt.grid()
    plt.show()
