"""Small Windows-compatible CLI for local authorised manga packages."""

import argparse
import json
import sys
from pathlib import Path

from .importer import ImportFailure, import_local, verify_export


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Authorised manga import and CBZ validation")
    commands = parser.add_subparsers(dest="command", required=True)
    ingest = commands.add_parser("import", help="Import pages, folders, CBZ or ZIP")
    ingest.add_argument("--source", type=Path, required=True)
    ingest.add_argument("--output", type=Path, required=True)
    ingest.add_argument("--registry", type=Path, default=Path(".manga-retriever/ids.json"))
    ingest.add_argument("--rights-json", type=Path)
    ingest.add_argument("--direction", choices=["rtl", "ltr", "vertical"], default="rtl")
    verify = commands.add_parser("verify", help="Verify candidate assets and chapter CBZs")
    verify.add_argument("--export", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        if args.command == "import":
            result = import_local(args.source, args.output, args.registry,
                                  rights_path=args.rights_json, direction=args.direction)
        else:
            result = verify_export(args.export)
    except (ImportFailure, OSError, ValueError, KeyError, TypeError, json.JSONDecodeError) as error:
        print(f"Import/verification failed: {error}", file=sys.stderr)
        return 1
    print(json.dumps({"status": "verified", **result}, sort_keys=True))
    return 0
