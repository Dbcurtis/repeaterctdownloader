#!/usr/bin/env python3
"""  TBD  """

import re
import copy
import dlxii
import rlc1plus

class KnownControllers:
    """ TBD
    """

    __kc = {
        'dlx2':(dlxii.DlxII(), re.compile(r"dlx(ii|2)", re.A|re.I)),
        'rlc1+':(rlc1plus.Rlc1Plus(), re.compile(r"rlc1(\+|p(lus)?)")),}

    def __init__(self):
        self._jj = KnownControllers.__kc

    def known_controllers(self):
        """known_controllers()

        Returns a dictionary with the controler reference name as key, and for each key
        a tuple of the controller object, and a re pattern for matching users input
        """
        return copy.deepcopy(self._jj)

    def __str__(self):
        return KnownControllers.__kc.keys()
    