# linkml/public/data/

YAML data files validated against `../schema/needs.yaml` and rendered as
MyST sphinx-needs by `needs-from-linkml`.

| File           | Top-level key       | LinkML class       |
| -------------- | ------------------- | ------------------ |
| `stories.yaml` | `stories`           | `UserStory`        |
| `usecases.yaml`| `use_cases`         | `UseCase`          |

Each output file follows the source file's stem: `stories.yaml` →
`docs/public/reqs_gen/stories.md`.

## Recognised top-level keys

`stories`, `user_stories`, `use_cases`, `usecases`,
`functional_requirements`, `freqs`, `non_functional_requirements`,
`nfreqs`, `tests`, `risks`, `decisions`, `glossary_terms`, `glossary`.

> **Avoid filename `glossary.yaml`** if you also use the Sphinx built-in
> `glossary` directive elsewhere. Sphinx may resolve the toctree entry to
> the wrong target. Prefer `glossary_terms.yaml` to sidestep the conflict.

## Adding a new collection

1. Add a slot to the `Container` class in `../schema/needs.yaml` (e.g.
   `meetings: { multivalued: true, range: Meeting }`).
2. Add the class itself.
3. Drop a new YAML file with the matching top-level key.
4. Run `make generate`.
