"""
Created on 2022-06-10

@author: jv
"""
from tests.fdstest import FunctionalDependencySetTest
from dbis_functional_dependencies.fdsbase import Notation, RelSchema
from dbis_functional_dependencies.BCNF import FunctionalDependencySet


class Test_Dbisvl_Examples(FunctionalDependencySetTest):
    """
    test examples for dbis-vl
    """

    def getPlayerExample(self):
        """
        test the 2022 dbis-vl dokunotebook synthesisexample
        """
        fds = FunctionalDependencySet()
        # Füge die Attribute zum FDSet hinzu
        fds.add_attribute("A", "givenName", "Vorname")
        fds.add_attribute("B", "familyName", "Familienname")
        fds.add_attribute("C", "position", "Position")
        fds.add_attribute("D", "team", "Verein")
        fds.add_attribute("E", "league", "Liga")
        fds.add_attribute("F", "yearOfBirth", "Geburtsjahr")
        fds.add_attribute("G", "speaks", "spricht")
        fds.add_attribute("H", "nationalOf", "Nationalität")
        fds.notation = Notation.math
        fds.add_dependency("B", "CFGH")
        fds.add_dependency("AB", "CFGH")
        fds.add_dependency("D", "E")
        fds.add_dependency("H", "ABG")
        fds.add_dependency("F", "ABCGH")
        rs = RelSchema(fds.attributes, fds, notation=Notation.math)
        return rs

    def testPlayerExample(self):
        """
        test the player example
        """
        rs = self.getPlayerExample()
        if self.debug:
            print(rs)
        self.assertEqual(
            "R=\{\{A,B,C,D,E,F,G,H\},{B \to CFGH,AB \to CFGH,D \to E,H \to ABG,F \to ABCGH}\}",
            str(rs),
        )
        for attribute in rs.fds.attribute_map.values():
            print(attribute)

    def testExampleCandidateKeys(self):
        """
        test candidate keys for the example
        """
        schema = self.getPlayerExample()
        ck = schema.fds.find_candidate_keys()
        print(ck)

    def testExampleLeftReduction(self):
        """
        test left reduction for the example
        """
        schema = self.getPlayerExample()
        print(schema.fds)
        schema.fds.left_reduction()
        print(schema.fds)

    def testExampleRightReduction(self):
        """
        test up to right reduction for the example
        """
        schema = self.getPlayerExample()
        print(schema)
        schema.fds.left_reduction()
        schema.fds.right_reduction()
        print(schema)

    def testExampleRemoveEmptyFds(self):
        """
        test up to removal of empty fds in canonical cover for the example
        """
        schema = self.getPlayerExample()
        print(schema)
        schema.fds.left_reduction()
        schema.fds.right_reduction()
        schema.fds.remove_empty_fds()
        print(schema)

    def testExampleCombineFds(self):
        """
        test up to canonical cover for the example
        """
        schema = self.getPlayerExample()
        print(schema)
        schema.fds.left_reduction()
        schema.fds.right_reduction()
        schema.fds.remove_empty_fds()
        schema.fds.combine_fds()
        print(schema)

    def testExampleCreateNewFdsets(self):
        """
        test canonical cover for the example
        """
        schema = self.getPlayerExample()
        print(schema)
        schema.fds.canonical_cover()
        fdsetlist = schema.fds.create_new_fdsets()
        for fdset in fdsetlist:
            rs = RelSchema(fdset.attributes, fdset, notation=Notation.math)
            print(rs)

    def testExampleCreateOptionalKeySchema(self):
        """
        test canonical cover for the example
        """
        schema = self.getPlayerExample()
        print(schema)
        schema.fds.canonical_cover()
        fdsetlist = schema.fds.create_new_fdsets()
        fdsetlist = schema.fds.create_optional_key_scheme(
            schema.fds.find_candidate_keys(), fdsetlist
        )
        for fdset in fdsetlist:
            rs = RelSchema(fdset.attributes, fdset, notation=Notation.math)
            print(rs)

    def testExampleSynthesize(self):
        """
        test complete synthesize for the example
        """
        schema = self.getPlayerExample()
        print(schema)
        sn = schema.fds.synthesize()
        for rel in sn:
            print(rel)
