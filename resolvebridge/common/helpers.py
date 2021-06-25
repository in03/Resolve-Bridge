""" Common helper functions in here
"""

import logging
import inspect
import re

logger = logging.getLogger(__name__)

def passmein(func):
    """ Lets functions reference themselves """
    def wrapper(*args, **kwargs):
        return func(func, *args, **kwargs)
    return wrapper

def get_current_module_name():
    """ Get the name of the module that called this function """
    return inspect.getmodulename(inspect.stack()[1][1])

def get_calling_module_name():
    """ Get the name of the module that called this function """
    return inspect.getmodulename(inspect.stack()[2][1])

def check_string_capitalised(string):
    """ Check to see if a string is in all CAPITAL letters. Boolean. """
    return bool(re.match('^[A-Z_]+$', string))

def get_module_logger(sublogger:str=""):
    """ Return a logger class for the calling module.
    Add a 'sublogger' string to differentiate multiple loggers in a module.
    """
    caller = inspect.getmodulename(inspect.stack()[2][1])
    if caller is None:
        caller = __name__
    return logging.getLogger(f"{caller}.{sublogger}")

def write_if_not_exist(filepath):
    """ Write an empty file if it doesn't exist at location """
    open(filepath, "a").close()
    return

def get_dict_depth(_dict):
    """ Get dictionary's depth or 'nestedness' """
    if isinstance(_dict, dict):
        return 1 + (min(map(get_dict_depth, _dict.values()))
            if _dict else 0)

    return 0
