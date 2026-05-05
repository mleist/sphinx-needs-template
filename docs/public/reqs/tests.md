# Tests

This page lists every test exposed by `pytest` as a sphinx-needs `test`-typed
item. The data is loaded from `docs/public/_generated/test_results.json`,
which is written automatically at the end of each pytest run.

If the table is empty, run `make test` (or the full `make all`) once.

```{needtable}
:types: test
:columns: id;title;status;links
:style: table
:colwidths: 25,45,10,20
```
