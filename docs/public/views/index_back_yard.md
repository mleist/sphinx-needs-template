# View: Back Yard

User stories filtered by `area == 'back_yard'`, plus their implementing
use cases.

## User Stories in the back yard

```{needtable}
:types: story
:filter: area == 'back_yard'
:columns: id;title;status;tags
:style: table
```

## Implementing use cases

Use cases that realise at least one back-yard story:

```{needtable}
:types: uc
:filter: any(s in implements for s in ['US_MOW_LAWN'])
:columns: id;title;implements;status
:style: table
```

## Full entries

```{needextract}
:types: story
:filter: area == 'back_yard'
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
