# docs/private/

Drop your **private documentation** here. Anything in this folder is
ignored by git (see the project root `.gitignore`).

The Sphinx build does *not* include this folder by default. To bring
private pages into the active view, add a `toctree` entry from one of
your `docs/public/` index files, for example:

```markdown
```{toctree}
:caption: Internal

../private/internal_notes
```
```

Or create your own master_doc under `docs/private/` and a separate
build target in the Makefile.
