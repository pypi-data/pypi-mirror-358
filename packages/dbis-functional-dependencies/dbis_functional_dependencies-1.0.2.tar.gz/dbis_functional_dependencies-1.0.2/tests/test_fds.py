"""
Created on 01.06.2022

@author: wf

Tests for https://dbis.rwth-aachen.de/dbis/RelDesign
using OER https://pypi.org/project/functional-dependencies/
"""
# from functional_dependencies.functional_dependencies import _rels2string

from tests.basetest import Basetest

# import from library
# import functional_dependencies as fd
# will not work if we use the same package name functional_depencencies

# import from local source code
import dbis_functional_dependencies.fds as fd


class TestSynthesisAndDecompositionAlgorithms(Basetest):
    """
    tests and playground for

    https://git.rwth-aachen.de/i5/teaching/dbis-digi-2022/-/issues/17

    using OER
    """

    def test_codd_1971_example(self):
        """'
        https://www.bibsonomy.org/bibtex/24b7b528f0502ff638c837f39a3ed3732
        https://forum.thethirdmanifesto.com/wp-content/uploads/asgarosforum/987737/00-efc-further-normalization.pdf
        """
        fde1 = fd.FD("EmpSerialNo", {"JobCode", "DeptNo", "Contract"})
        fdd1 = fd.FD("DeptNo", {"ManagerNo", "Contract"})
        fdd2 = fd.FD("ManagerNo", {"DeptNo", "Contract"})

        fds = fd.FDSet({fde1, fdd1, fdd2})
        employee = fd.RelSchema(fds.attributes(), fds)
        print(", ".join(attr for attr in employee.key()))

        print(
            not fds.isimplied({"DeptNo"}, {"EmpSerialNo"})
            and not fds.isimplied({"ManagerNo"}, {"EmpSerialNo"})
        )

        normalized = employee.synthesize(minimize=True)
        print("\n".join(str(schema) for schema in normalized))

    def testExample2013(self):
        """
        Synthese task 2013
        """
        fd1 = fd.FD({"A", "D"}, {"C"})
        fd2 = fd.FD({"B"}, {"D"})
        fd3 = fd.FD({"C"}, {"D", "E"})
        fd4 = fd.FD({"C", "D"}, "G")
        fd5 = fd.FD({"A", "B"}, {"E", "G"})
        fds = fd.FDSet({fd1, fd2, fd3, fd4, fd5})
        # print("basis\n",fds.basis(),"\n\n")
        rs2013 = fd.RelSchema(fds.attributes(), fds)
        print("synthesize\n", fd._rels2string(rs2013.synthesize()), "\n\n")

        #  a) Bestimmen Sie alle Schlüsselkandidaten von R
        # ck=fds.find_candidate_keys()

        sr = rs2013.synthesize(minimize=True)

        debug = True
        if debug:
            print("\n".join(str(schema) for schema in sr))

    def testSynthesisUB72020(self):
        """
        UB7 2020 Synthesealgorithmus
        """
        fd1 = fd.FD({"A", "G", "H"}, {"E"})
        fd2 = fd.FD({"C", "E"}, {"D", "H"})
        fd3 = fd.FD({"D"}, {"A", "C", "E"})
        fd4 = fd.FD({"D", "G"}, {"H"})
        fd5 = fd.FD({"G", "H"}, {"B", "D"})

        fds = fd.FDSet({fd1, fd2, fd3, fd4, fd5})
        rs2013 = fd.RelSchema(fds.attributes(), fds)
        #  a) Bestimmen Sie alle Schlüsselkandidaten von R
        # ck=fds.find_candidate_keys()

        sr = rs2013.synthesize(minimize=False)

        debug = True
        if debug:
            print("\n".join(str(schema) for schema in sr))

    def testBasis(self):
        """ """
