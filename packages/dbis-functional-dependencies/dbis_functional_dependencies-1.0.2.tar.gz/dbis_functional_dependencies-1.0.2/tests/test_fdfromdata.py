"""
Created on 2022-10-06

@author: wf
"""
from pathlib import Path
import json

from tests.fdstest import FunctionalDependencySetTest

from dbis_functional_dependencies.fdcheck import FDCheck


class Test_FD_FromData(FunctionalDependencySetTest):
    """
    test functional dependency from data
    """

    def setUp(self):
        debug = (False,)
        profile = True
        thisPath = Path(__file__).parent

        self.sampleDataPath = thisPath.parent / "sampledata"
        FunctionalDependencySetTest.setUp(self, debug=debug, profile=profile)

    def getExampleLoD(self, jsonFileName: str):
        """
        get the example tabular data

        Args:
            the jsonFileNme to read from
        """
        jsonFilePath = f"{self.sampleDataPath}/{jsonFileName}"
        with open(jsonFilePath, "r", encoding="utf-8") as f:
            lod = json.load(f)
        return lod

    def testExamples(self):
        """
        test getting the functional dependencies from the example

        """
        examples = [
            {"jsonFile": "football.json", "entityName": "player"},
            {"jsonFile": "singles.json", "entityName": "single"},
            {"jsonFile": "runways.json", "entityName": "runway"},
            {"jsonFile": "runwaysbcnf.json", "entityName": "runway"},
        ]
        expected = [{"len": 8}, {"len": 9}, {"len": 1140}, {"len": 22}]
        for i, example in enumerate(examples):
            exampleJsonFile = example["jsonFile"]
            lod = self.getExampleLoD(exampleJsonFile)
            if self.debug:
                print(lod)
            self.assertTrue(type(lod) is list)
            expectedLen = expected[i]["len"]
            self.assertEqual(expectedLen, len(lod))
            fdCheck = FDCheck(lod, debug=True)
            entityName = example["entityName"]
            fdCheck.createDatabase(entityName, doClose=False)
            fds = fdCheck.findFDs()
            if self.debug:
                print(fds)
            fds.canonical_cover()
            if self.debug:
                print(fds)
