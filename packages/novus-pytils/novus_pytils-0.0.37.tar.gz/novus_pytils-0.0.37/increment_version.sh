#!/bin/bash

# Script to increment version in pyproject.toml
# Usage: ./increment_version.sh [major|minor|patch]
# Default: patch increment

set -e  # Exit on any error

TOML_FILE="pyproject.toml"
INCREMENT_TYPE="${1:-patch}"  # Default to patch if no argument provided

# Check if pyproject.toml exists
if [[ ! -f "$TOML_FILE" ]]; then
    echo "Error: $TOML_FILE not found in current directory"
    exit 1
fi

# Function to validate version format
validate_version() {
    local version="$1"
    if [[ ! $version =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
        echo "Error: Invalid version format '$version'. Expected format: major.minor.patch"
        exit 1
    fi
}

# Function to increment version
increment_version() {
    local version="$1"
    local type="$2"
    
    # Split version into components
    IFS='.' read -r major minor patch <<< "$version"
    
    case "$type" in
        major)
            major=$((major + 1))
            minor=0
            patch=0
            ;;
        minor)
            minor=$((minor + 1))
            patch=0
            ;;
        patch)
            patch=$((patch + 1))
            ;;
        *)
            echo "Error: Invalid increment type '$type'. Use 'major', 'minor', or 'patch'"
            exit 1
            ;;
    esac
    
    echo "$major.$minor.$patch"
}

# Extract current version from pyproject.toml
current_version=$(grep '^version = ' "$TOML_FILE" | sed 's/version = "\(.*\)"/\1/')

if [[ -z "$current_version" ]]; then
    echo "Error: Could not find version field in $TOML_FILE"
    exit 1
fi

echo "Current version: $current_version"

# Validate current version format
validate_version "$current_version"

# Calculate new version
new_version=$(increment_version "$current_version" "$INCREMENT_TYPE")

echo "New version: $new_version"

# Create backup
cp "$TOML_FILE" "$TOML_FILE.backup"
echo "Created backup: $TOML_FILE.backup"

# Update version in pyproject.toml
sed -i.tmp "s/^version = \".*\"/version = \"$new_version\"/" "$TOML_FILE"
rm -f "$TOML_FILE.tmp"

echo "Successfully updated version from $current_version to $new_version in $TOML_FILE"

# Verify the change
echo "Verification:"
grep '^version = ' "$TOML_FILE"