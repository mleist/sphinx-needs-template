"""Minimal ReqIF import/export bridge for sphinx-needs.

Implements a small subset of ReqIF (1.2 / 1.0.1) sufficient for round-tripping
``id``/``title``/``description``/``status``/``tags`` between sphinx-needs and
external requirements management tools. Not a full ReqIF library.
"""
from .converter import import_reqif, export_reqif

__version__ = "0.1.0"
__all__ = ["import_reqif", "export_reqif", "__version__"]
