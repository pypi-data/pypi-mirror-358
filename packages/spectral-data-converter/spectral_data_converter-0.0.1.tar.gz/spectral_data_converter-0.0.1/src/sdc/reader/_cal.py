from typing import Iterable

from wai.spectralio.cal import Reader as SReader

from sdc.api import Spectrum2D
from ._nir import NIRReader


class CALReader(NIRReader):

    def name(self) -> str:
        """
        Returns the name of the handler, used as sub-command.

        :return: the name
        :rtype: str
        """
        return "from-cal"

    def description(self) -> str:
        """
        Returns a description of the reader.

        :return: the description
        :rtype: str
        """
        return "Loads the spectra in FOSS CAL format."

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
