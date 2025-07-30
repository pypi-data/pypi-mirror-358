"""
FilterTemplate class, used by all other filter classes
"""
# Standard library modules
import logging

logger = logging.getLogger("obsinfo")


class FilterTemplate(object):
    """
    FilterTemplate is superclass of all filter classes

    Attributes:
        type (str): filter type
        delay_samples (float): Samples that filter delays an impulse
            in digital filters
    """

    def __init__(self, attributes_dict, stage_id=-1):
        """
        Constructor

        Args:
            attributes_dict (dict or :class:`.ObsMetadata`): filter attributes
            stage_id (int): id of corresponding stage. Used for reporting only
        """
        logger.debug(f'in {self.__class__.__name__}.__init__()')
        self.delay_samples = attributes_dict.pop('delay.samples', None)
        self.delay_seconds = attributes_dict.pop('delay.seconds', None)
        self.resource_id = attributes_dict.pop('resource_id', None)
        self.stage_id = stage_id
        self.type = attributes_dict.pop('type', None)

    def _validate_empty_attributes_dict(self, attributes_dict):
        if not attributes_dict == {}:
            raise ValueError('attributes_dict has leftover keys: {}'
                             .format(list(attributes_dict.keys())))

    def __str__(self):
        s = f'{self.__class__.__name__}\n'
        s += f'    stage_id: {self.stage_id}'
        if self.delay_samples is not None:
            s += f'\n    delay_samples: {self.delay_samples}'
        if self.delay_seconds is not None:
            s += f'\n    delay_seconds: {self.delay_seconds}'
        return s
