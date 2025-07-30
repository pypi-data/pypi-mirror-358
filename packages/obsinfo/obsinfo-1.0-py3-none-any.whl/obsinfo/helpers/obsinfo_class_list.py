"""
ObsinfoClassList template class

A template for all lists of obsinfo classes.
Defines how __str__ is to be printed and checks to make sure that
all elements are of the desired class
"""
import warnings
import logging
import inspect

from .functions import str_indent

warnings.simplefilter("once")
warnings.filterwarnings("ignore", category=DeprecationWarning)
logger = logging.getLogger("obsinfo")


class ObsinfoClassList(list):
    def __init__(self, seq, element_class):
        """
        Args:
            seq (list or None): sequence of dicts or of :class:element_class.
                If dicts, converts to element_class type using element_class()
                If None, return empty instance
            element_class (:class:): the class that every element should be
                (or become)
        """
        if seq is not None and not isinstance(seq, list):
            raise TypeError(f'seq ({type(seq)}) is neither a list nor None')
        # Validate element_class
        if not inspect.isclass(element_class):
            raise TypeError('element_class is not a class')
        self.element_class = element_class
        
        if seq is None:
            super().__init__([])
            return
        elif len(seq) == 0:
            super().__init__([])
            return
        
        # Verify all elements are of same type
        for x in seq:
            if not isinstance(x, type(seq[0])):
                raise TypeError(f'seq elements are not all of same type '
                                f'({type(x)} != {type(seq[0])})')

        if not isinstance (seq[0], element_class):
            seq = [element_class(x) for x in seq]

        super().__init__(x for x in seq)

    def append(self, item):
        if not isinstance(item, self.element_class):
            item = element_class(item)
        super().append(item)

    def __eq__(self, other):
        if not isinstance(other, ObsinfoClassList):
            return False
        if not len(self) == len(other):
            return False
        for x, y in zip(self, other):
            if not x == y:
                return False
        return True

    def __str__(self, indent=0, n_subclasses=0):
        kwargs = dict(indent=indent, n_subclasses=n_subclasses-1)
        s = f'{self.__class__.__name__}:'
        if len(self) == 0:
            return s + ' []'
        elif len(self) == 1:
            return s + f' [{self[0].__str__(**kwargs)}]'
        if n_subclasses < 0:
            return s + f' {len(self)} {self.element_class.__name__}s'
        kwargs['indent'] += 6
        for x in self:
            s += f'\n    - {x.__str__(**kwargs)}'
        return str_indent(s, indent)
        
    def to_obspy(self):
        """Return list of element.to_obspy()"""
        if len(self) == 0:
            return None
        if getattr(self[0], 'to_obspy'):
            return [x.to_obspy() for x in self]
        else:
            raise ValueError('{self.element_class.__name__} class has no to_obspy() method')
