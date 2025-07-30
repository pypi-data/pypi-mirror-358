"""
Instrumentation class and all subclasses

nomenclature:
    * An "Instrument" (measurement instrument) records one physical parameter
    * A "Channel" is an Instrument + an orientation code and possibly
        starttime, endtime and location code
    * An "Instrumentation" combines one or more measurement Channels
"""
from .instrumentation import Instrumentation, Instrumentations
from .instrument_component import (InstrumentComponent, Datalogger, Sensor,
                                   Preamplifier)
from .equipment import Equipment
from .channel import Channel, Channels
from .filter import (Filter, FilterTemplate, PolesZeros, FIR, Coefficients,
                     ResponseList, Analog, Digital, ADConversion, Polynomial)
from .instrument import Instrument
from .orientation import Orientation
from .stages import Stage, Stages
