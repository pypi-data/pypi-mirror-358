"""
InstrumentComponent class and subclasses Sensor, Preamplifier, Datalogger.
Equipment class
"""
# Standard library modules
import warnings
import logging

# Non-standard modules
from obspy.core.inventory.util import Equipment as obspy_Equipment
from obspy.core.utcdatetime import UTCDateTime

# obsinfo
from ..obsmetadata import ObsMetadata
from ..helpers import OIDate, OIDates, str_indent, str_list_str

warnings.simplefilter("once")
warnings.filterwarnings("ignore", category=DeprecationWarning)
logger = logging.getLogger("obsinfo")


class Equipment(obspy_Equipment):
    """
    Equipment.

    Equivalent to :class: obspy.core.inventory.util.Equipment

    Attributes:
        type (str):
        channel_modif (str):
        selected_config (str):
        description (str):
        manufacturer (str):
        model (str):
        vendor (str):
        serial_number (str):
        installation_date (str in date format):
        removal_date (str in date format):
        calibration_dates (str in date format):
        resource_id (str):
        obspy_equipment (class `obspy.core.inventory.equipmentEquipment`)`
    """

    def __init__(self, attributes_dict):
        """
        Constructor

        Args:
            attributes_dict (dict or :class:`ObsMetadata`): attributes of
                component
        """
        attributes_dict = ObsMetadata(attributes_dict)
        self.type = attributes_dict.get('type', None)
        self.description = attributes_dict.get('description', None)
        self.model = attributes_dict.get('model', None)
        self.manufacturer = attributes_dict.get('manufacturer', None)
        self.vendor = attributes_dict.get('vendor', None)
        self.serial_number = attributes_dict.get('serial_number', None)
        self.resource_id = attributes_dict.get('resource_id', None)
        self.installation_date = OIDate(attributes_dict.get('installation_date', None))
        self.removal_date = OIDate(attributes_dict.get('removal_date', None))
        self.calibration_dates = OIDates(attributes_dict.get('calibration_dates', None))

    def __repr__(self):
        args = []
        if self.type:
            args.append(f"'type': '{self.type}'")
        if self.description:
            args.append(f"'description': '{self.description}'")
        if self.manufacturer:
            args.append(f"'manufacturer': '{self.manufacturer}'")
        if self.model:
            args.append(f"'model': '{self.model}'")
        if self.vendor:
            args.append(f"'vendor': '{self.vendor}'")
        if self.serial_number:
            args.append(f"'serial_number': '{self.serial_number}'")
        if self.installation_date.date is not None:
            args.append(f"'installation_date': {self.installation_date}")
        if self.removal_date.data is not None:
            args.append(f"'removal_date': {self.removal_date}")
        if self.calibration_dates:
            args.append(f"'calibration_dates': {self.calibration_dates}")
        return 'Equipment({' + ", ".join(args) + '})'

    def __str__(self, indent=0, n_subclasses=0):
        if n_subclasses < 0:
            return f"{type(self)}"
        s = 'Equipment:\n'
        s += f"    type: {self.type}\n"
        s += f"    description: {self.description}\n"
        s += f"    model: {self.model}"
        if self.manufacturer is not None:
            s += f"\n    manufacturer: {self.manufacturer}"
        if self.vendor is not None:
            s += f"\n    vendor: {self.vendor}"
        if self.serial_number is not None:
            s += f"\n    serial_number: {self.serial_number}"
        if self.resource_id is not None:
            s += f"\n    resource_id: {self.resource_id}"
        if self.installation_date.date is not None:
            s += f"\n    installation_date: {self.installation_date}"
        if self.removal_date.date is not None:
            s += f"\n    removal_date: {self.removal_date}"
        if self.calibration_dates:
            s += f"\n    calibration_dates: {self.calibration_dates.__str__(indent=4, n_subclasses=n_subclasses-1)}"
        return str_indent(s, indent)

    def to_obspy(self):
        """
        Convert an equipment (including the equipment description in
        components) to its obspy object

        Returns:
            (:class:`obspy.core.invertory.util.Equipment`)
        """
        return obspy_Equipment(
            type=self.type,
            description=self.description,
            manufacturer=self.manufacturer,
            vendor=self.vendor,
            model=self.model,
            serial_number=self.serial_number,
            installation_date=self.installation_date.to_obspy(),
            removal_date=self.removal_date.to_obspy(),
            calibration_dates=self.calibration_dates.to_obspy(),
            resource_id=self.resource_id)
