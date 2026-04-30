# tests/private/

Drop your **private tests** here. Files in this folder are ignored by git.
The pytest configuration in `pyproject.toml` already includes this folder
in `testpaths`, so any `test_*.py` will be picked up automatically.

The same `@pytest.mark.satisfies("XXX_yyy")` validation applies — your
private tests can verify private requirements as long as those needs are
loaded into `needs.json` during the build.
