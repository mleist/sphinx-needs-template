# Schedule

A time-based view of the project. The diagrams below are rendered
directly from the `start_date`, `duration` and `completion` fields of
the underlying needs — they update automatically whenever those values
change in the LinkML data files or in the hand-written requirement
pages.

## Use cases — execution timeline

```{needgantt}
:start_date: 2026-04-15
:timeline: weekly
:duration_option: duration
:completion_option: completion
:types: uc
```

```{note}
**How `{needgantt}` works.** The `:start_date:` option above sets the
**calendar origin** for the diagram (i.e. where day 0 sits on the x
axis). Each plotted bar then takes its own `start_date` field as its
left edge and its `duration` field as its width. The `completion` field
fills the bar with a darker shade up to that percentage — useful for
status-at-a-glance reviews. PlantUML does the actual rendering.
```

## Functional requirements — implementation timeline

```{needgantt}
:start_date: 2026-04-15
:timeline: weekly
:duration_option: duration
:completion_option: completion
:types: freq
```

## Coverage table

A flat table that combines all schedule-relevant items in one place,
sorted by start date.

```{needtable}
:types: uc;freq
:filter: start_date is not None
:columns: id;title;status;start_date;duration;completion
:style: table
:colwidths: 25,40,15,15,10,10
```
