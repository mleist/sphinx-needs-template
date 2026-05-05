# docs/private/

Drop your **private documentation, theme overrides and brand assets**
here. Anything in this folder is ignored by git (see the project root
`.gitignore`).

## Theme override hooks

The build looks for the following four files. Each is optional — if a
file is missing, the public default applies. If it exists, it is layered
on top of the default automatically.

### 1. `static/` — corporate CSS, logos, fonts

Drop CSS files, images, fonts here. The directory is automatically
appended to Sphinx's `html_static_path`. Reference an asset from your
own `_overrides.py` or from MyST pages by its filename:

```html
<img src="_static/my_logo.png" />
```

### 2. `latex_preamble.tex` — extra LaTeX preamble

The contents of this file are appended verbatim to
`latex_elements["preamble"]`. Use it for company colour packages,
custom title pages, header/footer redefinitions, etc.

```latex
% docs/private/latex_preamble.tex
\usepackage{xcolor}
\definecolor{corpblue}{HTML}{003c71}
\renewcommand{\sphinxtitleref}[1]{\textcolor{corpblue}{\textbf{#1}}}
```

### 3. `plantuml_preamble.iuml` — PlantUML skin parameters

Loaded into every PlantUML diagram via `-config`. Set company colours,
default fonts, layout direction, etc. — the file is plain PlantUML.

```plantuml
' docs/private/plantuml_preamble.iuml
skinparam BackgroundColor #FFFFFF
skinparam DefaultFontName "DejaVu Sans"
skinparam ClassBackgroundColor #E8F0FF
```

### 4. `conf_overrides.py` — free-form Python

For everything that the three asset hooks above can't express. Define a
single function `update(globals_: dict) -> None` that mutates the
Sphinx configuration in place. The file is imported via `importlib`
(no `exec`), so syntax errors surface with a normal traceback.

```python
# docs/private/conf_overrides.py
def update(globals_: dict) -> None:
    """Switch to the Furo theme and add a custom logo."""
    globals_["html_theme"] = "furo"
    globals_["html_logo"] = "_static/my_logo.png"
    globals_["html_theme_options"] = {
        "sidebar_hide_name": True,
    }
```

## Adding private documentation pages

The Sphinx build does *not* include `docs/private/` files in any view
by default. To bring a private page into the active view, add a
`toctree` entry from one of your `docs/public/` index files:

````markdown
```{toctree}
:caption: Internal

../private/internal_notes
```
````

Or create your own master_doc under `docs/private/` and add a separate
build target in the Makefile.
