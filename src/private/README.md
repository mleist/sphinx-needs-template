# src/private/

Drop your **private Python code** here. Files in this folder are ignored
by git.

To make this folder importable, add it to the project's `pythonpath` in
`pyproject.toml`:

```toml
[tool.pytest.ini_options]
pythonpath = ["src/public", "src/private"]
```

…or to your environment via `PYTHONPATH=src/private`.
