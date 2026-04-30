# docker/

The single-service Docker build for `sphinx-needs-template`.

| File                | Purpose                                                              |
| ------------------- | -------------------------------------------------------------------- |
| `Dockerfile`        | Builds the image with Python, LaTeX, PlantUML and the converters.   |
| `write_redirect.py` | Build-time helper: writes `index.html` redirects per HTML view.     |

## Use it

```bash
# Build the image once
docker compose build

# Run any Make target inside the container
docker compose run --rm builder make all
docker compose run --rm builder make html
docker compose run --rm builder make pdf
docker compose run --rm builder make test
docker compose run --rm builder make reqif-export
docker compose run --rm builder make jsonld-export
```

The repo is bind-mounted at `/workspace`, so anything the build produces
under `docs/public/_build/` and `docs/public/_generated/` appears
immediately on the host.

## Run as your host user (no root-owned outputs)

```bash
docker compose run --rm -u "$(id -u):$(id -g)" builder make all
```
