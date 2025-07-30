"""
Created on 2022-06-04

@author: wf
"""
from tests.fdstest import FunctionalDependencySetTest
from dbis_functional_dependencies.BCNF import FunctionalDependencySet


class Test_TUM_Examples(FunctionalDependencySetTest):
    """
    test examples of TUM München
    """

    def testTutorial(self):
        """
        https://docplayer.org/46338275-8-tutoruebung-zu-grundlagen-datenbanken.html
        """
        debug = True
        fds = FunctionalDependencySet("ABCDEFGH")
        fds.add_dependency("B", "DE")
        fds.add_dependency("A", "BC")
        fds.add_dependency("CE", "BF")
        fds.add_dependency("FG", "DH")
        self.checkAttributeClosure(fds, "A", expected="ABCDEF", debug=debug)
        # A->A
        # A->BC
        # B->DE : A->BCDE
        # CE-> BF : A->ABCDEF
