# Functional Requirements

This page lists the functional requirements derived from the user stories and
use cases. Each requirement is testable and is verified by at least one entry
in `tests.md`.

```{freq} Mowing-weather check
:id: FR_MOW_WEATHER
:status: implemented
:tags: mowing
:derives: US_MOW_LAWN
:start_date: 2026-04-15
:duration: 2
:completion: 100

The system MUST decide whether the lawn can be mowed today based on
temperature and recent precipitation. Mowing is permitted only when the
temperature is at or above 8 °C and there has been no rain in the
previous reading window.
```

```{freq} Harvest-day estimate
:id: FR_HARVEST_ESTIMATE
:status: implemented
:tags: planting
:derives: US_PLANT_VEGGIES
:start_date: 2026-04-20
:duration: 3
:completion: 100

Given a planting date and a maturity duration, the system MUST report the
remaining days until harvest. The result is non-negative; produce that is
already mature reports zero remaining days.
```

```{freq} Patio-capacity calculation
:id: FR_PARTY_CAPACITY
:status: implemented
:tags: party_prep
:derives: US_HOST_PARTY
:start_date: 2026-05-01
:duration: 2
:completion: 100

The system MUST estimate how many guests can comfortably stand on the patio
based on its area and a configurable area-per-guest factor (default 1.5 m²).
Negative or zero areas yield a capacity of zero.
```

```{freq} Trim-list generator
:id: FR_FRONT_TRIM_LIST
:status: open
:tags: mowing, party_prep
:derives: US_FRONT_LAWN_TRIM
:start_date: 2026-05-10
:duration: 4
:completion: 0

The system SHOULD produce a checklist of trim locations (driveway edge,
walkway edge, mailbox surround) so that the front yard is consistently
prepared before any planned event.
```

```{freq} Flower-bed planting plan
:id: FR_FLOWER_PLAN
:status: open
:tags: planting, party_prep
:derives: US_PLANT_FLOWERS
:start_date: 2026-05-20
:duration: 5
:completion: 0

The system SHOULD generate a planting plan for the flower bed that lists
species, quantities and spacing, given a target bloom date and the bed's
dimensions.
```

```{freq} Party-task timeline
:id: FR_PARTY_TIMELINE
:status: open
:tags: party_prep
:derives: US_HOST_PARTY
:start_date: 2026-05-25
:duration: 6
:completion: 0

The system SHOULD generate a backwards timeline of preparation tasks
counting down to the party day (e.g. "T-14 days: refresh flower bed",
"T-1 day: mow lawn").
```
