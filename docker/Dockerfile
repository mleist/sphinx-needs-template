# =============================================================================
# sphinx-needs-template — single-service dev container
#
# Usage:
#   docker compose run --rm builder make all
#   docker compose run --rm builder make html
#   docker compose run --rm builder pytest tests/public
#
# Image purpose: provide every tool needed to build, validate and test the
# template. Project source is mounted from the host so edits persist.
# =============================================================================
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1 \
    DEBIAN_FRONTEND=noninteractive

# System tools: make, git for editable installs, plantuml + graphviz for
# diagrams (PlantUML calls out to `dot` for layout in needflow diagrams),
# texlive-xetex + tex-gyre for PDF generation (XeLaTeX handles arbitrary
# Unicode characters natively, which pdflatex does not).
RUN apt-get update && apt-get install -y --no-install-recommends \
        make \
        git \
        plantuml \
        graphviz \
        librsvg2-bin \
        latexmk \
        texlive-xetex \
        texlive-latex-recommended \
        texlive-latex-extra \
        texlive-fonts-recommended \
        tex-gyre \
        fonts-freefont-otf \
        ca-certificates \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /workspace

# Copy only the manifests first to leverage the layer cache. The rest of the
# repo is bind-mounted at run-time via docker-compose.
COPY pyproject.toml README.md /workspace/
COPY src/public /workspace/src/public

RUN pip install --no-cache-dir -e ".[dev]"

# Default command shows help so newcomers see what's possible.
CMD ["make", "help"]
