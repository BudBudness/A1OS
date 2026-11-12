#!/usr/bin/env python3
"""Rehearse a Little Oaks COPY restore in a private, new SQLite database."""

import argparse
import gzip
import hashlib
import os
from pathlib import Path
import re
import sqlite3

COLUMNS = (
    "id", "parent_name", "child_name", "child_age",
    "programme", "phone", "message", "created_at",
)
COPY_HEADER = re.compile(r"^COPY public\.enquiries \(([^)]+)\) FROM stdin;$")
ESCAPES = re.compile(rb"\\([0-7]{1,3}|x[0-9a-fA-F]{1,2}|.)")
CONTROL = dict(zip(b"bfnrtv", (b"\b", b"\f", b"\n", b"\r", b"\t", b"\v")))


def decode_copy_field(value):
    if value == r"\N":
        return None

    def unescape(match):
        token = match[1]
        if token[:1] in (b"0", b"1", b"2", b"3", b"4", b"5", b"6", b"7"):
            return bytes([int(token, 8)])
        if token.startswith(b"x") and len(token) > 1:
            return bytes([int(token[1:], 16)])
        return CONTROL.get(token[0], token)

    return ESCAPES.sub(unescape, value.encode("utf-8")).decode("utf-8")


def read_enquiries(source):
    rows = None
    columns = None
    with gzip.open(source, "rt", encoding="utf-8", newline="") as dump:
        for line in dump:
            line = line.rstrip("\r\n")
            header = COPY_HEADER.fullmatch(line)
            if columns is None and header:
                if rows is not None:
                    raise ValueError("Multiple enquiry COPY sections")
                columns = tuple(part.strip() for part in header[1].split(","))
                if len(columns) != len(COLUMNS) or set(columns) != set(COLUMNS):
                    raise ValueError("Enquiry columns differ from the target schema")
                rows = []
            elif columns is not None:
                if line == r"\.":
                    columns = None
                    continue
                fields = line.split("\t")
                if len(fields) != len(columns):
                    raise ValueError("Unexpected enquiry field count")
                row = dict(zip(columns, map(decode_copy_field, fields), strict=True))
                for column in ("programme", "message"):
                    if row[column] is None:
                        row[column] = ""
                if any(row[column] is None for column in COLUMNS):
                    raise ValueError("Null in a required enquiry field")
                rows.append(tuple(row[column] for column in COLUMNS))
    if rows is None or columns is not None:
        raise ValueError("Missing or incomplete enquiry COPY section")
    return rows


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("dump", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--sha256", required=True)
    parser.add_argument("--expected-rows", required=True, type=int)
    args = parser.parse_args()

    try:
        with args.dump.open("rb") as source:
            if hashlib.file_digest(source, "sha256").hexdigest() != args.sha256.lower():
                raise ValueError("Snapshot SHA-256 mismatch")
            source.seek(0)
            rows = read_enquiries(source)
        if len(rows) != args.expected_rows:
            raise ValueError("Snapshot row count mismatch")
        schema = Path(__file__).resolve().parents[1] / "migrations" / "0001_enquiries.sql"
        with sqlite3.connect(":memory:") as restored:
            restored.executescript(schema.read_text(encoding="utf-8"))
            restored.executemany(
                "INSERT INTO enquiries VALUES (?, ?, ?, ?, ?, ?, ?, ?)", rows,
            )
            restored.commit()
            fd = os.open(args.output, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
            os.close(fd)
            with sqlite3.connect(args.output) as output:
                restored.backup(output)
                actual = output.execute("SELECT * FROM enquiries ORDER BY id").fetchall()
                if actual != sorted(rows, key=lambda row: row[0]):
                    raise ValueError("Restored rows differ from snapshot")
                if output.execute("PRAGMA integrity_check").fetchone() != ("ok",):
                    raise ValueError("Database integrity check failed")
    except (OSError, UnicodeError, ValueError, sqlite3.Error, EOFError) as error:
        parser.exit(1, f"Restore failed ({type(error).__name__}). Inspect the source and destination locally.\n")
    print(f"Restore verified: {len(rows)} enquiries. Database contains private records.")


if __name__ == "__main__":
    main()
