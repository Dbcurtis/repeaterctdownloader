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

    __known = ', '.join(sorted([a for a in __kc.keys()]))
    @staticmethod
    def get_controller_ids():
        """KnownControllers.get_controller_ids()

        Return the controller ID strings as a list
        """
        return sorted([
            c[0].get_Ctr_type for c in
            [n for n in KnownControllers.__kc.values()]
        ])

    @staticmethod
    def get_known():
        """KnownControllers.get_known()

        Returns a string that has recognized names for the known controllers.
        Not Sorted, other versions of the names can be recognized
        """
        return KnownControllers.__known

    @staticmethod
    def select_controller(_str):
        _ = _str.strip()
        result = None
        for _n in KnownControllers.__kc.values():
            _mx = _n[1].match(_)
            if _mx:
                result = _n[0]
                break
        return result

    def __init__(self):
        self._jj = copy.copy(KnownControllers.__kc)

    def known_controllers(self):
        """known_controllers()

        Returns a dictionary with the controler reference name as key, and for each key
        a tuple of the controller object, and a re pattern for matching users input
        """
        return copy.copy(self._jj)



    def __str__(self):
        return KnownControllers.get_known()

if __name__ == '__main__':
    print(KnownControllers.get_known())
    print(KnownControllers.get_controller_ids())
    