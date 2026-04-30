"""Convert LinkML-validated YAML into MyST-flavoured Markdown for sphinx-needs."""

from .converter import NeedsFromLinkML

__version__ = "0.1.0"
__all__ = ["NeedsFromLinkML", "__version__"]
