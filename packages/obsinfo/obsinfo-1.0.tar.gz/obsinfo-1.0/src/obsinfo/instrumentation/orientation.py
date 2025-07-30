"""
Orientation class
"""
# Standard library modules
import warnings
import logging

# Non-standard modules
import obspy.core.util.obspy_types as obspy_types

# obsinfo modules
from ..obsmetadata import (ObsMetadata)
from ..helpers import FloatWithUncert, str_indent, verify_dict_is_empty

warnings.simplefilter("once")
warnings.filterwarnings("ignore", category=DeprecationWarning)
logger = logging.getLogger("obsinfo")


class Orientation(object):
    """
    Class for sensor orientations. No channel modifs. Cannot change orientation
    as it is part of the channel identifiers. Azimuth and dip can be changed
    Orientation is coded by `FDSN standard <http://docs.fdsn.org/projects/
    source-identifiers/en/v1.0/channel-codes.html>`
    
    These are the dips to give for vertical/hydrophone channels:
        -90°:
            - vertical seismometer with positive voltage corresponding to
              upward motion (typical seismometer)
            - hydrophone with positive voltage corresponding to increase
              in pressure (compression)
         90°:
            - vertical seismometer with positive voltage corresponding to
              downward motion (typical geophone),
            - hydrophone with positive voltage corresponding to decrease
              in pressure (dilatation)

    Attributes:
        code (str): Single-letter orientation code
        azimuth (:class:`FloatWithUncert`): azimuth in degrees, clockwise from
            north
        dip (:class:`FloatWithUncert`): dip in degrees, -90 to 90, positive=down,
            negative=up
    """

    def __init__(self, attributes_dict):
        """
        Constructor

        Args:
            attributes_dict (dict or :class:`.ObsMetadata`): Orientation
                dictionary 'code', 'azimuth.deg' and 'dip.deg' attributes
        """
        attributes_dict = ObsMetadata(attributes_dict)
        VALID_CODES = ('1', '2', '3', 'H', 'G', 'X', 'Y', 'Z', 'E', 'N')
        if not attributes_dict:
            msg = 'No orientation'
            warnings.warn(msg)
            logger.error(msg)
            raise ValueError(msg)

        # Get and check code
        if 'code' not in attributes_dict:
            raise ValueError('orientation has no "code" attribute') # Shouldn't get here
        self.code = attributes_dict.pop('code')
        if self.code not in VALID_CODES:
            raise ValueError(f'orientation code "{self.code}" not in list of '
                             f'valid orientation codes"{VALID_CODES}"')
        
        # Get and check azimuth and dip
        azimuth = attributes_dict.pop('azimuth.deg', None)
        dip = attributes_dict.pop('dip.deg', None)
        if azimuth is None and dip is None:
            raise ValueError(f'orientation {self.code}: neither azimuth nor dip specified')
        if azimuth is not None:
            azimuth.safe_update({'unit': 'degrees'})
            self.azimuth = FloatWithUncert.from_dict(azimuth)
        else:
            self.azimuth = FloatWithUncert(0, unit='degrees')
        if dip is not None:
            dip.safe_update({'unit': 'degrees'})
            self.dip = FloatWithUncert.from_dict(dip)
        else:
            self.dip = FloatWithUncert(0, unit='degrees')
            
        verify_dict_is_empty(attributes_dict)
            
        # Validate required values
        # Required azimuth uncertainties
        if self.code in ('X', 'Y', 'E', 'N'):
            if self.azimuth.uncertainty is None:
                logger.warning(f"No azimuth uncertainty specified for orientation '{self.code}'")
            else:
                if self.azimuth.uncertainty > 5:
                    logger.warning("{self.code} orientation azimuth uncertainty > 5 degrees")
        elif self.code == 'Z':
            if self.azimuth.uncertainty is not None and self.azimuth.uncertainty > 5:
                logger.warning("{self.code} orientation dip uncertainty > 5 degrees")
        # Some channels need to be close to specified values
        if self.code == 'E':
            if self.azimuth.value <85 or self.azimuth.value > 95:
                raise ValueError('E orientation azimuth={self.azimuth.value), not between 85 and 95')
        elif self.code == 'N':
            if self.azimuth.value < 355 and self.azimuth.value > 5:
                raise ValueError('N orientation azimuth={self.azimuth.value), not between 355 and 5')
        if self.code == 'Z':
            if self.dip.value <-90 or self.dip.value > -85:
                raise ValueError(f'{self.code} dip={self.dip.value}, not between -85 and -90')
        elif self.code in ('H', 'G', 'O'):
            if abs(self.dip.value) > 90 or abs(self.dip.value) < 85:
                raise ValueError(f'{self.code} dip={self.dip.value}, not between -85 and -90 or 85 and 90')
            
    def __repr__(self):
        args=[]
        if self.azimuth.value != 0 or self.azimuth.uncertainty is not None or self.azimuth.measurement_method is not None:
            args.append(f"'azimuth': {self.azimuth.__repr__(True)}")
        if self.dip.value != 0 or self.dip.uncertainty is not None or self.dip.measurement_method is not None:
            args.append(f"'dip': {self.dip.__repr__(True)}")
        return "Orientation({" + f"'{self.code}':" + " {" + ", ".join(args) + "}})"

    def __str__(self, indent=0, n_subclasses=0):
        s = 'Orientation:\n'
        s += f'    code: {self.code}\n'
        s += f'    azimuth: {self.azimuth}\n'
        s += f'    dip: {self.dip}'
        return str_indent(s, indent)