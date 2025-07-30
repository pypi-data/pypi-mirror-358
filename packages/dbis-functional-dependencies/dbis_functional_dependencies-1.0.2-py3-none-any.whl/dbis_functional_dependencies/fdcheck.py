"""
Created on 2022-06-11
@author: wf
"""
import time
from dbis_functional_dependencies.BCNF import FunctionalDependencySet
import sqlite3


class FDCheck:
    """
    check functional dependencies for a tabular dataset in list of dicts form
    """

    def __init__(self, lod: list, debug: bool = False):
        """
        construct me with the given list of dicts

        Args:
            lod(list): the list of dicts (table) to check
            debug(bool): if true switch on debugging
        """
        self.lod = lod
        self.debug = debug
        self.entityInfo = None
        self.conn = None

    def createDatabase(
        self,
        entityName,
        primaryKey=None,
        executeMany=True,
        fixNone=False,
        fixDates=False,
        debug=False,
        doClose=True,
    ):
        """
        create a database for my list of Records

        Args:
           entityName(string): the name of the entity type to be used as a table name
           primaryKey(string): the name of the key / column to be used as a primary key
           executeMany(boolean): True if executeMany mode of sqlite3 should be used
           fixNone(boolean): fix dict entries that are undefined to have a "None" entry
           debug(boolean): True if debug information e.g. CREATE TABLE and INSERT INTO commands should be shown
           doClose(boolean): True if the connection should be closed

        """
        size = len(self.lod)
        if self.debug:
            print(
                "%s size is %d fixNone is %r fixDates is: %r"
                % (entityName, size, fixNone, fixDates)
            )

        self.conn = sqlite3.connect(":memory:")
        cursor = self.conn.cursor()

        # Infer schema
        keys = self.lod[0].keys()
        columns = []
        for k in keys:
            value = self.lod[0][k]
            sql_type = (
                "INTEGER"
                if isinstance(value, int)
                else "REAL"
                if isinstance(value, float)
                else "TEXT"
            )
            col_def = f"{k} {sql_type}"
            if k == primaryKey:
                col_def += " PRIMARY KEY"
            columns.append(col_def)
        create_stmt = f"CREATE TABLE {entityName} ({', '.join(columns)});"
        if debug:
            print(create_stmt)
        cursor.execute(create_stmt)

        # Prepare data
        col_names = list(keys)
        placeholders = ", ".join(["?"] * len(col_names))
        insert_stmt = (
            f"INSERT INTO {entityName} ({', '.join(col_names)}) VALUES ({placeholders})"
        )

        values = []
        for row in self.lod:
            values.append(tuple(row.get(k, None) for k in col_names))

        startTime = time.time()
        if executeMany:
            cursor.executemany(insert_stmt, values)
        else:
            for v in values:
                cursor.execute(insert_stmt, v)
        self.conn.commit()

        elapsed = max(1e-12, time.time() - startTime)
        if self.debug:
            print(
                f"adding {size} {entityName} records took {elapsed:.3f} s => {size/elapsed:.0f} records/s"
            )

            cursor.execute(f"SELECT * FROM {entityName}")
            resultList = cursor.fetchall()
            print(
                f"selecting {len(resultList)} {entityName} records took {elapsed:.3f} s => {len(resultList)/elapsed:.0f} records/s"
            )

        self.entityInfo = {
            "name": entityName,
            "typeMap": {k: type(self.lod[0][k]) for k in keys},
            "fields": list(keys),
        }

        if doClose:
            cursor.close()
            self.conn.close()
            self.conn = None

        return self.entityInfo

    def findFDs(self):
        """
        find functional dependencies

        https://github.com/gustavclausen/functional-dependency-finder/blob/master/main.py
        Return:
            FunctionalDependencySet: the set of functional dependencies
        """
        if self.entityInfo is None or not self.conn:
            raise Exception("createDatabase must be called before findFDs")

        table_name = self.entityInfo["name"]
        fields = self.entityInfo["fields"]

        fds = FunctionalDependencySet()
        for i, field in enumerate(fields):
            attr1_var = chr(ord("A") + i)
            fds.add_attribute(attr1_var, field)

        cursor = self.conn.cursor()
        for i, field_1 in enumerate(fields):
            attr1_var = chr(ord("A") + i)
            for j, field_2 in enumerate(fields):
                if i == j:
                    continue
                attr2_var = chr(ord("A") + j)
                sql = (
                    f"SELECT {field_1}, COUNT(DISTINCT {field_2}) as c\n"
                    f"FROM {table_name}\n"
                    f"GROUP BY {field_1}\n"
                    f"HAVING c > 1"
                )
                cursor.execute(sql)
                hits = cursor.fetchall()
                if self.debug:
                    print(f"{sql.strip()}\n{hits}")
                if not hits:
                    fds.add_dependency(attr1_var, attr2_var)

        cursor.close()
        self.fds = fds
        return fds
