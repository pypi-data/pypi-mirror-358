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
# configuration.host = "https://api.speechall.com/v1"
configuration.host = "http://127.0.0.1:8080/v1"

api_client = ApiClient(configuration)
api_instance = SpeechToTextApi(api_client)

# Example: Transcribe audio file
audio_file_path = os.path.expanduser("~/Downloads/how-dictop-works.mp3")  # Replace with your audio file path

if os.path.exists(audio_file_path):
    try:
        with open(audio_file_path, 'rb') as f:
            result = api_instance.transcribe(
                model=TranscriptionModelIdentifier.OPENAI_DOT_WHISPER_MINUS_1,
                body=f.read()
            )
        print(f"Transcription: {result.text}")
    except Exception as e:
        print(f"Error transcribing: {e}")
else:
    print(f"Audio file {audio_file_path} not found. Please provide a valid audio file.") 