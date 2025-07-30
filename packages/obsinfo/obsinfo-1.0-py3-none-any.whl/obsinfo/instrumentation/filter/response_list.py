"""
Filter class and subclasses
"""
import logging

from .filter_template import FilterTemplate
from ...helpers import str_indent

logger = logging.getLogger("obsinfo")


class ResponseList(FilterTemplate):
    """
    ResponseList Filter

    Attributes:
        elements (list of lists): list of responses instead of function
            coefficients.  Each response is [freq, value, phase (deg)]
    """

    def __init__(self, attributes_dict, stage_id=-1):
        """
        Constructor

        Args:
            attributes_dict (dict or :class:`.ObsMetadata`): filter attributes
            stage_id (int): id of corresponding stage. Used for reporting only
        """
        logger.debug(f'in {self.__class__.__name__}.__init__()')
        super().__init__(attributes_dict, stage_id)
        self.elements = attributes_dict.pop('elements', [])
        self._validate_empty_attributes_dict(attributes_dict)

        # Validate attributes
        for element in self.elements:
            if not len(element) == 3:
                raise ValueError(f'ResponseList element {element} does not have 3 values')

    def __repr__(self):
        return f'          ResponseList("{self.elements}")'

    def __str__(self, indent=0, n_subclasses=0):
        """
        Args:
            indent (int): number of extra characters to indent lines by
            n_subclasses (int): unused
        """
        if n_subclasses < 0:
            return f'{type(self)}'
        s = super().__str__() + '\n'
        s += f'    {len(self.elements)} elements'
        return str_indent(s, indent)
