# View: Party Preparation

Cross-cutting view of every artefact tagged `party_prep`, regardless of
need type.

## User Stories

```{needtable}
:types: story
:tags: party_prep
:columns: id;title;area;status
:style: table
:colwidths: 25,45,15,15
```

## Use Cases

```{needtable}
:types: uc
:tags: party_prep
:columns: id;title;status;implements
:style: table
:colwidths: 25,40,15,20
```

## Functional Requirements

```{needtable}
:types: freq
:tags: party_prep
:columns: id;title;status;derives;duration
:style: table
:colwidths: 25,35,15,20,10
```

## Non-Functional Requirements

```{needtable}
:types: nfreq
:tags: party_prep
:columns: id;title;status
:style: table
```

## Risks

```{needtable}
:types: risk
:tags: party_prep
:columns: id;title;status
:style: table
```

## Full entries

```{needextract}
:types: story;uc;freq;nfreq;risk
:tags: party_prep
```

## Schedule

Time-based view of every `party_prep` item that has a `start_date`.

```{needgantt}
:start_date: 2026-04-15
:timeline: weekly
:duration_option: duration
:completion_option: completion
:types: uc;freq
:tags: party_prep
```

```{toctree}
:hidden:

../reqs_gen/stories
../reqs_gen/usecases
../reqs/functional
../reqs/nonfunctional
../reqs/schedule
../reqs/tests
../reqs/coverage
../reqs/risks
../reqs/decisions
../reqs/glossary
../reqs_gen/classes
```
