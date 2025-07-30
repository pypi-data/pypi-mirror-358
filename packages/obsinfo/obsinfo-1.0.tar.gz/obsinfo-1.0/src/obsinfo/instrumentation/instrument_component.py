"""
InstrumentComponent class and subclasses Sensor, Preamplifier, Datalogger.
Equipment class
"""
# Standard library modules
import logging

# Non-standard modules
from obspy.core.inventory.response import Response as obspy_Response, InstrumentSensitivity

# obsinfo
from .stages import Stages
from .equipment import Equipment
from ..obsmetadata import (ObsMetadata)
from ..helpers import str_indent, str_list_str, verify_dict_is_empty

logger = logging.getLogger("obsinfo")


class InstrumentComponent(object):
    """
    InstrumentComponent class. Superclass of all component classes.
    No obspy/StationXML equivalent, because they only specify the whole
    sensor+amplifier+datalogger system

    Attributes:
        equipment (:class:`Equipment`)
        stages (:class:`Stages`)
        obspy_equipment (:class:`obspy_Equipment`)
        configuration_description (str): description of configuration to be added
            to equipment description
    """

    def __init__(self, attributes_dict, higher_modifs={}):
        """
        Creator.

        Args:
            attributes_dict (dict or :class:`ObsMetadata`): InstrumentComponent
                attributes
            higher_modifs (dict or :class:`ObsMetadata`): modifications
                inherited from instrumentation
        """
        if not attributes_dict:
            msg = 'No attributes_dict'
            logger.error(msg)
            raise TypeError(msg)
        if not isinstance(attributes_dict, ObsMetadata):
            attributes_dict = ObsMetadata(attributes_dict)

        # Remove elements to be processed in Stages()
        higher_stage_modifications = ObsMetadata(attributes_dict.pop('stage_modifications', {}))
        if 'stage_modifications' in higher_modifs:
            higher_stage_modifications.safe_update(higher_modifs.pop('stage_modifications'))

        # Put shortcuts in the right place:
        if 'serial_number' in attributes_dict:
            attributes_dict.safe_update(
                {'modifications':
                    {'equipment':
                        {'serial_number': attributes_dict.pop('serial_number')}
                }},
                warn_crush=True)
        if 'serial_number' in higher_modifs:
            higher_modifs.safe_update(
                {'modifications':
                    {'equipment':
                        {'serial_number': higher_modifs.pop('serial_number')}
                }},
                warn_crush=True)

        # Get base-configured-modified element
        base_dict = attributes_dict.get_configured_modified_base(higher_modifs)
        
        if 'notes' in base_dict:
            del base_dict['notes']

        self.equipment = Equipment(base_dict.pop('equipment', None))
        self.configuration = base_dict.pop('configuration', None)
        self.configuration_description = base_dict.pop('configuration_description', self.configuration)
        stage_modifications = ObsMetadata(base_dict.pop('stage_modifications', {}))
        stage_modifications.safe_update(higher_stage_modifications, warn_crush=True)
        self.stages = Stages(base_dict.pop('stages', []), {'stage_modifications': stage_modifications},
                             base_dict.get('correction', None))
        self.equipment.calibration_dates += self.stages.calibration_dates
        logger.info('Instrument_Component has {len(self.stages)} stages')
        self._error_check(self.stages)
        if self.configuration_description is not None:
            self.equipment.description += ' [config: {}]'.format(
                self.configuration_description)
        # self.obspy_equipment = self.equipment.to_obspy()
        self.base_dict = base_dict  # leftovers for specific components

    @property
    def input_units(self):
        return self.stages[0].input_units

    @property
    def output_units(self):
        return self.stages[-1].output_units

    @property
    def gain_frequency(self):
        return self.stages[0].gain_frequency

    @property
    def instrument_sensitivity(self):
        if self.input_units.upper() not in ('M', 'M/S', 'M/S^2', 'M/S**2'):
            iu = 'M/S'
        else:
            iu = self.input_units
        sens = InstrumentSensitivity(1, self.gain_frequency,
                                     iu, self.output_units)
        resp = obspy_Response(instrument_sensitivity=sens,
                              response_stages=[x.to_obspy()
                                               for x in self.stages])
        resp.recalculate_overall_sensitivity(self.gain_frequency)
        return resp.instrument_sensitivity

    def __repr__(self):
        s = ''
        if self.equipment.description:
            s += f', description="{self.equipment.description}"'
        if self.stages is not None:
            s += f'Response stages: {len(self.stages)}'
        return s

    def __str__(self, indent=0, n_subclasses=0):
        """
        Information common to all instrument_components, to be appended
        Args:
            indent (int): number of extra characters to indent lines by
            n_subclasses (int): number of levels of subclass to print out
        """
        kwargs = {'indent': 4, 'n_subclasses': n_subclasses-1}
        s = f'\n    equipment: {self.equipment.__str__(**kwargs)}'
        if self.stages is not None:
            s += f'\n    stages: {self.stages.__str__(**kwargs)}'
        return s

    def _error_check(self, stages):
        """Some of these checks seem redundant"""
        if stages is None:
            msg = f'stages is None {type(self)}'
            logger.warning(msg)
        elif not stages:
            msg = f'No response stages in {type(self)}'
            logger.error(msg)
            raise TypeError(msg)
        elif len(stages) == 0:
            msg = f'len(stages) == 0 in {type(self)}'
            logger.error(msg)
            raise TypeError(msg)


class Sensor(InstrumentComponent):
    """
    Sensor Instrument Component. No obspy equivalent

    Attributes:
        equipment (:class:`.Equipment`): Equipment information
        seed_band_base (str)): SEED band code ("broadband", "shortperiod",
            or a single letter). "broadband" and "shortperiod" will be
            modified by obsinfo to correspond to output sample rate
            (<http://docs.fdsn.org/projects/source-identifiers/en/v1.0/channel-codes.html>`
        seed_instrument_code(str (len 1)): SEED instrument code, determined
            by `FDSN standard <http://docs.fdsn.org/projects/source-
            identifiers/en/v1.0/channel-codes.html>`
        stages (:class:`Stages`): channel modifications
            inherited from station
    """
    def __init__(self, attributes_dict, higher_modifs={}):
        """
        Create Sensor instance from an attributes_dict

        Args:
            attributes_dict (dict or :class:`ObsMetadata`): InstrumentComponent
                attributes
            higher_modifs (dict or :class:`ObsMetadata`): modifications
                inherited from instrumentation
        """
        logger.info('Creating Sensor()')
        super().__init__(attributes_dict, higher_modifs)
        seed_dict = self.base_dict.pop('seed_codes', {})
        self.seed_band_base = seed_dict.get('band', None)
        self.seed_instrument_code = seed_dict.get('instrument', None)
        verify_dict_is_empty(self.base_dict)
        del self.base_dict

    def __str__(self, indent=0, n_subclasses=0):
        if n_subclasses < 0:
            return f'{type(self)}'
        s = f'{self.__class__.__name__}:'
        s += f"\n    band: {self.seed_band_base}"
        s += f"\n    instrument code: {self.seed_instrument_code}"
        s += super().__str__(indent, n_subclasses)
        return str_indent(s, indent)


class Datalogger(InstrumentComponent):
    """
    Datalogger Instrument Component.

    Obspy ``Datalogger`` only contains elements of :class:`Equipment`, the 
    rest is in :class:`Response`

    Attributes:
        equipment (:class:`Equipment`): equipment attributes
        stages (:class:`Stages`): channel modifications
            inherited from station
        sample_rate (float): sample rate of given configuration. Checked
            against actual sample rate
        correction (float or None): the delay correction of the
            component. If a float, it is applied to the last stage and the
            other stage corrections are set to 0.  If None, each stage's
            correction is set equal to its delay
    """
    def __init__(self, attributes_dict, higher_modifs={}):
        """
        Args:
            attributes_dict (dict or :class:`ObsMetadata`): InstrumentComponent
                attributes
            higher_modifs (dict or :class:`ObsMetadata`): modifications
                inherited from instrumentation
        Returns:
            (:class:`Datalogger`)
        """
        logger.info('Creating Datalogger()')
        super().__init__(attributes_dict, higher_modifs)
        self.sample_rate = self.base_dict.pop('sample_rate', None)
        self.correction = self.base_dict.pop('correction', 0)
        verify_dict_is_empty(self.base_dict)
        del self.base_dict

    def __str__(self, indent=0, n_subclasses=0):
        if n_subclasses < 0:
            return f'{type(self)}'
        s = f'{self.__class__.__name__}:'
        s += f"\n    sample_rate: {self.sample_rate}"
        s += f"\n    correction: {self.correction}"
        s += super().__str__(indent, n_subclasses)
        return str_indent(s, indent)


class Preamplifier(InstrumentComponent):
    """
    Preamplifier Instrument Component. No obspy equivalent

      Attributes:
        equipment (:class:`Equipment`): Equipment information
        stages (:class:`Stages`): channel modifications inherited from station
        configuration_description (str): the configuration description that was
                                         selected, added to equipment description
    """
    def __init__(self, attributes_dict, higher_modifs={}):
        """
        Args:
            attributes_dict (dict or :class:`ObsMetadata`): InstrumentComponent
                attributes
            higher_modifs (dict or :class:`ObsMetadata`): modifications
                inherited from instrumentation
        """
        logger.info('Creating Preamplifier()')
        if not attributes_dict:
            return None   # It is acceptable to have no preamplifier
        super().__init__(attributes_dict, higher_modifs)
        verify_dict_is_empty(self.base_dict)
        del self.base_dict

    def __str__(self, indent=0, n_subclasses=0):
        if n_subclasses < 0:
            return f'{type(self)}'
        s = f'{self.__class__.__name__}:'
        s += super().__str__(indent, n_subclasses)
        return str_indent(s, indent)

    def __repr__(self, indent=0, n_subclasses=0):
        s = super().__str__(indent, n_subclasses)
        return str_indent(s, indent)
