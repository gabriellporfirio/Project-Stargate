"""Application entry point. UI, workflow, rules and readers live separately."""

import json
import logging
from cli import build_parser, run_cli
from helpers.context import PlaybackContext


def main():
    logging.basicConfig(level=logging.ERROR)
    args = build_parser().parse_args()
    if args.check:
        try:
            width, height = (
                (int(x) for x in args.size.lower().split("x"))
                if args.size
                else (None, None)
            )
            context = PlaybackContext(
                platform=args.platform,
                scala_engine=args.scala_engine,
                dise_version=args.dise_version,
                dise_player=args.dise_player,
                pdf_workflow=args.pdf_workflow,
                canvas_width=width,
                canvas_height=height,
                simultaneous_videos=args.multi_video,
            )
        except ValueError:
            print(
                json.dumps(
                    {
                        "error": "Check the playback settings; use WIDTHxHEIGHT for the content size."
                    }
                )
            )
            return 3
        return run_cli(args.check, args.json, context)
    from desktop import launch

    launch(args.file)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
