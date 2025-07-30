"""
Digital filter (subclass of Coefficents, which is subclass of Filter)
"""
# Standard library modules
import logging

from .coefficients import Coefficients
from ...helpers import str_indent

logger = logging.getLogger("obsinfo")


class Digital(Coefficients):
    """
    Digital Filter (Flat Coefficients filter)
    """
    def __init__(self, attributes_dict, stage_id=-1):
        """
        Constructor

        Args:
            attributes_dict (dict or :class:`.ObsMetadata`): filter attributes
            stage_id (int): id of corresponding stage. Used for reporting only
        """
        logger.debug(f'in {self.__class__.__name__}.__init__()')
        attributes_dict["transfer_function_type"] = 'DIGITAL'
        attributes_dict["numerator_coefficients"] = [1.0]
        attributes_dict["denominator_coefficients"] = []
        super().__init__(attributes_dict, stage_id)
        self._validate_empty_attributes_dict(attributes_dict)

    def __repr__(self):
        return 'Digital(attributes_dict, stage_id)'

    def __str__(self, indent=0, n_subclasses=0):
        if n_subclasses < 0:
            return f'{type(self)}'
        s = super().__str__()
        return str_indent(s, indent)

