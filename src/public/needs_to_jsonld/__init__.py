"""Export sphinx-needs ``needs.json`` as JSON-LD using a LinkML schema."""
from .converter import NeedsToJsonLD

__version__ = "0.1.0"
__all__ = ["NeedsToJsonLD", "__version__"]
