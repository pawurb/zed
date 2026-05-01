#!/usr/bin/env python3
"""Add hotpath dep + features to every crates/*/Cargo.toml. Idempotent."""

import re
from pathlib import Path

DEP_LINE = 'hotpath = { version = "0.16", features = ["tokio", "futures"] }\n'
FEATURE_LINES = [
    'hotpath = ["hotpath/hotpath"]\n',
    'hotpath-alloc = ["hotpath/hotpath-alloc"]\n',
    'hotpath-alloc-meta = ["hotpath/hotpath-alloc-meta"]\n',
    'hotpath-mcp = ["hotpath/hotpath-mcp"]\n',
    'hotpath-mcp-meta = ["hotpath/hotpath-mcp-meta"]\n',
    'hotpath-meta = ["hotpath/hotpath-meta"]\n',
]


def process(path: Path):
    lines = path.read_text().splitlines(keepends=True)

    # strip prior insertions for idempotency
    cleaned = [l for l in lines if l != DEP_LINE and l not in FEATURE_LINES]

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
            out.extend(FEATURE_LINES)
            feat_added = True
        elif (
            re.match(r'^\[', line)
            and not re.match(r'^\[dependencies\]', line)
            and dep_added
            and not has_features
            and not feat_added
        ):
            out.insert(-1, '\n')
            out.insert(-1, '[features]\n')
            for fl in FEATURE_LINES:
                out.insert(-1, fl)
            out.insert(-1, '\n')
            feat_added = True
        i += 1

    if dep_added and not has_features and not feat_added:
        out.append('\n[features]\n')
        out.extend(FEATURE_LINES)
        feat_added = True

    path.write_text(''.join(out))
    status = 'ok' if (dep_added and feat_added) else 'WARN'
    print(f"[{status}] {path}")


def main():
    crates = Path(__file__).parent / 'crates'
    for p in sorted(crates.glob('*/Cargo.toml')):
        process(p)


if __name__ == '__main__':
    main()
