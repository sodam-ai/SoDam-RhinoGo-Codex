#!/usr/bin/env python3
"""Check live Rhino 7 parameters before opening Rhino."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--parameters", type=Path)
    args = parser.parse_args()
    assets = Path(__file__).resolve().parents[1] / "assets"
    sys.path.insert(0, str(assets))
    from sodam_rhinogo_parameters import load_parameters
    try:
        load_parameters(str(args.parameters) if args.parameters else "")
    except (OSError, ValueError, TypeError) as exc:
        parser.exit(2, "Invalid Rhino 7 parameters: {}\n".format(exc))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
