from textwrap import indent
import inspect
import logging

logger = logging.getLogger("obsinfo")

def str_indent(s, nchars: int):
    """
    Indents all lines of a string by a given # of spaces

    Normally indents all but the first line, if nchars is negative then indents
    all lines including the first, by -nchars

    Args:
        s (str): string to be indented
        nchars (int):  if > 0: indent all lines except the first by nchars.
                       if < -: indent all lines by -nchars
    """
    if nchars == 0:
        return s
    elif nchars > 0:
        return (nchars * ' ').join(s.splitlines(True))
    else:
        return indent(s, -nchars * ' ')


def str_list_str(slist, indent=0, n_subclasses=0):
    """
    Returns list of strings formatted for obsinfo printing
    Args:
        slist (list of str): list of strs
        indent (int):  # of characters to indent by
        n_subclasses (int): if < 0, return a one-line string
    """
    if slist is None:
        return 'None'
    if not isinstance(slist, list):
        raise TypeError('slist is not a list')

    if n_subclasses < 0:
        if len(slist) == 0:
            return '[]'
        elif len(slist) == 1:
            return f'["{slist[0]}"]'
        return f'List of {len(slist)} strings'
    s = 'List of strings:'
    for x in slist:
        s += f'\n- {x}'
    return str_indent(s, indent)


def verify_dict_is_empty(attributes_dict):
    if len(attributes_dict) == 0:
        return
    stack = inspect.stack()
    the_class = stack[1][0].f_locals["self"].__class__.__name__
    the_method = stack[1][0].f_code.co_name
    logger.error(f'attributes dict in {the_class}.{the_method} has '
                     f'leftover keys: {list(attributes_dict.keys())}')

        