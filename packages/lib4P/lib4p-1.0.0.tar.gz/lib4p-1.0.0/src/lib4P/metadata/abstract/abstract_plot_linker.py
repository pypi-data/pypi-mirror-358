from ..interface.plot_interface import IPlot
from ..interface.plot_linker_interface import IPlotLinker


class AbstractPlotLinker(IPlotLinker):
    """
    Abstract class defining various functions useful for binding a plot instance to another object instance.
    """

    def __init__(self):
        super().__init__()
        self._plot = None

    def link_plot(self, plot):
        """
        Links a plot to the current instance.

        Only one plot can be linked.

        :param plot: plot to link
        :type plot: Plot
        """
        if not isinstance(plot, IPlot):
            raise TypeError(f"Argument 'plot' must be of type {IPlot}, "
                            f"type {type(plot)} found")
        self._plot = plot

    def has_plot(self):
        """
        Returns True if a plot is linked to the current instance.

        :return: True if a plot is linked to the current instance
        :rtype: bool
        """
        return self._plot is not None

    def get_plot(self):
        """
        Returns the plot linked to the current instance (None if not linked).

        :return: plot linked to the current instance (None if not linked)
        :rtype: Plot or None
        """
        return self._plot
