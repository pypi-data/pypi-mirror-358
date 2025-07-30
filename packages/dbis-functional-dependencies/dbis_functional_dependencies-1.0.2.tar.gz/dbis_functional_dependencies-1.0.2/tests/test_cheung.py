"""
Created on 2022-06-18

test for http://www.mathcs.emory.edu/~cheung/Courses/377/Syllabus/9-NormalForms/examples.html example
@author: wf
"""
from tests.fdstest import FunctionalDependencySetTest
from dbis_functional_dependencies.fdsbase import Notation, RelSchema, Set, FD
from dbis_functional_dependencies.BCNF import FunctionalDependencySet
import dbis_functional_dependencies.fds as fd
import logging


class Test_Checung(FunctionalDependencySetTest):
    """
    test examples for http://www.mathcs.emory.edu/~cheung/Courses/377/Syllabus/9-NormalForms/examples.html example
    """

    def getExampleSchema(self):
        """
        get the example Schema
        """
        fds = FunctionalDependencySet()
        fds.add_attribute("A", "SSN")
        fds.add_attribute("B", "FName")
        fds.add_attribute("C", "LName")
        fds.add_attribute("D", "SupSSN")
        fds.add_attribute("E", "DNum")
        fds.add_attribute("F", "DName")
        fds.add_attribute("G", "MgrSSN")
        fds.add_attribute("H", "MgrStartDate")
        fds.add_attribute("I", "PNum")
        fds.add_attribute("J", "PName")
        fds.add_attribute("K", "Hours")
        fds.add_attribute("L", "DependName")
        fds.add_attribute("M", "RelationShip")
        fds.add_dependency("A", "BCDE")
        fds.add_dependency("E", "FGH")
        fds.add_dependency("I", "J")
        fds.add_dependency("AI", "K")
        fds.add_dependency("AL", "M")
        rs = RelSchema(fds.attributes, fds)
        return rs

    def testFindAllKeys(self):
        """
        test find all Keys
        """
        debug = True
        rs = self.getExampleSchema()
        expected = ["AIL"]
        self.checkCandidateKeys(rs.fds, expected, debug)

    def testBCNF(self):
        """
        test BCNF
        """
        rs = self.getExampleSchema()
        self.assertFalse(rs.fds.isBCNF())
        fd = rs.fds.getNonBCNF()
        print(fd)

    def testDecompose(self):
        """
        test decomposition
        """
        rs = self.getExampleSchema()
        # rs.fds.decompose2(verbose=False)
