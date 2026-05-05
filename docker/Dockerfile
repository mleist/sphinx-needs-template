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

# System tools: make, git for editable installs, plantuml for diagrams,
# Build-time pin for PlantUML. Override with
# `docker compose build --build-arg PLANTUML_VERSION=1.2026.x`
# to update without editing the Dockerfile.
ARG PLANTUML_VERSION=1.2026.2
# Optional integrity check. Set this to the sha256 sum of the jar to make
# the build reject a tampered or replaced upstream artefact. Leave empty
# (default) to skip the check on first build, then look up the sha from
# the verified jar with:
#     sha256sum /opt/plantuml/plantuml.jar
# inside a running container, and re-build with
#     --build-arg PLANTUML_JAR_SHA256=<that sha>
ARG PLANTUML_JAR_SHA256=3cdce52133c424dea22425b947ae9d47f2167b0866dfcf99e714d4ea1689975c

# System tools: make, git for editable installs, graphviz for layout
# (PlantUML calls out to `dot` for needflow diagrams), default-jre-headless
# to run the PlantUML jar (Ubuntu's `plantuml` apt package is too old —
# v1.2020 from 2020 — to support the in-script `language <code>` directive
# we need for German Gantt rendering, so we pull a current jar instead),
# librsvg2-bin for SVG→PDF conversion in LaTeX builds,
# diagrams (PlantUML calls out to `dot` for layout in needflow diagrams),
# texlive-xetex + tex-gyre for PDF generation (XeLaTeX handles arbitrary
# Unicode characters natively, which pdflatex does not).
RUN apt-get update && apt-get install -y --no-install-recommends \
        make \
        git \
        default-jre-headless \
        graphviz \
        librsvg2-bin \
        curl \
        latexmk \
        texlive-xetex \
        texlive-latex-recommended \
        texlive-latex-extra \
        texlive-fonts-recommended \
        tex-gyre \
        fonts-freefont-otf \
        ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Download a recent PlantUML jar and install a thin launcher script.
# When PLANTUML_JAR_SHA256 is set (see ARG above), the jar is verified
# against that hash for reproducible, tamper-resistant builds.
RUN set -eux; \
    mkdir -p /opt/plantuml; \
    curl -fsSL -o /opt/plantuml/plantuml.jar \
        "https://github.com/plantuml/plantuml/releases/download/v${PLANTUML_VERSION}/plantuml-${PLANTUML_VERSION}.jar"; \
    if [ -n "${PLANTUML_JAR_SHA256}" ]; then \
        echo "${PLANTUML_JAR_SHA256}  /opt/plantuml/plantuml.jar" | sha256sum -c -; \
    fi; \
    printf '%s\n' \
        '#!/bin/sh' \
        'exec java -Djava.awt.headless=true -jar /opt/plantuml/plantuml.jar "$@"' \
        > /usr/local/bin/plantuml; \
    chmod +x /usr/local/bin/plantuml; \
    plantuml -version

WORKDIR /workspace

# Copy only the manifests first to leverage the layer cache. The rest of the
# repo is bind-mounted at run-time via docker-compose.
COPY pyproject.toml README.md /workspace/
COPY src/public /workspace/src/public

RUN pip install --no-cache-dir -e ".[dev]"

# Default command shows help so newcomers see what's possible.
CMD ["make", "help"]
