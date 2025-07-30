"""
Site Class
"""
# Standard library modules
import warnings
import logging

from obspy.core.inventory.util import Site as obspy_site

from ..helpers import str_indent, verify_dict_is_empty

warnings.simplefilter("once")
warnings.filterwarnings("ignore", category=DeprecationWarning)
logger = logging.getLogger("obsinfo")


class Site(object):
    def __init__(self, obj):
        "obj can be a string or an dict"
        if isinstance(obj, str):
            self.name = obj
            self.description = None
            self.town = None
            self.county = None
            self.region = None
            self.country = None
        elif isinstance(obj, dict):
            if 'name' not in obj:
                raise ValueError('site object has no "name" field')
            self.name = obj.pop('name', None)
            self.description = obj.pop('description', None)
            self.town = obj.pop('town', None)
            self.county = obj.pop('county', None)
            self.region = obj.pop('region', None)
            self.country = obj.pop('country', None)
            verify_dict_is_empty(obj)
        else:
            raise TypeError('Unauthorized type for site: {type(obj)}')
        
    def __str__(self, indent=0, n_subclasses=0):
        s = f'Site: {self.name}'
        for x in ('description', 'town', 'county', 'region', 'country'):
            if (a:=getattr(self, x)) is not None:
                s += f'\n    {x}: {a}'
        return str_indent(s, indent)
    
    def to_obspy(self):
        return obspy_site(name=self.name,
                          description=self.description,
                          town=self.town,
                          county=self.county,
                          region=self.region,
                          country=self.country)