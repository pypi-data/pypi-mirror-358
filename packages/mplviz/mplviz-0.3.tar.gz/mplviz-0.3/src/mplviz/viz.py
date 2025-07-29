"""
viz.py

A module that defines the Viz class for creating and manipulating
matplotlib-based visualizations with a consistent interface. Includes
plotting methods (e.g., bar, line, scatter), layout utilities, and
tools for combining multiple plots into a single figure.
"""

from IPython.display import display, clear_output
import matplotlib.pyplot as plt
import numpy as np


class _VizCore:
    def save(self, path, **kwargs):
        """
        Saves the figure to a file.

        Parameters
        ----------
        path : str
            The file path to save the figure.
        kwargs : dict, optional
            Additional keyword arguments passed to `fig.savefig()`, such as:
            - dpi : int, optional (dots per inch for image resolution)
            - bbox_inches : str or 'tight', optional (to adjust bounding box)
            - transparent : bool, optional (if True, the background is transparent)
        """
        self.fig.savefig(path, **kwargs)

    def show(self, clear=False):
        """
        Displays the plot.

        Parameters
        ----------
        clear : bool, optional
            If True, the previous output is cleared before showing the plot.
        """
        if clear:
            clear_output(wait=True)
        try:
            display(self.fig)
        except NameError:
            plt.show()

    def clear(self):
        """
        Clears the current axis.

        Returns
        -------
        self : Viz
            The Viz object itself, allowing for method chaining.
        """
        self.ax.cla()
        return self

    def twinx(self):
        """
        Creates a twin axis sharing the same x-axis but different y-axis.

        Returns
        -------
        Viz
            A new Viz object with the twin axis.
        """
        twin_ax = self.ax.twinx()
        return Viz(twin_ax, self.fig)

    def imshow(self, *args, **kwargs):
        """
        Displays an image on the plot.

        Parameters
        ----------
        args : tuple
            The image data (e.g., a 2D array representing pixel intensities).
        kwargs : dict, optional
            Additional keyword arguments passed to `ax.imshow()`, such as:
            - cmap : str, optional (colormap for displaying the image)
            - interpolation : str, optional (method for interpolation, e.g., 'nearest', 'bilinear')
            - alpha : float, optional (transparency, from 0 to 1)

        Returns
        -------
        self : Viz
            The Viz object itself, allowing for method chaining.
        """
        self.ax.imshow(*args, **kwargs)
        return self

    @staticmethod
    def combine_viz(viz_list, nrows=None, ncols=None):
        """
        Combines multiple Viz objects into a single figure with subplots.

        Parameters
        ----------
        viz_list : list
            A list of Viz objects to combine.
        nrows : int, optional
            The number of rows for the subplot grid (default is None).
        ncols : int, optional
            The number of columns for the subplot grid (default is None).

        Returns
        -------
        Viz
            A new Viz object containing the combined plots.
        """
        if nrows is None or ncols is None:
            # If grid size is not provided, calculate it based on the length of viz_list
            total_plots = len(viz_list)
            ncols = int(np.ceil(np.sqrt(total_plots)))  # Approx square grid
            nrows = int(np.ceil(total_plots / ncols))  # Make sure all plots fit

        # Create a new figure and subplot grid
        fig, axs = plt.subplots(nrows, ncols, figsize=(ncols * 5, nrows * 5))

        # Flatten the axes for easy iteration (if it's a multi-dimensional grid)
        axs = axs.flatten() if nrows * ncols > 1 else [axs]

        # Iterate over the list of Viz objects and corresponding axes
        for i, viz in enumerate(viz_list):
            # Get the current axis to plot on
            ax = axs[i]

            # Transfer the plot to the new axis (copying the properties)
            # viz_copy = Viz(ax, fig)  # Create a new Viz instance with the current subplot axis
            # Copy the plot and other settings from the original Viz object to the new axis
            ax.set_title(viz.ax.get_title())  # Copy the title
            ax.set_xlabel(viz.ax.get_xlabel())  # Copy the xlabel
            ax.set_ylabel(viz.ax.get_ylabel())  # Copy the ylabel
            # Copy grid visibility and style
            xgridlines = viz.ax.get_xgridlines()
            ygridlines = viz.ax.get_ygridlines()
            gridlines = xgridlines + ygridlines

            if any(line.get_visible() for line in gridlines):
                gridline = next(
                    (line for line in gridlines if line.get_visible()), None
                )
                if gridline:
                    ax.grid(
                        True,
                        linestyle=gridline.get_linestyle(),
                        color=gridline.get_color(),
                        linewidth=gridline.get_linewidth(),
                    )
            else:
                ax.grid(False)
            # Copy other properties like lines, scatter, etc., based on what the viz object has
            for line in viz.ax.lines:
                ax.plot(line.get_xdata(), line.get_ydata(), label=line.get_label())
            for scatter in viz.ax.collections:
                ax.scatter(
                    scatter.get_offsets()[:, 0],
                    scatter.get_offsets()[:, 1],
                    label=scatter.get_label(),
                )

        # Adjust layout to avoid overlap
        # fig.tight_layout()
        plt.close(fig)
        # Return a new Viz instance wrapping the combined figure
        return Viz(axs[0], fig)

    def close(self):
        """
        Closes the figure.

        Returns
        -------
        self : Viz
            The Viz object itself, allowing for method chaining.
        """
        plt.close(self.fig)
        return self


class _LayoutMixin:
    def set_title(self, txt, **kwargs):
        """
        Sets the title of the plot.

        Parameters
        ----------
        txt : str
            The title text.
        kwargs : dict, optional
            Additional keyword arguments passed to `ax.set_title()`, such as:
            - fontsize : int or float, optional
            - fontweight : {'normal', 'bold', 'heavy', 'light', 'ultrabold', 'ultralight'}, optional
            - color : str, optional (e.g., 'red', 'blue', etc.)
            - pad : float, optional (distance from the top of the axes)

        Returns
        -------
        self : Viz
            The Viz object itself, allowing for method chaining.
        """
        self.ax.set_title(txt, **kwargs)
        return self

    def xlabel(self, txt, **kwargs):
        """
        Sets the label for the x-axis.

        Parameters
        ----------
        txt : str
            The label text for the x-axis.
        kwargs : dict, optional
            Additional keyword arguments passed to `ax.set_xlabel()`, such as:
            - fontsize : int or float, optional
            - fontweight : {'normal', 'bold', 'heavy', 'light', 'ultrabold', 'ultralight'}, optional
            - color : str, optional (e.g., 'red', 'blue', etc.)

        Returns
        -------
        self : Viz
            The Viz object itself, allowing for method chaining.
        """
        self.ax.set_xlabel(txt, **kwargs)
        return self

    def ylabel(self, txt, **kwargs):
        """
        Sets the label for the y-axis.

        Parameters
        ---------
        txt : str
            The label text for the y-axis.
        kwargs : dict, optional
            Additional keyword arguments passed to `ax.set_ylabel()`, such as:
            - fontsize : int or float, optional
            - fontweight : {'normal', 'bold', 'heavy', 'light', 'ultrabold', 'ultralight'}, optional
            - color : str, optional (e.g., 'red', 'blue', etc.)

        Returns
        -------
        self : Viz
            The Viz object itself, allowing for method chaining.
        """
        self.ax.set_ylabel(txt, **kwargs)
        return self

    def legend(self, **kwargs):
        """
        Adds a legend to the plot.

        Parameters
        ----------
        kwargs : dict, optional
            Additional keyword arguments passed to `ax.legend()`, such as:
            - loc : str or int, optional (location of the legend, e.g., 'best', 'upper left', 0)
            - fontsize : int or float, optional
            - title : str, optional (title of the legend)
            - shadow : bool, optional (whether to add shadow)
            - bbox_to_anchor : tuple, optional (to specify a custom position for the legend)

        Returns
        -------
        self : Viz
            The Viz object itself, allowing for method chaining.
        """
        self.ax.legend(**kwargs)
        return self

    def grid(self, flag=True, **kwargs):
        """
        Enables or disables the grid on the plot.

        Parameters
        ----------
        flag : bool, optional, default True
            If True, the grid is enabled, otherwise it is disabled.
        kwargs : dict, optional
            Additional keyword arguments passed to `ax.grid()`, such as:
            - color : str, optional (e.g., 'gray', 'blue', etc.)
            - linestyle : {'-', '--', '-.', ':'}, optional
            - linewidth : float, optional (line thickness)
            - which : {'major', 'minor'}, optional (gridlines for major or minor ticks)

        Returns
        -------
        self : Viz
            The Viz object itself, allowing for method chaining.
        """
        self.ax.grid(flag, **kwargs)
        return self

    def tight_layout(self, **kwargs):
        """
        Adjusts the layout to prevent overlap of plot elements.

        Parameters
        ----------
        kwargs : dict, optional
            Additional keyword arguments passed to `fig.tight_layout()`, such as:
            - pad : float, optional (padding between plot elements)
            - h_pad : float, optional (height padding)
            - w_pad : float, optional (width padding)
            - rect : tuple, optional (the area to which the layout is confined,
            e.g., (left, bottom, right, top))

        Returns
        -------
        self : Viz
            The Viz object itself, allowing for method chaining.
        """
        self.fig.tight_layout(**kwargs)
        return self

    def suptitle(self, txt, **kwargs):
        """
        Sets the title for the entire figure.

        Parameters
        ----------
        txt : str
            The title text.
        kwargs : dict, optional
            Additional keyword arguments passed to `fig.suptitle()`, such as:
            - fontsize : int or float, optional (size of the title text)
            - fontweight : {'normal', 'bold', 'heavy', 'light', 'ultrabold', 'ultralight'}, optional
            - color : str, optional (e.g., 'red', 'blue', etc.)

        Returns
        -------
        self : Viz
            The Viz object itself, allowing for method chaining.
        """
        self.fig.suptitle(txt, **kwargs)
        return self

    def set_xticks(self, ticks, **kwargs):
        """
        Sets the ticks on the x-axis.

        Parameters
        ----------
        ticks : list
            A list of positions where ticks should appear on the x-axis.
        kwargs : dict, optional
            Additional keyword arguments passed to `ax.set_xticks()`, such as:
            - minor : bool, optional (if True, the minor ticks are set instead of the major ones)

        Returns
        -------
        self : Viz
            The Viz object itself, allowing for method chaining.
        """
        self.ax.set_xticks(ticks, **kwargs)
        return self

    def set_yticks(self, ticks, **kwargs):
        """
        Sets the ticks on the y-axis.

        Parameters
        ----------
        ticks : list
            A list of positions where ticks should appear on the y-axis.
        kwargs : dict, optional
            Additional keyword arguments passed to `ax.set_yticks()`, such as:
            - minor : bool, optional (if True, the minor ticks are set instead of the major ones)

        Returns
        -------
        self : Viz
            The Viz object itself, allowing for method chaining.
        """
        self.ax.set_yticks(ticks, **kwargs)
        return self

    def invert_x(self):
        """
        Inverts the x-axis.

        Returns
        -------
        self : Viz
            The Viz object itself, allowing for method chaining.
        """
        self.ax.invert_xaxis()
        return self

    def invert_y(self):
        """
        Inverts the y-axis.

        Returns
        -------
        self : Viz
            The Viz object itself, allowing for method chaining.
        """
        self.ax.invert_yaxis()
        return self

    def set_xlim(self, *args, **kwargs):
        """
        Sets the limits for the x-axis.

        Parameters
        ----------
        args : tuple
            The limits to set as (min, max).
        kwargs : dict, optional
            Additional keyword arguments passed to `ax.set_xlim()`, such as:
            - xmin : float, optional (minimum limit for x-axis)
            - xmax : float, optional (maximum limit for x-axis)

        Returns
        -------
        self : Viz
            The Viz object itself, allowing for method chaining.
        """
        self.ax.set_xlim(*args, **kwargs)
        return self

    def set_ylim(self, *args, **kwargs):
        """
        Sets the limits for the y-axis.

        Parameters
        ----------
        args : tuple
            The limits to set as (min, max).
        kwargs : dict, optional
            Additional keyword arguments passed to `ax.set_ylim()`, such as:
            - ymin : float, optional (minimum limit for y-axis)
            - ymax : float, optional (maximum limit for y-axis)

        Returns
        -------
        self : Viz
            The Viz object itself, allowing for method chaining.
        """
        self.ax.set_ylim(*args, **kwargs)
        return self

    def annotate(self, *args, **kwargs):
        """
        Adds an annotation to the plot.

        Parameters
        ----------
        args : tuple
            The annotation arguments, typically (text, xy).
        kwargs : dict, optional
            Additional keyword arguments passed to `ax.annotate()`, such as:
            - xytext : tuple, optional (position of annotation text)
            - arrowprops : dict, optional (properties of the arrow, e.g., {'arrowstyle': '->'})
            - fontsize : int, optional (font size of the annotation text)

        Returns
        -------
        self : Viz
            The Viz object itself, allowing for method chaining.
        """
        self.ax.annotate(*args, **kwargs)
        return self

    def style(self, style_name="seaborn-v0_8-whitegrid"):
        """
        Applies a matplotlib style to the plot.

        Parameters
        ----------
        style_name : str, optional, default='seaborn-v0_8-whitegrid'
            The style to apply. For example, 'seaborn-darkgrid', 'ggplot', etc.

        Returns
        -------
        self : Viz
            The Viz object itself, allowing for method chaining.
        """
        plt.style.use(style_name)
        return self

    def figsize(self, size):
        """
        Sets the figure size.

        Parameters
        ----------
        size : tuple
            The size of the figure as (width, height) in inches.

        Returns
        -------
        self : Viz
            The Viz object itself, allowing for method chaining.
        """
        self.fig.set_size_inches(*size, forward=True)
        return self

    def aspect(self, value="auto"):
        """
        Sets the aspect ratio of the plot.

        Parameters
        ----------
        value : str or float, optional, default='auto'
            The aspect ratio to set:
            - 'auto' (default): automatic aspect ratio based on the data
            - 'equal': equal scaling on both axes
            - float: fixed aspect ratio, e.g., 1.0 for equal scaling
            - 'scaled': scaled based on the data range

        Returns
        -------
        self : Viz
            The Viz object itself, allowing for method chaining.
        """
        self.ax.set_aspect(value)
        return self


class _PlotMixin:

    def plot(self, *args, **kwargs):
        """
        Plots data on the axis.

        Parameters
        ----------
        args : tuple
            The data to plot. The first element is typically the x-data,
            and the second is the y-data.
        kwargs : dict, optional
            Additional keyword arguments passed to `ax.plot()`, such as:
            - label : str, optional (label for the plot, used in legend)
            - linestyle : {'-', '--', '-.', ':'}, optional
            - color : str, optional (e.g., 'red', 'blue', etc.)
            - marker : {'o', 'x', 's', '^', etc.}, optional (marker style)
            - linewidth : float, optional (line thickness)

        Returns
        -------
        self : Viz
            The Viz object itself, allowing for method chaining.
        """
        self.ax.plot(*args, **kwargs)
        return self

    def scatter(self, *args, **kwargs):
        """
        Creates a scatter plot.

        Parameters
        ----------
        args : tuple
            The data to plot as scatter. The first element is typically
            the x-data, and the second is the y-data.
        kwargs : dict, optional
            Additional keyword arguments passed to `ax.scatter()`, such as:
            - color : str, optional (e.g., 'red', 'blue', etc.)
            - marker : {'o', 'x', 's', '^', etc.}, optional (marker style)
            - s : scalar or array-like, optional (size of markers)
            - alpha : float, optional (transparency, from 0 to 1)

        Returns
        -------
        self : Viz
            The Viz object itself, allowing for method chaining.
        """
        self.ax.scatter(*args, **kwargs)
        return self

    def bar(self, *args, **kwargs):
        """
        Creates a bar plot.

        Parameters
        ----------
        args : tuple
            The data to plot as bars. The first element is the x-data (positions),
            and the second is the y-data (height).
        kwargs : dict, optional
            Additional keyword arguments passed to `ax.bar()`, such as:
            - color : str, optional (e.g., 'red', 'blue', etc.)
            - width : float, optional (width of bars)
            - align : {'center', 'edge'}, optional (alignment of bars)

        Returns
        -------
        self : Viz
            The Viz object itself, allowing for method chaining.
        """
        self.ax.bar(*args, **kwargs)
        return self

    def hlines(self, *args, **kwargs):
        """
        Draws horizontal lines across the plot.

        Parameters
        ----------
        args : tuple
            Arguments passed to `ax.hlines()`, typically:
            - y : scalar or array-like (y positions of the lines)
            - xmin : scalar, optional (left limit for the line)
            - xmax : scalar, optional (right limit for the line)
        kwargs : dict, optional
            Additional keyword arguments passed to `ax.hlines()`, such as:
            - color : str, optional (line color)
            - linewidth : float, optional (thickness of the line)
            - linestyle : {'-', '--', '-.', ':'}, optional (line style)

        Returns
        -------
        self : Viz
            The Viz object itself, allowing for method chaining.
        """
        self.ax.hlines(*args, **kwargs)
        return self

    def vlines(self, *args, **kwargs):
        """
        Draws vertical lines across the plot.

        Parameters
        ----------
        args : tuple
            Arguments passed to `ax.vlines()`, typically:
            - x : scalar or array-like (x positions of the lines)
            - ymin : scalar, optional (bottom limit for the line)
            - ymax : scalar, optional (top limit for the line)
        kwargs : dict, optional
            Additional keyword arguments passed to `ax.vlines()`, such as:
            - color : str, optional (line color)
            - linewidth : float, optional (thickness of the line)
            - linestyle : {'-', '--', '-.', ':'}, optional (line style)

        Returns
        -------
        self : Viz
            The Viz object itself, allowing for method chaining.
        """
        self.ax.vlines(*args, **kwargs)
        return self

    def contour(self, *args, **kwargs):
        """
        Creates a contour plot.

        Parameters
        ----------
        args : tuple
            The contour data, typically (X, Y, Z) where Z represents the contour levels.
        kwargs : dict, optional
            Additional keyword arguments passed to `ax.contour()`, such as:
            - levels : int or array-like, optional (specific contour levels)
            - colors : str or array-like, optional (colors for the contours)
            - linewidths : float, optional (width of contour lines)

        Returns
        -------
        self : Viz
            The Viz object itself, allowing for method chaining.
        """
        self.ax.contour(*args, **kwargs)
        return self

    def add_subplot(self, *args, **kwargs):
        """
        Adds a new subplot to the figure.

        Parameters
        ----------
        args : tuple
            Arguments for `fig.add_subplot()`, such as (nrows, ncols, index).
        kwargs : dict, optional
            Additional keyword arguments passed to `fig.add_subplot()`.

        Returns
        -------
        Viz
            A new Viz object wrapping the new subplot.
        """
        ax = self.fig.add_subplot(*args, **kwargs)
        return Viz(ax, self.fig)


class Viz(_PlotMixin, _LayoutMixin, _VizCore):
    """
    Viz class for plotting on a matplotlib axis.

    Parameters
    ----------
    ax : matplotlib.axes.Axes
        The axis on which the plot will be drawn.
    fig : matplotlib.figure.Figure, optional
        The figure containing the axis. Defaults to None, in which case ax.figure is used.

    Methods
    -------
    add_subplot(*args, **kwargs)
        Adds a new subplot to the figure.
    """

    def __init__(self, ax=None, fig=None):
        """
        Initializes the Viz object with a given axis and optional figure.

        Parameters
        ----------
        ax : matplotlib.axes.Axes
            The axis on which the plot will be drawn.
        fig : matplotlib.figure.Figure, optional
            The figure containing the axis (default is None, which means it uses ax.figure).
        """
        if ax is None:
            fig, ax = plt.subplots()
        self.ax = ax
        self.fig = fig or ax.figure

    def __getattr__(self, attr):
        """
        Retrieves attributes of the underlying axis.

        Parameters
        ----------
        attr : str
            The name of the attribute to retrieve.

        Returns
        -------
        method : function
            The method of the underlying axis for the given attribute.
        """
        if hasattr(self.ax, attr):

            def method(*args, **kwargs):
                result = getattr(self.ax, attr)(*args, **kwargs)
                return self if result is None else result

            return method
        raise AttributeError(f"'PlotWrapper' has no attribute '{attr}'")

    def __dir__(self):
        """
        Returns a list of the attributes and methods available for the Viz
        object.
        """
        return sorted(set(super().__dir__()) | set(dir(self.ax)))

    def __enter__(self):
        """
        Initializes the Viz object for use in a context manager (e.g., with
        `with` statement).
        """
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Displays the plot when exiting a context manager.
        """
        self.show()

    def __getitem__(self, key):
        """
        Retrieves the item from the axis using the provided key.

        Parameters
        ----------
        key : index or key
            The key or index for the item.

        Returns
        -------
        item : object
            The item from the axis corresponding to the key.
        """
        return self.ax[key]

