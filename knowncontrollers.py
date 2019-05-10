#!/usr/bin/env python3
"""  TBD  """

import os
import re
import importlib
import copy
import logging
import logging.handlers
#import dlxii
#import rlc1plus

LOGGER = logging.getLogger(__name__)

LOG_DIR = os.path.dirname(os.path.abspath(__file__)) + '/logs'
LOG_FILE = '/knowncontrollers'



CTRL_DICT_A = {

    'dlx2':(re.compile(r"dlx(ii|2)", re.A|re.I), 'dlxii'),
    'rlclub': (re.compile(r"(rlcclub|club|rlclub)", re.A|re.I), 'club'),
    'rlc1+':(re.compile(r"rlc1(\+|p(lus)?)", re.A|re.I), 'rlc1plus'),
}

_KNOWN = ', '.join(sorted([a for a, b in CTRL_DICT_A.items()]))

def get_controller_ids():
    """KnownControllers.get_controller_ids()

    Return the controller ID strings as a list
    """
    return sorted([
        c[1] for c in
        [n for n in CTRL_DICT_A.values()]
    ])


def get_known():
    """KnownControllers.get_known()

    Returns a string that has recognized names for the known controllers.
    Not Sorted, other versions of the names can be recognized
    """
    return _KNOWN

def select_controller(_str):
    """select_controller(str)

    Matches _str against controlled class/regex tuples
    If no match, returns None, otherwise returns an object of the specifiec controler class
    """
    _ = _str.strip()
    result = None
    for _n in CTRL_DICT_A.values():
        _mx = _n[0].match(_)
        if _mx:
            #result = _n[0]  # get the object corrosponding to the match
            ctrl = importlib.import_module(_n[1])
            result = (_n[1], ctrl.Device())
            break
    return result

class KnownControllers:
    """ TBD
    """
    # pylint: disable=R0903
    def __init__(self):
        self._jj = copy.copy(CTRL_DICT_A)

    def known_controllers(self):
        """known_controllers()

        Returns a dictionary with the controler reference name as key, and for each key
        a tuple of a re pattern for matching users input, and the controller id
        """
        return copy.copy(self._jj)

    def __str__(self):
        return get_known()

if __name__ == '__main__':
    if not os.path.isdir(LOG_DIR):
        os.mkdir(LOG_DIR)
    LF_HANDLER = logging.handlers.RotatingFileHandler(
        ''.join([LOG_DIR, LOG_FILE, ]),
        maxBytes=10000,
        backupCount=5,
    )
    LF_HANDLER.setLevel(logging.DEBUG)
    LC_HANDLER = logging.StreamHandler()
    LC_HANDLER.setLevel(logging.DEBUG)  #(logging.ERROR)
    LF_FORMATTER = logging.Formatter(
        '%(asctime)s - %(name)s - %(funcName)s - %(levelname)s - %(message)s')
    LC_FORMATTER = logging.Formatter('%(name)s: %(levelname)s - %(message)s')
    LC_HANDLER.setFormatter(LC_FORMATTER)
    LF_HANDLER.setFormatter(LF_FORMATTER)
    THE_LOGGER = logging.getLogger()
    THE_LOGGER.setLevel(logging.DEBUG)
    THE_LOGGER.addHandler(LF_HANDLER)
    THE_LOGGER.addHandler(LC_HANDLER)
    THE_LOGGER.info('commandreader executed as main')
    #LOGGER.setLevel(logging.DEBUG)
    print(get_known())
    print(get_controller_ids())
