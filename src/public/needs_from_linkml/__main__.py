"""Allow running ``python -m needs_from_linkml``."""
from .cli import main

if __name__ == "__main__":
    raise SystemExit(main())
