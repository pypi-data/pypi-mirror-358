"""
File to define the class Data, which is used to store and manipulate data.

This is the main class of the package and is used to store data and metadata
for a measurement.
"""

from typing import Any


class Data:
    """
    Class to store data and metadata for a measurement.

    Attributes:
        data (dict): Dictionary containing measurement data.
        metadata (dict): Dictionary containing metadata.

    """

    def __init__(self, data=None, metadata=None):
        """
        Initialize the Data object with data and metadata.

        Args:
            data (dict): Dictionary containing measurement data.
            metadata (dict): Dictionary containing metadata.

        """
        self.data = data if data is not None else {}
        self.metadata = metadata if metadata is not None else {}
        self._ms_type = self.metadata.get("Measurement", "unknown")
        self._analysis= {}
        # TODO add another atrybute that is a dictionary with type of analysis
        # performed maybe with the results associated.

    def __repr__(self):
        """Override the default representation of the Data object."""
        return f"Data(metadata={self.metadata},data={list(self.data.keys())})"

    def get_metadata(self, key):
        """
        Get metadata value by key.

        Args:
            key (str): The key for the metadata.

        Returns:
            The value of the metadata for the given key.

        """
        return self.metadata.get(key, None)

    def get_data(self, key):
        """
        Get data value by key.

        Args:
            key (str): The key for the data.

        Returns:
            The value of the data for the given key.

        """
        return self.data.get(key, None)

    def add_metadata(self, key: str, value: Any):
        """
        Add a metadata entry.

        Args:
            key (str): The key for the metadata.
            value (Any): The value for the metadata.

        """
        self.metadata[key] = value

    def add_data(self, key: str, value: Any):
        """
        Add a data entry.

        Args:
            key (str): The key for the data.
            value (Any): The value for the data.

        """
        self.data[key] = value

    def add_analysis(self, key: str, value: Any):
        """
        Add an analysis entry.

        Args:
            key (str): The key for the analysis.
            value (Any): The value for the analysis.

        """
        self._analysis[key] = value

    def get_analysis(self, key: str):
        """
        Get an analysis entry by key.

        Args:
            key (str): The key for the analysis.

        Returns:
            The value of the analysis for the given key.

        """
        return self._analysis.get(key, None)

    def plot(self, x_key: None | str = None, y_key: None | str = None, **kwargs):
        """
        Plot the data using matplotlib.

        Args:
            x_key (str): The key for the x-axis data, if None the first key is used.
            y_key (str): The key for the y-axis data, if None all keys will be
                plotted on top of each other.
            **kwargs: Additional keyword arguments for plotting.

        """
        if x_key is None:
            x_key = list(self.data.keys())[0]
        if y_key is None:
            if len(self.data.keys()) > 1:
                y_key_list = list(self.data.keys())[1:]
            else:
                y_key_list = None
        for key in y_key_list if isinstance(y_key_list, list) else [y_key]:
            print(f"Plotting {x_key} vs {key}")
            if key is None:
                continue
            x_data = self.get_data(x_key)
            y_data = self.get_data(key)
            if x_data is None or y_data is None:
                raise ValueError(f"Data for keys '{x_key}' or '{key}' not found.")
            self.plot_x_y(x_key, key, **kwargs)

    def plot_x_y(self, x_key: None | str = None, y_key: None | str = None, **kwargs):
        """
        Plot the data using matplotlib.

        Args:
            x_key (str): The key for the x-axis data.
            y_key (str): The key for the y-axis data.
            **kwargs: Additional keyword arguments for plotting.

        """
        import matplotlib.pyplot as plt

        if x_key is None or y_key is None:
            raise ValueError("Both x_key and y_key must be provided for plotting.")

        x_data = self.get_data(x_key)
        y_data = self.get_data(y_key)

        if x_data is None or y_data is None:
            raise ValueError(f"Data for keys '{x_key}' or '{y_key}' not found.")

        plt.plot(x_data, y_data, **kwargs)
        plt.xlabel(x_key)
        plt.ylabel(y_key)
        plt.title(f"{self._ms_type} Data")
        plt.grid()
