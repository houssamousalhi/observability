#!/bin/bash

# Create a temporary file to store all output
TEMP_OUTPUT=$(mktemp)

# Set TF_EXTERNAL environment variable to indicate we're running from Terraform
export TF_EXTERNAL=1

# Run the build script
"${0%/*}/build_package.sh" > "$TEMP_OUTPUT" 2>&1

# Extract only the JSON output (the last line starting with {)
grep -E "^{.*}$" "$TEMP_OUTPUT" | tail -1

# Cleanup
rm -f "$TEMP_OUTPUT" 