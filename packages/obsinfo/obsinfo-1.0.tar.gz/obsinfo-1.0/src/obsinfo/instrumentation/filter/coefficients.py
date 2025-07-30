"""
Coefficients Filter
"""
import logging

from .filter_template import FilterTemplate
from ...helpers import str_indent

logger = logging.getLogger("obsinfo")


class Coefficients(FilterTemplate):
    """
    Coefficients Filter Class

    Attributes:
        transfer_function_type (str): one of "ANALOG (RADIANS/SECOND)",
            "ANALOG (HERTZ)", or "DIGITAL"
        numerator_coefficients (list of floats)
        denominator_coefficients (list of floats)
    """
    def __init__(self, attr_dict, stage_id=-1):
        """
        Constructor

        Args:
            attr_dict (dict or :class:`.ObsMetadata`): filter attributes
            stage_id (int): id of corresponding stage. Used for reporting only
        """
        logger.debug(f'in {self.__class__.__name__}.__init__()')
        super().__init__(attr_dict, stage_id)
        self.transfer_function_type = attr_dict.pop('transfer_function_type',
                                                    'DIGITAL')
        self.numerator_coefficients = attr_dict.pop('numerator_coefficients',
                                                    [1.])
        self.denominator_coefficients = attr_dict.pop('denominator_coefficients', [])
        self._validate_empty_attributes_dict(attr_dict)

        if self.transfer_function_type not in ["ANALOG (RADIANS/SECOND)",
                                               "ANALOG (HERTZ)",
                                               "DIGITAL"]:
            msg = f'Illegal transfer function type: "{self.transfer_function_type}"'
            logger.error(msg)
            raise TypeError(msg)

    def __repr__(self):
        s = '          Coefficients("Transfer Function Type='
        s += f'{self.transfer_function_type}", '
        s += f'Numerator={self.numerator_coefficients}, '
        s += f'Denominator={self.denominator_coefficients})'
        return s

    def __str__(self, indent=0, n_subclasses=0):
        if n_subclasses < 0:
            return f'{type(self)}'
        s = super().__str__() + '\n'
        s += f"    transfer_function_type: {self.transfer_function_type}\n"
        s += f"    {len(self.numerator_coefficients)} numerator coefficients\n"
        s += f"    {len(self.denominator_coefficients)} denominator coefficients"
        return str_indent(s, indent)
