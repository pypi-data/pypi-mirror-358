"""
Polynomial Filter
"""
import logging

from .filter_template import FilterTemplate
from ...helpers import str_indent

logger = logging.getLogger("obsinfo")


class Polynomial(FilterTemplate):
    """
    Polynomial Filter Class (never tested)
    """

    def __init__(self, attr_dict, stage_id=-1):
        """
        Constructor

        Args:
            attr_dict (dict or :class`ObsMetadata`): filter attributes
           stage_id (int): id of corresponding stage. Used for reporting only
        """
        logger.debug(f'in {self.__class__.__name__}.__init__()')
        super().__init__(attr_dict, stage_id)
        self.frequency_lower_bound = attr_dict.pop('frequency_lower_bound', 0.)
        self.frequency_upper_bound = attr_dict.pop('frequency_upper_bound', 0.)
        self.approximation_lower_bound = attr_dict.pop('approximation_lower_bound', None)
        self.approximation_upper_bound = attr_dict.pop('approximation_upper_bound', None)
        self.maximum_error = attr_dict.pop('maximum_error', None)
        self.coefficients = attr_dict.pop('coefficients', [])
        self.approximation_type = attr_dict.pop('approximation_type', 'MACLAURIN')
        self._validate_empty_attributes_dict(attr_dict)

        if not self.approximation_type == "MACLAURIN":
            msg = f'Illegal approximation_type: "{self.approximation_type}"'
            logger.error(msg)
            raise TypeError(msg)

    def __str__(self, indent=0, n_subclasses=0):
        """
        Args:
            indent (int): number of extra characters to indent lines by
            n_subclasses (int): unused
        """
        if n_subclasses < 0:
            return f'{type(self)}'
        s = super().__str__() + '\n'
        s += f"    {len(self.coefficients)} coefficients\n"
        s += f"    Approximation type: {self.approximation_type}"
        if not (self.frequency_lower_bound == 0 and self.frequency_upper_bound==0):
            s += f"\n    Frequency bounds: {self.frequency_lower_bound} - {self.frequency_upper_bound}"
        if not (self.approximation_lower_bound is None and self.approximation_upper_bound is None):
            s += f"\n    Approximation bounds: {self.approximation_lower_bound} - {self.approximation_upper_bound}"
        if not (self.maximum_error is None):
            s += f"\n   Maximum error: {self.maximum_error}"
        return str_indent(s, indent)
