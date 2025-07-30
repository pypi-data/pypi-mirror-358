# Speechall Python SDK Makefile

# Configuration
OPENAPI_SPEC_PATH = ../speechall-openapi/openapi.yaml
GENERATOR = python-pydantic-v1
OUTPUT_DIR = .

.PHONY: help install regenerate test example clean

# Default target
help:
	@echo "🎙️  Speechall Python SDK Commands"
	@echo "=================================="
	@echo ""
	@echo "📦 Setup:"
	@echo "  make install     - Install dependencies with uv"
	@echo ""
	@echo "🔄 Code generation:"
	@echo "  make regenerate  - Regenerate client from OpenAPI spec"
	@echo "  make force-regen - Force regenerate (skip validation)"
	@echo "  make fix         - Apply TranscriptionResponse oneOf fix"
	@echo ""
	@echo "🧪 Testing:"
	@echo "  make test        - Run tests"
	@echo "  make example     - Run example script"
	@echo ""
	@echo "🧹 Cleanup:"
	@echo "  make clean       - Clean generated files and cache"

# Install dependencies
install:
	@echo "📦 Installing dependencies..."
	uv sync

# Regenerate client from OpenAPI spec
regenerate:
	@echo "🔄 Regenerating OpenAPI client..."
	@if [ ! -f "$(OPENAPI_SPEC_PATH)" ]; then \
		echo "❌ Error: OpenAPI spec not found at $(OPENAPI_SPEC_PATH)"; \
		echo "Please ensure the speechall-openapi repository is cloned"; \
		exit 1; \
	fi
	./regenerate.sh

# Force regenerate (for development)
force-regen:
	@echo "🔄 Force regenerating OpenAPI client..."
	openapi-generator generate \
		-i $(OPENAPI_SPEC_PATH) \
		-g $(GENERATOR) \
		-o $(OUTPUT_DIR) \
		--skip-validate-spec
	@echo "⚠️  Note: This may overwrite custom files!"

# Apply TranscriptionResponse oneOf fix
fix:
	@echo "🔧 Applying TranscriptionResponse oneOf fix..."
	python3 fix_transcription_response.py

# Run tests
test:
	@echo "🧪 Running tests..."
	uv run python -m pytest test/ -v

# Run example script
example:
	@echo "🎤 Running example script..."
	@if [ -z "$$SPEECHALL_API_TOKEN" ]; then \
		echo "⚠️  Warning: SPEECHALL_API_TOKEN not set"; \
		echo "Set it with: export SPEECHALL_API_TOKEN='your-token'"; \
	fi
	uv run python example_transcribe.py

# Run simple example
simple:
	@echo "🎤 Running simple example..."
	@if [ -z "$$SPEECHALL_API_TOKEN" ]; then \
		echo "⚠️  Warning: SPEECHALL_API_TOKEN not set"; \
		echo "Set it with: export SPEECHALL_API_TOKEN='your-token'"; \
	fi
	uv run python simple_example.py

# Clean up generated files and cache
clean:
	@echo "🧹 Cleaning up..."
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -name "*.pyc" -delete 2>/dev/null || true
	rm -rf backup_*/ 2>/dev/null || true
	@echo "✅ Cleanup complete"

# Development helpers
check-spec:
	@echo "📋 Checking OpenAPI specification..."
	@if [ -f "$(OPENAPI_SPEC_PATH)" ]; then \
		echo "✅ OpenAPI spec found at $(OPENAPI_SPEC_PATH)"; \
		openapi-generator validate -i $(OPENAPI_SPEC_PATH) || echo "⚠️  Validation warnings found"; \
	else \
		echo "❌ OpenAPI spec not found at $(OPENAPI_SPEC_PATH)"; \
	fi

# List available models (requires API token)
list-models:
	@echo "📋 Listing available models..."
	@uv run python -c "import os; from openapi_client import *; from openapi_client.api.speech_to_text_api import SpeechToTextApi; config = Configuration(); config.access_token = os.getenv('SPEECHALL_API_TOKEN'); api = SpeechToTextApi(ApiClient(config)); [print(f'{m.model_id}: {m.display_name}') for m in api.list_speech_to_text_models()[:10]]" 2>/dev/null || echo "❌ Failed to list models (check your API token)" 