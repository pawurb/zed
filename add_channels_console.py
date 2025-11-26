#!/usr/bin/env python3
"""
Script to add channels-console dependency and feature to all top-level crates.
"""

import os
import re
from pathlib import Path

DEPENDENCY_LINE = 'channels-console = { version = "0.2", optional = true, features=[\'tokio\', \'futures\'] }\n'
FEATURE_LINE = '\n'


def process_cargo_toml(file_path):
    """Process a single Cargo.toml file."""
    print(f"Processing {file_path}")

    with open(file_path, 'r') as f:
        lines = f.readlines()

    # First pass: check if [features] section exists and remove any previously added lines
    features_exists = False
    cleaned_lines = []
    for line in lines:
        # Skip lines we may have added previously
        if line == DEPENDENCY_LINE or line == FEATURE_LINE:
            continue
        # Check if [features] exists
        if re.match(r'^\[features\]', line):
            features_exists = True
        cleaned_lines.append(line)

    # Second pass: add the dependency and feature lines
    new_lines = []
    dependency_added = False
    feature_added = False
    dependencies_section_ended = False

    i = 0
    while i < len(cleaned_lines):
        line = cleaned_lines[i]
        new_lines.append(line)

        # Add dependency line after [dependencies]
        if re.match(r'^\[dependencies\]', line) and not dependency_added:
            new_lines.append(DEPENDENCY_LINE)
            dependency_added = True

        # Add feature line after [features]
        elif re.match(r'^\[features\]', line) and not feature_added:
            new_lines.append(FEATURE_LINE)
            feature_added = True

        # If we hit another section after [dependencies] and [features] doesn't exist
        elif re.match(r'^\[', line) and not re.match(r'^\[dependencies\]', line):
            if dependency_added and not features_exists and not feature_added:
                # Insert [features] section before this new section
                new_lines.insert(-1, '\n')
                new_lines.insert(-1, '[features]\n')
                new_lines.insert(-1, FEATURE_LINE)
                feature_added = True

        i += 1

    # If we never added features section and need to (at end of file)
    if dependency_added and not features_exists and not feature_added:
        new_lines.append('\n')
        new_lines.append('[features]\n')
        new_lines.append(FEATURE_LINE)
        feature_added = True

    # Write back the modified content
    with open(file_path, 'w') as f:
        f.writelines(new_lines)

    if dependency_added and feature_added:
        print(f"  ✓ Added dependency and feature")
    else:
        print(f"  ⚠ Warning: Could not add all required lines")


def main():
    """Main function to process all Cargo.toml files in crates/."""
    crates_dir = Path(__file__).parent / 'crates'

    if not crates_dir.exists():
        print(f"Error: {crates_dir} does not exist")
        return

    # Find all top-level Cargo.toml files in crates/
    cargo_files = list(crates_dir.glob('*/Cargo.toml'))

    print(f"Found {len(cargo_files)} Cargo.toml files to process\n")

    for cargo_file in sorted(cargo_files):
        process_cargo_toml(cargo_file)

    print(f"\nDone! Processed {len(cargo_files)} files.")


if __name__ == '__main__':
    main()
