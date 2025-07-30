"""
Stages and Stage classes
"""
# Standard library modules
import warnings
import re
import logging

# Non-standard modules
from obspy.core.inventory.response import (
    PolesZerosResponseStage, FIRResponseStage,
    CoefficientsTypeResponseStage, ResponseListResponseStage,
    PolynomialResponseStage, ResponseListElement)
import obspy.core.util.obspy_types as obspy_types

# Local modules
from ..obsmetadata import ObsMetadata
from .filter import (Filter, PolesZeros, FIR, Coefficients, ResponseList,
                     Analog, Digital, ADConversion, Polynomial)
from ..helpers import str_indent, OIDates

warnings.simplefilter("once")
warnings.filterwarnings("ignore", category=DeprecationWarning)
logger = logging.getLogger("obsinfo")


class Stage(object):
    """
    Stage is a discrete portion of the response of the instrument

    Attributes:
        name (str): name of stage, if any
        description (str): description of stage
        input_units (str): validated in schema
        input_units_description (str)
        output_units (str): validated in schema
        output_units_description (str)
        gain (float): value of gain
        gain_frequency (float): frequency at which gain is measured
        filter (object of :class:`Filter`)
        stage_sequence_number: sequence number in total response, assigned
            later
        input_sample_rate (float): input sample rate in sps
        delay (float): delay in seconds of stage. If not present, will be
            calculated from delay from digital stages
        decimation_factor (float): decimation factor of stage
        decimation_offset (int): decimation offset (0 to decimation_factor-1, default=0)
        correction (float) : delay correction. Calculated from instrument
            delay correction
        polarity (str, either "+" or "-"): whether stage changes polarity
        resource_id (str)
        instrument_sensitivity (float): Not used, set to None. Sensitivity
            is calculated for the whole response.

    """
    def __init__(self, attributes_dict, higher_modifs=ObsMetadata({}),
                 correction=None, sequence_number=-1,
                 ext_config_name=None):
        """
        Args:
            attributes_dict (dict or :class:`ObsMetadata`): attributes of
                component
            higher_modifs (dict or :class:`ObsMetadata`):
                response modifications from higher level 
                (key = regex for stage #, value = modification dictionary)
            correction (float): used only for datalogger, it's the delay
                correction of the whole instrument
            sequence_number (int): sequence number, starting at 1. First
                assigned within component, then for the whole instrument
                response
           ext_config_name (str): higher-level configuration definition (overrides
                whatever is in self)
        """
        if attributes_dict is None:
            return None
        
        # input parameters, for __repr__
        self.inputs = {'attributes_dict': '<ObsMetadata>',
                       'higher_modifs': '<ObsMetadata>',
                       'correction': correction,
                       'sequence_number': sequence_number,
                       'ext_config_name': ext_config_name}
        if not higher_modifs:
                    self.inputs['higher_modifs'] = '{}'

        if not isinstance(attributes_dict, ObsMetadata):
            attributes_dict = ObsMetadata(attributes_dict)
        if not isinstance(higher_modifs, ObsMetadata):
            higher_modifs = ObsMetadata(higher_modifs)

        # put appropriate "stage_modifications" in "modifications"
        m = self._get_stage_modifications(
            attributes_dict.pop('stage_modifications', {}), sequence_number)
        if "modifications" in attributes_dict:
            attributes_dict['modifications'].safe_update(m)
        elif not m == {}:
            attributes_dict['modifications'] = m

        hm = self._get_stage_modifications(
            higher_modifs.pop('stage_modifications', {}), sequence_number)
        if "modifications" in higher_modifs:
            higher_modifs['modifications'].safe_update(hm)
        elif not hm == {}:
            higher_modifs['modifications'] = hm

        base_dict = attributes_dict.get_configured_modified_base(higher_modifs)

        self.name = base_dict.pop('name', None)  
        self.configuration = base_dict.pop('configuration', None)
        # CalibrationDates belongs in equipment, but is more logical to state
        # in stage, rely on equipment to look for it.    
        self.calibration_dates = OIDates(base_dict.pop('calibration_dates', []) )     
        self.configuration_description = base_dict.pop('configuration_description',
                                                       self.configuration)      
        self.description = base_dict.pop('description', '')
        if self.configuration_description is not None:
            if self.name is None:
                self.name = f'[config: {self.configuration_description}]'
            else:
                self.name += f' [config: {self.configuration_description}]'

        gd = base_dict.pop('gain', None)
        if gd is None:
            msg = f'No gain specified in stage {self.name}'
            logger.error(msg)
            raise TypeError(msg)
        self.gain = gd.get('value', 1.0)
        self.gain_frequency = gd.get('frequency', 0.0)
        self.stage_sequence_number = sequence_number


        self.filter = Filter.construct(base_dict.pop('filter'),
                                       self.stage_sequence_number,
                                       self.name,
                                       self.gain_frequency)
        if not self.filter:
            msg = f'No filter in stage {self.name}'
            logger.error(msg)
            raise TypeError(msg)
        if hasattr(filter, 'gain'):
            if (pct := 100*abs(filter.gain - self.gain)/self.gain) > 1:
                logger.error(
                    f'{filter.type} gain ({filter.gain:.5g}) is {pct:.1f}\% '
                    f'off of stage gain ({stage.gain:.5g})'
                )

        x = base_dict.pop('input_units', None)
        if x:
            self.input_units = x.get('name', None)
            self.input_units_description = x.get('description', None)

        x = base_dict.pop('output_units', None)
        if x:
            self.output_units = x.get('name', None)
            self.output_units_description = x.get('description', None)

        self.input_sample_rate = base_dict.pop('input_sample_rate', None)

        # Set an unconfigured delay to None so that it can be
        # calculated in self.delay(), once input_sample_rate
        # is known
        self._delay = base_dict.pop('delay', None)
        self.decimation_factor = base_dict.pop('decimation_factor', 1)
        self.decimation_offset = base_dict.pop('decimation_offset', 0)
        self.correction = correction

        # default polarity is positive
        self.polarity = base_dict.pop('polarity', 1)
        self.resource_id = base_dict.pop('resource_id', None)
        self.instrument_sensitivity = None
        # Instrument sensitivity will be calculated using obspy and stored in
        # first stage
        if len(base_dict) > 0:
            raise ValueError('base_dict has remaing fields: {}'
                             .format([x for x in base_dict.keys()]))

    @property
    def output_sample_rate(self):
        """
        Output sample rate is not specified but calculated from
        input sample rate and decimation factor
        """
        if self.input_sample_rate and self.decimation_factor:
            return self.input_sample_rate / self.decimation_factor
        else:
            return None

    @property
    def delay(self):
        """
        Calculates delay in seconds

        Delay is a function of filter offset for digital filters if not
        specified in info file
        """
        filter_delay = None
        
        # Check for "impossible" error
        if self.filter.delay_seconds is not None and self.filter.delay_samples is not None:
            ValueError('delay_seconds and delay_samples both set for {self.filter.type} filter')

        # Calculate delay based on filter
        if self.filter.delay_seconds is not None:
            filter_delay = self.filter.delay_seconds
        elif self.filter.delay_samples is not None:
            if not self.input_sample_rate:
                # Delay is already none, leave it like that
                msg = ('Cannot calculate delay from delay_samples '
                       f'because stage {self.name} has no input_sample_rate')
                logger.warning(msg)
                warnings.warn(msg)
            else:
                filter_delay = self.filter.delay_samples / self.input_sample_rate

        if self._delay is None:
            if filter_delay is not None:
                return filter_delay
            else:
                return 0
        
        # Compare stage-given and filter-based delays
        if filter_delay is not None and not self._delay == filter_delay:
            msg = ("stage-set delay does not equal filter delay"
                   f" ({self._delay} != {filter_delay}): ignoring filter "
                   "delay")
            warnings.warn(msg)
            logger.warning(msg)
        return self._delay
        
    def __repr__(self):
        return (f"Stage({self.inputs['attributes_dict']}, "
                f"{self.inputs['higher_modifs']}, "
                f"{self.inputs['correction']}, "
                f"{self.inputs['sequence_number']}, "
                f"{self.inputs['ext_config_name']})")

    def __str__(self, indent=0, n_subclasses=0):
        if n_subclasses < 0:
            return f'{self.__class__.__name__} "{self.name}"'
        kwargs = {'indent': 4, 'n_subclasses': n_subclasses-1}
        s = f'Stage:\n'
        s += f'    name: {self.name}\n'
        s += f'    description: {self.description}\n'
        s += f'    input_units: {self.input_units}\n'
        s += f'    output_units: {self.output_units}\n'
        s += f'    gain: {self.gain}\n'
        s += f'    gain_frequency: {self.gain_frequency:g}\n'
        s += f'    filter: {self.filter.__str__(**kwargs)}\n'
        if not self.stage_sequence_number == -1:
            s += f'    stage_sequence_number: {self.stage_sequence_number}\n'
        if self.calibration_dates is not None:
            s += f'    calibration_dates: {self.calibration_dates.__str__(**kwargs)}\n'
        if self.input_units_description:
            s += f'    input_units_description: {self.input_units_description}\n'
        if self.output_units_description:
            s += f'    output_units_description: {self.output_units_description}\n'
        if self.input_sample_rate:
            s += f'    input_sample_rate: {self.input_sample_rate}\n'

        s += f'    decimation_factor: {self.decimation_factor}\n'
        s += f'    decimation_offset: {self.decimation_offset}\n'
        s += f'    delay: {self.delay}\n'
        s += f'    correction: {self.correction}'

        return str_indent(s, indent)

    def to_obspy(self):
        """
        Return equivalent *obspy.core.inventory.response* classes stage:

        Possible stage classes:

           * PolesZerosResponseStage
           * FIRResponseStage
           * CoefficientsTypeResponseStage
           * ResponseListResponseStage
           * Response

        :returns: object of one the above classes
        """
        # Arguments for all
        args = (self.stage_sequence_number, self.gain, self.gain_frequency,
                self.input_units, self.output_units)
        kwargs = dict(name=self.name,
                      input_units_description=self.input_units_description,
                      output_units_description=self.output_units_description,
                      description=self.description,
                      decimation_input_sample_rate=self.input_sample_rate,
                      decimation_factor=self.decimation_factor,
                      decimation_offset=self.decimation_offset,
                      decimation_delay=self.delay,
                      decimation_correction=self.correction if self.correction is not None else 0,
                      resource_id=self.resource_id,
                      resource_id2=self.filter.resource_id)

        # Filter-dependent arguments
        filt = self.filter

        # If stage is digital, must have offset and delay
        if isinstance(filt, (FIR, Coefficients, ResponseList)):
            if kwargs['decimation_offset'] is None:
                logger.warning(f'{type(filt)} has no decimation offset, setting to 0')
                kwargs['decimation_offset'] = 0
            if kwargs['decimation_delay'] is None:
                logger.warning(f'{type(filt)} has no decimation delay, setting to 0.')
                kwargs['decimation_delay'] = 0.

        # Generate the obspy filter stage
        if isinstance(filt, Analog):  # subclass of PolesZeros, so test first
            if not filt.normalization_frequency:
                filt.normalization_frequency = self.gain_frequency
            obspy_stage = PolesZerosResponseStage(
                *args, **kwargs,
                pz_transfer_function_type=filt.transfer_function_type,
                normalization_frequency=filt.normalization_frequency,
                zeros=filt.zeros,
                poles=filt.poles,
                normalization_factor=filt.normalization_factor)
        elif isinstance(filt, PolesZeros):
            if not filt.normalization_frequency:
                filt.normalization_frequency = self.gain_frequency
            obspy_stage = PolesZerosResponseStage(
                *args, **kwargs,
                pz_transfer_function_type=filt.transfer_function_type,
                normalization_frequency=filt.normalization_frequency,
                zeros=[obspy_types.ComplexWithUncertainties(t)
                       for t in filt.zeros],
                poles=[obspy_types.ComplexWithUncertainties(t)
                       for t in filt.poles],
                normalization_factor=filt.normalization_factor)
        elif isinstance(filt, FIR):
            obspy_stage = FIRResponseStage(
                *args, **kwargs,
                symmetry=filt.symmetry,
                coefficients=[obspy_types.FloatWithUncertaintiesAndUnit(
                    c / filt.coefficient_divisor) for c in filt.coefficients])
        # subclasses of Coefficients, so test first
        elif (isinstance(filt, Digital) or isinstance(filt, ADConversion)):
            obspy_stage = CoefficientsTypeResponseStage(
                *args, **kwargs,
                cf_transfer_function_type=filt.transfer_function_type,
                numerator=filt.numerator_coefficients,
                denominator=filt.denominator_coefficients)
        elif isinstance(filt, Coefficients):
            obspy_stage = CoefficientsTypeResponseStage(
                *args, **kwargs,
                cf_transfer_function_type=filt.transfer_function_type,
                numerator=[obspy_types.FloatWithUncertaintiesAndUnit(
                           n, lower_uncertainty=0.0, upper_uncertainty=0.0)
                           for n in filt.numerator_coefficients],
                denominator=[obspy_types.FloatWithUncertaintiesAndUnit(
                             n, lower_uncertainty=0.0, upper_uncertainty=0.0)
                             for n in filt.denominator_coefficients])
        elif isinstance(filt, ResponseList):
            obspy_stage = ResponseListResponseStage(
                *args, **kwargs,
                response_list_elements=[
                    ResponseListElement(x[0], x[1], x[2])
                    for x in filt.elements])
        elif isinstance(filt, Polynomial):
            coeffs = filt.coefficients
            obspy_stage = PolynomialResponseStage(
                *args, **kwargs,
                approximation_type=filt.approximation_type,
                frequency_lower_bound=self._toFlUncertUnit(filt.frequency_lower_bound),
                frequency_upper_bound=self._toFlUncertUnit(filt.frequency_upper_bound),
                approximation_lower_bound=filt.approximation_lower_bound,
                approximation_upper_bound=filt.approximation_upper_bound,
                maximum_error=filt.maximum_error,
                coefficients=[self._toFlUncert(x) for x in filt.coefficients])
        else:
            msg = 'Unhandled response stage type in stage '\
                  f'#{self.stage_sequence_number}: "{filt.type}"'
            warnings.warn(msg)
            logger.error(msg)
            raise TypeError(msg)

        return obspy_stage
        
    @staticmethod
    def _toFlUncert(mydict):
        return obspy_types.FloatWithUncertainties(
            mydict['value'],
            lower_uncertainty=mydict.get('minus_error', None),
            upper_uncertainty=mydict.get('plus_error', None),
            measurement_method=mydict.get('measurement_method', None))
    
    @staticmethod
    def _toFlUncertUnit(mydict):
        return obspy_types.FloatWithUncertaintiesAndUnit(
            mydict['value'],
            lower_uncertainty=mydict.get('minus_error', None),
            upper_uncertainty=mydict.get('plus_error', None),
            measurement_method=mydict.get('measurement_method', None),
            unit=mydict.get('unit', None))
    
    
    @staticmethod
    def _get_stage_modifications(resp_modifs, sequence_number):
        """
        Select which channel modifications specified at station level apply
        to a given stage,  with the stage number (WITHIN an instrument
        component) as key code

        Args:
            resp_modifs (dict or :class:`.ObsMetadata`): response modifications:
                key = regex stage number e.g.: "*", "[1,2,4]" or "[1-3]"
                value = modification dict
            sequence_number (int): stage sequence number (within component)
        """
        stage_code = str(sequence_number)
        default_dict = range_dict = {}
        modif = resp_modifs.get(str(stage_code), {})

        match_key = None
        for k, v in resp_modifs.items():
            if k[0] == "*":
                default_dict = v
            elif k[0][0] == "[":
                if re.match(k, stage_code):
                    if match_key is not None:
                        msg = 'There is an overlap in stage_modifications'\
                              f' for stage {sequence_number}. Taking the '\
                              f'first applicable pattern = "{match_key}"'
                        warnings.warn(msg)
                        logger.warning(msg)
                        break  # Only use first match, to avoid conflicts
                    range_dict = v
                    match_key = k

        # Gather all modifications in a single dict
        # Do this in order: particular mods have priority over range
        # specific which has priority over default
        for k, v in range_dict.items():
            if k not in modif:
                modif[k] = v

        for k, v in default_dict.items():
            if k not in modif:
                modif[k] = v

        return modif

