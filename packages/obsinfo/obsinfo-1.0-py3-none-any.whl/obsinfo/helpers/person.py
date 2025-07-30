"""
Person class
"""
# Standard library modules
import warnings
import logging

from obspy.core.inventory.util import Person as obspy_Person

from .phone import Phones
from .functions import str_indent, str_list_str
from .obsinfo_class_list import ObsinfoClassList

warnings.simplefilter("once")
warnings.filterwarnings("ignore", category=DeprecationWarning)
logger = logging.getLogger("obsinfo")


class Persons(ObsinfoClassList):
    """
    A list of :class:`Person` objects
    """
    def __init__(self, seq):
        """
        Args:
            seq: (list of :class:`Person` or None): list of attribute dicts
                describing a :class:`Person`
        """
        super().__init__(seq, Person)


class Person(object):
    """
    Equivalent of StationXMl Person

    Attributes:
        names (list of str): Name(s) written out normally
        agencies (list of str): agencies worked for
        emails (list of str): emails
        phones (list of :class:`Phone``): person's telephone number(s)
    """

    def __init__(self, attributes_dict):
        """
        Args:
            attributes_dict (dict or :class:`.ObsMetadata`):
                operator information
        """
        if not attributes_dict:
            raise ValueError('No attributes dict!')

        self.names = attributes_dict['names']                  # required
        self.agencies = attributes_dict.get('agencies', [])
        self.emails = attributes_dict.get('emails', [])
        self.phones = Phones(attributes_dict.get('phones', []))

    def repr(self):
        args = [f'names={self.names}']
        if len(self.agencies) > 0:
            args.append(f'agencies={self.agencies}')
        if len(self.emails) > 0:
            args.append(f'emails={self.emails}')
        if len(self.phones) > 0:
            args.append(f'phones={self.phones}')
        return 'Person(' + ", ".join(args) + ")"

    def __str__(self, indent=0, n_subclasses=0):
        kwargs = dict(indent=indent, n_subclasses=n_subclasses-1)
        if n_subclasses < 0:
            return f'{self.__class__.__name__} {str_list_str(self.names, **kwargs)}'
        s = f'{self.__class__.__name__}:\n'
        s += f'    names: {str_list_str(self.names, **kwargs)}\n'
        s += f'    agencies: {str_list_str(self.agencies, **kwargs)}\n'
        s += f'    emails: {str_list_str(self.emails, **kwargs)}\n'
        s += f'    phones: {self.phones.__str__(**kwargs)}'
        return str_indent(s, indent)

    def to_obspy(self):
        return obspy_Person(names=self.names,
                            agencies=self.agencies,
                            emails=self.emails,
                            phones=self.phones.to_obspy())
