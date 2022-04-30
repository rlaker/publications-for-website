Forked from [publistgen](https://github.com/t-wissmann/publistgen) and adapted for my needs.

For Python 3.10 you will need to change `collections.Iterable` to `collections.abc.Iterable` (see this [issue](https://github.com/nerdocs/pydifact/issues/46)).

Changes are:
1. Use logging instead of print, so that I can debug easier
2. Make the module importable
3. Make author list expandable
4. moved css and js files out of the python script

For use with Jekyll I also had to turn off Liquid injection for this page like this:
```
{% raw %}
the html goes here
{% endraw %}
```

