#!/bin/bash

# OpenAPI Client Regeneration Script
# This script regenerates the OpenAPI client code while preserving custom files

set -e  # Exit on any error

# Configuration
OPENAPI_SPEC_PATH="../speechall-openapi/openapi.yaml"
GENERATOR="python-pydantic-v1"
OUTPUT_DIR="."
TEMP_OUTPUT_DIR="./temp_generated_client"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🔄 Speechall OpenAPI Client Regeneration${NC}"
echo "=============================================="

# Check if OpenAPI spec exists
if [ ! -f "$OPENAPI_SPEC_PATH" ]; then
    echo -e "${RED}❌ Error: OpenAPI spec not found at $OPENAPI_SPEC_PATH${NC}"
    echo "Please ensure the speechall-openapi repository is cloned at ../speechall-openapi/"
    exit 1
fi

# Check if openapi-generator is available
if ! command -v openapi-generator &> /dev/null; then
    echo -e "${RED}❌ Error: openapi-generator command not found${NC}"
    echo "Please install it with: npm install @openapitools/openapi-generator-cli -g"
    echo "Or use: brew install openapi-generator"
    exit 1
fi

# Show current status
echo -e "${YELLOW}📋 Current status:${NC}"
echo "  OpenAPI Spec: $OPENAPI_SPEC_PATH"
echo "  Generator: $GENERATOR"
echo "  Output Directory: $OUTPUT_DIR"
echo ""

# Backup custom files (just in case)
echo -e "${YELLOW}💾 Creating backup of custom files...${NC}"
BACKUP_DIR="backup_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"

# Read .openapi-generator-ignore and backup all files listed there
if [ -f ".openapi-generator-ignore" ]; then
    echo "  📋 Reading .openapi-generator-ignore file..."
    while IFS= read -r line; do
        # Skip empty lines and comments
        if [[ -z "$line" || "$line" =~ ^[[:space:]]*# ]]; then
            continue
        fi
        
        # Handle different types of patterns
        if [[ "$line" == *"/**" ]]; then
            # Handle directory patterns like .venv/**, __pycache__/**
            dir_pattern="${line%/**}"
            if [ -d "$dir_pattern" ]; then
                mkdir -p "$BACKUP_DIR/$(dirname "$dir_pattern")" 2>/dev/null
                cp -r "$dir_pattern" "$BACKUP_DIR/$(dirname "$dir_pattern")/" 2>/dev/null
                echo "  ✅ Backed up directory $dir_pattern"
            fi
        elif [[ "$line" != *"*"* ]]; then
            # Handle simple files (with or without directory paths)
            if [ -f "$line" ]; then
                # Create directory structure if needed
                mkdir -p "$BACKUP_DIR/$(dirname "$line")" 2>/dev/null
                cp "$line" "$BACKUP_DIR/$line"
                echo "  ✅ Backed up $line"
            fi
        fi
    done < .openapi-generator-ignore
else
    echo "  ⚠️  .openapi-generator-ignore file not found, using fallback list"
    # Fallback to original hardcoded list
    for file in example_transcribe.py simple_example.py EXAMPLE_README.md pyproject.toml; do
        if [ -f "$file" ]; then
            cp "$file" "$BACKUP_DIR/"
            echo "  ✅ Backed up $file"
        fi
    done
fi

# Regenerate the client
echo ""
echo -e "${BLUE}🔧 Regenerating OpenAPI client into temporary directory...${NC}"
# Create or clean the temporary directory
rm -rf "$TEMP_OUTPUT_DIR"
mkdir -p "$TEMP_OUTPUT_DIR"

openapi-generator generate \
    -i "$OPENAPI_SPEC_PATH" \
    -g "$GENERATOR" \
    -o "$TEMP_OUTPUT_DIR" \
    --package-name speechall \
    --skip-validate-spec \
    --additional-properties="packageVersion=0.2.0"

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Client regeneration into temporary directory completed successfully!${NC}"
else
    echo -e "${RED}❌ Client regeneration failed!${NC}"
    rm -rf "$TEMP_OUTPUT_DIR" # Clean up temp dir on failure
    exit 1
fi

echo -e "${BLUE}🔄 Syncing generated files to output directory...${NC}"
# Remove old generated directories and files from the primary output directory
# Be careful here not to delete essential non-generated files.
# Common generated items: speechall/, openapi_client/, docs/, test/, tests/, README.md, setup.py, .openapi-generator-ignore, tox.ini (sometimes)
# The custom files backed up are: example_transcribe.py, simple_example.py, EXAMPLE_README.md, pyproject.toml
# So, it should be safe to remove these:
rm -rf \
    "$OUTPUT_DIR/speechall" \
    "$OUTPUT_DIR/openapi_client" \
    "$OUTPUT_DIR/docs" \
    "$OUTPUT_DIR/test" \
    "$OUTPUT_DIR/tests" \
    "$OUTPUT_DIR/README.md" \
    "$OUTPUT_DIR/setup.py" \
    "$OUTPUT_DIR/.openapi-generator-ignore" \
    "$OUTPUT_DIR/tox.ini" \
    "$OUTPUT_DIR/git_push.sh" \
    "$OUTPUT_DIR/requirements.txt" # This was deleted in a previous step, but good to include

# Using rsync to copy, which is generally robust. -a preserves attributes.
# Ensure trailing slash on source for rsync to copy contents.
# Removed --delete as rm -rf above should handle major cleaning.
rsync -av "$TEMP_OUTPUT_DIR/" "$OUTPUT_DIR/"

echo -e "${GREEN}✅ Sync complete.${NC}"

# Restore all backed up files
# This must happen AFTER rsync, as rsync would have overwritten these files
echo -e "${YELLOW}🔧 Restoring backed up files...${NC}"
if [ -d "$BACKUP_DIR" ]; then
    # Restore all files from backup directory
    find "$BACKUP_DIR" -type f | while read -r backup_file; do
        # Get relative path by removing backup directory prefix
        relative_path="${backup_file#"$BACKUP_DIR/"}"
        
        # Skip if this is a directory backup
        if [ -f "$backup_file" ]; then
            # Create directory if it doesn't exist
            mkdir -p "$(dirname "$relative_path")"
            cp "$backup_file" "$relative_path"
            echo "  ✅ Restored $relative_path"
        fi
    done
    
    # Also restore directories
    find "$BACKUP_DIR" -type d -mindepth 1 | while read -r backup_dir; do
        relative_path="${backup_dir#"$BACKUP_DIR/"}"
        if [ -d "$backup_dir" ] && [ ! -d "$relative_path" ]; then
            cp -r "$backup_dir" "$relative_path"
            echo "  ✅ Restored directory $relative_path"
        fi
    done
else
    echo "  ⚠️  No backup directory found"
fi

# Fix hardcoded author information in setup.py
echo -e "${YELLOW}🔧 Fixing author information in setup.py...${NC}"
if [ -f "$OUTPUT_DIR/setup.py" ]; then
    sed -i '' 's/author="Speechall Support"/author="Speechall"/' "$OUTPUT_DIR/setup.py"
    sed -i '' 's/author_email="team@openapitools.org"/author_email="info@actondon.com"/' "$OUTPUT_DIR/setup.py"
    echo "  ✅ Author information updated in setup.py"
fi

# Clean up temporary directory
echo -e "${YELLOW}🧹 Cleaning up temporary directory...${NC}"
rm -rf "$TEMP_OUTPUT_DIR"
echo "  ✅ Temporary directory cleaned up."

# Apply automatic fixes for known issues
echo ""
echo -e "${BLUE}🔧 Applying automatic fixes...${NC}"

# Fix TranscriptionResponse oneOf issue
if [ -f "fix_transcription_response.py" ]; then
    python3 fix_transcription_response.py
    if [ $? -eq 0 ]; then
        echo "  ✅ TranscriptionResponse oneOf fix applied"
    else
        echo -e "${YELLOW}  ⚠️  TranscriptionResponse fix failed - you may need to apply it manually${NC}"
    fi
else
    echo -e "${YELLOW}  ⚠️  fix_transcription_response.py not found - skipping automatic fix${NC}"
fi

# Fix Accept header to use */* instead of prioritizing JSON
if [ -f "fix_accept_header.py" ]; then
    python3 fix_accept_header.py
    if [ $? -eq 0 ]; then
        echo "  ✅ Accept header fix applied"
    else
        echo -e "${YELLOW}  ⚠️  Accept header fix failed - you may need to apply it manually${NC}"
    fi
else
    echo -e "${YELLOW}  ⚠️  fix_accept_header.py not found - skipping automatic fix${NC}"
fi

# Fix dual-format responses (JSON and text/plain based on Content-Type)
if [ -f "fix_dual_format_responses.py" ]; then
    python3 fix_dual_format_responses.py
    if [ $? -eq 0 ]; then
        echo "  ✅ Dual-format response fix applied"
    else
        echo -e "${YELLOW}  ⚠️  Dual-format response fix failed - you may need to apply it manually${NC}"
    fi
else
    echo -e "${YELLOW}  ⚠️  fix_dual_format_responses.py not found - skipping automatic fix${NC}"
fi

# Reinstall dependencies
echo ""
echo -e "${BLUE}📦 Updating dependencies...${NC}"
if command -v uv &> /dev/null; then
    uv sync
    echo -e "${GREEN}✅ Dependencies updated with uv${NC}"
else
    # pip install -r requirements.txt # requirements.txt is no longer used
    pip install . # Install from pyproject.toml / setup.py
    echo -e "${GREEN}✅ Dependencies updated with pip (from pyproject.toml)${NC}"
fi

# Clean up old backup if successful
echo ""
echo -e "${YELLOW}🧹 Cleaning up...${NC}"
if [ -d "$BACKUP_DIR" ]; then
    echo "Backup created at: $BACKUP_DIR"
    echo "You can safely delete it if everything looks good: rm -rf $BACKUP_DIR"
fi

echo ""
echo -e "${GREEN}🎉 Regeneration complete!${NC}"
echo ""
echo -e "${BLUE}📚 Next steps:${NC}"
echo "1. Test your examples: uv run python example_transcribe.py"
echo "2. Check for any new models or features in the updated client"
echo "3. Update your code if there are breaking changes"
echo "4. Delete the backup folder once you've verified everything works" 