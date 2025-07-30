"""
Python equivalent of obspy FloatWithUncertaintiesFixedUnit class
"""
# Standard library modules
import warnings
import logging

# Non-standard modules
from obspy.core.util.obspy_types import (FloatWithUncertaintiesFixedUnit,
                                         FloatWithUncertaintiesAndUnit)

from .functions import verify_dict_is_empty

warnings.simplefilter("once")
warnings.filterwarnings("ignore", category=DeprecationWarning)
logger = logging.getLogger("obsinfo")


class FloatWithUncert(object):
    """
    Python equivalent of obspy :class:`FloatWithUncertaintiesFixedUnit` and
    :class:`FloatWithUncertaintiesAndUnit`

    Attributes:
        value (float): float value
        uncertainty (float): uncertainty in value
        measurement_method (str): measurement method
    """

    def __init__(self, value, uncertainty=None, measurement_method=None,
                 unit=None):
        self.value = value
        self.uncertainty = uncertainty
        self.measurement_method = measurement_method
        self.unit = unit

    @classmethod
    def from_dict(cls, attributes_dict):
        """
        Create object and assign attributes from attributes_dict.

        Args:
            attributes_dict (dict or :class:`ObsMetadata`): dict with
                relevant keys
        """
        obj =  cls(attributes_dict.pop('value'),        # required
                   attributes_dict.pop('uncertainty', None),
                   attributes_dict.pop('measurement_method', None),
                   attributes_dict.pop('unit', None))
        verify_dict_is_empty(attributes_dict)
        return obj

    def __str__(self, indent=0, n_subclasses=0):
        """ Writes everything out, one line, no subclasses """
        s = 'FloatWithUncert: {} +- {}'.format(self.value, self.uncertainty)
        if self.unit is not None:
            s += f' {self.unit}'
        if self.measurement_method is not None:
            s += f', measurement_method = {self.measurement_method}'
        return s

    def __repr__(self, no_title=False):
        """
        Args:
            no_title (bool): don't surround dict with 'FloatWithUncert()'
        """
        args = [f"'value': {self.value}"]
        if self.uncertainty:
            args.append(f"'uncertainty': {self.uncertainty}")
        if self.measurement_method:
            args.append(f"'measurement_method': '{self.measurement_method}'")
        if self.unit:
            args.append(f"'unit': '{self.unit}'")
        dict_string = '{' + ", ".join(args) + '}'
        if no_title:
            return dict_string
        return 'FloatWithUncert(' + dict_string + ')'

    def to_obspy(self):
        """
        Return obspy object:
          - :class:`FloatWithUncertaintiesFixedUnit` if unit=None
          - :class:`FloatWithUncertaintiesAndUnit` otherwise
        """
        if self.unit is None:
            return FloatWithUncertaintiesFixedUnit(
                value=self.value,
                lower_uncertainty=self.uncertainty,
                upper_uncertainty=self.uncertainty,
                measurement_method=self.measurement_method)
        else:
            return FloatWithUncertaintiesAndUnit(
                value=self.value,
                lower_uncertainty=self.uncertainty,
                upper_uncertainty=self.uncertainty,
                measurement_method=self.measurement_method,
                unit=self.unit)
