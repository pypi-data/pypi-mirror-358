"""
Created on 2022-06-08

@author: wf
"""

from tests.basetest import Basetest
from dbis_functional_dependencies.fdsbase import Set, FD, Notation


class FdsBaseTest(Basetest):
    """
    test for base classes
    """

    def test_Set(self):
        """
        test set operations
        """
        s1 = Set("ABCD")
        debug = True
        expected = ["\{A,B,C,D\}", "{A,B,C,D}", "{A,B,C,D}", "ABCD"]
        for i, notation in enumerate(Notation):
            Set.notation = notation

            if debug:
                print(f"{i+1} {notation}:{s1}")
            self.assertEqual(expected[i], str(s1))

    def test_FD(self):
        """
        test functional dependency stringification

        https://git.rwth-aachen.de/i5/teaching/dbis-functional-dependencies/-/issues/10
        """
        debug = True
        fd = FD("AB", "CD")
        expected = ["AB \to CD", "AB→CD", "AB->CD", "AB->CD"]
        for i, notation in enumerate(Notation):
            FD.notation = notation
            if debug:
                print(f"{i+1} {notation}:{fd}")
            self.assertEqual(expected[i], str(fd))
