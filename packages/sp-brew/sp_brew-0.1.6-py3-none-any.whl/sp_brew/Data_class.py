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

    def __init__(self,
                 data=None,
                 metadata=None,
                 extraction_point=None,
                 extraction_value=None):
        """
        Initialize the Data object with data and metadata.

        Args:
            data (dict): Dictionary containing measurement data.
            metadata (dict): Dictionary containing metadata.
            extraction_point (dict): Dict with extracted points from the analysis.
            extraction_value (dict): Dict with extracted values from the analysis.

        """
        self.data = data if data is not None else {}
        self.metadata = metadata if metadata is not None else {}
        self.extraction_point = extraction_point if extraction_point is not None else {}
        self.extraction_value = extraction_value if extraction_value is not None else {}
        self._ms_type = self.metadata.get("Measurement", "unknown")
        self._analysis = {}

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

    def get_extraction_point(self, key):
        """
        Get extraction point value by key.

        Args:
            key (str): The key for the extraction point.

        Returns:
            The value of the extraction point for the given key.

        """
        return self.extraction_point.get(key, None)

    def get_extraction_value(self, key):
        """
        Get extraction value by key.

        Args:
            key (str): The key for the extraction value.

        Returns:
            The value of the extraction value for the given key.

        """
        return self.extraction_value.get(key, None)

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

    def add_extraction_point(self, key: str, value: Any):
        """
        Add an extraction point entry.

        Args:
            key (str): The key for the extraction point.
            value (Any): The value for the extraction point.

        """
        self.extraction_point[key] = value

    def add_extraction_value(self, key: str, value: Any):
        """
        Add an extraction value entry.

        Args:
            key (str): The key for the extraction value.
            value (Any): The value for the extraction value.

        """
        self.extraction_value[key] = value

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

    def plot(self,
             x_key: None | str = None,
             y_key: None | str = None,
             show_extraction_point: bool = False,
             figure=None,
             **kwargs):
        """
        Plot the data using matplotlib.

        Args:
            x_key (str): The key for the x-axis data, if None the first key is used.
            y_key (str): The key for the y-axis data, if None all keys will be
                plotted on top of each other.
            show_extraction_point (bool): If True, plot the extraction points.
            figure: matplotlib Figure object to plot on. If None, create new figure.
            **kwargs: Additional keyword arguments for plotting.

        Returns:
            The matplotlib Figure object used for plotting.
        """

        import matplotlib.pyplot as plt
        if x_key is None:
            x_key = list(self.data.keys())[0]
        if y_key is None:
            if len(self.data.keys()) > 1:
                y_key_list = list(self.data.keys())[1:]
            else:
                y_key_list = None
        else:
            y_key_list = [y_key]

        fig = figure
        if fig is None:
            fig = plt.figure()
        for key in y_key_list:
            if key is None:
                continue
            x_data = self.get_data(x_key)
            y_data = self.get_data(key)
            if x_data is None or y_data is None:
                raise ValueError(f"Data for keys '{x_key}' or '{key}' not found.")
            self.plot_x_y(x_key, key, figure=fig, **kwargs)
            if show_extraction_point:
                self.plot_extraction_points(figure=fig)
        return fig

    def plot_x_y(self,
                 x_key: None | str = None,
                 y_key: None | str = None,
                 figure=None,
                 **kwargs):
        """
        Plot the data using matplotlib.

        Args:
            x_key (str): The key for the x-axis data.
            y_key (str): The key for the y-axis data.
            figure: matplotlib Figure object to plot on. If None, create new figure.
            **kwargs: Additional keyword arguments for plotting.

        Returns:
            The matplotlib Figure object used for plotting.
        """

        import matplotlib.pyplot as plt
        if x_key is None or y_key is None:
            raise ValueError("Both x_key and y_key must be provided for plotting.")
        x_data = self.get_data(x_key)
        y_data = self.get_data(y_key)
        if x_data is None or y_data is None:
            raise ValueError(f"Data for keys '{x_key}' or '{y_key}' not found.")
        fig = figure
        if fig is None:
            fig = plt.figure()
        ax = fig.gca()
        ax.plot(x_data, y_data, **kwargs)
        ax.set_xlabel(x_key)
        ax.set_ylabel(y_key)
        ax.set_title(f"{self._ms_type} Data")
        ax.grid()
        return fig

    def plot_extraction_points(self, key_list: list[str] | None = None, figure=None):
        """
        Plot the extraction points on the current figure.

        Args:
            key_list (list[str]): List of keys for the extraction points to plot.
                If None, all extraction points will be plotted.
            figure: matplotlib Figure object to plot on. If None, use current figure.

        Returns:
            The matplotlib Figure object used for plotting.
        """

        import matplotlib.pyplot as plt
        fig = figure
        if fig is None:
            fig = plt.gcf()
        ax = fig.gca()
        for key, value in self.extraction_point.items():
            if key_list is None or key in key_list:
                ax.scatter(x=value[0], y=value[1], label=f"{key}")
        ax.legend()
        return fig
