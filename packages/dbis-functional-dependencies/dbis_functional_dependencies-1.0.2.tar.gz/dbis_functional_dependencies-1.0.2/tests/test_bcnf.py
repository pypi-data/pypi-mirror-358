"""
Created on 2022-05-25

@author: wf
@author: rcf
@author: jv

Tests for https://dbis.rwth-aachen.de/dbis-vl/RelDesign
"""
from tests.fdstest import FunctionalDependencySetTest
from dbis_functional_dependencies.fdsbase import Set, Notation
from dbis_functional_dependencies.BCNF import FunctionalDependencySet


class TestSynthesisAndDecompositionAlgorithms(FunctionalDependencySetTest):
    """
    tests and playground for

    https://git.rwth-aachen.de/i5/teaching/dbis-digi-2022/-/issues/17

    https://gist.github.com/maxwellgerber/4caae07161ea66123de4d6c374387786
    https://github.com/Xuefeng-Zhu/bcnf/blob/master/BCNF.py

    """

    def setUp(self, debug=False, profile=True):
        """
        setUp for test environment
        """
        FunctionalDependencySetTest.setUp(self, debug=debug, profile=profile)
        self.kemperBook = "Alfons Kemper, André Eickler: DATENBANK-SYSTEME, De Gruyter, 10. Ausgabe 2015, ISBN-13 9-783110-443752"
        # do not run assertions/tests for open tickets
        self.testOpenTickets = False

    def testFindCandidateKeys(self):
        """
        test candidate key finding
        """
        # https://stackoverflow.com/questions/2718420/candidate-keys-from-functional-dependencies
        # https://stackoverflow.com/a/14595217/1497139
        debug = self.debug
        debug = False
        fds = FunctionalDependencySet("ABCDE")
        fds.add_dependency("A", "B")
        fds.add_dependency("BC", "E")
        fds.add_dependency("ED", "A")
        # expected checked against https://normalizer.db.in.tum.de/index.py ✅ by WF
        self.checkCandidateKeys(fds, expected=["ACD", "BCD", "CDE"], debug=debug)

        ex1 = FunctionalDependencySet()
        ex1.add_attribute("A", "id", "id")
        ex1.add_attribute("B", "class_id", "Klassen_id")
        ex1.add_attribute("C", "name", "Name")
        ex1.add_attribute("D", "score", "Punktzahl")
        ex1.add_dependency("A", "C")
        ex1.add_dependency("AB", "D")
        # self.checkDecompose(ex1,debug=debug)
        # expected checked against https://normalizer.db.in.tum.de/index.py ✅ by WF
        self.checkCandidateKeys(ex1, expected=["AB"], debug=debug)

        ex2 = FunctionalDependencySet("BTSPDCHAR")
        ex2.add_dependency("R", "SP")
        ex2.add_dependency("SP", "DCH")
        ex2.add_dependency("B", "SCT")
        ex2.add_dependency("DH", "A")
        ex2.add_dependency("TS", "R")
        ex2.add_dependency("SPR", "B")
        ex2.add_dependency("S", "P")
        # expected checked against https://normalizer.db.in.tum.de/index.py ✅ by WF
        self.checkCandidateKeys(ex2, expected=["B", "R", "ST"], debug=debug)

    def testAttributeClosure(self):
        """
        test calculating the attribute closure
        """
        debug = self.debug
        debug = False
        fds = FunctionalDependencySet("ABCDEF")
        fds.add_dependency("AB", "C")
        fds.add_dependency("A", "D")
        fds.add_dependency("D", "E")
        fds.add_dependency("AC", "B")
        expected = ["ADE", "ABCDE", "B", "DE"]
        for i, attr_set in enumerate(["A", "AB", "B", "D"]):
            # expected checked against
            # https://de.wikipedia.org/wiki/Funktionale_Abh%C3%A4ngigkeit#Attributh%C3%BClle ✅ by JV
            self.checkAttributeClosure(fds, attr_set, expected[i], debug=debug)

        fds = FunctionalDependencySet("ABCDEFGH")
        fds.add_dependency("AB", "C")
        fds.add_dependency("D", "EF")
        fds.add_dependency("A", "GH")
        fds.add_dependency("G", "B")
        # expected checked against
        # https://de.wikipedia.org/wiki/Funktionale_Abh%C3%A4ngigkeit#Attributh%C3%BClle ✅ by WF
        self.checkAttributeClosure(fds, "A", expected="ABCGH", debug=debug)

    def testDecompose(self):
        """
        test decomposition algorithm
        """
        debug = False
        fds = FunctionalDependencySet("ABCDEFG")
        fds.add_dependency("AB", "CD")
        fds.add_dependency("C", "EF")
        fds.add_dependency("G", "A")
        fds.add_dependency("G", "F")
        fds.add_dependency("CE", "F")
        # expected checked against https://normalizer.db.in.tum.de/index.py  ✅ by WF
        self.checkDecompose(fds, expected=["ABCD", "AG", "BEG", "FG"], debug=debug)
        if debug:
            print(fds.is_lossy())

        fds = FunctionalDependencySet("ANBGP")
        fds.add_dependency("A", "N")
        fds.add_dependency("B", "GP")
        # expected checked against https://normalizer.db.in.tum.de/index.py  ✅ by WF
        self.checkDecompose(fds, expected=["AB", "AN", "BGP"], debug=debug)
        if debug:
            print(fds.is_lossy())

        fds = FunctionalDependencySet("ABC")
        fds.add_dependency("AB", "C")
        fds.add_dependency("C", "A")
        # both expected checked against https://normalizer.db.in.tum.de/index.py  ✅ by JV
        self.checkCandidateKeys(fds, expected=["AB", "BC"], debug=debug)
        self.checkDecompose(fds, expected=["AC", "BC"], debug=debug)
        if debug:
            print(fds.is_lossy())

        fds = FunctionalDependencySet("ABCDE")
        fds.add_dependency("AE", "BC")
        fds.add_dependency("AC", "D")
        fds.add_dependency("CD", "BE")
        fds.add_dependency("D", "E")
        # expected checked against https://normalizer.db.in.tum.de/index.py  ✅ by JV
        self.checkCandidateKeys(fds, expected=["AC", "AD", "AE"], debug=debug)

        print(fds.decompose())
        # expected checked against https://normalizer.db.in.tum.de/index.py  ❌ by JV correct answer: ['ACD', 'DE', 'BCD']
        # self.checkDecompose(fds, expected=['ACD', 'DE', 'BCD'], debug=debug)

    def testDecompose2(self):
        """
        test decomposition algorithm 2
        """
        debug = False
        fds = FunctionalDependencySet("ABCDEFG")
        fds.add_dependency("AB", "CD")
        fds.add_dependency("C", "EF")
        fds.add_dependency("G", "A")
        fds.add_dependency("G", "F")
        fds.add_dependency("CE", "F")
        # expected checked against https://normalizer.db.in.tum.de/index.py  ✅ by WF
        self.checkDecompose2(
            fds, expected=["ABCD", "AG", "BEG", "FG"], debug=debug, genEx=False
        )
        if debug:
            print(fds.is_lossy())

        fds = FunctionalDependencySet("ANBGP")
        fds.add_dependency("A", "N")
        fds.add_dependency("B", "GP")
        # expected checked against https://normalizer.db.in.tum.de/index.py  ✅ by WF
        self.checkDecompose2(fds, expected=["AB", "AN", "BGP"], debug=debug)
        if debug:
            print(fds.is_lossy())

        fds = FunctionalDependencySet("ABC")
        fds.add_dependency("AB", "C")
        fds.add_dependency("C", "A")
        # both expected checked against https://normalizer.db.in.tum.de/index.py  ✅ by JV
        self.checkCandidateKeys(fds, expected=["AB", "BC"], debug=debug)
        self.checkDecompose2(fds, expected=["AC", "BC"], debug=debug)
        if debug:
            print(fds.is_lossy())

        fds = FunctionalDependencySet("ABCDE")
        fds.add_dependency("AE", "BC")
        fds.add_dependency("AC", "D")
        fds.add_dependency("CD", "BE")
        fds.add_dependency("D", "E")
        # expected checked against https://normalizer.db.in.tum.de/index.py  ✅ by JV
        self.checkCandidateKeys(fds, expected=["AC", "AD", "AE"], debug=debug)
        # expected checked against https://normalizer.db.in.tum.de/index.py  ✅ by JV correct answer: ['ACD', 'DE', 'BCD']
        self.checkDecompose2(fds, expected=["ACD", "DE", "BCD"], debug=debug)

    def getTumWS145L7(self):
        """
        https://db.in.tum.de/teaching/ws1415/grundlagen/Loesung07.pdf
        """
        fds = FunctionalDependencySet("ABCDEF")
        fds.add_dependency("A", "BC")
        fds.add_dependency("C", "DA")
        fds.add_dependency("E", "ABC")
        fds.add_dependency("F", "CD")
        fds.add_dependency("CD", "BEF")
        return fds

    def testExampleTumWS1415Loesung7_Hausaufgabe1(self):
        """
        https://db.in.tum.de/teaching/ws1415/grundlagen/Loesung07.pdf
        """
        debug = self.debug
        debug = False
        fds = self.getTumWS145L7()
        # all expected checked against  https://db.in.tum.de/teaching/ws1415/grundlagen/Loesung07.pdf  ✅
        # by WF

        # a) calculate Attribute closure of A
        self.checkAttributeClosure(fds, "A", expected="ABCDEF", debug=debug)
        # b) find candidate keys
        self.checkCandidateKeys(fds, expected=["A", "C", "E", "F"], debug=debug)
        # c) canonical cover
        self.checkCanonicalCover(fds, expected="{A→C,E→A,F→CD,C→BEF}", debug=debug)
        # d) synthesis algorithm
        fds = self.getTumWS145L7()
        self.checkSynthesis(fds, expected="{A→C,E→A,F→CD,C→BEF}", debug=debug)

    def testExampleSQLQuery(self):
        fds = FunctionalDependencySet("ABCDEFGH")
        fds.add_dependency("B", "A")
        fds.add_dependency("B", "G")
        fds.add_dependency("B", "H")
        fds.add_dependency("D", "E")
        fds.add_dependency("D", "G")
        fds.add_dependency("F", "A")
        fds.add_dependency("F", "B")
        fds.add_dependency("F", "C")
        fds.add_dependency("F", "G")
        fds.add_dependency("F", "H")

        self.checkCanonicalCover(fds, "{B→AGH,D→EG,F→BC}", False)
        # expected checked against https://normalizer.db.in.tum.de/index.py  ✅ by JV

        fds2 = FunctionalDependencySet("ABCDEFGH")
        fds2.add_dependency("B", "AGH")
        fds2.add_dependency("D", "EG")
        fds2.add_dependency("F", "ABCGH")

        # expected checked against https://normalizer.db.in.tum.de/index.py  ✅ by JV
        self.checkCanonicalCover(fds2, "{B→AGH,D→EG,F→BC}", False)

    def testExample2017(self):
        """
        example from 2017
        """
        debug = False
        fds = FunctionalDependencySet("ABCDEF")
        fds.add_dependency("A", "CD")
        fds.add_dependency("AC", "E")
        fds.add_dependency("BE", "F")
        fds.add_dependency("C", "B")
        fds.add_dependency("D", "EF")
        # expected checked against https://normalizer.db.in.tum.de/index.py  ✅ by JV
        self.checkCandidateKeys(fds, expected=["A"], debug=debug)

        # expected checked against https://normalizer.db.in.tum.de/index.py  ❌ by JV correct answer: ['BEF', 'BC', 'DE', 'ACD']
        self.checkDecompose2(fds, expected=["BEF", "BC", "DE", "ACD"], debug=debug)
        if debug:
            fdslist = fds.decompose2()
            for fdset in fdslist:
                print(fdset)

        # tables=fds.decompose_all()
        # if debug:
        #     print(tables)
        # self.assertEqual(13,len(tables))

    def getExamples(self):
        return [
            self.getExample2013(),
            self.getExample2020_71(),
            self.getExample2021_71(),
            self.getExampleMultiplePaths(),
            self.getIdenticalToWikipediaExample(),
            self.getNotIdenticalToWikipediaExample(),
            self.getTumWS145L7(),
            self.getWikipediaExample(),
        ]

    def getExample2020_71(self):
        """ """
        fds = FunctionalDependencySet("ABCDEGHI")
        fds.add_dependency("A", "CH")
        fds.add_dependency("AC", "B")
        fds.add_dependency("D", "E")
        fds.add_dependency("G", "BE")
        fds.add_dependency("GI", "DH")
        fds.add_dependency("H", "AC")
        return fds

    def getExample2023synthe(self):
        """
        get example for 2023 synthe
        """
        fds = FunctionalDependencySet("ABCDEFG")
        fds.add_dependency("AB", "E")
        fds.add_dependency("ABC", "DEF")
        fds.add_dependency("ED", "F")
        fds.add_dependency("F", "G")
        fds.add_dependency("EFG", "BD")
        fds.add_dependency("E", "B")
        return fds

    def getExample2023deko(self):
        """
        get example for 2023 deko
        """
        fds = FunctionalDependencySet("ABCDEF")
        fds.add_dependency("B", "C")
        fds.add_dependency("A", "EF")
        fds.add_dependency("C", "D")
        fds.add_dependency("EF", "ABC")
        return fds

    def testGenerateFDsetClosure(self):
        debug = self.debug
        fds = self.getExample2023deko()
        fds.completeFDsetToClosure(verbose=False)

        if debug:
            for fd in fds:
                print(f"{fd}")

        return

    def testHausaufgabe2020(self):
        """
        test Aufgabe 7.1
        """
        debug = self.debug
        debug = False
        fds = self.getExample2020_71()
        self.checkAttributeClosure(fds, "A", expected="ABCH", debug=debug)
        if debug:
            print(fds.get_attr_closure("A"))
        return

        acABC = fds.get_attr_closure("ABC")
        acGI = fds.get_attr_closure("GI")
        subsetFD2ACH = fds.calculate_fds_in_subset(["Aa", "Cc", "Hh"])

        ck = fds.find_candidate_keys()
        if debug:
            print(acABC)
            print(acGI)
            print(ck)
            print(subsetFD2ACH)
        tables = fds.decompose()
        if debug:
            print(tables)

        fds2 = FunctionalDependencySet(["Aa", "Bb", "Cc", "Dd", "Ee", "Gg", "Hh", "Ii"])
        fds2.add_dependency(["Aa"], ["Cc", "Hh"])
        fds2.add_dependency(["Aa", "Cc"], ["Bb"])
        fds2.add_dependency(["Dd"], ["Ee"])
        fds2.add_dependency(["Gg"], ["Bb", "Ee"])
        fds2.add_dependency(["Gg", "Ii"], ["Dd", "Hh"])
        fds2.add_dependency(["Hh"], ["Aa", "Cc"])

        ac2ABC = fds2.get_attr_closure(["Aa", "Bb", "Cc"])
        ac2GI = fds2.get_attr_closure(["Gg", "Ii"])
        subsetFDs2ACH = fds2.calculate_fds_in_subset(["Aa", "Cc", "Hh"])
        debug = True
        ck = fds2.find_candidate_keys()
        if debug:
            print(ac2ABC)
            print(ac2GI)
            print(ck)
            print(subsetFDs2ACH)
        tables = fds2.decompose()
        if debug:
            print(tables)
        self.fail("assertions missing")

    def getExample2021_71(self):
        """
        Excercise 2021 7.1
        """
        fds = FunctionalDependencySet("ABCDEG")
        fds.add_dependency("ADE", "CG")
        fds.add_dependency("B", "AD")
        fds.add_dependency("CG", "D")
        fds.add_dependency("DG", "A")
        fds.add_dependency("G", "BC")
        return fds

    def getExampleMultiplePaths(self):
        """
        Diferrent reductions possible, all should be recognized
        """
        fds = FunctionalDependencySet("ABCDE")
        fds.add_dependency("AE", "BC")
        fds.add_dependency("A", "BC")
        fds.add_dependency("E", "BC")
        fds.add_dependency("D", "A")
        fds.add_dependency("D", "BC")
        return fds

    def testExampleMultiplePaths(self):
        """
        Example multiple paths
        """
        debug = self.debug
        debug = False
        fds = self.getExampleMultiplePaths()
        self.checkCandidateKeys(fds, expected=["DE"], debug=debug)
        fdslist = fds.synthesize(verbose=debug, genEx=False)
        if debug:
            for fds in fdslist:
                print(fds)

    def getWikipediaExample(self):
        fds = FunctionalDependencySet("ABCDEF")
        fds.add_dependency("A", "BE")
        fds.add_dependency("AE", "BD")
        fds.add_dependency("F", "CD")
        fds.add_dependency("CD", "BEF")
        fds.add_dependency("CF", "B")
        return fds

    def getIdenticalToWikipediaExample(self):
        fds = FunctionalDependencySet("ABCDEF")
        fds.add_dependency("AE", "DB")
        fds.add_dependency("CF", "B")
        fds.add_dependency("F", "CD")
        fds.add_dependency("A", "BE")
        fds.add_dependency("DC", "EBF")
        return fds

    def getNotIdenticalToWikipediaExample(self):
        fds = FunctionalDependencySet("ABCDEF")
        fds.add_dependency("AE", "DB")
        fds.add_dependency("CF", "B")
        fds.add_dependency("F", "CD")
        fds.add_dependency("A", "B")
        fds.add_dependency("DC", "EBF")
        return fds

    def testIsIdentical(self):
        fds1 = self.getWikipediaExample()
        self.assertTrue(fds1.isIdentical(fds1))

        fds2 = self.getIdenticalToWikipediaExample()
        self.assertTrue(fds1.isIdentical(fds2))

        fds3 = self.getNotIdenticalToWikipediaExample()
        self.assertFalse(fds3.isIdentical(fds1))
        self.assertFalse(fds2.isIdentical(fds3))

    def testIsCorrectLeftReduction(self):
        # Testing against own left reduction method
        fds = self.getWikipediaExample()
        original = fds.copy()
        fds.left_reduction(genEx=False)
        self.assertTrue(original.isCorrectLeftReduction(fds))

        fds = self.getExample2020_71()
        original = fds.copy()
        fds.left_reduction()
        self.assertTrue(original.isCorrectLeftReduction(fds))

        fds = self.getExample2021_71()
        original = fds.copy()
        fds.left_reduction()
        self.assertTrue(original.isCorrectLeftReduction(fds))

        fds = self.getExample2013()
        original = fds.copy()
        fds.left_reduction()
        self.assertTrue(original.isCorrectLeftReduction(fds))

        fds = self.getExampleMultiplePaths()
        original = fds.copy()
        fds.left_reduction()
        self.assertTrue(original.isCorrectLeftReduction(fds))

        fds = self.getTumWS145L7()
        original = fds.copy()
        fds.left_reduction()
        self.assertTrue(original.isCorrectLeftReduction(fds))

        # Testing against wrong left reductions
        fds = FunctionalDependencySet("ABCDEF")
        fds.add_dependency("A", "BE")
        fds.add_dependency("AE", "BD")
        fds.add_dependency("F", "CD")
        fds.add_dependency("CD", "BEF")
        fds.add_dependency("CF", "B")

        # expected_dependencies = [({'A'}, {'B', 'E'}), ({'A'}, {'B', 'D'}), ({'F'}, {'C', 'D'}), ({'C', 'D'}, {'B', 'E', 'F'}), ({'F'}, {'B'})] # Correct solution

        # Attribute is missing from dependency right
        proposedSolution = FunctionalDependencySet("ABCDEF")
        proposedSolution.add_dependency("A", "B")
        proposedSolution.add_dependency("A", "BD")
        proposedSolution.add_dependency("F", "CD")
        proposedSolution.add_dependency("CD", "BEF")
        proposedSolution.add_dependency("F", "B")

        self.assertFalse(fds.isCorrectLeftReduction(proposedSolution))

        # Attribute is missing from dependency left
        proposedSolution = FunctionalDependencySet("ABCDEF")
        proposedSolution.add_dependency("", "BE")
        proposedSolution.add_dependency("A", "BD")
        proposedSolution.add_dependency("F", "CD")
        proposedSolution.add_dependency("CD", "BEF")
        proposedSolution.add_dependency("F", "B")

        self.assertFalse(fds.isCorrectLeftReduction(proposedSolution))

        # Too many dependencies
        proposedSolution = FunctionalDependencySet("ABCDEF")
        proposedSolution.add_dependency("A", "BE")
        proposedSolution.add_dependency("AB", "BE")
        proposedSolution.add_dependency("A", "BD")
        proposedSolution.add_dependency("F", "CD")
        proposedSolution.add_dependency("CD", "BEF")
        proposedSolution.add_dependency("F", "B")

        self.assertFalse(fds.isCorrectLeftReduction(proposedSolution))

        # Attribute is too much on dependency right
        proposedSolution = FunctionalDependencySet("ABCDEF")
        proposedSolution.add_dependency("A", "BDE")
        proposedSolution.add_dependency("A", "BD")
        proposedSolution.add_dependency("F", "CD")
        proposedSolution.add_dependency("CD", "BEF")
        proposedSolution.add_dependency("F", "B")

        self.assertFalse(fds.isCorrectLeftReduction(proposedSolution))

        # Left side has too many attributes
        proposedSolution = FunctionalDependencySet("ABCDEF")
        proposedSolution.add_dependency("AD", "BE")
        proposedSolution.add_dependency("A", "BD")
        proposedSolution.add_dependency("F", "CD")
        proposedSolution.add_dependency("CD", "BEF")
        proposedSolution.add_dependency("F", "B")

        self.assertFalse(fds.isCorrectLeftReduction(proposedSolution))

    def testIsCorrectRightReduction(self):
        fds = self.getWikipediaExample()
        fds.left_reduction()
        afterLeftReduction = fds.copy()
        fds.right_reduction(genEx=False)
        self.assertTrue(afterLeftReduction.isCorrectRightReduction(fds))

        fds = self.getExample2020_71()
        fds.left_reduction()
        afterLeftReduction = fds.copy()
        fds.right_reduction()
        self.assertTrue(afterLeftReduction.isCorrectRightReduction(fds))

        fds = self.getExample2021_71()
        fds.left_reduction()
        afterLeftReduction = fds.copy()
        fds.right_reduction()
        self.assertTrue(afterLeftReduction.isCorrectRightReduction(fds))

        fds = self.getExample2013()
        fds.left_reduction()
        afterLeftReduction = fds.copy()
        fds.right_reduction()
        self.assertTrue(afterLeftReduction.isCorrectRightReduction(fds))

        fds = self.getExampleMultiplePaths()
        fds.left_reduction()
        afterLeftReduction = fds.copy()
        fds.right_reduction()
        self.assertTrue(afterLeftReduction.isCorrectRightReduction(fds))

        fds = self.getTumWS145L7()
        fds.left_reduction()
        afterLeftReduction = fds.copy()
        fds.right_reduction()
        self.assertTrue(afterLeftReduction.isCorrectRightReduction(fds))

        # Test against wrong right reductions
        fds = FunctionalDependencySet("ABCDEF")
        fds.add_dependency("A", "BE")
        fds.add_dependency("A", "BD")
        fds.add_dependency("F", "CD")
        fds.add_dependency("CD", "BEF")
        fds.add_dependency("F", "B")

        fds.right_reduction()

        # expected_dependencies = [({'A'}, {'E'}), ({'A'}, {'B', 'D'}), ({'F'}, {'C', 'D'}), ({'C', 'D'}, {'E', 'F'}), ({'F'}, {'B'})] expected solution

        # Not correctly reduced
        proposedSolution = FunctionalDependencySet("ABCDEF")
        proposedSolution.add_dependency("A", "BE")
        proposedSolution.add_dependency("A", "BD")
        proposedSolution.add_dependency("F", "CD")
        proposedSolution.add_dependency("CD", "EF")
        proposedSolution.add_dependency("F", "B")

        self.assertFalse(fds.isCorrectRightReduction(proposedSolution))

        # Left side is empty
        proposedSolution = FunctionalDependencySet("ABCDEF")
        proposedSolution.add_dependency("", "E")
        proposedSolution.add_dependency("A", "BD")
        proposedSolution.add_dependency("F", "CD")
        proposedSolution.add_dependency("CD", "EF")
        proposedSolution.add_dependency("F", "B")

        self.assertFalse(fds.isCorrectRightReduction(proposedSolution))

        # Left side is too big
        proposedSolution = FunctionalDependencySet("ABCDEF")
        proposedSolution.add_dependency("AB", "E")
        proposedSolution.add_dependency("A", "BD")
        proposedSolution.add_dependency("F", "CD")
        proposedSolution.add_dependency("CD", "EF")
        proposedSolution.add_dependency("F", "B")

        self.assertFalse(fds.isCorrectRightReduction(proposedSolution))

        # Right side has not enough attributes
        proposedSolution = FunctionalDependencySet("ABCDEF")
        proposedSolution.add_dependency("A", "")
        proposedSolution.add_dependency("A", "BD")
        proposedSolution.add_dependency("F", "CD")
        proposedSolution.add_dependency("CD", "EF")
        proposedSolution.add_dependency("F", "B")

        self.assertFalse(fds.isCorrectRightReduction(proposedSolution))

        # Not enough dependencies
        proposedSolution = FunctionalDependencySet("ABCDEF")
        proposedSolution.add_dependency("A", "BD")
        proposedSolution.add_dependency("F", "CD")
        proposedSolution.add_dependency("CD", "EF")
        proposedSolution.add_dependency("F", "B")

        self.assertFalse(fds.isCorrectRightReduction(proposedSolution))

        # Too many dependencies
        proposedSolution = FunctionalDependencySet("ABCDEF")
        proposedSolution.add_dependency("A", "")
        proposedSolution.add_dependency("A", "")
        proposedSolution.add_dependency("A", "BD")
        proposedSolution.add_dependency("F", "CD")
        proposedSolution.add_dependency("CD", "EF")
        proposedSolution.add_dependency("F", "B")

        self.assertFalse(fds.isCorrectRightReduction(proposedSolution))

    def testIsCorrectRemovingEmptyFDs(self):
        fds = self.getWikipediaExample()
        fds.left_reduction()
        fds.right_reduction()
        afterRightReduction = fds.copy()
        fds.remove_empty_fds()
        self.assertTrue(afterRightReduction.isCorrectRemovingEmptyFDs(fds))

        fds = self.getExample2020_71()
        fds.left_reduction()
        fds.right_reduction()
        afterRightReduction = fds.copy()
        fds.remove_empty_fds()
        self.assertTrue(afterRightReduction.isCorrectRemovingEmptyFDs(fds))

        fds = self.getExample2021_71()
        fds.left_reduction()
        fds.right_reduction()
        afterRightReduction = fds.copy()
        fds.remove_empty_fds()
        self.assertTrue(afterRightReduction.isCorrectRemovingEmptyFDs(fds))

        fds = self.getExample2013()
        fds.left_reduction()
        fds.right_reduction()
        afterRightReduction = fds.copy()
        fds.remove_empty_fds()
        self.assertTrue(afterRightReduction.isCorrectRemovingEmptyFDs(fds))

        fds = self.getExampleMultiplePaths()
        fds.left_reduction()
        fds.right_reduction()
        afterRightReduction = fds.copy()
        fds.remove_empty_fds()
        self.assertTrue(afterRightReduction.isCorrectRemovingEmptyFDs(fds))

        fds = self.getTumWS145L7()
        fds.left_reduction()
        fds.right_reduction()
        afterRightReduction = fds.copy()
        fds.remove_empty_fds()
        self.assertTrue(afterRightReduction.isCorrectRemovingEmptyFDs(fds))

    def testIsCorrectCombinationOfDependencies(self):
        fds = self.getWikipediaExample()
        fds.left_reduction()
        fds.right_reduction()
        fds.remove_empty_fds()
        afterRemove = fds.copy()
        fds.combine_fds(genEx=False)
        self.assertTrue(
            afterRemove.isCorrectCombinationOfDependencies(fds, verbose=self.debug)
        )

        fds = self.getExample2020_71()
        fds.left_reduction()
        fds.right_reduction()
        fds.remove_empty_fds()
        afterRemove = fds.copy()
        fds.combine_fds()
        self.assertTrue(
            afterRemove.isCorrectCombinationOfDependencies(fds, verbose=self.debug)
        )

        fds = self.getExample2021_71()
        fds.left_reduction()
        fds.right_reduction()
        fds.remove_empty_fds()
        afterRemove = fds.copy()
        fds.combine_fds()
        self.assertTrue(
            afterRemove.isCorrectCombinationOfDependencies(fds, verbose=self.debug)
        )

        fds = self.getExample2013()
        fds.left_reduction()
        fds.right_reduction()
        fds.remove_empty_fds()
        afterRemove = fds.copy()
        fds.combine_fds()
        self.assertTrue(
            afterRemove.isCorrectCombinationOfDependencies(fds, verbose=self.debug)
        )

        fds = self.getExampleMultiplePaths()
        fds.left_reduction()
        fds.right_reduction()
        fds.remove_empty_fds()
        afterRemove = fds.copy()
        fds.combine_fds()
        self.assertTrue(
            afterRemove.isCorrectCombinationOfDependencies(fds, verbose=self.debug)
        )

        fds = self.getTumWS145L7()
        fds.left_reduction()
        fds.right_reduction()
        fds.remove_empty_fds()
        afterRemove = fds.copy()
        fds.combine_fds()
        self.assertTrue(
            afterRemove.isCorrectCombinationOfDependencies(fds, verbose=self.debug)
        )

    def testIsCorrectCanonicalCover(self):
        examples = self.getExamples()
        for fds in examples:
            solution = fds.copy()
            solution.canonical_cover()
            self.assertTrue(fds.isCorrectCanonicalCover(solution))

    def testIsCorrectCreationOfNewFDS(self):
        examples = self.getExamples()
        for fds in examples:
            fds_copy = fds.copy()
            solution = fds_copy.create_new_fdsets()
            self.assertTrue(fds.isCorrectCreationOfNewFDS(solution))

    def testHausaufgabe2021(self):
        """
        Exercise 2021
        """
        debug = self.debug
        debug = False
        fds = self.getExample2021_71()
        # expected checked against https://normalizer.db.in.tum.de/index.py  ✅ by JV
        self.checkCandidateKeys(fds, expected=["ADE", "BE", "EG"], debug=debug)

    def getExample2013(self):
        fds = FunctionalDependencySet("ABCDEG")
        fds.add_dependency("AD", "C")
        fds.add_dependency("B", "D")
        fds.add_dependency("C", "DE")
        fds.add_dependency("DC", "G")
        fds.add_dependency("AB", "EG")
        return fds

    def testExample2013(self):
        """
        Synthese task 2013
        """
        fds = self.getExample2013()

        debug = False
        #  a) Bestimmen Sie alle Schlüsselkandidaten von R
        ck = fds.find_candidate_keys()
        if debug:
            print(ck)
        # expected checked against https://normalizer.db.in.tum.de/index.py  ✅ by JV
        self.assertEqual([{"A", "B"}], ck)
        fdslist = fds.synthesize()
        if debug:
            for fds in fdslist:
                print(fds)

    def testSample2013WithAlgorithmSteps(self):
        """
        Synthese task 2013 with steps
        """
        debug = False
        fds = self.getExample2013()
        keys = self.checkCandidateKeys(fds, ["AB"], debug=debug)
        self.checkCanonicalCover(fds, expected="{AD→C,B→D,C→DEG}", debug=debug)
        # checked up to here by WF ✅
        # fdsets = fds.create_new_fdsets()
        # fdsets_with_key = fds.create_optional_key_scheme(keys, fdsets)
        # reduced_fdsets = fds.remove_subset_relations(fdsets_with_key)
        fds = self.getExample2013()
        if self.testOpenTickets:
            self.checkSynthesis(fds, expected="", debug=debug)

    def test_key_candidates(self):
        """
        another key candidate test
        """
        debug = False
        klima = FunctionalDependencySet()
        klima.add_attribute("A", "name", "Name")
        klima.add_attribute("B", "country", "Land")
        klima.add_attribute("C", "continent", "Kontinent")
        klima.add_attribute("D", "climate", "Klima")
        klima.add_attribute("E", "damage", "Schaden")
        klima.add_attribute("F", "warning system", "Warnstufenskala")
        klima.add_dependency("B", "C")
        klima.add_dependency("D", "CE")
        klima.add_dependency("C", "F")
        klima.add_dependency("AE", "D")
        # expected checked against https://normalizer.db.in.tum.de/index.py  ✅ by JV
        self.checkCandidateKeys(klima, expected=["ABD", "ABE"], debug=debug)
        fds2 = FunctionalDependencySet("ABCDEFG")
        fds2.add_dependency("GDA", "FE")
        fds2.add_dependency("FG", "B")
        # expected checked against https://normalizer.db.in.tum.de/index.py  ✅ by JV
        self.checkCandidateKeys(fds2, expected=["ACDG"], debug=debug)

    def test_attribute_map(self):
        """
        test handling Attribute Maps
        """
        # concrete
        fdsPerson = FunctionalDependencySet()
        fdsPerson.add_attribute("A", "personId", "person_Nr")
        fdsPerson.add_attribute("B", "name", "Name")
        fdsPerson.add_attribute("C", "fieldOfWork", "Arbeitsgebiet")
        # fdsAbstract
        fdsAbstract = FunctionalDependencySet("ABCDEF")
        fdsList = [fdsPerson, fdsAbstract]

        expectedList = [
            {"len": 3, "key": "A", "en": "personId", "de": "person_Nr"},
            {"len": 6, "key": "F", "en": "F", "de": "F"},
        ]
        debug = self.debug
        # debug=True
        for i, fds in enumerate(fdsList):
            if debug:
                for attr in fds.attribute_map.values():
                    print(attr)
            attrMap = fds.attribute_map
            expected = expectedList[i]
            self.assertEqual(expected["len"], len(attrMap))
            key = expected["key"]
            self.assertTrue(key in attrMap)
            attr = attrMap[key]
            self.assertEqual(expected["en"], attr.english_name)
            self.assertEqual(expected["de"], attr.german_name)

    def test_stringify_dependencies(self):
        """
        test if dependencies are stringified correctly
        """
        debug = self.debug
        debug = False
        fds = FunctionalDependencySet("ABCDE")
        fds.add_dependency("AB", "C")
        fds.add_dependency("B", "D")
        fds.add_dependency("DE", "B")
        expectedText = [
            "{AB \to C,B \to D,DE \to B}",
            "{AB→C,B→D,DE→B}",
            "{AB->C,B->D,DE->B}",
            "{AB→C,B→D,DE→B}",
        ]
        for i, notation in enumerate(Notation):
            fds.notation = notation
            self.checkFdsResult(fds, expectedText[i], debug=debug)

    def test2NF(self):
        debug = False

        profVorlN = FunctionalDependencySet("ABCDEFG")
        profVorlN.add_dependency(["A"], ["B", "C", "D"])
        profVorlN.add_dependency(["E"], ["F", "G"])
        profVorlP = FunctionalDependencySet("ABCDEFG")
        profVorlP.add_dependency(["A", "E"], ["B", "C", "D", "F", "G"])
        examples = [
            {"fds": profVorlN, "expected": False},
            {"fds": profVorlP, "expected": True},
        ]
        for i, example in enumerate(examples):
            fds = example["fds"]
            ck = fds.find_candidate_keys()
            is2NF = fds.is2NF()
            expected = example["expected"]
            if debug:
                print(
                    f"Example {i}: key candidate {ck}: is2NF {is2NF}: expected {expected}"
                )
                print(is2NF)
            # expected checked against https://normalizer.db.in.tum.de/index.py  ✅ by JV
            self.assertEqual(expected, is2NF)

    def test3NF(self):
        debug = False
        profAddrN = FunctionalDependencySet("ABCDEFGHI")
        profAddrN.add_dependency("AD", "ABCDEFGHI")
        profAddrN.add_dependency("D", "A")
        profAddrN.add_dependency("EI", "H")
        profAddrN.add_dependency("EFI", "G")

        # key candidate: D
        profAddrP1 = FunctionalDependencySet("ABCDEFGHI")
        profAddrP1.add_dependency("AD", "ABCDEFGHI")
        profAddrP1.add_dependency("D", "A")

        # key candidate: AD
        profAddrP2 = FunctionalDependencySet("ABCDEFGHI")
        profAddrP2.add_dependency("AD", "ABCDEFGHI")

        examples = [
            {"fds": profAddrN, "expected": False},
            {"fds": profAddrP1, "expected": True},
            {"fds": profAddrP2, "expected": True},
        ]
        for i, example in enumerate(examples):
            fds = example["fds"]
            ck = fds.find_candidate_keys()
            is3NF = fds.is3NF()
            expected = example["expected"]
            if debug:
                print(
                    f"Example {i}: key candidate {ck}: is3NF {is3NF}: expected {expected}"
                )
            # expected checked against https://normalizer.db.in.tum.de/index.py  ✅ by JV
            self.assertEqual(expected, is3NF)

    def testBCNF(self):
        debug = False
        profAddrN = FunctionalDependencySet("ABCDEFGHI")
        profAddrN.add_dependency("AD", "ABCDEFGHI")
        profAddrN.add_dependency("D", "A")
        profAddrN.add_dependency("EI", "H")
        profAddrN.add_dependency("EFI", "G")

        profAddrP1 = FunctionalDependencySet("ACH")
        profAddrP1.add_dependency("A", "CH")
        profAddrP1.add_dependency("H", "AC")

        examples = [
            {"fds": profAddrN, "expected": False},
            {"fds": profAddrP1, "expected": True},
        ]
        for i, example in enumerate(examples):
            fds = example["fds"]
            ck = fds.find_candidate_keys()
            isBCNF = fds.isBCNF()
            expected = example["expected"]
            if debug:
                print(
                    f"Example {i}: key candidate {ck}: isBCNF {isBCNF}: expected {expected}"
                )
            # expected checked against https://normalizer.db.in.tum.de/index.py  ✅ by JV
            self.assertEqual(expected, isBCNF)

    def testSynthesisKemper(self):
        """
        see Kemper 6. 10th edition Relationale Entwurfstheorie Page 196
        """
        debug = self.debug
        debug = False
        professorenAdr = FunctionalDependencySet(
            title="ProfessorenAdr",
            description=f"Chapter 6.3 {self.kemperBook}",
            debug=debug,
        )
        professorenAdr.add_attribute("A", "personId", "PersNr")
        professorenAdr.add_attribute("B", "personId", "Name")
        professorenAdr.add_attribute("C", "rank", "Rang")
        professorenAdr.add_attribute("D", "room", "Raum")
        professorenAdr.add_attribute("E", "location", "Ort")
        professorenAdr.add_attribute("F", "street", "Straße")
        professorenAdr.add_attribute("G", "postalCode", "PLZ")
        professorenAdr.add_attribute("H", "areaCode", "Vorwahl")
        professorenAdr.add_attribute("I", "province", "BLand")
        professorenAdr.add_attribute("J", "population", "EW")
        professorenAdr.add_attribute("K", "stateGoverningParty", "Landesregierung")
        pa = professorenAdr
        pa.add_dependency("A", "D")
        pa.add_dependency("D", "A")
        pa.add_dependency("AD", "BCEFGHIJK")
        pa.add_dependency("EFI", "G")
        pa.add_dependency("G", "EI")
        pa.add_dependency("EI", "HJ")
        pa.add_dependency("I", "K")
        gv_markup = pa.as_graphviz()
        print(gv_markup)
        if self.testOpenTickets:
            self.checkSynthesis(pa, expected=[], debug=debug)

    def testRemoveDependency(self):
        """
        test removing a dependency
        """
        fds = FunctionalDependencySet("ABCDE")
        fds.add_dependency(["A", "B"], ["C"])
        fds.add_dependency(["B"], ["D"])
        fds.add_dependency(["D", "E"], ["B"])

        fds.remove_dependency(["B"], ["D"])
        self.assertEqual(2, len(fds.dependencies))
        self.assertFalse(({"B"}, {"D"}) in fds.dependencies)

    def testLeftReduction(self):
        """
        test the left reduction
        """
        fds = FunctionalDependencySet("ABCDEF")
        fds.add_dependency("A", "BE")
        fds.add_dependency("AE", "BD")
        fds.add_dependency("F", "CD")
        fds.add_dependency("CD", "BEF")
        fds.add_dependency("CF", "B")

        fds.left_reduction()

        expected_dependencies = [
            ({"A"}, {"B", "E"}),
            ({"A"}, {"B", "D"}),
            ({"F"}, {"C", "D"}),
            ({"C", "D"}, {"B", "E", "F"}),
            ({"F"}, {"B"}),
        ]
        for dep in expected_dependencies:
            self.assertTrue(dep in fds.dependencies)
        for dep in fds.dependencies:
            self.assertTrue(dep in expected_dependencies)

    def testRightReduction(self):
        """
        test the right reduction
        """
        fds = FunctionalDependencySet("ABCDEF")
        fds.add_dependency("A", "BE")
        fds.add_dependency("A", "BD")
        fds.add_dependency("F", "CD")
        fds.add_dependency("CD", "BEF")
        fds.add_dependency("F", "B")

        fds.right_reduction()

        expected_dependencies = [
            ({"A"}, {"E"}),
            ({"A"}, {"B", "D"}),
            ({"F"}, {"C", "D"}),
            ({"C", "D"}, {"E", "F"}),
            ({"F"}, {"B"}),
        ]
        for dep in expected_dependencies:
            self.assertTrue(dep in fds.dependencies)
        for dep in fds.dependencies:
            self.assertTrue(dep in expected_dependencies)

    def testRemoveEmptyDependencies(self):
        """
        test removing empty dependencies
        """
        fds = FunctionalDependencySet("ABCDEF")
        fds.add_dependency("A", "BD")
        fds.add_dependency("A", "")

        fds.remove_empty_fds()

        expected_dependencies = [({"A"}, {"B", "D"})]
        self.assertEqual(expected_dependencies, fds.dependencies)

    def testCombineDependencies(self):
        """
        test combining dependencies
        """
        fds = FunctionalDependencySet("ABCDEF")
        fds.add_dependency("A", "B")
        fds.add_dependency("A", "CD")
        fds.add_dependency("C", "B")
        fds.add_dependency("F", "A")
        fds.add_dependency("C", "A")

        fds.combine_fds()
        print(fds.dependencies)
        expected_dependencies = [
            ({"A"}, {"B", "C", "D"}),
            ({"C"}, {"B", "A"}),
            ({"F"}, {"A"}),
        ]
        for dep in expected_dependencies:
            self.assertTrue(dep in fds.dependencies)
        for dep in fds.dependencies:
            self.assertTrue(dep in expected_dependencies)

    def testCanonicalCover(self):
        """
        test the canonical cover
        """
        fds = FunctionalDependencySet("ABCDEF")
        fds.add_dependency("A", "BE")
        fds.add_dependency("AE", "BD")
        fds.add_dependency("F", "CD")
        fds.add_dependency("CD", "BEF")
        fds.add_dependency("CF", "B")

        fds.canonical_cover()

        print(fds.dependencies)
        expected_dependencies = [
            ({"A"}, {"E", "B", "D"}),
            ({"F"}, {"C", "D", "B"}),
            ({"C", "D"}, {"E", "F"}),
        ]
        for dep in expected_dependencies:
            self.assertTrue(dep in fds.dependencies)
        for dep in fds.dependencies:
            self.assertTrue(dep in expected_dependencies)

    def testCreateNewFDSets(self):
        fds = FunctionalDependencySet("ABCDEF")
        fds.add_dependency("A", "BDE")
        fds.add_dependency("CD", "EF")
        fds.add_dependency("F", "BCD")

        fdsets = fds.create_new_fdsets(genEx=False)

        self.assertEqual(3, len(fdsets))
        self.assertTrue(({"A"}, {"B", "E", "D"}) in fdsets[0].dependencies)
        self.assertEqual({"C", "D", "B", "F"}, fdsets[2].attributes)
        for i, fdset in enumerate(fdsets):
            self.assertEqual("R" + str(i + 1), fdset.title)

    def testCreateOptionalKeyScheme(self):
        fds = FunctionalDependencySet("")
        fds_0 = FunctionalDependencySet("ABDE", "R1")
        fds_1 = FunctionalDependencySet("CDEF", "R2")
        fds_2 = FunctionalDependencySet("FBCD", "R3")
        fds_0.add_dependency("A", "BED")
        fds_1.add_dependency("CD", "EF")
        fds_2.add_dependency("F", "BCD")
        fdsets = [fds_0, fds_1, fds_2]

        key_fdsets = fds.create_optional_key_scheme(["AF"], fdsets)

        self.assertEqual(4, len(key_fdsets))
        self.assertEqual({"A", "F"}, key_fdsets[3].attributes)
        self.assertEqual([({"A", "F"}, {"A", "F"})], key_fdsets[3].dependencies)
        for i, fdset in enumerate(fdsets):
            self.assertEqual("R" + str(i + 1), fdset.title)

    def testRemoveSubsetRelations(self):
        """
        test removing subset relations
        """
        fds = FunctionalDependencySet("")
        fds_0 = FunctionalDependencySet("ABDE", "R1")
        fds_1 = FunctionalDependencySet("CDEF", "R2")
        fds_2 = FunctionalDependencySet("ABD", "R3")
        fdsets = [fds_0, fds_1, fds_2]

        reduced_fdsets = fds.remove_subset_relations(fdsets)

        self.assertEqual(2, len(reduced_fdsets))
        for fdset in reduced_fdsets:
            self.assertNotEqual({"A", "B", "D"}, fdset.attributes)

    def testSynthesis(self):
        """
        test synthesis algorithm
        """
        fds = FunctionalDependencySet("ABCDEF")
        fds.add_dependency("A", "BE")
        fds.add_dependency("AE", "BD")
        fds.add_dependency("F", "CD")
        fds.add_dependency("CD", "BEF")
        fds.add_dependency("CF", "B")

        synthesized_sets = fds.synthesize(verbose=False, genEx=False)

        # print(synthesized_sets)
        self.assertEqual(4, len(synthesized_sets))

    def testGenerateCluster(self):
        """
        test the graphviz subgraph generation
        """
        fds = FunctionalDependencySet("ABCDEF", title="Cluster markup test")
        fds.add_dependency("A", "BE")
        fds.add_dependency("AE", "BD")
        fds.add_dependency("F", "CD")
        fds.add_dependency("CD", "BEF")
        fds.add_dependency("CF", "B")

        gv_markup = fds.as_graphviz(withCluster=True)
        debug = False
        expected = """label="Cluster markup test"
  B [shape=box label="B≡B≡B"]
  subgraph cluster_AE{
   label="AE"
    A [shape=box label="A≡A≡A"]
    E [shape=box label="E≡E≡E"]
  }"""
        if debug:
            print(gv_markup)
        self.assertTrue(expected in gv_markup)
        # self.checkResult(gv_markup, expected, "graphviz markup", debug=debug)
