Forked from [publistgen](https://github.com/t-wissmann/publistgen) and adapted for my needs.

Changes are:
1. Use logging instead of print, so that I can debug easier
2. Make the module importable
3. Make author list expandable
4. moved css and js files out of the python script
5. Add a flag to escape Jekyll liquid injection for doubly curly braces ("-e")
6. Added a flag to include yaml at the start of the file ("-yaml")

# Installation

Make an environment with Python 3.9 then clone the [biblib](https://github.com/aclements/biblib) package to this folder.

Then run the following command:
```
python publistgen.py --yaml -e my_pubs.bib > publications.html
```

Does not work with Python 3.10. You will need to change `collections.Iterable` to `collections.abc.Iterable` (see this [issue](https://github.com/nerdocs/pydifact/issues/46)).



