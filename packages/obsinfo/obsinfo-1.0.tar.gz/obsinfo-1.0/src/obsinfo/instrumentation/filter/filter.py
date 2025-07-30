"""
Filter class and subclasses
"""
# Standard library modules
import logging

from .poles_zeros import PolesZeros
from .analog import Analog
from .digital import Digital
from .AD_conversion import ADConversion
from .FIR import FIR
from .response_list import ResponseList
from .coefficients import Coefficients
from .polynomial import Polynomial
from ...obsmetadata import ObsMetadata

logger = logging.getLogger("obsinfo")


class Filter(object):
    """
    Filter is a gateway to the other filter classes
    """
    @staticmethod
    def construct(attributes_dict, stage_sequence_number, stage_name,
                  sensitivity_gain_frequency=1.):
        """
        Constructs an appropriate Filter subclass from an attributes_dict

        Args:
            attributes_dict (dict or list of dicts): information file
                dict for stages
            stage_sequence_number (int): sequence_number of corresponding stage.
            stage_name (str): name of corresponding stage. Used for reporting only
            sensitivity_gain_frequency (float): frequency at which gain was
                specified.
                Used for PoleZeros Normalization factor/frequency
        Returns:
            (:class:`.Filter`): object of the adequate filter subclass
        Raises:
            (TypeError): if filter type is not valid
        """
        logger.debug('in Filter.construct()')
        if attributes_dict is None:
            msg = "No attributes in filter"
            logger.error(msg)
            raise TypeError(msg)
        if not isinstance(attributes_dict, ObsMetadata):
            attributes_dict = ObsMetadata(attributes_dict)

        stage_description = f'#{stage_sequence_number}'
        if stage_name is not None:
                stage_description += f' ("{stage_name}")'

        if "type" not in attributes_dict:
            msg = f'No "type" specified for filter in stage {stage_description}'
            logger.error(msg)
            raise TypeError(msg)
        else:
            args = (attributes_dict, stage_description)
            filter_type = attributes_dict.get('type', None)
            if filter_type == 'PolesZeros':
                attributes_dict['sensitivity_gain_frequency'] = sensitivity_gain_frequency
                obj = PolesZeros(*args)
            elif filter_type == 'FIR':
                obj = FIR(*args)
            elif filter_type == 'Coefficients':
                obj = Coefficients(*args)
            elif filter_type == 'ResponseList':
                obj = ResponseList(*args)
            elif filter_type == 'ADCONVERSION':
                obj = ADConversion(*args)
            elif filter_type == 'ANALOG':
                attributes_dict['sensitivity_gain_frequency'] = sensitivity_gain_frequency
                obj = Analog(*args)
            elif filter_type == 'DIGITAL':
                obj = Digital(*args)
            elif filter_type == 'Polynomial':
                obj = Polynomial(*args)
            else:
                msg = (f'Unknown Filter type: "{filter_type}" in '
                       'stage #{stage_id}')
                logger.error(msg)
                raise TypeError(msg)
        return obj
