"""python -m zomato_surface"""

import sys

from zomato_surface.cli import main

if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
