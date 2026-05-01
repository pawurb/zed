#!/usr/bin/env python3
"""Add channels-console optional dep + feature to every crates/*/Cargo.toml. Idempotent."""

import re
from pathlib import Path

DEP_LINE = 'channels-console = { version = "0.2", optional = true, features = ["tokio", "futures"] }\n'
FEATURE_LINE = 'channels-console = ["dep:channels-console"]\n'


def process(path: Path):
    lines = path.read_text().splitlines(keepends=True)
    cleaned = [l for l in lines if l != DEP_LINE and l != FEATURE_LINE]

    has_features = any(re.match(r'^\[features\]', l) for l in cleaned)

    out = []
    dep_added = False
    feat_added = False
    i = 0
    while i < len(cleaned):
        line = cleaned[i]
        out.append(line)
        if not dep_added and re.match(r'^\[dependencies\]', line):
            out.append(DEP_LINE)
            dep_added = True
        elif not feat_added and re.match(r'^\[features\]', line):
            out.append(FEATURE_LINE)
            feat_added = True
        elif (
            re.match(r'^\[', line)
            and not re.match(r'^\[dependencies\]', line)
            and dep_added
            and not has_features
            and not feat_added
        ):
            out.insert(-1, '\n[features]\n')
            out.insert(-1, FEATURE_LINE)
            out.insert(-1, '\n')
            feat_added = True
        i += 1

    if dep_added and not has_features and not feat_added:
        out.append('\n[features]\n')
        out.append(FEATURE_LINE)
        feat_added = True

    path.write_text(''.join(out))
    print(f"[{'ok' if (dep_added and feat_added) else 'WARN'}] {path}")


def main():
    crates = Path(__file__).parent / 'crates'
    for p in sorted(crates.glob('*/Cargo.toml')):
        process(p)


if __name__ == '__main__':
    main()
