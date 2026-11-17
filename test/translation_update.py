#!/usr/bin/env python3
"""Prepare autonomous AI tasks or DeepL translations, then validate/apply."""

import argparse
import json
from pathlib import Path
import sys

from translation_tools.update import DeepL, apply_bundle, load_deepl_key, prepare
from translation_tools.verify import DEFAULT_CONFIG, ROOT, load_config


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=ROOT / "en-us/docs")
    parser.add_argument("--target", type=Path, default=ROOT / "zh-cn/docs")
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--files", nargs="+", default=[], help="Source-relative paths, directories, or globs")
    parser.add_argument("--mode", choices=["autonomous", "deepl"], default="autonomous")
    parser.add_argument("--bundle", type=Path, help="Prepared task/output JSON (required unless --apply)")
    parser.add_argument("--apply", type=Path, help="Validate a completed task bundle")
    parser.add_argument("--write", action="store_true", help="Write validated translations; default is validation only")
    args = parser.parse_args(argv)
    try:
        config = load_config(args.config)
        if args.apply:
            if args.bundle or args.mode != "autonomous" or args.files:
                parser.error("--apply cannot be combined with --bundle, --mode deepl, or --files")
            bundle = json.loads(args.apply.read_text(encoding="utf-8"))
        else:
            if not args.bundle:
                parser.error("--bundle is required when preparing translations")
            if args.write and args.mode == "autonomous":
                parser.error("Autonomous preparation cannot --write; fill the task, then --apply")
            bundle = prepare(args.source, args.target, config, args.files)
            if args.mode == "deepl":
                DeepL(load_deepl_key()).fill(bundle)
            args.bundle.parent.mkdir(parents=True, exist_ok=True)
            args.bundle.write_text(json.dumps(bundle, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            if args.mode == "autonomous":
                print(f"Prepared {len(bundle['files'])} file(s). Fill translation fields, then run --apply.")
                return 0
        outputs = apply_bundle(bundle, args.source, args.target, config, args.write)
        print(f"{'Wrote' if args.write else 'Validated'} {len(outputs)} file(s). Semantic review and production build still required.")
        return 0
    except (OSError, ValueError, KeyError, TypeError) as error:
        print(f"Translation update failed: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
