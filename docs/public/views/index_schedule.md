# View: Schedule

Time-focused view of every artefact with a `start_date`. The Gantt
charts on the schedule page are the primary deliverable here; the
status tables below provide a flat readout sorted by start date.

```{toctree}
:maxdepth: 2
:caption: Contents

../reqs/schedule
```

## Use cases by start date

```{needtable}
:types: uc
:filter: start_date is not None
:columns: id;title;status;start_date;duration;completion
:style: table
:colwidths: 25,40,15,15,10,10
```

## Functional requirements by start date

```{needtable}
:types: freq
:filter: start_date is not None
:columns: id;title;status;start_date;duration;completion
:style: table
:colwidths: 25,40,15,15,10,10
```

```{toctree}
:hidden:

../reqs_gen/stories
../reqs_gen/usecases
../reqs/functional
../reqs/nonfunctional
../reqs/tests
../reqs/coverage
../reqs/risks
../reqs/decisions
../reqs/glossary
../reqs_gen/classes
```
