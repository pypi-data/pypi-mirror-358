"""File used to test the utility functions of the package."""

import os

import sp_brew.utils_files as brew


def test_find_datafiles():
    """Test the find_datafiles function."""
    # Create a temporary directory and files for testing
    test_dir = "test_dir"
    os.makedirs(test_dir, exist_ok=True)
    test_file1 = os.path.join(test_dir, "test_file1.txt")
    test_file2 = os.path.join(test_dir, "test_file2.txt")
    noshow_file3 = os.path.join(test_dir, "noshow_file3.txt")
    with open(test_file1, "w") as f:
        f.write("This is a test file.")
    with open(test_file2, "w") as f:
        f.write("This is another test file.")
    with open(noshow_file3, "w") as f:
        f.write("this file should not be found.")

    # Test the function
    result = brew.find_datafiles(["test"], test_dir)
    assert len(result) == 2
    assert test_file1 in result
    assert test_file2 in result
    assert noshow_file3 not in result
    # Test with no keywords
    result = brew.find_datafiles([], test_dir)
    assert len(result) == 3
    # Clean up
    os.remove(test_file1)
    os.remove(test_file2)
    os.remove(noshow_file3)
    os.rmdir(test_dir)


def test_save_data_to_csv():
    """Test the save_data_to_csv function."""
    # Create a temporary directory for testing
    test_dir = "test_save_dir"
    os.makedirs(test_dir, exist_ok=True)

    # Create a sample list of dictionaries
    data = [
        {"col_0": [1, 2, 3], "col_1": 2, "col_2": 3},
        {"col_0": 4, "col_1": 5, "col_2": 6},
    ]

    # Save the data to CSV
    file_path = os.path.join(test_dir, "test_data.csv")
    brew.save_data_to_csv(
        save_folder=test_dir, data_list=data, filename="test_data.csv"
    )

    # Check if the file exists and is not empty
    assert os.path.exists(file_path)
    assert os.path.getsize(file_path) > 0

    # Clean up
    os.remove(file_path)
    os.rmdir(test_dir)
