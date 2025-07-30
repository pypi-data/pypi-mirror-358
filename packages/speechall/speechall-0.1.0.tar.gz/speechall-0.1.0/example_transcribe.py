#!/usr/bin/env python3
"""
Example script demonstrating how to use the Speechall API transcribe endpoint.

This script shows how to:
1. Set up the API client with authentication
2. Upload and transcribe an audio file
3. Use different models and options
4. Handle responses in different formats

Requirements:
- Set SPEECHALL_API_TOKEN environment variable with your API token
- Have an audio file to transcribe (or use the remote URL example)
"""

import os
import sys
from pathlib import Path
import json

from speechall import ApiClient, Configuration
from speechall.api.speech_to_text_api import SpeechToTextApi
from speechall.models.transcription_model_identifier import TranscriptionModelIdentifier
from speechall.models.transcript_language_code import TranscriptLanguageCode
from speechall.models.transcript_output_format import TranscriptOutputFormat
from speechall.models.remote_transcription_configuration import RemoteTranscriptionConfiguration
from speechall.exceptions import ApiException


def setup_client():
    """Set up the API client with authentication."""
    # Get API token from environment variable
    api_token = os.getenv('SPEECHALL_API_TOKEN')
    if not api_token:
        print("Error: Please set SPEECHALL_API_TOKEN environment variable")
        print("Export your API token like: export SPEECHALL_API_TOKEN='your-token-here'")
        sys.exit(1)
    
    # Configure the API client
    configuration = Configuration()
    configuration.access_token = api_token
    configuration.host = "https://api.speechall.com/v1"  # Default host
    
    # Create API client
    api_client = ApiClient(configuration)
    return SpeechToTextApi(api_client)


def list_available_models(api_instance):
    """List all available speech-to-text models."""
    try:
        print("📋 Available Speech-to-Text Models:")
        print("=" * 50)
        
        models = api_instance.list_speech_to_text_models()
        
        for model in models[:3]:  # Show first 3 models
            print(f"🤖 {model.id}")
            print(f"   Name: {model.display_name}")
            print(f"   Provider: {model.provider}")
            if hasattr(model, 'description') and model.description:
                print(f"   Description: {model.description}")
            print()
            
        if len(models) > 3:
            print(f"... and {len(models) - 3} more models available")
            
    except ApiException as e:
        print(f"❌ Error listing models: {e}")


def transcribe_local_file(api_instance, file_path, model_id="openai.whisper-1", language="en"):
    """Transcribe a local audio file."""
    try:
        print(f"🎤 Transcribing local file: {file_path}")
        print(f"   Model: {model_id}")
        print(f"   Language: {language}")
        print("-" * 50)
        
        # Check if file exists
        if not Path(file_path).exists():
            print(f"❌ File not found: {file_path}")
            return
        
        # Read audio file
        with open(file_path, 'rb') as audio_file:
            audio_data = audio_file.read()
        
        # Make transcription request
        result = api_instance.transcribe(
            model=TranscriptionModelIdentifier(model_id),
            body=audio_data,
            language=TranscriptLanguageCode(language),
            output_format=TranscriptOutputFormat.JSON,
            punctuation=True
        )
        
        print("✅ Transcription completed!")
        
        # Access the text directly
        transcribed_text = result.actual_instance.text
        print(f"📝 Transcribed Text:\n{transcribed_text}")
        
        # Also show the full result structure
        # print(f"\n🔍 Full Result:\n{json.dumps(result.to_dict(), indent=2, default=str)}")
        
    except FileNotFoundError:
        print(f"❌ File not found: {file_path}")
    except ApiException as e:
        print(f"❌ API Error: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")


def transcribe_remote_url(api_instance, audio_url, model_id="openai.whisper-1"):
    """Transcribe an audio file from a remote URL."""
    try:
        print(f"🌐 Transcribing remote URL: {audio_url}")
        print(f"   Model: {model_id}")
        print("-" * 50)
        
        # Create remote transcription configuration
        config = RemoteTranscriptionConfiguration(
            url=audio_url,
            model=TranscriptionModelIdentifier(model_id),
            language=TranscriptLanguageCode.EN,
            output_format=TranscriptOutputFormat.JSON,
            punctuation=True,
            timestamp_granularity="word"  # Get word-level timestamps
        )
        
        # Make transcription request
        result = api_instance.transcribe_remote(config)
        
        print("✅ Transcription completed!")
        print(f"📝 Result: {result}")
        
    except ApiException as e:
        print(f"❌ API Error: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")


def transcribe_with_advanced_features(api_instance, file_path):
    """Demonstrate advanced transcription features."""
    try:
        print(f"🚀 Advanced transcription with features:")
        print(f"   File: {file_path}")
        print(f"   Features: Diarization, Custom vocabulary, Smart formatting")
        print("-" * 50)
        
        if not Path(file_path).exists():
            print(f"❌ File not found: {file_path}")
            return
        
        with open(file_path, 'rb') as audio_file:
            audio_data = audio_file.read()
        
        # Use Deepgram model which supports advanced features
        result = api_instance.transcribe(
            model=TranscriptionModelIdentifier.ASSEMBLYAI_DOT_BEST,
            body=audio_data,
            language=TranscriptLanguageCode.EN,
            output_format=TranscriptOutputFormat.JSON,
            punctuation=True,
            timestamp_granularity="word",
            diarization=True,  # Speaker identification
            smart_format=True,  # Smart formatting for numbers, dates, etc.
            custom_vocabulary=["Speechall", "API", "Python", "SDK"],  # Custom words
            speakers_expected=2,  # Hint about number of speakers
        )
        
        print("✅ Advanced transcription completed!")
        print(f"📝 Result:\n{json.dumps(result.to_dict(), indent=2, default=str)}")
        
    except ApiException as e:
        print(f"❌ API Error: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")


def main():
    """Main function demonstrating different transcription scenarios."""
    print("🎙️  Speechall Python SDK - Transcription Examples")
    print("=" * 60)
    
    # Set up API client
    api_instance = setup_client()
    
    # Example 1: List available models
    # list_available_models(api_instance)
    
    # Example 2: Transcribe a local file (you'll need to provide your own audio file)
    local_audio_file = os.path.expanduser("~/Downloads/how-dictop-works.mp3")  # Replace with your audio file path
    if Path(local_audio_file).exists():
        transcribe_local_file(api_instance, local_audio_file)
    else:
        print(f"ℹ️  Skipping local file example - {local_audio_file} not found")
    
    # Example 3: Transcribe from remote URL (example URL - replace with real audio URL)
    sample_audio_url = "https://example.com/sample-audio.wav"
    print(f"ℹ️  Remote URL example (replace with real audio URL): {sample_audio_url}")
    # Uncomment the following line to test with a real audio URL:
    # transcribe_remote_url(api_instance, sample_audio_url)
    
    # Example 4: Advanced features (if you have a local audio file)
    # if Path(local_audio_file).exists():
    #     transcribe_with_advanced_features(api_instance, local_audio_file)
    
    print("\n✨ Examples completed!")
    print("\n📚 Next steps:")
    print("1. Set your SPEECHALL_API_TOKEN environment variable")
    print("2. Replace 'example_audio.wav' with your actual audio file path")
    print("3. Customize the models and parameters for your use case")
    print("4. Check the API documentation for more advanced features")


if __name__ == "__main__":
    main() 