"""
Phone class
"""
# Standard library modules
import warnings
import re
import logging
from string import digits

from obspy.core.inventory.util import PhoneNumber

from .functions import str_indent
from .obsinfo_class_list import ObsinfoClassList

warnings.simplefilter("once")
warnings.filterwarnings("ignore", category=DeprecationWarning)
logger = logging.getLogger("obsinfo")


class Phones(ObsinfoClassList):
    """
    List of :class:`Phone` objects
    """
    def __init__(self, seq):
        """
        Args:
            seq: (list of :class:`Phone` or None): list of attribute dicts
                    describing a Phone number
        """
        seq = [Phone.str_to_dict(x) if isinstance(x, str) else x for x in seq]
        super().__init__(seq, Phone)


class Phone(object):
    """
    Equivalent of StationXML ``<PhoneNumber>``

    Attributes:
        description (str): Description of the phone # (work, mobile...)
        country_code (str): Telephone country code
        area_code (int): Telephone area code
        phone_number (str): Telephone number
    """

    def __init__(self, attributes_dict_or_str):
        """
        Phone # must be provided as one of the following:
            - an international format str:
                "+{country_code}{area_code}{phone_number}"
                only numbers are allowed, no dashes, no parentheses, etc
            - a US format string (for legacy):
                "+{country_code} ({area_code}) {phone_number}"
                "00{country_code} ({area_code}) {phone_number}"
                where phone_number can have dashes
            - a dict with fields "country_code, "area_code" and "phone_number"
        Args:
            attributes_dict_or_str (dict, :class:`.ObsMetadata`, or str):
                phone information
        """
        if not attributes_dict_or_str:
            raise ValueError('No str or attributes dict!')

        if isinstance(attributes_dict_or_str, str):
            # self.convert_phone_number(attributes_dict_or_str)
            attributes_dict_or_str = self.str_to_dict(attributes_dict_or_str)
        self.phone_number = attributes_dict_or_str['phone_number']
        self.description = attributes_dict_or_str.get('description', None)
        self.country_code = attributes_dict_or_str.get('country_code',
                                                           None)
        self.area_code = int(attributes_dict_or_str.get('area_code', 0))
        self._clean_phone_number()

    def __str__(self, indent=0, n_subclasses=0):
        """Always a one_liner"""
        s = f"{self.__class__.__name__}: "
        if self.country_code:
            s += f'+{self.country_code} '
        if not self.area_code == 0:
            s += f'{self.area_code}'
        s += f'{self.phone_number}'
        if self.description:
            s += ' f({self.description})'
        return str_indent(s, indent)

    def __repr__(self):
        args = []
        if self.country_code:
            args.append(f'country_code="{self.country_code}"')
        if self.area_code:
            args.append(f'area_code={self.area_code}')
        args.append(f'phone_number="{self.phone_number}"')
        if self.description:
            args.append(f'description="{self.description}"')
        return 'Phone(dict(' + ', '.join(args) + '))'

    @staticmethod
    def str_to_dict(phone):
        """
        Return attribute_dict corresponding to phone number string
        Try to convert international numbers to the FDSN American standard.
        If already in American standard, use area code.
        Requires country codes, because we're not just the USA!

        Args:
            phone (str): phone number in (hopefully) one of several
                recognisable formats
        Returns:
            (tuple):
                ``country_code``
                ``area_code``: default=0
                ``phone_number``
                
        >>> Phone("+33 6 12345678")
        Phone(dict(country_code="33", phone_number="612345678"))
        >>> str(Phone("+33 6 12345678"))
        '+33 612345678'
        >>> Phone("+33 (6) 12345678")
        Phone(dict(country_code="33", phone_number="612345678"))
        >>> Phone("+1 (415) 123-4567")
        Phone(dict(country_code="1", area_code=415, phone_number="1234567"))
        >>> Phone("001 (415) 123-4567")
        Phone(dict(country_code="1", area_code=415, phone_number="1234567"))
        >>> Phone("+001 (415) 123-4567")
        Phone(dict(country_code="1", area_code=415, phone_number="1234567"))
        >>> Phone("(415) 123-4567")
        ValueError: "(415) 123-4567" returned no phone number
        """
        attr_dict = {'area_code': 0,
                     'phone_number': "",
                     'country_code': None}

        # For reference:
        # country = re.compile("^(\+{0,1}|00)[0-9]{1,3}$")
        # area = re.compile("^\({0,1}[0-9]{3}\){0,1}$")
        # phone = re.compile("^[0-9]{3}\-[0-9]{4}$")

        us_phone_match = re.match('(\\+00|\\+|00)(?P<country>[0-9]{1,3}) '
                                  '*(?P<area>\\({0,1}[0-9]{3}\\){0,1}) '
                                  '*(?P<phone>[0-9]{3}\\-[0-9]{4})$',
                                  phone)

        if us_phone_match:
            # print(us_phone_match.groupdict())
            attr_dict['country_code'] = us_phone_match.group('country')
            attr_dict['area_code'] = int(''.join(c for c in us_phone_match.group('area')
                                         if c in digits))
            attr_dict['phone_number'] = ''.join(c for c in us_phone_match.group('phone')
                                        if c in digits)
        else:
            c_code_plus_ptn = '^\+([0-9]{1,3})'
            c_code_zero_ptn = "^00([0-9]{1,3})"
            c_code_plus_re = re.compile(c_code_plus_ptn)
            c_code_zero_re = re.compile(c_code_zero_ptn)
            phone_ptn = "(?P<phone>(\([0-9]+\))* *([0-9]+[ \-\.]*)*[0-9]+)$"

            c_code = c_code_plus_re.match(phone)
            if not c_code:  # | for alternatives in regex doesn't work
                c_code = c_code_zero_re.match(phone)
                phone_re = re.compile(c_code_zero_ptn + " *" + phone_ptn)
            else:
                phone_re = re.compile(c_code_plus_ptn + " *" + phone_ptn)

            if c_code:
                attr_dict['country_code'] = c_code.group(1)

            mtch = phone_re.match(phone)
            if mtch:
                phone_number = mtch.group('phone')
                # The following is done to avoid FDSN reg exp restrictions
                # for phones, American based
                for chr in ["(", ")", ".", "-", " "]:
                    phone_number = phone_number.replace(chr, "")
                # self.phone_number = phone_number[0:3] + "-" + phone_number[3:]
                attr_dict['phone_number'] = phone_number
        if not attr_dict['phone_number']:
            raise ValueError(f'"{phone}" returned no phone number')
        return attr_dict

    def _clean_phone_number(self):
        """
        Make sure there are no non-digits
        """
        self.phone_number = "".join([c for c in self.phone_number if c in digits])
        if self.country_code is not None:
            self.country_code = "".join([c for c in self.country_code if c in digits])

    def to_obspy(self):
        """ Stupidly, phone_number has to have a dash inside of it 
        FDSN pattern search rule, copied by obspy
        """
        return PhoneNumber(self.area_code,
                           self.phone_number[:3] + '-' + self.phone_number[3:],
                           self.country_code,
                           self.description)
