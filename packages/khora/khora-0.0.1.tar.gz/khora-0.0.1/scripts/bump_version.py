#!/usr/bin/env python3
"""Script to bump version in pyproject.toml"""

import argparse
import re
import sys
from pathlib import Path


def get_current_version():
    """Get current version from pyproject.toml"""
    pyproject_path = Path("pyproject.toml")
    if not pyproject_path.exists():
        print("Error: pyproject.toml not found")
        sys.exit(1)

    content = pyproject_path.read_text()
    match = re.search(r'^version = "([^"]+)"', content, re.MULTILINE)
    if not match:
        print("Error: Could not find version in pyproject.toml")
        sys.exit(1)

    return match.group(1)


def parse_version(version_str):
    """Parse version string into components"""
    parts = version_str.split(".")
    if len(parts) != 3:
        print(f"Error: Invalid version format: {version_str}")
        sys.exit(1)

    try:
        return [int(part) for part in parts]
    except ValueError:
        print(f"Error: Invalid version format: {version_str}")
        sys.exit(1)


def bump_version(current_version, bump_type):
    """Bump version according to type"""
    major, minor, patch = parse_version(current_version)

    if bump_type == "major":
        major += 1
        minor = 0
        patch = 0
    elif bump_type == "minor":
        minor += 1
        patch = 0
    elif bump_type == "patch":
        patch += 1
    else:
        print(f"Error: Invalid bump type: {bump_type}")
        sys.exit(1)

    return f"{major}.{minor}.{patch}"


def update_version_in_file(new_version):
    """Update version in pyproject.toml"""
    pyproject_path = Path("pyproject.toml")
    content = pyproject_path.read_text()

    # Update version
    updated_content = re.sub(
        r'^version = "[^"]+"', f'version = "{new_version}"', content, flags=re.MULTILINE
    )

    pyproject_path.write_text(updated_content)


def update_init_file(new_version):
    """Update version in __init__.py"""
    init_path = Path("src/khora/__init__.py")
    if init_path.exists():
        content = init_path.read_text()
        updated_content = re.sub(
            r'^__version__ = "[^"]+"',
            f'__version__ = "{new_version}"',
            content,
            flags=re.MULTILINE,
        )
        init_path.write_text(updated_content)


def main():
    parser = argparse.ArgumentParser(description="Bump version in pyproject.toml")
    parser.add_argument(
        "bump_type", choices=["major", "minor", "patch"], help="Type of version bump"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be changed without making changes",
    )

    args = parser.parse_args()

    current_version = get_current_version()
    new_version = bump_version(current_version, args.bump_type)

    print(f"Current version: {current_version}")
    print(f"New version: {new_version}")

    if args.dry_run:
        print("(Dry run - no changes made)")
        return

    # Make changes
    update_version_in_file(new_version)
    update_init_file(new_version)

    print(f"✅ Version bumped from {current_version} to {new_version}")
    print("")
    print("Next steps:")
    print("1. Review the changes:")
    print("   git diff")
    print("2. Commit and create tag:")
    print("   git add .")
    print(f"   git commit -m 'Bump version to {new_version}'")
    print(f"   git tag v{new_version}")
    print("3. Push changes and tag:")
    print("   git push origin main")
    print(f"   git push origin v{new_version}")
    print("4. The publish workflow will automatically publish to PyPI")


if __name__ == "__main__":
    main()
