"""
Created on 2022-06-10

@author: wf
"""
from tests.fdstest import FunctionalDependencySetTest
from dbis_functional_dependencies.fdsbase import Notation, RelSchema, Set
from dbis_functional_dependencies.BCNF import FunctionalDependencySet
from tabulate import tabulate


class Test_BITPlan_Examples(FunctionalDependencySetTest):
    """
    test examples of https://wiki.bitplan.com/index.php/Functional_Dependencies
    """

    def getSinglesSchema(self):
        """
        get the 2022 Singles example
        """
        fds = FunctionalDependencySet()
        fds.add_attribute("A", "single")
        fds.add_attribute("B", "language")
        fds.add_attribute("C", "collectionId")
        fds.add_attribute("D", "collection")
        fds.add_attribute("E", "collectionType")
        fds.add_attribute("F", "performerId")
        fds.add_attribute("G", "performer")
        fds.add_attribute("H", "followerCount")
        fds.add_attribute("I", "youtubeVideoId")
        fds.add_attribute("J", "publicationYear")
        fds.notation = Notation.math
        fds.add_dependency("A", "BCFIJ")
        fds.add_dependency("C", "DE")
        fds.add_dependency("F", "GH")
        rs = RelSchema(fds.attributes, fds, notation=Notation.math)
        return rs

    def testSinglesSchema(self):
        """
        test the 2022 Singles example
        """
        rs = self.getSinglesSchema()
        print(rs)
        for attribute in rs.fds.attribute_map.values():
            print(f"{attribute.var_name}≡{attribute.english_name}")

    def testGraphviz(self):
        """ """
        rs = self.getSinglesSchema()
        print(rs.fds.as_graphviz())

    def testAttributeClosures(self):
        """
        test attribute closure
        """
        rs = self.getSinglesSchema()
        lod = []
        for attribute in rs.fds.attribute_map.keys():
            clos = rs.fds.get_attr_closure(attribute)
            lod.append(
                {
                    "attribute": attribute,
                    "closure": Set.stringify_set(clos, notation=Notation.short),
                }
            )
        headers = {"attribute": "attribute", "closure": "closure"}
        print(tabulate(lod, headers, tablefmt="mediawiki"))

    def testCandidateKeys(self):
        """
        test retrieving the candidate keys
        """
        rs = self.getSinglesSchema()
        cks = rs.findCandidateKeys()
        for ck in cks:
            print(ck)
