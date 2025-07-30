#!/usr/bin/env python3
"""Script to create a complete release with version bump and git tag."""

import argparse
import subprocess
import sys

from bump_version import (
    bump_version,
    get_current_version,
    update_init_file,
    update_version_in_file,
)


def run_command(cmd, check=True):
    """Run a shell command and return the result."""
    print(f"Running: {cmd}")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if check and result.returncode != 0:
        print(f"Error running command: {cmd}")
        print(f"stdout: {result.stdout}")
        print(f"stderr: {result.stderr}")
        sys.exit(1)
    return result


def check_git_status():
    """Check if git working directory is clean."""
    result = run_command("git status --porcelain", check=False)
    if result.stdout.strip():
        print("Error: Git working directory is not clean.")
        print("Please commit or stash your changes before creating a release.")
        sys.exit(1)


def check_on_main_branch():
    """Check if we're on the main branch."""
    result = run_command("git branch --show-current", check=False)
    current_branch = result.stdout.strip()
    if current_branch != "main":
        print(f"Warning: You're on branch '{current_branch}', not 'main'.")
        response = input("Continue anyway? (y/N): ")
        if response.lower() != "y":
            sys.exit(1)


def create_release(bump_type, dry_run=False):
    """Create a complete release."""
    # Get versions
    current_version = get_current_version()
    new_version = bump_version(current_version, bump_type)

    print(f"Creating release: {current_version} → {new_version}")

    if dry_run:
        print("(Dry run - no changes will be made)")
        return

    # Check git status
    check_git_status()
    check_on_main_branch()

    # Update version files
    print("\n📝 Updating version files...")
    update_version_in_file(new_version)
    update_init_file(new_version)

    # Run tests
    print("\n🧪 Running tests...")
    run_command("pytest tests/unit -v")

    # Run code quality checks
    print("\n🔍 Running code quality checks...")
    run_command("black --check src tests")
    run_command("ruff check src tests")

    # Git operations
    print("\n📦 Creating git commit and tag...")
    run_command("git add .")
    run_command(f'git commit -m "Bump version to {new_version}"')
    run_command(f"git tag v{new_version}")

    print(f"\n✅ Release v{new_version} created successfully!")
    print("\nTo publish the release:")
    print("1. Push the changes:")
    print("   git push origin main")
    print(f"   git push origin v{new_version}")
    print("2. The GitHub Actions workflow will automatically publish to PyPI")
    print("\nOr to push everything at once:")
    print("   git push origin main --tags")


def main():
    parser = argparse.ArgumentParser(
        description="Create a complete release with version bump and git tag"
    )
    parser.add_argument(
        "bump_type", choices=["major", "minor", "patch"], help="Type of version bump"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be done without making changes",
    )
    parser.add_argument(
        "--push",
        action="store_true",
        help="Automatically push changes and tags to origin",
    )

    args = parser.parse_args()

    try:
        create_release(args.bump_type, args.dry_run)

        if args.push and not args.dry_run:
            print("\n🚀 Pushing to origin...")
            run_command("git push origin main --tags")
            print("Release pushed! Check GitHub Actions for publishing status.")

    except KeyboardInterrupt:
        print("\nRelease creation cancelled.")
        sys.exit(1)


if __name__ == "__main__":
    main()
