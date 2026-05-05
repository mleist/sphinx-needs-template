# Schema (Class Reference)

<!-- AUTO-GENERATED from the LinkML schema. Do not edit by hand. -->
<!-- Re-run `make generate` after editing the schema YAML. -->

Each class in the LinkML schema is rendered as a `cls`-typed need so it can be filtered, listed and back-linked from any need page.

```{cls} Decision
:id: CLS_DECISION

An architectural or organisational decision.

**Slots**

- `id` → `string`
- `title` → `string` *(required)*
- `description` → `string`
- `tags` → `string`
- `status` → `StatusEnum`
- `links` → `string`

**Inherits from:** `Need`
```

```{cls} FunctionalRequirement
:id: CLS_FUNCTIONAL_REQUIREMENT

A capability the system must provide.

**Slots**

- `derives` → `string`
- `start_date` → `string`
- `duration` → `integer`
- `completion` → `integer`
- `id` → `string` *(required)*
- `title` → `string` *(required)*
- `description` → `string`
- `tags` → `string`
- `status` → `StatusEnum`
- `links` → `string`

**Inherits from:** `Need`
```

```{cls} GlossaryTerm
:id: CLS_GLOSSARY_TERM

A controlled vocabulary entry.

**Slots**

- `id` → `string` *(required)*
- `title` → `string` *(required)*
- `description` → `string`
- `tags` → `string`
- `status` → `StatusEnum`
- `links` → `string`

**Inherits from:** `Need`
```

```{cls} NonFunctionalRequirement
:id: CLS_NON_FUNCTIONAL_REQUIREMENT

A constraint or quality attribute (e.g. noise, water use).

**Slots**

- `derives` → `string`
- `start_date` → `string`
- `duration` → `integer`
- `completion` → `integer`
- `id` → `string` *(required)*
- `title` → `string` *(required)*
- `description` → `string`
- `tags` → `string`
- `status` → `StatusEnum`
- `links` → `string`

**Inherits from:** `Need`
```

```{cls} Risk
:id: CLS_RISK

An identified risk with potential impact on the project.

**Slots**

- `id` → `string` *(required)*
- `title` → `string` *(required)*
- `description` → `string`
- `tags` → `string`
- `status` → `StatusEnum`
- `links` → `string`

**Inherits from:** `Need`
```

```{cls} Test
:id: CLS_TEST

A test that verifies one or more requirements.

**Slots**

- `verifies` → `string`
- `id` → `string` *(required)*
- `title` → `string` *(required)*
- `description` → `string`
- `tags` → `string`
- `status` → `StatusEnum`
- `links` → `string`

**Inherits from:** `Need`
```

```{cls} UseCase
:id: CLS_USE_CASE

A concrete interaction scenario.

**Slots**

- `implements` → `string`
- `start_date` → `string`
- `duration` → `integer`
- `completion` → `integer`
- `id` → `string` *(required)*
- `title` → `string` *(required)*
- `description` → `string`
- `tags` → `string`
- `status` → `StatusEnum`
- `links` → `string`

**Inherits from:** `Need`
```

```{cls} UserStory
:id: CLS_USER_STORY

A short user-centric description of a desired outcome.

**Slots**

- `area` → `AreaEnum` *(required)*
- `implements` → `string`
- `id` → `string` *(required)*
- `title` → `string` *(required)*
- `description` → `string`
- `tags` → `string`
- `status` → `StatusEnum`
- `links` → `string`

**Inherits from:** `Need`
```
