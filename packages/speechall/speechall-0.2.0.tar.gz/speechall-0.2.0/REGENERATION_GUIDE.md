# OpenAPI Client Regeneration Guide

This guide explains how to regenerate the Speechall Python SDK when the OpenAPI specification changes.

## Quick Start

### Method 1: Using the Script (Recommended)
```bash
./regenerate.sh
```

### Method 2: Using Make
```bash
make regenerate
```

### Method 3: Manual Command
```bash
openapi-generator generate -i ../speechall-openapi/openapi.yaml -g python-pydantic-v1 -o .
```

## Prerequisites

### 1. OpenAPI Generator
Install the OpenAPI Generator:

```bash
# Using npm (recommended)
npm install @openapitools/openapi-generator-cli -g

# Using brew (macOS)
brew install openapi-generator

# Using docker (alternative)
# See: https://openapi-generator.tech/docs/installation
```

### 2. OpenAPI Specification
Ensure the OpenAPI specification is available at:
```
../speechall-openapi/openapi.yaml
```

Or clone the repository:
```bash
cd ..
git clone https://github.com/speechall/speechall-openapi.git
cd speechall-python-sdk
```

## Protected Files

The following files are protected from regeneration and will be preserved:

### Custom Code Files
- `example_transcribe.py` - Comprehensive example script
- `simple_example.py` - Simple example script  
- `EXAMPLE_README.md` - Examples documentation
- `REGENERATION_GUIDE.md` - This guide

### Configuration Files
- `pyproject.toml` - Modified for uv package management
- `uv.lock` - Dependency lock file
- `.venv/` - Virtual environment
- `Makefile` - Build automation
- `regenerate.sh` - Regeneration script

### Automatic Fix Scripts
- `fix_transcription_response.py` - Automatically fixes the oneOf validation issue in TranscriptionResponse

### Generated Files (Will Be Regenerated)
- `openapi_client/` - All client code
- `docs/` - API documentation
- `test/` - Generated test files
- `requirements.txt` - Requirements file
- `setup.py` - Setup script
- `README.md` - Generated README

## Regeneration Workflow

### Step 1: Backup Custom Changes
The regeneration script automatically creates backups:
```bash
backup_YYYYMMDD_HHMMSS/
├── example_transcribe.py
├── simple_example.py
├── EXAMPLE_README.md
└── pyproject.toml
```

### Step 2: Regenerate Client Code
The script runs:
```bash
openapi-generator generate \
    -i ../speechall-openapi/openapi.yaml \
    -g python-pydantic-v1 \
    -o . \
    --skip-validate-spec
```

### Step 3: Restore Custom Configuration
- Restores the custom `pyproject.toml` for uv compatibility
- Keeps example scripts intact
- Preserves custom documentation

### Step 3.5: Apply Automatic Fixes
- Runs `fix_transcription_response.py` to automatically fix the oneOf validation issue
- Ensures the generated code works correctly without manual intervention

### Step 4: Update Dependencies
```bash
uv sync  # or pip install -r requirements.txt
```

## Advanced Usage

### Force Regeneration
To regenerate without safeguards (⚠️ **USE WITH CAUTION**):
```bash
make force-regen
```

### Custom OpenAPI Spec Location
Edit the script or Makefile to change the spec path:
```bash
# In regenerate.sh or Makefile
OPENAPI_SPEC_PATH="path/to/your/openapi.yaml"
```

### Different Generator
To use a different generator:
```bash
openapi-generator generate \
    -i ../speechall-openapi/openapi.yaml \
    -g python \
    -o .
```

Available Python generators:
- `python` - Standard Python client
- `python-pydantic-v1` - Pydantic v1 models (current)
- `python-fastapi` - FastAPI compatible
- `python-flask` - Flask compatible

## Testing After Regeneration

### 1. Verify Installation
```bash
uv sync
```

### 2. Test Imports
```bash
uv run python -c "from openapi_client.api.speech_to_text_api import SpeechToTextApi; print('✅ Imports work!')"
```

### 3. Run Examples
```bash
# Set your API token first
export SPEECHALL_API_TOKEN="your-token-here"

# Run examples
make example
make simple
```

### 4. Check for Breaking Changes
Review the generated code for:
- New or removed models
- Changed method signatures
- New API endpoints
- Deprecated features

## Common Issues & Solutions

### Issue: "openapi-generator command not found"
**Solution:** Install OpenAPI Generator:
```bash
npm install @openapitools/openapi-generator-cli -g
```

### Issue: "OpenAPI spec not found"
**Solution:** Ensure the spec file exists:
```bash
ls -la ../speechall-openapi/openapi.yaml
```

### Issue: Custom pyproject.toml overwritten
**Solution:** The regeneration script should handle this automatically. If not:
```bash
# Restore from backup
cp backup_*/pyproject.toml ./pyproject.toml
uv sync
```

### Issue: Import errors after regeneration
**Solution:** Reinstall dependencies:
```bash
uv sync
# or
pip install -r requirements.txt
```

### Issue: "Multiple matches found when deserializing TranscriptionResponse"
**Problem:** When one model is a superset of another (e.g., `TranscriptionDetailed` contains all fields of `TranscriptionOnlyText` plus optional ones), the generated oneOf validation fails because both schemas match.

**Automatic Solution:** The regeneration script now automatically applies the fix via `fix_transcription_response.py`. No manual intervention required!

**Manual Solution (if automatic fix fails):** Run the fix script manually:
```bash
python3 fix_transcription_response.py
```

The fix script:
- Detects if the fix is already applied to avoid duplicate changes
- Modifies the `from_json` method to try the more specific schema first
- Updates the validator to prevent "multiple matches" errors
- Is preserved during regeneration (listed in `.openapi-generator-ignore`)

## Best Practices

### 1. Always Use Version Control
Commit your changes before regenerating:
```bash
git add .
git commit -m "Before regenerating OpenAPI client"
./regenerate.sh
```

### 2. Test Thoroughly
After regeneration, test all your custom code:
- Run example scripts
- Test API calls
- Verify model compatibility

### 3. Update Examples
If new features are added to the API:
- Update example scripts to showcase new capabilities
- Add new models to the examples
- Update documentation

### 4. Handle Breaking Changes
- Check the API changelog
- Update method calls if signatures changed
- Add migration notes for users

## Automation Options

### GitHub Actions
Create `.github/workflows/regenerate.yml`:
```yaml
name: Regenerate Client
on:
  repository_dispatch:
    types: [openapi-updated]
  
jobs:
  regenerate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '18'
      - name: Install OpenAPI Generator
        run: npm install @openapitools/openapi-generator-cli -g
      - name: Regenerate Client
        run: ./regenerate.sh
      - name: Create Pull Request
        # Use a PR creation action
```

### Pre-commit Hook
Add to `.git/hooks/pre-commit`:
```bash
#!/bin/bash
# Check if OpenAPI spec has changed
if git diff --cached --name-only | grep -q "../speechall-openapi/openapi.yaml"; then
    echo "⚠️  OpenAPI spec changed. Consider regenerating the client."
    echo "Run: ./regenerate.sh"
fi
```

## Support

If you encounter issues with regeneration:
1. Check this guide for common solutions
2. Review the OpenAPI Generator documentation
3. Contact the Speechall team for API-specific questions 