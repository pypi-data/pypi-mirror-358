"""
Comments Class
"""
# Standard library modules
import warnings
import logging
import json

from obspy.core.inventory.util import Comment as obspy_comment

from .functions import str_indent, verify_dict_is_empty
from .person import Persons
from .oi_date import OIDate
from .obsinfo_class_list import ObsinfoClassList

warnings.simplefilter("once")
warnings.filterwarnings("ignore", category=DeprecationWarning)
logger = logging.getLogger("obsinfo")


class Comments(ObsinfoClassList):
    """
    A list of :class:`Comment` objects
    """
    def __init__(self, inps):
        """
            Args:
                attributes_list: (list of dict, str or :class:`Comment``): list
                    of comments read from YAML/JSON file
        """
        if inps is None:
            super().__init__([], Comment)
        else:
            super().__init__([x if isinstance(x, Comment)
                              else Comment(x)
                              for x in inps], Comment)

    @classmethod
    def from_extras(cls, extras_dict):
        """
        Create `Comments` object from "extras" (freeform dict object)
        """
        if extras_dict is None:
            return cls(None)
        else:
            return cls(['Extra attributes: ' + json.dumps(extras_dict)])


class Comment(object):
    def __init__(self, inp):
        """
        Create a `Comment` object from a string or dict
        """
        if isinstance(inp, str):
            self.value = inp
            self.authors = Persons(None)
            self.begin_effective_time = OIDate(None)
            self.end_effective_time = OIDate(None)
            self.id = None
            self.subject = None
        elif isinstance(inp, dict):
            self.value = inp.pop('value')
            self.authors = Persons(inp.pop('authors', None))
            self.begin_effective_time = OIDate(inp.pop('begin_effective_time', None))
            self.end_effective_time = OIDate(inp.pop('end_effective_time', None))
            self.id = inp.pop('id', None)
            self.subject = inp.pop('subject', None)
            verify_dict_is_empty(inp)
        else:
            raise TypeError(f'illegal input type for Comment: {type(inp)}')

    def __eq__(self, other):
        if not isinstance(other, Comment):
            return False
        for attr in ('value', 'subject', 'authors', 'begin_effective_time',
                     'end_effective_time', 'id'):
            if not getattr(self, attr) == getattr(other, attr):
                return False
        return True

    def __str__(self, indent=0, n_subclasses=0):
        if n_subclasses < 0:
            if self.subject is None:
                return(f'{self.__class__.__name__}: {self.value}')
            else:
                return(f'<{self.__class__.__name__}, subject={self.subject}>: {self.value}')
        s = 'Comment:\n'
        s += f'    value: {self.value}'
        if len(self.authors) > 0:
            s += f'\n    authors: {self.authors.__str__(indent=4, n_subclasses=n_subclasses-1)}'
        if self.begin_effective_time.to_obspy() is not None:
            s += f'\n    begin_effective_time: {self.begin_effective_time}'
        if self.end_effective_time.to_obspy() is not None:
            s += f'\n    end_effective_time: {self.end_effective_time}'
        if self.id is not None:
            s += f'\n    id: {self.id}'
        if self.subject is not None:
            s += f'\n    subject: {self.subject}'
        return str_indent(s, indent)

    def to_obspy(self):
        return obspy_comment(
            value=self.value,
            begin_effective_time=self.begin_effective_time.to_obspy(),
            end_effective_time=self.end_effective_time.to_obspy(),
            authors=self.authors.to_obspy(),
            id=self.id,
            subject=self.subject
        )
