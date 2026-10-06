"""Application entry point. UI, workflow, rules and readers live separately."""

import logging
import sys

from desktop import launch


def main():
    logging.basicConfig(level=logging.ERROR)
    # A file dropped onto the launcher, or opened with "Open with", arrives
    # as the first argument and is checked as soon as the window opens.
    launch(sys.argv[1] if len(sys.argv) > 1 else None)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
