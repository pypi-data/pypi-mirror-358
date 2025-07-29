import argparse
from typing import List, Iterable, Union

from seppl.io import locate_files
from seppl.placeholders import PlaceholderSupporter, placeholder_list
from wai.logging import LOGGING_WARNING
from wai.spectralio.nir import Reader as SReader

from sdc.api import Reader
from sdc.api import Spectrum2D


class NIRReader(Reader, PlaceholderSupporter):

    def __init__(self, source: Union[str, List[str]] = None, source_list: Union[str, List[str]] = None,
                 resume_from: str = None, instrument: str = None, format: str = None, keep_format: bool = None,
                 type_field: str = None, id_field: str = None, start: int = None, max: int = None,
                 logger_name: str = None, logging_level: str = LOGGING_WARNING):
        """
        Initializes the reader.

        :param source: the filename(s)
        :param source_list: the file(s) with filename(s)
        :param resume_from: the file to resume from (glob)
        :type resume_from: str
        :param instrument: the instrument name to use
        :type instrument: str
        :param format: the spectral format
        :type format: str
        :param keep_format: whether to keep the format determined by the reader
        :type keep_format: bool
        :param type_field: the field with the sample type
        :type type_field: str
        :param id_field: the field with the sample ID
        :type id_field: str
        :param start: the spectrum number to start loading from
        :type start: int
        :param max: the maximum number of spectra to load, None or -1 for unlimited
        :type max: int
        :param logger_name: the name to use for the logger
        :type logger_name: str
        :param logging_level: the logging level to use
        :type logging_level: str
        """
        super().__init__(instrument=instrument, format=format, keep_format=keep_format,
                         logger_name=logger_name, logging_level=logging_level)
        self.source = source
        self.source_list = source_list
        self.resume_from = resume_from
        self.type_field = type_field
        self.id_field = id_field
        self.start = start
        self.max = max
        self._inputs = None
        self._current_input = None

    def name(self) -> str:
        """
        Returns the name of the handler, used as sub-command.

        :return: the name
        :rtype: str
        """
        return "from-nir"

    def description(self) -> str:
        """
        Returns a description of the reader.

        :return: the description
        :rtype: str
        """
        return "Loads the spectra in FOSS NIR format."

    def _create_argparser(self) -> argparse.ArgumentParser:
        """
        Creates an argument parser. Derived classes need to fill in the options.

        :return: the parser
        :rtype: argparse.ArgumentParser
        """
        parser = super()._create_argparser()
        parser.add_argument("-i", "--input", type=str, help="Path to the NIR file(s) to read; glob syntax is supported; " + placeholder_list(obj=self), required=False, nargs="*")
        parser.add_argument("-I", "--input_list", type=str, help="Path to the text file(s) listing the NIR files to use; " + placeholder_list(obj=self), required=False, nargs="*")
        parser.add_argument("--resume_from", type=str, help="Glob expression matching the file to resume from, e.g., '*/012345.nir'", required=False)
        parser.add_argument("--type_field", type=str, help="Code|Field1|Field2|Field3|ID|[sample_type]", required=False, default="Code")
        parser.add_argument("--id_field", type=str, help="ID|Field1|Field2|Field3|[prefix]", required=False, default="ID")
        parser.add_argument("-s", "--start", type=int, help="The spectrum number to start loading from", required=False, default=1)
        parser.add_argument("-m", "--max", type=int, help="The maximum number of spectra to load, -1 for all", required=False, default=-1)
        return parser

    def _apply_args(self, ns: argparse.Namespace):
        """
        Initializes the object with the arguments of the parsed namespace.

        :param ns: the parsed arguments
        :type ns: argparse.Namespace
        """
        super()._apply_args(ns)
        self.source = ns.input
        self.source_list = ns.input_list
        self.resume_from = ns.resume_from
        self.type_field = ns.type_field
        self.id_field = ns.id_field
        self.start = ns.start
        self.max = ns.max

    def generates(self) -> List:
        """
        Returns the list of classes that get produced.

        :return: the list of classes
        :rtype: list
        """
        return [Spectrum2D]

    def initialize(self):
        """
        Initializes the processing, e.g., for opening files or databases.
        """
        super().initialize()
        if self.type_field is None:
            self.type_field = "Code"
        if self.id_field is None:
            self.id_field = "ID"
        if self.start is None:
            self.start = 1
        if self.max is None:
            self.max = -1
        self._inputs = locate_files(self.source, input_lists=self.source_list, fail_if_empty=True, default_glob="*.nir", resume_from=self.resume_from)

    def _compile_options(self) -> List[str]:
        """
        Compiles the options for initializing the underlying reader.

        :return: the list of options to use
        :rtype: list
        """
        result = super()._compile_options()
        result.extend(["--type-field", self.type_field])
        result.extend(["--id-field", self.id_field])
        result.append("--start=%s" % str(self.start))
        result.append("--max=%s" % str(self.max))
        return result

    def read(self) -> Iterable:
        """
        Loads the data and returns the items one by one.

        :return: the data
        :rtype: Iterable
        """
        self._current_input = self._inputs.pop(0)
        self.session.current_input = self._current_input
        self.logger().info("Reading from: " + str(self.session.current_input))

        reader = SReader()
        reader.options = self._compile_options()
        for sp in reader.read(self.session.current_input):
            yield Spectrum2D(source=self.session.current_input, spectrum=sp, spectrum_name=sp.id)

    def has_finished(self) -> bool:
        """
        Returns whether reading has finished.

        :return: True if finished
        :rtype: bool
        """
        return len(self._inputs) == 0
