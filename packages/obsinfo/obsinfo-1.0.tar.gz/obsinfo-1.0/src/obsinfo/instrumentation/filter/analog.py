"""
Analog Filter (subclass of PolesZeros)
"""
# Standard library modules
import logging

from .poles_zeros import PolesZeros
from ...helpers import str_indent

logger = logging.getLogger("obsinfo")


class Analog(PolesZeros):
    """
    Analog Filter (Flat PolesZeros filter)
    """
    def __init__(self, attributes_dict, stage_id=-1):
        """
        Constructor

        Args:
            attributes_dict (dict or :class:`.ObsMetadata`): filter attributes
            stage_id (int): id of corresponding stage. Used for reporting only
        """
        logger.debug(f'in {self.__class__.__name__}.__init__()')
        attributes_dict["transfer_function_type"] = "LAPLACE (RADIANS/SECOND)"
        attributes_dict["poles"] = []
        attributes_dict["zeros"] = []
        if not "normalization_factor" in attributes_dict:
            attributes_dict["normalization_factor"] = 1.0
        # if not "normalization_frequency" in attributes_dict:
        #     attributes_dict["normalization_frequency"] = 1.
        super().__init__(attributes_dict, stage_id)
        self._validate_empty_attributes_dict(attributes_dict)

        if not (self.normalization_frequency and self.normalization_factor):
            self.normalization_factor = 1.0

    def __repr__(self):
        return 'Analog(attributes_dict, stage_id)'

    def __str__(self, indent=0, n_subclasses=0):
        if n_subclasses < 0:
            return f'{type(self)}'
        s = super().__str__()
        return str_indent(s, indent)
