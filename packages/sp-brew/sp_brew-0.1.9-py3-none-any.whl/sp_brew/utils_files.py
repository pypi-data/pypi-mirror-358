"""
Functions for file management, data parsing, and data import/export.

It includes functions to select folders, find data files, parse files with
metadata.
"""

import os
from os import PathLike
from tkinter import filedialog
from typing import Union
import csv

import numpy as np
import pandas as pd

from .Data_class import Data


def select_wanted_folder(initial_dir=None):
    """
    Open a GUI for selecting a folder.

    If an initial_dir is specified, the search starts from that directory

    :return: The filepath chosen by the user.
    """
    if initial_dir is not None:
        filepath = filedialog.askdirectory(initialdir=initial_dir)
    else:
        filepath = filedialog.askdirectory()
    print(f"The filepath chosen is: {filepath}")
    return filepath


def find_datafiles(key_words: list[str] = [""], directory_to_search="./") -> list:
    """
    Collect all files in a specific folder with a pattern in the name.

    The words in the key_words list must be all present in the files otherwise
    the file is not returned.

    Args:
        key_words(list[str]): the keyword in the datafiles
        directory_to_search: gives a directory where the data are located.

    Returns:
        list of filenames

    """
    datafiles = []
    for subdir in os.walk(directory_to_search):
        for filenames in subdir[2]:
            add_element = True
            for key_word in key_words:
                if key_word not in filenames:
                    add_element = False
            if add_element:
                datafiles.append(os.path.join(subdir[0], filenames))
    return datafiles


def find_rows_to_skip(datafile) -> int:
    """
    Openepda files finds row of metadata to skip.

    Openepda files start with an arbitrary number of rows that are used to carry
    metadato with this function the row before all the actual data is selected
    and the row number returned.

    Args:
        datafile: the path to the datafile.

    """
    with open(datafile, "r") as f:
        for i, line in enumerate(f):
            if "---" in line:
                return i
        print(datafile)
        raise ValueError("Not found the end of the documentation")


def parse_files_with_metadata(
    folder_path: str, file_list: list[str], delimiter: str = ","
) -> list[dict]:
    """
    Parse multiple files containing metadata and measurement data.

    Args:
        folder_path (str): Path to the folder containing the files
        file_list (list[str]): List of filenames to process
        delimiter (str): The delimiter used to separate values in the file
            (default: ',')

    Returns:
        list[dict]: List of dictionaries containing metadata and measurements
            for each file

    """
    results = []

    total_file_length = len(file_list)
    for idf, filename in enumerate(file_list):
        # Calculate and print progress percentage
        progress_percent = (idf + 1) / total_file_length * 100
        print(f"Processing files: {progress_percent:.1f}% complete", end="\r")
        file_path = os.path.join(folder_path, filename)

        # Initialize dictionary for this file
        file_data = {"filename": filename, "metadata": {}, "measurements": {}}

        with open(file_path, "r") as f:
            # Find where metadata ends
            metadata_end = find_rows_to_skip(file_path)

            # Process metadata (lines before the separator)
            for i, line in enumerate(f):
                if i >= metadata_end:
                    break

                # Skip empty lines
                if not line.strip():
                    continue

                # Parse metadata lines (format: "key: value")
                if ":" in line:
                    key, value = map(str.strip, line.split(":", 1))
                    file_data["metadata"][key] = value

            # Get the column names (first line after metadata)
            column_names = [col.strip() for col in next(f).strip().split(delimiter)]

            # Initialize arrays for each column
            for col in column_names:
                file_data["measurements"][col] = []

            # Read all remaining lines of data
            for line in f:
                if not line.strip():  # Skip empty lines
                    continue

                values = line.strip().split(",")
                for col, val in zip(column_names, values):
                    try:
                        # Try to convert to float if possible
                        file_data["measurements"][col].append(float(val))
                    except ValueError:
                        # Keep as string if not a number
                        file_data["measurements"][col].append(val)

            # Convert lists to numpy arrays for numerical data
            for col in column_names:
                if all(
                    isinstance(x, (int, float)) for x in file_data["measurements"][col]
                ):
                    file_data["measurements"][col] = np.array(
                        file_data["measurements"][col]
                    )

        results.append(file_data)

    print("All Data Loaded")

    return results


def import_wldata_openepda(datafile, wl_min=None, wl_max=None) -> tuple:
    """
    Import a datafile in openepda format.

    The data are expected to be wavelength dependent.

    Args:
        datafile: datafile path
        wl_min: minimum wavelength, used to truncate the data at a min
            wavelength, in nm
        wl_max: maximum wavelength, used to truncate the data at a max
            wavelength, in nm

    Returns:
        tuple: (wavelength array in m, power array in mW)

    """
    # Import raw data
    try:
        row_skip = find_rows_to_skip(datafile)
    except ValueError:
        raise ValueError("no data in the file")

    df = pd.read_csv(
        datafile, delimiter=",", decimal=".", header=row_skip + 1, index_col=False
    )
    X = wl_min
    Y = wl_max
    if wl_min is not None and wl_max is not None:
        filtered_df = df[(df["Wavelength, nm"] >= X) & (df["Wavelength, nm"] <= Y)]
    elif wl_min is not None:
        filtered_df = df[(df["Wavelength, nm"] >= X)]
    elif wl_max is not None:
        filtered_df = df[(df["Wavelength, nm"] <= Y)]
    else:
        filtered_df = df
    wl_arr = np.array(filtered_df["Wavelength, nm"]) * 1e-09
    i_arr = np.array(filtered_df["Current, A"]) * -1000
    p_arr = i_arr * 2 / 0.85
    return wl_arr, p_arr


def check_and_mkdir(path):
    """Check if a directory exists, and create it if it does not."""
    if not os.path.exists(path):
        os.mkdir(path)


def save_data_to_csv(
    save_folder: Union[str, PathLike],
    data_list: list[dict],
    filename: Union[str, PathLike] = "compiled_data.csv",
) -> None:
    """
    Save data from a list of dictionaries to a CSV file.

    Args:
        save_folder (str): Path to the folder where the file should be saved
        data_list (list[dict]): List of dictionaries containing the data to save
        filename (str): Name of the output file (default: "compiled_data.csv")

    """
    if not data_list:
        raise ValueError("Data list is empty")

    # Ensure the save folder exists
    check_and_mkdir(save_folder)

    # Get column names from the first dictionary's keys
    columns = list(data_list[0].keys())

    # Create full file path
    file_path = os.path.join(save_folder, filename)

    # Write data to CSV
    with open(file_path, "w") as f:
        # Write header
        f.write(",".join(columns) + "\n")

        # Write data row by row
        for data_dict in data_list:
            row_values = [str(data_dict[col]) for col in columns]
            f.write(",".join(row_values) + "\n")

    print(f"Data saved to: {file_path}")


def import_openepda_file(filepath: str, delimiter: str = ",") -> Data:
    """
    Import an OPENepda file, splitting metadata and table.

    Args:
        filepath (str): Path to the OPENepda file.
        delimiter (str): Delimiter used in the table (default: ',').

    Returns:
        Data: Data object with metadata and table columns as np arrays.

    """
    metadata = {}
    table = {}
    with open(filepath, "r") as f:
        # Read metadata
        for line in f:
            if line.strip().startswith("---"):
                break
            if ":" in line:
                key, value = map(str.strip, line.split(":", 1))
                metadata[key] = value

        # Read table header
        header_line = next(f)
        reader = csv.reader([header_line], delimiter=delimiter)
        columns = [col.strip().strip('"') for col in next(reader)]
        for col in columns:
            table[col] = []

        # Read table data
        for line in f:
            if not line.strip():
                continue
            csv_line = next(csv.reader([line], delimiter=delimiter))
            values = [val.strip() for val in csv_line]
            for col, val in zip(columns, values):
                try:
                    table[col].append(float(val))
                except ValueError:
                    table[col].append(val)

    # Convert lists to numpy arrays
    for col in table:
        try:
            table[col] = np.array(table[col], dtype=float)
        except ValueError:
            table[col] = np.array(table[col], dtype=object)

    return Data(data=table, metadata=metadata)


if __name__ == "__main__":
    # use example to import a file

    path_to_check = (
        r"C:\Users\DamianoMassella\Smart Photonics\Design Enablement - Documents"
        r"\Device Engineering\Compact Modeling\DBR_modelling\Scripts_and_data"
    )
    datas = find_datafiles(
        ["sp_dbr_sh", "T1J6", "slow"], directory_to_search=path_to_check
    )
    pd_file = find_datafiles(
        ["sp_basic_pin_sh", "T1K21", "slow"], directory_to_search=path_to_check
    )
    ng = 3.67  # group index
    print(pd_file)
    result = []
    lengths = []

    wl_dbr, I_raw = import_wldata_openepda(datas[4])
