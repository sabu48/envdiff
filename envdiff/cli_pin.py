"""CLI commands: envdiff-pin save / check."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from envdiff.parser import parse_env_file
from envdiff.pinner import check_pin, load_pin, pin, save_pin
from envdiff.pin_reporter import render_pin


def build_pin_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="envdiff-pin",
        description="Pin env values and detect deviations.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    save_p = sub.add_parser("save", help="Save current env as pin baseline.")
    save_p.add_argument("env_file", help="Path to .env file")
    save_p.add_argument("--pin-file", default=".env.pin", help="Destination pin file")

    check_p = sub.add_parser("check", help="Check current env against pin baseline.")
    check_p.add_argument("env_file", help="Path to .env file")
    check_p.add_argument("--pin-file", default=".env.pin", help="Pin baseline file")
    check_p.add_argument("--format", choices=["text", "json"], default="text")
    check_p.add_argument(
        "--strict",
        action="store_true",
        help="Exit 1 when deviations are found.",
    )
    return parser


def _run_save(args: argparse.Namespace) -> int:
    env = parse_env_file(Path(args.env_file))
    pinned = pin(env)
    save_pin(pinned, Path(args.pin_file))
    print(f"Pinned {len(pinned)} keys to {args.pin_file}")
    return 0


def _run_check(args: argparse.Namespace) -> int:
    pin_path = Path(args.pin_file)
    if not pin_path.exists():
        print(f"Pin file not found: {pin_path}", file=sys.stderr)
        return 2
    current = parse_env_file(Path(args.env_file))
    pinned = load_pin(pin_path)
    result = check_pin(pinned, current)
    print(render_pin(result, fmt=args.format), end="")
    if args.strict and result.has_deviations():
        return 1
    return 0


def main(argv: list[str] | None = None) -> None:
    parser = build_pin_parser()
    args = parser.parse_args(argv)
    if args.command == "save":
        sys.exit(_run_save(args))
    else:
        sys.exit(_run_check(args))


if __name__ == "__main__":
    main()
