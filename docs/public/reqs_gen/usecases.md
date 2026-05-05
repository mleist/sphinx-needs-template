# Use Cases

<!-- AUTO-GENERATED from `usecases.yaml`. Do not edit by hand. -->
<!-- Re-run `make generate` after editing the source YAML. -->

```{uc} Mow the back-yard lawn
:id: UC_MOW_BACK_LAWN
:status: accepted
:tags: mowing
:start_date: 2026-05-02
:duration: 1
:completion: 100
:implements: US_MOW_LAWN

Weekly Saturday morning routine.

1. Check weather and grass moisture (see `garden_helper.is_mowing_weather`).
2. Mow lawn in alternating directions.
3. Empty grass catcher into compost bin.
4. Sweep clippings off the patio.
```

```{uc} Plant tomatoes and herbs in the vegetable bed
:id: UC_PLANT_VEG_BED
:status: in_progress
:tags: planting
:start_date: 2026-05-09
:duration: 2
:completion: 60
:implements: US_PLANT_VEGGIES

One-off planting day after the last frost.

1. Loosen and amend soil with compost.
2. Plant tomato seedlings 60 cm apart, stake each.
3. Sow basil and parsley seeds in the front row.
4. Water generously and apply mulch.
```

```{uc} Prepare the patio for a small garden party
:id: UC_PREPARE_GARDEN_PARTY
:status: open
:tags: party_prep
:start_date: 2026-06-13
:duration: 7
:completion: 0
:implements: US_HOST_PARTY;US_FRONT_LAWN_TRIM;US_PLANT_FLOWERS

Week-long preparation leading up to the party day.

1. Refresh flower bed two weeks ahead.
2. Trim front-yard edges three days ahead.
3. Mow back-yard lawn the day before.
4. Set up tables, string lights and barbecue on party day.
```
