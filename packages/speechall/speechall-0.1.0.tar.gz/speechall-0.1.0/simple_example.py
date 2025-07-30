#!/usr/bin/env python3
"""
Simple example of using the Speechall API to transcribe audio.

Set your API token: export SPEECHALL_API_TOKEN="your-token-here"
"""

import os
from speechall import ApiClient, Configuration
from speechall.api.speech_to_text_api import SpeechToTextApi
from speechall.models.transcription_model_identifier import TranscriptionModelIdentifier
from speechall.models.transcript_language_code import TranscriptLanguageCode

# Set up the API client
configuration = Configuration()
configuration.access_token = os.getenv('SPEECHALL_API_TOKEN')
configuration.host = "https://api.speechall.com/v1"

api_client = ApiClient(configuration)
api_instance = SpeechToTextApi(api_client)

# Example: List available models
try:
    print("Available models:")
    models = api_instance.list_speech_to_text_models()
    for model in models[:5]:  # Show first 5
        print(f"- {model.model_id}: {model.display_name}")
except Exception as e:
    print(f"Error listing models: {e}")

# Example: Transcribe audio file
audio_file_path = "your_audio_file.wav"  # Replace with your audio file

if os.path.exists(audio_file_path):
    try:
        with open(audio_file_path, 'rb') as f:
            result = api_instance.transcribe(
                model=TranscriptionModelIdentifier.OPENAI_DOT_WHISPER_MINUS_1,
                body=f.read(),
                language=TranscriptLanguageCode.EN
            )
        print(f"Transcription: {result}")
    except Exception as e:
        print(f"Error transcribing: {e}")
else:
    print(f"Audio file {audio_file_path} not found. Please provide a valid audio file.") 