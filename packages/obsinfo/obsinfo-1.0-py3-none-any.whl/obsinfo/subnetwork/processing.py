"""
Processing Class, holds list of data processing steps
"""

# Standard library modules
import warnings
import logging
import json
from copy import deepcopy
from pprint import pformat, pprint

# Non-standard modules

# obsinfo modules
from ..helpers import str_indent, str_list_str, Comments, Comment
from ..obsmetadata import ObsMetadata

warnings.simplefilter("once")
warnings.filterwarnings("ignore", category=DeprecationWarning)
logger = logging.getLogger("obsinfo")


class Processing(object):
    """
    No equivalent class in obspy/StationXML

    Saves a list of Processing steps as strings
    For now, just stores the list. Will be converted to StationXML comments

    Attributes:
        processing_list (list): list of processing steps with attributes,
            either linear_drift or leapsecond

    """

    def __init__(self, attributes, leapseconds=None):
        """
        Constructor

        Args:
        attributes (list): list of processing steps (clock_correction is
            only one for now) with attributes.
        leapseconds (dict or None): leapseconds information from the
            subnetwork level, to be injected and completed, as necessary
        """
        self.attributes = []

        if self.attributes is None:
            return

        # self.attributes should be a list of single-keyed dicts
        path = 'subnetwork:processing'
        if not isinstance(attributes, list):
            raise ValueError(f'{path} is not a list')
        attributes = [ObsMetadata(x) for x in attributes]
        for attr, i in zip(attributes, range(len(attributes))):
            if not isinstance(attr, dict):
                raise ValueError(f'{path}[{i}] is not a dict')
            if not len(attr.keys()) == 1:
                raise ValueError('{}[{}] has multiple keys: ({})'
                                 .format(path, i, list(attr.keys())))
            k = list(attr.keys())[0]
            # Handle any base-config-modification structures
            if 'base' in attr[k]:
                attr[k] = attr[k].get_configured_modified_base(accept_extras=True)
            self.attributes.append(attr)
        self._handle_leapseconds(leapseconds)

    def _handle_leapseconds(self, leapsecs):
        """
        Enter subnetwork-scale leapseconds information into Processing element
        """
        clockcorr_str = 'clock_correction'
        ls_change_applied_str = 'leapsecond_applied_corrections'
        if leapsecs is not None:
            x = deepcopy(leapsecs) # COPY leapseconds dict to avoid overwriting
            ls_defapplied_str = 'default_applied_corrections'
            ls_applied_str = 'applied_corrections'
            for attr in self.attributes:
                # If the processing has a clock correction element, modify it
                if clockcorr_str in attr:
                    cc = attr[clockcorr_str]
                    cc['leapseconds'] = x 
                    # rename key default_applied_str to applied_str
                    cc['leapseconds'][ls_applied_str] =  cc['leapseconds'].pop(ls_defapplied_str)
                    # insert any change_applied_str
                    for k, v in cc.pop(ls_change_applied_str, {}).items():
                        cc['leapseconds'][ls_applied_str][k] = v
                else: # Otherwise create a clock correction element with leap seconds
                    attr[clockcorr_str] = {'leapseconds': x}
        else:  # If there is no subnetwork-level leapseconds, 
               # there shouldn't be any station level, either
            for attr in self.attributes:
                if ls_change_applied_str in attr.get(clockcorr_str, {}):
                    raise ValueError(f'station {ls_change_applied_str} '
                                     'specified, but no leapseconds defined '
                                     'at subnetwork level')

    def __repr__(self):
        s = f'Processing({self.processing_list})'
        return s

    def __str__(self, indent=0, n_subclasses=0):
        if n_subclasses < 0:
            return f'{self.__class__.__name__}'
        kwargs = dict(indent=indent+4, n_subclasses=n_subclasses-1)
        s = f'{self.__class__.__name__}:\n'
        s += f'        {str_list_str([pformat(self.attributes, compact=True, width=120)], **kwargs)}'
        return str_indent(s, indent)

    def to_comments(self):
        """
        Returns processing list as :class:`.Comments`

        Top level name becomes the :class:`.Comment`'s ``subject`` attribute, each element
        below becomes an individual :class:`.Comment`
        """
        clist = []
        for x in self.attributes:
            for k, v in x.items():
                comment_subject = k
                if k == "clock_correction":
                    comment_subject = "Clock Correction"
                clist.append(Comment({'subject': comment_subject,
                                      'value': json.dumps(v)}))
        return Comments(clist)
