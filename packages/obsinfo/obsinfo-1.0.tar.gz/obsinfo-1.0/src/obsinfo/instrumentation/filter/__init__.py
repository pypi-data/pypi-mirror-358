"""
Filter classes:
- Coefficients
- FIR
- PolesZeros
- ResponseList
- Polynomial (never tested)
- ADConversion (subclass of PolesZeros)
- Analog (subclass of PolesZeros)
- Digital (subclass of Coefficients)
"""
from .filter import Filter
from .filter_template import FilterTemplate
from .coefficients import Coefficients
from .FIR import FIR
from .poles_zeros import PolesZeros
from .response_list import ResponseList
from .polynomial import Polynomial
from .AD_conversion import ADConversion
from .analog import Analog
from .digital import Digital
