"""
Finite Impulse Response Filter
"""
# Standard library modules
import logging

from .filter_template import FilterTemplate
from ...helpers import str_indent

logger = logging.getLogger("obsinfo")


class FIR(FilterTemplate):
    """
    FIR Filter

    Attributes:
        symmetry (str): filter symmetry, one of "EVEN", "ODD", "NONE"
        coefficients (list of floats)
        coefficient_divisor (float)
        delay_samples (float)
    """
    def __init__(self, attributes_dict, stage_description):

        """
        Constructor

        Args:
            attributes_dict (dict): information file
                dictionaries for stages
            stage_description (str): id + name of corresponding stage,
                used for reporting only
        """
        logger.debug(f'in {self.__class__.__name__}.__init__()')
        super().__init__(attributes_dict)
        self.symmetry = attributes_dict.pop('symmetry', None)
        self.coefficients = attributes_dict.pop('coefficients', [])
        self.coefficient_divisor = attributes_dict.pop('coefficient_divisor', 1)
        self._validate_empty_attributes_dict(attributes_dict)
        self._validate_values(stage_description)

    @property
    def expanded_coefficients(self):
        """ Returns full coefficient list (symmetry=NONE)"""
        if self.symmetry == 'NONE':
            return self.coefficients
        elif self.symmetry == 'EVEN':
            return self.coefficients+self.coefficients[-1::-1]
        elif self.symmetry == 'ODD':
            return self.coefficients+self.coefficients[-2::-1]
        else:
            return ValueError(f'Unknown {self.symmetry=}')
    
    def _validate_values(self, stage_description):
        # Validate values
        if not self.delay_samples:
            msg = 'No delay.samples in FIR filter'
            logger.error(msg)
            raise TypeError(msg)

        if self.symmetry not in ['ODD', 'EVEN', 'NONE']:
            msg = f'Illegal FIR symmetry: "{self.symmetry} in stage #{stage_id}"'
            logger.error(msg)
            raise TypeError(msg)

        sum_coeff = 0
        coeff_cnt = 0
        if len(self.coefficients) > 0:
            for coeff in self.coefficients:
                sum_coeff += coeff
                coeff_cnt += 1
            if self.symmetry == 'EVEN':
                sum_coeff *= 2.
                coeff_cnt *= 2
            if self.symmetry == 'ODD':
                sum_coeff += sum_coeff - self.coefficients[-1]
                coeff_cnt += coeff_cnt - 1
            norm_coeff = sum_coeff / self.coefficient_divisor
            norm_coeff = round(norm_coeff, 2)  # check up to two decimal places
            # last conditional verifies that there is at least one coeff
            if norm_coeff != 1:
                logger.warning(f'Sum of {coeff_cnt} coefficients in stage '
                               f'{stage_description} is {norm_coeff}, not 1 ')

    def __str__(self, indent=0, n_subclasses=0):
        if n_subclasses < 0:
            return f'{type(self)}'
        s = super().__str__() + '\n'
        s += f"    symmetry: {self.symmetry}\n"
        s += f"    coefficient_divisor: {self.coefficient_divisor}\n"
        s += f"    {len(self.coefficients)} coefficients\n"
        return str_indent(s, indent)
