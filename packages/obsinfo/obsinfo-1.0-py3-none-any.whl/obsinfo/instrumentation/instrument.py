"""
Instrument and Operator classes
"""
# Standard library modules
import warnings
import logging
from copy import deepcopy

# Non-standard modules
from obspy.core.inventory.response import (Response, InstrumentSensitivity
                                           as obspy_Sensitivity)

# obsinfo modules
from .instrument_component import (InstrumentComponent,
                                   Datalogger, Sensor, Preamplifier)

warnings.simplefilter("once")
warnings.filterwarnings("ignore", category=DeprecationWarning)
logger = logging.getLogger("obsinfo")


class Instrument(object):    # Was a Channel subclass, but don't see why
    """
    An instrument is an ensemble of a sensor, a datalogger and possibly a
    preamplifier. It also includes a selected configuration for each one of
    these instrument components.

    Attributes:
        datalogger (:class:`Datalogger`)
        sensor: (:class:`Sensor`)
        preamplifier: (:class:`Preamplifier`)
        sample_rate (float): from datalogger sample rate
        correction (float): from datalogger delay correction
        seed_band_base (str): from sensor band base
        seed_instrument_code (str): from sensor instrument code
    """

    def __init__(self, attributes_dict, modifs={}):
        """
        Constructor

        Args:
            attributes_dict (dict or :class:`.ObsMetadata`): instrument attributes_dict
            modifs (dict or :class:`ObsMetadata`): modifications passed
                down from the Instrumentation level (including channel selection)
        """
        # For __repr__()
        if modifs:
            self.inputs = {'modifs': "<ObsMetadata>"}
        else:
            self.inputs = {'modifs': {}}
        
        self.correction = None
        self.delay = None

        if not attributes_dict:
            msg = 'No instrument attributes_dict'
            logger.error(msg)
            raise ValueError(msg)

        # Create the three InstrumentComponents
        self.datalogger = Datalogger(attributes_dict.pop('datalogger', {}),
                                     modifs.get('datalogger', {}))
        self.sensor = Sensor(attributes_dict.pop('sensor', {}),
                             modifs.get('sensor', {}))
        if not 'preamplifier' in attributes_dict:
            self.preamplifier = None
        else:
            self.preamplifier = Preamplifier(attributes_dict.pop('preamplifier', {}),
                                             modifs.get('preamplifier', {}))
        # Combine the InstrumentComponents' response stages
        self._combine_stages()
        # Validate inputs and outputs and correct delay
        self._integrate_stages()
        
        if attributes_dict:
            raise ValueError(f'attributes_dict is not empty after reading: {attributes_dict=}')

    def __repr__(self):
        s =   'Instrument(attributes_dict = <ObsMetadata>\n',
        s += f'           modifs={self.inputs["modifs"]}'
        return s

    def __str__(self, indent=0, n_subclasses=0):
        if n_subclasses < 0:
            return self.__class__.__name__

        kwargs = dict(indent=4, n_subclasses=n_subclasses-1)
        s =  'Instrument:\n'
        s += f'  sensor: {self.sensor.equipment.__str__(**kwargs)}\n'
        if self.preamplifier is not None:
            s += f'  preamplifier: {self.preamplifier.equipment.description}\n'
        else:
            s += f'  preamplifier: None\n'
        s += f'  datalogger: {self.datalogger.equipment.__str__(**kwargs)}\n'
        s += f'  stages: {self.stages.__str__(**kwargs)}\n'
        s += f'  sample_rate: {self.sample_rate}\n'
        s += f'  delay: {self.delay}\n'
        if self.correction is None:
            corrections = [x.correction for x in self.stages if x.correction is not None and not x.correction == 0]
            s += '  correction: {} (sum of non-zero corrections in {} stages)\n'.format(
                sum(corrections), len(corrections))
        else:
            s += f'  correction: {self.correction}\n'
        s += f'  seed_band_base: {self.seed_band_base}\n'
        s += f'  seed_instrument_code: {self.seed_instrument_code}'
        return s

    def to_obspy(self):
        """
        Return equivalent obspy class

        Returns:
            ():class:`obspy.core.inventory.response.Response`)
        """
        sensitivity = self._calc_sensitivity()
        if self.stages is not None:
            obspy_stages = [x.to_obspy() for x in self.stages]
        else:
            obspy_stages = None
        return Response(resource_id=None,
                        instrument_sensitivity=sensitivity,
                        instrument_polynomial=None,
                        response_stages=obspy_stages)

    def _combine_stages(self):
        """
        Adds all response stages as obsinfo and obpsy objects and renumbers
        them

        Returns stages as a Stages object
        """
        if self.sensor.stages is not None:
            self.stages = self.sensor.stages
        else:
            self.stages = Stages()

        if self.preamplifier is not None:
            if self.preamplifier.stages is not None:
                self.stages += self.preamplifier.stages

        if self.datalogger.stages is not None:
            self.stages += self.datalogger.stages

        # Order the stage_sequence_numbers
        i = 1
        for s in self.stages:
            s.stage_sequence_number = i
            i += 1

    def _integrate_stages(self):
        """
        Integrates the stages with one another

        1) Renumber stages sequentially
        2) Verify/set units and sample rates
        3) Assure same frequency is used for consecutive PZ filters
        4) Calculate global polarity of the whole set of response stages
        5) Set global response delay correction
        6) Validate sample_rate expressed in datalogger component is equal to
           global response sample rate
        """
        if self.stages is None or len(self.stages) == 0:
            self.polarity = None
            return

        polarity = 1
        prev_pz_norm_freq = None
        prev_stage = None
        for stage in self.stages:
            if prev_stage is not None:
                prev_ssn = prev_stage.stage_sequence_number
                this_ssn = stage.stage_sequence_number

                # 2a) Verify continuity of units
                if prev_stage.output_units != stage.input_units:
                    msg = "Stage {} and {} units don't match".format(
                        prev_ssn, this_ssn)
                    warnings.warn(msg)
                    logger.error(msg)
                    raise ValueError(msg)

                # 2b) Verify/set continuity of sample rate
                if prev_stage.output_sample_rate:
                    if stage.input_sample_rate:
                        if prev_stage.output_sample_rate != stage_input_sample_rate:
                            msg = ("stage {this_ssn} input sample rate "
                                   "doesn't match previous stage's output "
                                   "sample rate ({stage.input_sample_rate} "
                                   "!= {prev_stage.output_sample_rate)}")
                            warnings.warn(msg)
                            logger.error(msg)
                            raise ValueError(msg)
                    else:
                        stage.input_sample_rate = prev_stage.output_sample_rate
                        
                # 3) Check that all PZ stages have the same normalization frequency.
                if stage.filter.type == 'PolesZeros':
                    if prev_pz_norm_freq is not None:
                        if (prev_pz_norm_freq != stage.filter.normalization_frequency
                            and prev_pz_norm_freq != 0):
                            msg = ("Normalization frequencies for PZ stages "
                                   f"{prev_ssn} and {this_ssn} don't match "
                                   f"({prev_pz_norm_freq} "
                                   f"!= {stage.filter.normalization_frequency})")
                            warnings.warn(msg)
                            logger.warning(msg)
                    prev_pz_norm_freq = stage.filter.normalization_frequency

            # 4) Calculate/verify delay and correction
            if self.delay is None:
                self.delay = stage.delay
            elif stage.delay is not None:
                self.delay += stage.delay
            if self.correction is None and stage.delay is not None:
                stage.correction = stage.delay

            # 5) Calculate global polarity
            if not stage.polarity:  # default polarity is positive
                stage.polarity = 1
            polarity *= stage.polarity

            # Save previous stage for comparison
            prev_stage = deepcopy(stage)
            first_stage = False

        if self.correction is not None:
            self.stages[-1].correction = self.correction

        # Check global output sample rate
        if not self.stages[-1].output_sample_rate == self.sample_rate:
            msg = ('Declared sample rate != calculated sample rate '
                   f'({self.sample_rate} != {self.stages[-1].output_sample_rate})')
            logger.error(msg)
            raise ValueError(msg)

        # Set global response attributes
        self.polarity = polarity

    def _calc_sensitivity(self):
        """
        Calculates sensitivity
        Based on ..misc.obspy_routines.response_with_sensitivity
        """
        response_stg = self.stages
        gain_prod = 1.
        if response_stg is None:
            iu = "None"
            ou = "None"
            iud = "None"
            oud = "None"
            gain_freq = 0
        else:
            iu = response_stg[0].input_units
            ou = response_stg[-1].output_units
            iud = response_stg[0].input_units_description
            oud = response_stg[-1].output_units_description
            # gain_frequency could be provided, according to StationXML, but we
            # assume it's equal to the gain frequency of first stage
            gain_freq = response_stg[0].gain_frequency

            if "PA" in iu.upper():
                # MAKE OBSPY THINK ITS M/S TO CORRECTLY CALCULATE SENSITIVITY
                sens_iu = "M/S"
            else:
                sens_iu = iu
            for stage in response_stg:
                gain_prod *= stage.gain

        sensitivity = obspy_Sensitivity(gain_prod, gain_freq,
                                        input_units=sens_iu, output_units=ou,
                                        input_units_description=iud,
                                        output_units_description=oud)
        sensitivity.iu = iu
        return sensitivity

    def get_response_stage(self, num):
        """
        Returns the response stage in a given position

        Args:
            num (int): stage number, starting with zero and ordered from
                sensor to datalogger
        """
        # All response stages are at the instrument_component level
        stages = self.stages
        assert(num <= stages[-1].stage_sequence_number), \
            'response stage out of range: {num}'
        return stages[num]

    @property
    def equipment_datalogger(self):
        return self.datalogger.equipment

    @property
    def equipment_sensor(self):
        return self.sensor.equipment

    @property
    def equipment_preamplifier(self):
        return self.preamplifier.equipment

    @property
    def sample_rate(self):
        return self.datalogger.sample_rate

    @property
    def seed_band_base(self):
        return self.sensor.seed_band_base

    @property
    def seed_instrument_code(self):
        return self.sensor.seed_instrument_code

    @property
    def seed_band_code(self):
        """
        Return the instrument's band code
        """
        return self._seed_band_code(self.sample_rate, self.sensor.seed_band_base)
        
    @staticmethod
    def _seed_band_code(sr, bbc):
        """
        Return band code for a given sample rate and band base_code
        
        Args:
            sr (float): sample_rate
            bbc (str): band code
        """
        VALID_BBCs = ("broadband", "shortperiod", "A", "I", "O", "L", "S")
        if not bbc in VALID_BBCs:
            msg = f'Unknown band base code: "{bbc}"'
            warnings.warn(msg)
            logger.error(msg)
            raise TypeError(msg)
        if len(bbc) == 1:
            return bbc
        if bbc == "broadband":
            if sr >= 1000:
                return "F"
            elif sr >= 250:
                return "C"
            elif sr >= 80:
                return "H"
            elif sr >= 10:
                return "B"
            elif sr > 1:
                return "M"
            elif sr > 0.3:
                return "L"
            elif sr >= 0.1:
                return "V"
            elif sr >= 0.01:
                return "U"
            elif sr >= 0.001:
                return "W"
            elif sr >= 0.0001:
                return "R"
            elif sr >= 0.00001:
                return "P"
            elif sr >= 0.000001:
                return "T"
            else:
                return "Q"
        elif bbc == "shortperiod":
            if sr >= 1000:
                return "G"
            elif sr >= 250:
                return "D"
            elif sr >= 80:
                return "E"
            elif sr >= 10:
                return "S"
            else:
                msg = "Short period sensor sample rate < 10 sps"
                warnings.warn(msg)
                logger.warning(msg)
                return "S"  # Return a code anyway
        else:
            msg = f'Unknown band base code: "{bbc}"'
            warnings.warn(msg)
            logger.error(msg)
            raise TypeError(msg)
