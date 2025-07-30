"""
stores dates and converts to UTCDateTime
"""
# Standard library modules
import logging
import re

# Non-standard modules
from obspy.core import UTCDateTime

from .obsinfo_class_list import ObsinfoClassList

logger = logging.getLogger("obsinfo")


class OIDates(ObsinfoClassList):
    """
    A list of :class:`OIDate`  d objects
    """
    def __init__(self, seq):
        """
        Args:
            seq: (list of OIDate or None): list of attribute dicts
                describing an OIDate
        """
        super().__init__(seq, OIDate)


class OIDate(object):
    """
    Store dates before converting to :class:`UTCDateTime`

    Attributes:
        date
    """
    def __init__(self, datestr):
        """
        Create object and assign attributes from attributes_dict.

        Args:
            attributes_dict (dict or :class:`ObsMetadata`): dict with
                relevangt keys
        """
        self.date = self.validated_date(datestr)

    def __str__(self, *args, **kwargs):
        if self.date is None:
            return('NONE')
        return(self.date)

    def __repr__(self):
        return f"OIDate('{self.date}')"

    def __eq__(self, other):
        if not isinstance(other, OIDate):
            return False
        return self.date == other.date

    def to_obspy(self):
        """
        Return :class:`UTCDateTime` object:
        """
        if self.date is None:
            return None
        return UTCDateTime(self.date)

    @staticmethod
    def validated_date(str_date):
        """
        Reformats an individual date string

        Uses regular expressions to match known dates, either in UTC date
        format or in UTC date and time format.
        The separator can be either "/" or "-"

        Args:
            date (str): a date in a given format
        Returns:
            (str): a reformatted date as string or None if no value
        """
        if str_date is None or str_date == int(0):
            # 0 is sometimes the default, the epoch date, 1/1/1970
            return None
        try:
            dt = UTCDateTime(str_date)
        except Exception as e:
            logger.error(f"Unrecognized date: {str_date}")
            return None
        regexp_date_UTC = re.compile(r"^[0-9]{4}[-\/][0-1]{0,1}[0-9][-\/][0-3]{0,1}[0-9]")
        regexp_date_and_time_UTC = re.compile(r"^[0-9]{4}[-\/][0-1]{0,1}[0-9][-\/][0-3]{0,1}[0-9]T[0-2][0-9]:[0-6][0-9]:{0,1}[0-6]{0,1}[0-9]{0,1}Z{0,1}")
        if not ((re.match(regexp_date_UTC, str_date) or re.match(regexp_date_and_time_UTC, str_date))):
            if dt.hours==0 and dt.minutes==0 and dt.seconds==0 and dt.microseconds==0:
                str_date = dt.strftime('%Y-%m-%d')
            else:
                str_date = dt.isoformat()
        return str_date

    @staticmethod
    def validated_dates(dates):
        """
        Convert list of dates to a standard format

        Args:
            dates (list): dates as strings
        Returns:
            (list): formatted dates as strings
        """
        if dates is None or not isinstance(dates, list):
            return []
        else:
            return [OIDate.validated_date(dt) for dt in dates]
