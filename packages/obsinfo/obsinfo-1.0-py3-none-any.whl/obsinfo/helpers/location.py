"""
Location classe
"""
# Standard library modules
import warnings
import numpy as np
import logging

from .float_with_uncert import FloatWithUncert
from ..obsmetadata import ObsMetadata
from .functions import str_indent
from .obsinfo_class_list import ObsinfoClassList

warnings.simplefilter("once")
warnings.filterwarnings("ignore", category=DeprecationWarning)
logger = logging.getLogger("obsinfo")

class Locations(ObsinfoClassList):
    """
    A list of :class:`Location` objects
    """
    def __init__(self, inp):
        super().__init__(inp, Location)

    def get_by_loc_code(self, loc_code):
        for loc in self:
            if loc.code == loc_code:
                return loc
        logger.error(f'no position defined for location code {loc_code}')
        return None

    @classmethod
    def from_locations_dict(cls, locations_dict):
        """
        Create from a locations dict (key=location_code, value=location_dict)
        """
        return cls([Location(v, c) for c, v in locations_dict.items()])

class Location(object):
    """
    Location class.

    Attributes:
        code (str): location code
        latitude (float): station latitude (degrees N)
        longitude (float): station longitude (degrees E)
        elevation (float): station elevation (meters above sea level)
        uncertainties_m (dict): 'lat', 'lon', 'elev' in METERS
        geology (str): site geology
        vault (str): vault type
        depth_m (float): depth of station beneath surface (meters)
        water_level_m (float): elevation of water_level (non-zero for lakes)
        localisation_method (str): method used to determine position
        obspy_latitude: latitude as an *obspy* object
        obspy_longitude: longitude as an *obspy* object

    """

    def __init__(self, attributes_dict, code:str=None):
        """
        Create Location object and assign attributes from attributes_dict.
        Validate required location attributes exist
        Convert to obspy longitude and latitude

        Args:
            attributes_dict (dict or :class:`ObsMetadata`): location
                information
            code (str): location code, error if 'code' in attributes_dict
        """
        attributes_dict = ObsMetadata(attributes_dict)
        if code is not None:
            if 'code' in attributes_dict:
                raise ValueError('provided location code as argument AND dict key')
            else:
                attributes_dict['code'] = code

        position = attributes_dict.pop('position', None)
        if position is None:
            msg = 'No position in location'
            warnings.warn(msg)
            logger.error(msg)
            raise TypeError(msg)
        self._lat = position.pop('lat.deg')
        self._lon = position.pop('lon.deg')
        self._elev = position.pop('elev.m')
        self._position = position  # for __repr__()
        self.code = attributes_dict.pop('code', None)
        self.water_level_m = attributes_dict.pop('water_level.m', None)
        attributes_dict.pop('notes', None)  # Clear out notes (if any)

        # Get base-config elements
        base_dict = attributes_dict.get_configured_modified_base()
        self.geology = base_dict.get('geology', None)
        self.vault = base_dict.get('vault', None)
        self.depth_m = base_dict.get('depth.m', None)
        self._uncert_m = base_dict.get('uncertainties.m', None)
        self._measurement_method = base_dict.get('measurement_method', None)

        self.latitude = FloatWithUncert(self._lat,
                                        uncertainty=self._uncert('lat'),
                                        measurement_method=self._measurement_method)
        self.longitude = FloatWithUncert(self._lon,
                                         uncertainty=self._uncert('lon'),
                                         measurement_method=self._measurement_method)
        self.elevation = FloatWithUncert(self._elev,
                                         uncertainty=self._uncert('elev'),
                                         measurement_method=self._measurement_method)

    def __repr__(self):
        args = []
        args.append(f"'position': {self._position}")
        args.append(f"'uncertainties.m': {self._uncert_m}")
        args.append(f"'measurement_method': '{self._measurement_method}'")
        if not self.geology == 'unknown':
            args.append(f"'geology': '{self.geology}'")
        if self.vault:
            args.append(f"'vault'='{self.vault}'")
        if self.depth_m is not None:
            args.append(f"'depth_m'={self.depth_m:g}")
        s = 'Location({' + ', '.join(args) + '})'
        return s

    def __str__(self, indent=0, n_subclasses=0):
        s = f'Location:\n'
        s += f'    code: {self.code}\n'
        s += f'    latitude: {self.latitude}\n'
        s += f'    longitude: {self.longitude}\n'
        s += f'    elevation: {self.elevation}'
        if not self.geology == 'unknown':
            s += f'\n    geology: {self.geology}'
        if self.vault:
            s += f'\n    vault: {self.vault}'
        if self.depth_m is not None:
            s += f'\n    depth: {self.depth_m:g}m'
        if self.water_level_m is not None:
            s += f'\n    water_level: {self.water_level_m:g}m'
        if self._measurement_method:
            s += f'\n    measurement_method: "{self._measurement_method}"'
        return str_indent(s, indent)

    def _uncert(self, which):
        """
        Returns uncertainty in appropriate units

        Args:
            which (str): must be 'lat'', 'lon', or 'elev'
        """
        if which == 'elev':
            return self._uncert_m.get('elev', None)
        elif which == 'lat':
            uncert_m = self._uncert_m.get('lat', None) \
                if self._uncert_m else None
            if uncert_m is None:
                return None
            else:
                meters_per_degree_lat = 1852.0 * 60.0
                lat_uncert = uncert_m / meters_per_degree_lat
                # cut off extraneous digits
                lat_uncert = float("{:.3g}".format(lat_uncert))
                return lat_uncert
        elif which == 'lon':
            uncert_m = self._uncert_m.get('lon', None) \
                if self._uncert_m else None
            if uncert_m is None or abs(self._lat) == 90:
                return None
            else:
                m_per_deg_lon = (1852.0 * 60.0 * np.cos(np.radians(self._lat)))
                lon_uncert = uncert_m / m_per_deg_lon
                lon_uncert = float("{:.3g}".format(lon_uncert))
                return lon_uncert
        else:
            raise ValueError('Illegal position type "{which}", should be lat, '
                             'lon or elev')


def null_location(code: str):
    """
    Return a Location object with zero position and the given location code
    """
    return Location({'position': {'lat.deg': 0,
                                  'lon.deg': 0,
                                  'elev.m': 0},
                         'base': {'uncertainties.m': {'lat': 0,
                                                      'lon': 0,
                                                      'elev': 0},
                                  'depth.m': 0,
                                  'geology': 'seafloor',
                                  'vault': 'seafloor'},
                         'code': code})
