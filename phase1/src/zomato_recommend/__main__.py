"""Allow ``python -m zomato_recommend`` or ``python -m zomato_recommend serve``."""

import sys

from zomato_recommend.cli import main

if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
