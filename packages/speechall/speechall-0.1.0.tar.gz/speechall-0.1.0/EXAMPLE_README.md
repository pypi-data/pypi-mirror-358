# Speechall Python SDK Example

This repository contains a Python SDK for the Speechall API, generated using OpenAPI Generator, with example scripts demonstrating how to use the transcribe endpoint.

## Quick Start

### 1. Install Dependencies

Make sure you have `uv` installed, then run:

```bash
uv sync
```

### 2. Set Up Authentication

Set your Speechall API token as an environment variable:

```bash
export SPEECHALL_API_TOKEN="your-api-token-here"
```

### 3. Run the Example

```bash
uv run python example_transcribe.py
```

## Features Demonstrated

The example script shows how to:

- **List Available Models**: Get all available speech-to-text models and their capabilities
- **Transcribe Local Files**: Upload and transcribe audio files from your local machine
- **Transcribe Remote URLs**: Transcribe audio files directly from URLs
- **Advanced Features**: Use speaker diarization, custom vocabulary, and smart formatting

## Available Models

The SDK supports numerous speech-to-text providers and models, including:

- **OpenAI**: `openai.whisper-1`, `openai.gpt-4o-transcribe`
- **Deepgram**: `deepgram.nova-2`, `deepgram.nova-3`, `deepgram.whisper-large`
- **AssemblyAI**: `assemblyai.best`, `assemblyai.nano`
- **Google**: `google.enhanced`, `google.standard`
- **Azure**: `azure.standard`
- **Groq**: `groq.whisper-large-v3`, `groq.whisper-large-v3-turbo`
- And many more!

## Example Usage

### Basic Transcription

```python
from openapi_client import ApiClient, Configuration
from openapi_client.api.speech_to_text_api import SpeechToTextApi
from openapi_client.models.transcription_model_identifier import TranscriptionModelIdentifier

# Set up client
configuration = Configuration()
configuration.access_token = "your-api-token"
api_client = ApiClient(configuration)
api_instance = SpeechToTextApi(api_client)

# Transcribe audio file
with open("audio.wav", "rb") as f:
    result = api_instance.transcribe(
        model=TranscriptionModelIdentifier.OPENAI_DOT_WHISPER_MINUS_1,
        body=f.read(),
        language="en"
    )
    print(result)
```

### Advanced Features

```python
# Use advanced features like diarization and custom vocabulary
result = api_instance.transcribe(
    model=TranscriptionModelIdentifier.DEEPGRAM_DOT_NOVA_MINUS_2,
    body=audio_data,
    language="en",
    output_format="verbose_json",
    diarization=True,
    custom_vocabulary=["technical", "terms"],
    speakers_expected=2
)
```

## Supported Audio Formats

The API supports various audio formats including:
- WAV
- MP3
- FLAC
- OGG
- M4A
- And more (depends on the selected model/provider)

## Error Handling

The SDK includes proper error handling for common scenarios:

```python
from openapi_client.exceptions import ApiException

try:
    result = api_instance.transcribe(...)
except ApiException as e:
    print(f"API Error: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
```

## Next Steps

1. Get your API token from the Speechall dashboard
2. Replace the example audio file path with your actual audio file
3. Experiment with different models and parameters
4. Check the [Speechall API documentation](https://docs.speechall.com) for more details

## Support

For support and questions:
- Check the [Speechall documentation](https://docs.speechall.com)
- Contact support at team@speechall.com 