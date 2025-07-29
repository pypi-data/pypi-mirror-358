#!/bin/bash
set -e

# Check if gh CLI is installed
if ! command -v gh &> /dev/null; then
    echo "Error: GitHub CLI (gh) is not installed."
    exit 1
fi

# Check if version type is provided
if [ $# -eq 0 ]; then
    echo "Usage: ./release.sh [patch|minor|major] [--dry-run]"
    exit 1
fi

# Check if we're on main branch
CURRENT_BRANCH=$(git branch --show-current)
if [ "$CURRENT_BRANCH" != "main" ]; then
    echo "Error: Release script can only be run from the main branch."
    echo "Current branch: $CURRENT_BRANCH"
    echo "Please checkout main and try again: git checkout main"
    exit 1
fi

# Check if workspace is clean
if [ -n "$(git status --porcelain)" ]; then
    echo "Error: Working directory is not clean. Please commit or stash your changes first."
    git status --short
    exit 1
fi

# Ensure main is up to date
echo "Pulling latest changes from main..."
git pull origin main

VERSION_TYPE=$1
DRY_RUN=${2:-""}

if [ "$DRY_RUN" = "--dry-run" ]; then
    echo "DRY RUN MODE - No actual changes will be made"
    CURRENT_VERSION=$(grep 'current_version = ' .bumpversion.toml | sed 's/current_version = "\(.*\)"/\1/')
    echo "Current version: $CURRENT_VERSION"
    echo "Would bump $VERSION_TYPE version..."
    uv run bump-my-version bump $VERSION_TYPE --dry-run --allow-dirty --verbose
    exit 0
fi

# Bump version without creating commit or tag
echo "Bumping $VERSION_TYPE version (without commit)..."
uv run bump-my-version bump $VERSION_TYPE

# Get the new version 
NEW_VERSION=$(grep 'current_version = ' .bumpversion.toml | sed 's/current_version = "\(.*\)"/\1/')
echo "New version: $NEW_VERSION"

# Create release branch with new version number
RELEASE_BRANCH="release/v${NEW_VERSION}"
echo "Creating release branch: $RELEASE_BRANCH"
git checkout -b $RELEASE_BRANCH

# Commit the version changes
echo "Committing version changes..."
git add -A
git commit -m "Release v$NEW_VERSION"

# Push release branch
echo "Pushing release branch..."
git push origin $RELEASE_BRANCH

# Create PR for release (manual review required)
echo "Creating PR for release..."

# Ensure gh is authenticated
if ! gh auth status >/dev/null 2>&1; then
    echo "GitHub CLI not authenticated. Starting authentication..."
    gh auth login
fi

gh pr create --title "Release v${NEW_VERSION}" \
  --body "Automated release v${NEW_VERSION}

- Bumped version to ${NEW_VERSION}
- Created by release automation script
- **Review and merge to trigger release workflow**" \
  --base main

echo "Release PR created!"
echo "- Release branch: $RELEASE_BRANCH"
echo "- PR created for manual review and merge"
echo "- Tag and release will be created automatically when PR is merged"