"""Package for sp_brew."""

from . import utils_files, utils_math
from .Data_class import Data
from .waveguide_module import (
    calculate_group_index,
    calculate_waveguide_losses,
    calculate_peak_height_waveguide_loss,
    find_peaks_plot,
)

__all__ = [
    "utils_files",
    "utils_math",
    "Data",
    "calculate_group_index",
    "calculate_waveguide_losses",
    "calculate_peak_height_waveguide_loss",
    "find_peaks_plot"
]


def main() -> None:
    print("Hello from sp-brew!")
