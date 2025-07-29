"""
Test module for waveguide analysis functions.

This module provides comprehensive tests for all functions in the waveguide_module,
using field propagation simulation to create test data with known parameters.
"""

import numpy as np
import pytest
from sp_brew.Data_class import Data
from sp_brew.waveguide_module import (
    find_data_peaks,
    calculate_group_index,
    calculate_waveguide_losses,
    calculate_peak_height_waveguide_loss,
    find_peaks_plot,
)


def simulate_cavity_transmission(
    wavelengths,
    neff,
    cavity_length,
    reflection_coeff,
    loss_dB_per_cm=0.5,
    peak_wavelength=None,
    peak_height_dB=None,
    noise_level=0.005,
):
    """
    Simulate optical field propagation in a Fabry-Perot cavity with losses.

    This function creates synthetic transmission data that mimics real waveguide
    measurements, including Fabry-Perot interference fringes and optional
    wavelength-dependent peaks for testing loss analysis functions.

    Args:
        wavelengths (np.ndarray): Wavelength array in nm.
        neff (np.ndarray): Effective refractive index array.
        cavity_length (float): Physical length of the cavity in nm.
        reflection_coeff (float): Reflection coefficient at the facets (0-1).
        loss_dB_per_cm (float): Propagation loss in dB/cm.
        peak_wavelength (float, optional): Center wavelength for absorption peak in nm.
        peak_height_dB (float, optional): Height of absorption peak in dB.
        noise_level (float): Relative noise level to add to the transmission data.

    Returns:
        np.ndarray: Simulated optical power transmission.

    """
    # Set random seed for reproducible noise
    np.random.seed(42)

    # Convert wavelengths to meters for calculations
    wl_m = wavelengths * 1e-9
    cavity_length_m = cavity_length * 1e-9

    # Calculate phase accumulation (round trip) using effective index
    phase = 4 * np.pi * neff * cavity_length_m / wl_m

    # Convert loss from dB/cm to linear loss coefficient (1/m)
    loss_linear = loss_dB_per_cm * np.log(10) / 10 * 100  # per meter

    # Add wavelength-dependent absorption peak if specified
    if peak_wavelength is not None and peak_height_dB is not None:
        linewidth = 2.0  # nm FWHM, adjust as needed
        # Lorentzian profile, normalized to 1 at the center
        peak_profile = 1 / (1 + 4 * ((wavelengths - peak_wavelength) / linewidth) ** 2)
        # Calculate the required *additional* loss at the peak (in 1/m)
        # This ensures the transmission dip is peak_height_dB at the center
        peak_loss_linear = (peak_height_dB / (10 * np.log10(np.e))) / (
            2 * cavity_length_m
        )
        # Apply the Lorentzian profile
        loss_linear = loss_linear + peak_loss_linear * peak_profile

    # Calculate transmission through cavity with losses
    round_trip_loss_factor = np.exp(-2 * loss_linear * cavity_length_m)
    # Fabry-Perot transmission formula with losses
    # T = (1-R)² * exp(-αL) / [(1-R*exp(-αL))² + 4*R*exp(-αL)*sin²(φ/2)]
    R_eff = reflection_coeff * round_trip_loss_factor
    numerator = (1 - reflection_coeff) ** 2 * round_trip_loss_factor
    denominator = (1 - R_eff) ** 2 + 4 * R_eff * np.sin(phase / 2) ** 2
    transmission = numerator / denominator

    # Add small amount of noise to make it realistic
    noise = np.random.normal(0, noise_level * np.mean(transmission), len(transmission))
    transmission += noise

    # Ensure positive values
    transmission = np.maximum(transmission, 1e-12)

    return transmission


class TestWaveguideModule:
    """Test class for waveguide analysis functions."""

    def setup_method(self):
        """Set up test data before each test method."""
        # Define test parameters
        self.wavelengths = np.linspace(1540, 1560, 5000)  # nm
        self.neff = 3.2 + self.wavelengths * 0.004  # Effective index, constant for now
        self.cavity_length = 4.6e6  # nm (4.6 mm)
        self.reflection_coeff = 0.32
        self.loss_dB_per_cm = 3  # dB/cm
        self.peak_wavelength = 1550.0  # nm
        self.peak_height_dB = 2.5  # dB
        self.noise_level = 0.005  # Noise level for simulation

        # Generate basic test data without absorption peak
        self.basic_power = simulate_cavity_transmission(
            self.wavelengths,
            self.neff,
            self.cavity_length,
            self.reflection_coeff,
            self.loss_dB_per_cm,
            noise_level=self.noise_level,
        )

        # Generate test data with absorption peak
        self.peak_power = simulate_cavity_transmission(
            self.wavelengths,
            self.neff,
            self.cavity_length,
            self.reflection_coeff,
            self.loss_dB_per_cm,
            self.peak_wavelength,
            self.peak_height_dB,
            noise_level=self.noise_level,
        )

        # Create Data objects
        self.basic_data = Data(
            data={
                "Wavelength, nm": self.wavelengths,
                "Optical power TE, W": self.basic_power,
            },
            metadata={"Measurement": "Test Cavity Transmission"},
        )

        self.peak_data = Data(
            data={
                "Wavelength, nm": self.wavelengths,
                "Optical power TE, W": self.peak_power,
            },
            metadata={"Measurement": "Test Cavity Transmission with Peak"},
        )

    def test_find_data_peaks_basic(self):
        """Test peak finding on a pure sinusoidal signal with known maxima."""
        # Generate a sine wave with known peaks
        x = np.linspace(0, 2 * np.pi, 1000)
        y = np.sin(x)
        # Peaks at x = pi/2 + 2*pi*n
        expected_peaks = np.array([np.pi / 2])
        while expected_peaks[-1] + 2 * np.pi < x[-1]:
            expected_peaks = np.append(expected_peaks, expected_peaks[-1] + 2 * np.pi)
        # Find closest indices in x
        expected_peak_indices = [
            np.abs(x - xp).argmin() for xp in expected_peaks if xp <= x[-1]
        ]
        # Prepare Data object
        data = Data(data={"Wavelength, nm": x, "Optical power TE, W": y}, metadata={})
        # Find peaks
        peaks_result = find_data_peaks(
            data, data_key="Optical power TE, W", distance=50, prominence=0.5
        )
        found_indices = peaks_result.get_data("peaks")
        # Check that all expected peaks are found (allowing for small index error)
        for idx in expected_peak_indices:
            assert np.any(
                np.abs(found_indices - idx) <= 1
            ), f"Expected peak at {idx} not found"

    def test_find_data_peaks_reverse(self):
        """Test valley finding on a pure sinusoidal signal with known minima."""
        # Generate a sine wave with known valleys
        x = np.linspace(0, 2 * np.pi, 1000)
        y = np.sin(x)

        # Valleys at x = 3*pi/2 + 2*pi*n
        expected_valleys = np.array([3 * np.pi / 2])
        while expected_valleys[-1] + 2 * np.pi < x[-1]:
            expected_valleys = np.append(
                expected_valleys, expected_valleys[-1] + 2 * np.pi
            )
        expected_valley_indices = [
            np.abs(x - xv).argmin() for xv in expected_valleys if xv <= x[-1]
        ]
        data = Data(data={"Wavelength, nm": x, "Optical power TE, W": y}, metadata={})
        valleys_result = find_data_peaks(
            data,
            data_key="Optical power TE, W",
            reverse=True,
            distance=50,
            prominence=0.5,
        )
        found_indices = valleys_result.get_data("peaks")
        for idx in expected_valley_indices:
            assert np.any(
                np.abs(found_indices - idx) <= 1
            ), f"Expected valley at {idx} not found"

    def test_find_data_peaks_invalid_data(self):
        """Test peak finding with invalid data."""
        # Create Data object without required keys
        invalid_data = Data(data={"Wrong key": [1, 2, 3]}, metadata={})

        with pytest.raises(
            ValueError, match="Optical power and wavelength data are required"
        ):
            find_data_peaks(invalid_data)

    def test_calculate_group_index(self):
        """
        Test to verify the group index calculation.

        Test verifies that the calculated group index matches the analytical
        group index derived from the effective refractive index (neff) and wavelength.

        """
        # Calculate group index with relaxed parameters
        ng_result = calculate_group_index(
            self.basic_data,
            data_key="Optical power TE, W",
            length_wg=self.cavity_length,
            N_average=5,
        )

        calculated_wl = ng_result.get_data("Wavelength, nm")
        calculated_ng = ng_result.get_data("Group index")
        assert calculated_wl is not None and calculated_wl.size > 0
        assert calculated_ng is not None and calculated_ng.size > 0

        # Calculate analytical group index from neff
        # Interpolate neff to calculated_wl
        neff_interp = np.interp(calculated_wl, self.wavelengths, self.neff)
        dneff_dlambda = np.gradient(self.neff, self.wavelengths)
        dneff_dlambda_interp = np.interp(calculated_wl, self.wavelengths, dneff_dlambda)
        analytical_ng = neff_interp - calculated_wl * dneff_dlambda_interp

        # Compare calculated group index to analytical
        rel_error = np.abs(calculated_ng - analytical_ng) / np.abs(analytical_ng)

        assert np.all(rel_error < 0.05), f"Group index error too large: {rel_error}"

        # Verify metadata
        assert ng_result.get_metadata("Measurement") == "Group Index Calculation"

    def test_calculate_group_index_invalid_data(self):
        """Test group index calculation with invalid data."""
        invalid_data = Data(data={}, metadata={})

        with pytest.raises(
            ValueError, match="Optical power and wavelength data are required"
        ):
            calculate_group_index(invalid_data)

    def test_calculate_waveguide_losses(self):
        """Test waveguide loss calculation accuracy."""
        # Calculate losses
        loss_result = calculate_waveguide_losses(
            self.basic_data,
            data_key="Optical power TE, W",
            reflection_coeff=self.reflection_coeff,
        )

        # Check results
        loss_wl = loss_result.get_data("Wavelength, nm")
        loss_values = loss_result.get_data("Loss, dB")

        # Assert arrays are not None and not empty
        assert loss_wl is not None and len(loss_wl) > 0
        assert loss_values is not None and len(loss_values) > 0

        # Compare calculated loss to expected simulated value (mean loss)
        # The simulated loss is set by self.loss_dB_per_cm
        expected_loss = (
            self.loss_dB_per_cm * 2 * self.cavity_length / 1e7
        )  # Convert cm to nm
        mean_loss = np.mean(loss_values)

        assert np.isclose(
            mean_loss, expected_loss, rtol=0.05
        ), f"Mean loss {mean_loss} differs from expected {expected_loss}"

        # Verify metadata
        assert loss_result.get_metadata("Measurement") == "Propagation Loss, dB"

    def test_calculate_waveguide_losses_invalid_data(self):
        """Test loss calculation with invalid data."""
        invalid_data = Data(data={}, metadata={})

        with pytest.raises(
            ValueError, match="Optical power and wavelength data are required"
        ):
            calculate_waveguide_losses(invalid_data)

    def test_calculate_peak_height_waveguide_loss_no_peak(self):
        """Test peak height calculation with no absorption peak."""
        peak_height_result = calculate_peak_height_waveguide_loss(
            self.basic_data,
            data_key="Optical power TE, W",
            reflection_coeff=self.reflection_coeff,
        )
        # Check extraction fields
        peak_height = peak_height_result.get_extraction_value("peak_height")
        pos_start_lowpeak = peak_height_result.get_extraction_point("pos_start_lowpeak")
        pos_end_highpeak = peak_height_result.get_extraction_point("pos_end_highpeak")
        assert peak_height is not None
        assert pos_start_lowpeak is not None
        assert pos_end_highpeak is not None
        # The calculated peak height should match the simulated peak height
        assert np.isclose(
            peak_height, 0, atol=0.15
        ), f"Peak height {peak_height} dB does not match simulated value {0} dB"
        # Check data arrays
        wl_array = peak_height_result.get_data("Wavelength, nm")
        loss_array = peak_height_result.get_data("Loss, dB")
        assert wl_array is not None and loss_array is not None

    def test_calculate_peak_height_waveguide_loss_with_peak(self):
        """Test peak height calculation with known absorption peak."""
        peak_height_result = calculate_peak_height_waveguide_loss(
            self.peak_data,
            data_key="Optical power TE, W",
            reflection_coeff=self.reflection_coeff,
        )
        # Check extraction fields
        peak_height = peak_height_result.get_extraction_value("peak_height")
        pos_start_lowpeak = peak_height_result.get_extraction_point("pos_start_lowpeak")
        pos_end_highpeak = peak_height_result.get_extraction_point("pos_end_highpeak")
        assert peak_height is not None
        assert pos_start_lowpeak is not None
        assert pos_end_highpeak is not None
        # The calculated peak height should match the simulated peak height
        assert np.isclose(
            peak_height,
            self.peak_height_dB,
            rtol=0.1
        ), (
            f"Peak height {peak_height} does not match simulated value "
            f"{self.peak_height_dB}"
        )
        # Check data arrays
        wl_array = peak_height_result.get_data("Wavelength, nm")
        loss_array = peak_height_result.get_data("Loss, dB")
        assert wl_array is not None and loss_array is not None

    def test_find_peaks_plot(self):
        """Test plotting function (check it doesn't crash and returns a figure)."""
        try:
            import matplotlib
            matplotlib.use("Agg")  # Use non-interactive backend
            fig = find_peaks_plot(self.basic_data, figure=None)
            assert fig is not None
        except Exception as e:
            pytest.fail(f"find_peaks_plot raised an exception: {e}")

    def test_find_peaks_plot_invalid_data(self):
        """Test plotting function with invalid data."""
        invalid_data = Data(data={}, metadata={})
        import matplotlib
        matplotlib.use("Agg")
        with pytest.raises(
            ValueError, match="Optical power and wavelength data are required"
        ):
            find_peaks_plot(invalid_data, figure=None)


if __name__ == "__main__":
    # Run tests if script is executed directly
    pytest.main([__file__])
