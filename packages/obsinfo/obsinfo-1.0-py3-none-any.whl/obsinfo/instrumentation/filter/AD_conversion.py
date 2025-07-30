"""
Filter class and subclasses
"""
# Standard library modules
import logging

import numpy as np

from .coefficients import Coefficients
from ...helpers import str_indent

logger = logging.getLogger("obsinfo")


class ADConversion(Coefficients):
    """
    ADConversion Filter (Flat Coefficients filter)

    Attributes:
        v_plus (float): A/D's input high voltage
        v_minus (float): A/D's input low voltage
        counts_dtype (str): counts data type (numpy dtype name, like 'int32',
            'uint32')
        counts_plus (dtype): A/D's input high counts
        counts_minus (dtype): A/D's input low counts
        delay_samples (float): number of samples that the filter delays an
            impulse
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
        # Pop these before super, or it will give an error.
        v_minus = float(attributes_dict.pop('v_minus'))
        v_plus = float(attributes_dict.pop('v_plus'))
        counts_minus = attributes_dict.pop('counts_minus')
        counts_plus = attributes_dict.pop('counts_plus')
        counts_dtype = attributes_dict.pop('counts_dtype')
        super().__init__(attributes_dict, stage_id)
        self._validate_empty_attributes_dict(attributes_dict)
        counts_minus, counts_plus = self._calc_counts(counts_minus, counts_plus, counts_dtype)
        self.gain = (counts_plus - counts_minus) / (v_plus - v_minus)
        self.v_plus = v_plus
        self.v_minus = v_minus
        self.counts_plus = counts_plus
        self.counts_minus = counts_minus
        self.counts_dtype = counts_dtype

    @staticmethod
    def _calc_counts(counts_minus, counts_plus, dtype):
        ACCEPTED_DTYPES =  ('uint16', 'uint24', 'uint32', 'int16', 'int24', 'int32')
        if dtype not in ACCEPTED_DTYPES:
            raise TypeError(f'{dtype=} not in {ACCEPTED_DTYPES}')
        if isinstance(counts_minus, str):
            if counts_minus[:2] in ('0x', '0X'): # shouldn't get 2nd but check anyway
                if (l:=len(counts_minus)-2) != (expct:=int(int(dtype[-2:])/4)):
                    raise ValueError(f'{dtype} {counts_minus=} has {l-2:d} digits, should have {expct:2}')
            counts_minus = eval(counts_minus)
        if isinstance(counts_plus, str):
            if counts_plus[:2] in ('0x', '0X'): # shouldn't get 2nd but check anyway
                if (l:=len(counts_plus)-2) != (expct:=int(int(dtype[-2:])/4)):
                    raise ValueError(f'{dtype} {counts_plus=} has {l-2:d} digits, should have {expct:d}')         
            counts_plus = eval(counts_plus)
        if dtype[:4] == 'uint':
            if counts_minus < 0:
                raise ValueError(f'{dtype} {counts_minus=} is less than zero')
            if dtype == 'uint16':
                hexmax = 0xFFFF
            elif dtype == 'uint24':
                hexmax= 0xFFFFFF
            elif dtype == 'uint32':
                hexmax = 0xFFFFFFFF
            else:
                raise TypeError(f'Unknown {dtype=}')
            if counts_plus > hexmax:
                raise ValueError(f'{dtype} {counts_plus=} > 0x{hexmax:x}')
        elif dtype[:3] == 'int':
            if dtype == 'int16':
                fun, hexmin, hexmax = ADConversion.s16, 0x8000, 0x7FFF
            elif dtype == 'int24':
                fun, hexmin, hexmax = ADConversion.s24, 0x800000, 0x7FFFFF
            elif dtype == 'int32':
                fun, hexmin, hexmax = ADConversion.s32, 0x80000000, 0x7FFFFFFF
            else:
                raise TypeError(f'Unknown {dtype=}')
            counts_minus = fun(counts_minus)
            counts_plus = fun(counts_plus)
            if counts_plus > fun(hexmax):
                raise ValueError(f'{dtype} {counts_plus=} > 0x{hexmax:x}')
            if counts_minus < fun(hexmin):
                raise ValueError(f'{dtype} {counts_minus=} < 0x{hexmin:x}')
        if counts_minus >= counts_plus:
            raise ValueError(f'{dtype} {counts_minus=} >= {counts_plus=}')
        return counts_minus, counts_plus

    @staticmethod
    def s16(value):
        return -(value & 0x8000) | (value & 0x7fff)

    @staticmethod
    def s24(value):
        return -(value & 0x800000) | (value & 0x7fffff)

    @staticmethod
    def s32(value):
        return -(value & 0x80000000) | (value & 0x7fffffff)

    def __str__(self, indent=0, n_subclasses=0):
        if n_subclasses < 0:
            return f'{type(self)}'
        s = super().__str__() + '\n'
        s += f'    v_plus: {self.v_plus}\n'
        s += f'    v_minus: {self.v_minus}\n'
        s += f'    counts_plus: {self.counts_plus}\n'
        s += f'    counts_minus: {self.counts_minus}\n'
        s += f'    CALCULATED GAIN: {self.gain}\n'
        s += f'    delay_samples: {self.delay_samples}'
        return str_indent(s, indent)

