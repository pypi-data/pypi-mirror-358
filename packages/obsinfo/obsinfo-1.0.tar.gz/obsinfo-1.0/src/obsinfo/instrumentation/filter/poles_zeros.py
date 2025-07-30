"""
Filter class and subclasses
"""
# Standard library modules
import math as m
import logging

# Non-standard modules
from .filter_template import FilterTemplate
from ...helpers import str_indent

logger = logging.getLogger("obsinfo")


class PolesZeros(FilterTemplate):
    """
    PolesZeros filter

    Attributes:
        transfer_function_type (str): one of  'LAPLACE (RADIANS/SECOND)',
            'LAPLACE (HERTZ)','DIGITAL (Z-TRANSFORM)'
        poles (list of complex numbers)
        zeros (list of complex numbers)
        normalization_frequency (float)
        normalization_factor (float)
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
        self.transfer_function_type = attr_dict.pop(
            'transfer_function_type', 'LAPLACE (RADIANS/SECOND)')
        self.poles = [complex(x.replace(" ", ""))
                      for x in attr_dict.pop('poles', [])]
        self.zeros = [complex(x.replace(" ", ""))
                      for x in attr_dict.pop('zeros', [])]
        # sensitivity_gain_frequency is handed down by Filter superclass,
        # in case the normalization frequency is not specified
        self.normalization_frequency = attr_dict.pop('sensitivity_gain_frequency', 1.)
        if 'normalization_frequency' in attr_dict:  # Overrides sensitivity_gain_frequency
            self.normalization_frequency = attr_dict.pop('normalization_frequency')
        if self.normalization_frequency == 0:
            self.normalization_frequency = 1
        self.normalization_factor = attr_dict.pop('normalization_factor', None)
        self._validate_empty_attributes_dict(attr_dict)

        # poles and zeros should be lists of complex numbers
        if self.transfer_function_type not in ['LAPLACE (RADIANS/SECOND)',
                                               'LAPLACE (HERTZ)',
                                               'DIGITAL (Z-TRANSFORM)']:
            msg = (f'Illegal transfer_function_type in PolesZeros: '
                   f'"{self.transfer_function_type}" in stage #{stage_id}')
            logger.error(msg)
            raise TypeError(msg)

        # Set/calculate normalization factor
        if not (self.normalization_frequency and self.normalization_factor):
            self.normalization_factor = self.calc_normalization_factor(stage_id)

    def __str__(self, indent=0, n_subclasses=0):
        """
        Args:
            indent (int): number of extra characters to indent lines by
            n_subclasses (int): number of levels of subclass to print out
        """
        if n_subclasses < 0:
            return f'{type(self)}'
        s = super().__str__() + '\n'
        s += f'    {len(self.poles)} poles, {len(self.zeros)} zeros\n'
        s += f'    transfer_function_type: {self.transfer_function_type}\n'
        s += f'    normalization_frequency: {self.normalization_frequency:g}\n'
        s += f'    normalization_factor: {self.normalization_factor:g}'
        return str_indent(s, indent)

    def calc_normalization_factor(self, stage_id=-1, debug=False):
        """
        Calculate the normalization factor for a given set of poles-zeros

        The norm factor A0 is calculated such that

        .. parsed-literal::
                                  sequence_product_over_n(s - zero_n)
                       A0 * abs(—--------------------------------------) == 1
                                  sequence_product_over_m(s - pole_m)

            for s_f = i*2pi*f if the transfer function is Laplace in radians
                      i*f if the transfer function is Laplace in Hertz

        There is no calculation for the digital z-transform

        Returns:
            normalization factor as a float or None if not Laplace
        """
        if not self.normalization_frequency:
            msg = (f'No normalization frequency in {self.__class__.__name__} at stage "{stage_id}"')
            logger.error(msg)
            raise ValueError(msg)

        A0 = 1.0 + (1j * 0.0)
        if self.transfer_function_type == "LAPLACE (HERTZ)":
            s = 1j * self.normalization_frequency
        elif self.transfer_function_type == "LAPLACE (RADIANS/SECOND)":
            s = 1j * 2 * m.pi * self.normalization_frequency
        else:
            logger.warning("Don't know how to calculate normalization factor"
                           "for z-transform poles and zeros!")
            return None

        for p in self.poles:
            A0 *= (s - p)
        for z in self.zeros:
            A0 /= (s - z)

        logger.debug(f"poles={self.poles}, zeros={self.zeros}, s={s}, A0={A0}")

        A0 = abs(A0)
        return A0
