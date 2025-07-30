# DBIS Functional Dependencies

Functional Dependencies and Normal Forms for Relational Databases

[![PyPI Status](https://img.shields.io/pypi/v/dbis-functional-dependencies.svg)](https://pypi.python.org/pypi/dbis-functional-dependencies/)
[![pypi](https://img.shields.io/pypi/pyversions/dbis-functional-dependencies)](https://pypi.org/project/dbis-functional-dependencies/)
[![License](https://img.shields.io/pypi/l/dbis-functional-dependencies)](https://www.apache.org/licenses/LICENSE-2.0)
[![Pipeline Status](https://git.rwth-aachen.de/i5/teaching/dbis/dbis-functional-dependencies/badges/main/pipeline.svg)](https://git.rwth-aachen.de/i5/teaching/dbis/dbis-functional-dependencies/-/packages)

This library provides a Python implementation of the [synthesis algorithm](https://de.wikipedia.org/wiki/Synthesealgorithmus) and decomposition algorithm according to the DBIS lecture. For more background and application of functional dependencies and the algorithms, see [Doku-FunctionalDependencies](https://git.rwth-aachen.de/i5/teaching/dbis-jupyter/dbis-ss-2023-test/-/blob/main/doku/Doku-FunctionalDependencies.ipynb).

# Features
 - Create sets of Functional dependencies (FDSets).
 - Calculate candidate keys of an FDSet.
 - Calculate attribute closure of an attribute or set of attributes.
 - Test whether an FDSet is in 2NF, 3NF or BCNF.
 - Execute the synthesis algorithm to transform the FDSet into 3NF.
 - Execute the decomposition algorithm to transform the FDSet into BCNF.
 - Generate the closure $F^+$ of an FDSet $F$.
 - Generate true/false questions w.r.t. synthesis and decomposition algorithm.

# Installation
Install via pip:
```bash
pip install dbis-functional-dependencies
```

# Usage
### Creating an FDSet
Create a new instance of `FunctionalDependencySet`. The set of attributes is passed as parameter. 
```python
fdset = FunctionalDependencySet('ABCDE')
```
You can add more attributes later by using the `add_attribute` function. 
```python
fdset.add_attribute('F')
```
Add dependencies with the `add_dependency` function ...
```python
fdset.add_dependency("AC", "DE")
fdset.add_dependency("DEF", "B")
fdset.add_dependency("B", "D")
```
... or remove them with the `remove_dependency` function.
```python
fdset.remove_dependency("B", "D")
```

Printing an FDSet shows the dependencies in a more readable form.
```python
print(f"{fdset}")
```

### Attribute closure and candidate keys
Calculate the attribute closure of one or multiple attributes.
```python
closureA = fdset.get_attr_closure('A')
closureAC = fdset.get_attr_closure('AC')
```

Calculate all candidate keys.
```python
ckeys = fdset.find_candidate_keys()
```

### Check for normal forms
Since we only work with schemas (no actual values for the attributes), we assume that a corresponding database is in 1NF.

Check whether the FDSet is in 2NF, 3NF or BCNF.
```python
is2NF = fdset.is2NF()
is3NF = fdset.is3NF()
isBCNF = fdset.isBCNF()
```

### Execute the synthesis algorithm
Execute the synthesis algorithm on an FDSet to generate a corresponding list of FDSets in 3NF.
```python
fdslist = fdset.synthesize()
```
The algorithm performs the following steps:

0. Find the candidate keys.
1. Calculate the canonical cover.
    - left reduction
    - right reduction
    - remove dependencies with empty rhs
    - combine dependencies with same lhs
2. Create a new relation for every dependency in the canonical cover.
3. Create the optional key scheme if no candidate key is included in the attribute set of one of the relations of step 2.
4. Remove subset relations.

You receive additional information on the steps of the algorithm by toggling the parameter `verbose`.
```python
fdslist = fdset.synthesize(vebose=True)
```
Alternatively, you can also execute the single steps with the following functions:
```python
fdset_step.canonical_cover()
fdslist_step = fdset_step.create_new_fdsets()
fdslist_step_with_key = FunctionalDependencySet.create_optional_key_scheme(self, ckeys, fdslist_step)
reduced_fdslist_step = FunctionalDependencySet.remove_subset_relations(self, fdslist_step_with_key)
```
The verbose option exists for all steps.

### Execute the decomposition algorithm
Execute the decomposition algorithm on an FDSet to generate a corresponding decomposition of FDSets in BCNF.
```python
fdslist = fdset.decompose2()
```
Before performing the actual algorithm, the the closure of the FDSet is calculated.

### Closure of an FDSet
Calculate the closure $F^+$ of an FDSet $F$.
```python
fdset.completeFDsetToClosure()
```
This function just adds dependencies with all subset combinations of the attribute set with their corresponding closures on the rhs of the dependency, so that no implicit dependency is missed by the decomposition algorithm.

### Exercise generator
Generate true/false statements based on the different steps of the algorithms.
```python
fdslist = fdset.synthesize(genEx=True)
```
The `genEx` option is available for the following functions:
* `find_candidate_keys`
* `synthesize`
  * `canonical_cover`
    * `left_reduction`
    * `right_reduction`
    * `remove_empty_fds`
    * `combine_fds`
  * `create_new_fdsets`
  * `create_optional_key_scheme`
  * `remove_subset_relations`
* `decompose2`

### Checking results against expected
Checks a given calculated step of an FDSet during the synthesis algorithm (according to the DBIS lecture) for correctness.
```python
original = fdset.copy()
fdset.left_reduction()
original.isCorrectLeftReduction(fdset)
```
For this purpose, the following functions exist:
* `isCorrectLeftReduction`
* `isCorrectRightReduction`
* `isCorrectRemovingEmptyFDs`
* `isCorrectCombinationOfDependencies`
* `isCorrectCanonicalCover`
* `isCorrectCreationOfNewFDS`

These functions are called on the FDSet with all steps before already calculated on it.
