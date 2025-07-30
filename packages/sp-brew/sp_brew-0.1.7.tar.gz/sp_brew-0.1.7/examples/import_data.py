"""
Example script to import data from an OPENepda file to the Data class.

This script imports a sample OPENepda file and prints the data and metadata.
It demonstrates how to use the import_openepda_data function from the
sp_brew.utils_files module.
"""

import sp_brew as brew
import matplotlib.pyplot as plt

def main():
    """Import data from a file and print data and metadata."""
    file_to_import = "./examples/data_files/"
    file_path = file_to_import + "Raw Data ADT Example.txt"
    my_data = brew.utils_files.import_openepda_file(file_path)

    #brew.find_peaks_plot(my_data)
    #plt.show()
    #out_data = brew.calculate_group_index(my_data)
    #out_data.plot()

    #out_data = brew.calculate_waveguide_losses(my_data)
    #out_data.plot(y_key="Loss, dB")

    out_data = brew.calculate_peak_height_waveguide_loss(my_data)
    out_data.plot(show_extraction_point=True)
    plt.show()

if __name__ == "__main__":
    main()
