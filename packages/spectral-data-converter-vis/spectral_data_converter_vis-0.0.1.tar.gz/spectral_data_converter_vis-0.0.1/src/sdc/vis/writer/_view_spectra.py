import argparse
import matplotlib.pyplot as plt
from typing import List

from wai.logging import LOGGING_WARNING

from sdc.api import Spectrum2D, BatchWriter

LEGEND_LOCATIONS = [
    'best',
    'upper right',
    'upper left',
    'lower left',
    'lower right',
    'right',
    'center left',
    'center right',
    'lower center',
    'upper center',
    'center',
]


class ViewSpectra(BatchWriter):

    def __init__(self, title: str = None, legend: bool = None, legend_loc: str = None,
                 logger_name: str = None, logging_level: str = LOGGING_WARNING):
        """
        Initializes the display.

        :param title: the title for the plot
        :type title: str
        :param legend: whether to display the legend
        :type legend: bool
        :param legend_loc: where to place the legend
        :type legend_loc: str
        :param logger_name: the name to use for the logger
        :type logger_name: str
        :param logging_level: the logging level to use
        :type logging_level: str
        """
        super().__init__(logger_name=logger_name, logging_level=logging_level)
        self.title = title
        self.legend = legend
        self.legend_loc = legend_loc

    def name(self) -> str:
        """
        Returns the name of the handler, used as sub-command.

        :return: the name
        :rtype: str
        """
        return "view-spectra"

    def description(self) -> str:
        """
        Returns a description of the writer.

        :return: the description
        :rtype: str
        """
        return "Displays the spectra in a plot."

    def _create_argparser(self) -> argparse.ArgumentParser:
        """
        Creates an argument parser. Derived classes need to fill in the options.

        :return: the parser
        :rtype: argparse.ArgumentParser
        """
        parser = super()._create_argparser()
        parser.add_argument("-t", "--title", type=str, help="The title for the plot.", required=False, default=None)
        parser.add_argument("--legend", action="store_true", help="Whether to display the legend.")
        parser.add_argument("--legend_loc", choices=LEGEND_LOCATIONS, help="The location for the legend.", required=False, default="best")
        return parser

    def _apply_args(self, ns: argparse.Namespace):
        """
        Initializes the object with the arguments of the parsed namespace.

        :param ns: the parsed arguments
        :type ns: argparse.Namespace
        """
        super()._apply_args(ns)
        self.title = ns.title
        self.legend = ns.legend
        self.legend_loc = ns.legend_loc

    def accepts(self) -> List:
        """
        Returns the list of classes that are accepted.

        :return: the list of classes
        :rtype: list
        """
        return [Spectrum2D]

    def write_batch(self, data):
        """
        Saves the data in one go.

        :param data: the data to write
        :type data: Iterable
        """
        if len(data) == 0:
            return

        x = data[0].spectrum.waves
        for sp in data:
            y = sp.spectrum.amplitudes
            plt.plot(x, y, label=sp.spectrum.id)
        if self.title is not None:
            plt.title(self.title)
        if self.legend:
            plt.legend(loc=self.legend_loc)
        plt.show()
