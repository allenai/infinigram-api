#!/usr/bin/env python3
"""
Generate a CSV manifest for s2pdf `.npy` shards by invoking the AWS CLI.

Usage:
    python scripts/generate_s2pdf_csv.py [--output PATH] [--prefix S3_URI]

Key options:
    --prefix          S3 prefix to scan (default: s2pdf v0.2 path)
    --output          Destination CSV path (default: stdout)
    --aws-cli         AWS CLI executable (default: aws)
    --profile         AWS CLI profile name, if needed
    --extra-aws-args  Additional flags passed to the AWS CLI

Example:
    python scripts/generate_s2pdf_csv.py --output indexing/dolma2/s2pdf.csv
"""

from __future__ import annotations

import argparse
import csv
import shlex
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List, Sequence, Tuple
from urllib.parse import urlparse


S2PDF_PREFIX = "s3://ai2-llm/preprocessed/dolma2-0625/v0.2/allenai/dolma2-tokenizer/s2pdf/"


class AwsCliError(RuntimeError):
    """Raised when the AWS CLI command fails."""


@dataclass
class ObjectInfo:
    key: str
    size: int
    subset: str
    category: str


def parse_args(argv: Sequence[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Generate a CSV manifest for s2pdf `.npy` shards using `aws s3 ls` output."
        )
    )
    parser.add_argument(
        "--prefix",
        default=S2PDF_PREFIX,
        help=f"S3 prefix to scan (default: {S2PDF_PREFIX})",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Destination CSV path (default: stdout).",
    )
    parser.add_argument(
        "--aws-cli",
        default="aws",
        help="AWS CLI executable to invoke (default: aws).",
    )
    parser.add_argument(
        "--profile",
        default=None,
        help="AWS CLI profile to use.",
    )
    parser.add_argument(
        "--extra-aws-args",
        default="",
        help="Additional arguments passed verbatim to the AWS CLI.",
    )
    return parser.parse_args(argv)


def ensure_trailing_slash(prefix: str) -> str:
    return prefix if prefix.endswith("/") else f"{prefix}/"


def split_s3_uri(uri: str) -> Tuple[str, str]:
    parsed = urlparse(uri)
    if parsed.scheme != "s3" or not parsed.netloc:
        raise ValueError(f"Invalid S3 URI: {uri}")
    key_prefix = parsed.path.lstrip("/")
    return parsed.netloc, key_prefix


def run_aws_s3_ls(
    cli: str, prefix: str, profile: str | None, extra_args: str
) -> str:
    bucket, key_prefix = split_s3_uri(prefix)
    cmd: List[str] = [cli]
    if profile:
        cmd.extend(["--profile", profile])
    cmd.extend(["s3", "ls", f"s3://{bucket}/{key_prefix}", "--recursive"])
    if extra_args:
        cmd.extend(shlex.split(extra_args))

    result = subprocess.run(
        cmd,
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    if result.returncode != 0:
        raise AwsCliError(
            f"`{' '.join(cmd)}` failed with code {result.returncode}:\n{result.stderr}"
        )
    return result.stdout


def parse_ls_output(prefix: str, stdout: str) -> Iterable[ObjectInfo]:
    bucket, key_prefix = split_s3_uri(prefix)
    normalized_prefix = ensure_trailing_slash(key_prefix) if key_prefix else ""
    rows: List[ObjectInfo] = []

    for raw_line in stdout.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        # Expected format: YYYY-MM-DD HH:MM:SS <size> <key>
        parts = line.split()
        if len(parts) < 4:
            continue
        size_str = parts[2]
        reported_key = " ".join(parts[3:])
        if not reported_key.endswith(".npy"):
            continue
        size = int(size_str)
        full_key_path = reported_key
        if normalized_prefix and not reported_key.startswith(normalized_prefix):
            full_key_path = f"{normalized_prefix}{reported_key.lstrip('/')}"
        category = Path(full_key_path).parent.name
        full_key = f"s3://{bucket}/{full_key_path}"
        rows.append(ObjectInfo(key=full_key, size=size, subset="s2pdf", category=category))

    rows.sort(key=lambda row: row.key)
    return rows


def write_csv(rows: Iterable[ObjectInfo], dest: Path | None) -> None:
    headers = ("key", "size", "subset", "category")
    if dest is None:
        writer = csv.writer(sys.stdout)
        writer.writerow(headers)
        for row in rows:
            writer.writerow((row.key, row.size, row.subset, row.category))
    else:
        dest.parent.mkdir(parents=True, exist_ok=True)
        with dest.open("w", newline="") as handle:
            writer = csv.writer(handle)
            writer.writerow(headers)
            for row in rows:
                writer.writerow((row.key, row.size, row.subset, row.category))


def main(argv: Sequence[str]) -> int:
    args = parse_args(argv)
    prefix = ensure_trailing_slash(args.prefix)
    try:
        stdout = run_aws_s3_ls(args.aws_cli, prefix, args.profile, args.extra_aws_args)
    except (AwsCliError, ValueError) as exc:
        print(exc, file=sys.stderr)
        return 1

    rows = parse_ls_output(prefix, stdout)
    write_csv(rows, args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))

