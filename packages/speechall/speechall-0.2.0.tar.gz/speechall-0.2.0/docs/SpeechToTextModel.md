# SpeechToTextModel

Describes an available speech-to-text model, its provider, capabilities, and characteristics.

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | [**TranscriptionModelIdentifier**](TranscriptionModelIdentifier.md) |  | 
**display_name** | **str** | A user-friendly name for the model. | 
**provider** | [**TranscriptionProvider**](TranscriptionProvider.md) |  | 
**description** | **str** | A brief description of the model, its intended use case, or version notes. | [optional] 
**cost_per_second_usd** | **float** | The cost per second of audio processed in USD. | [optional] 
**is_available** | **bool** | Indicates whether the model is currently available for use. | [default to True]
**supported_languages** | **List[str]** | A list of language codes (preferably BCP 47, e.g., \&quot;en-US\&quot;, \&quot;en-GB\&quot;, \&quot;es-ES\&quot;) supported by this model. May include &#x60;auto&#x60; if automatic language detection is supported across multiple languages within a single audio file.  | [optional] 
**punctuation** | **bool** | Indicates whether the model generally supports automatic punctuation insertion. | [optional] 
**diarization** | **bool** | Indicates whether the model generally supports speaker diarization (identifying different speakers). | [optional] 
**streamable** | **bool** | Indicates whether the model can be used for real-time streaming transcription via a WebSocket connection (if offered by Speechall). | [optional] 
**real_time_factor** | **float** | An approximate measure of processing speed for batch processing. Defined as (audio duration) / (processing time). A higher value means faster processing (e.g., RTF&#x3D;2 means it processes 1 second of audio in 0.5 seconds). May not be available for all models or streaming scenarios.  | [optional] 
**max_duration_seconds** | **float** | The maximum duration of a single audio file (in seconds) that the model can reliably process in one request. May vary by provider or plan. | [optional] 
**max_file_size_bytes** | **int** | The maximum size of a single audio file (in bytes) that can be uploaded for processing by this model. May vary by provider or plan. | [optional] 
**version** | **str** | The specific version identifier for the model. | [optional] 
**release_date** | **date** | The date when this specific version of the model was released or last updated. | [optional] 
**model_type** | **str** | The primary type or training domain of the model. Helps identify suitability for different audio types. | [optional] 
**accuracy_tier** | **str** | A general indication of the model&#39;s expected accuracy level relative to other models. Not a guaranteed metric. | [optional] 
**supported_audio_encodings** | **List[str]** | A list of audio encodings that this model supports or is optimized for (e.g., LINEAR16, FLAC, MP3, Opus). | [optional] 
**supported_sample_rates** | **List[int]** | A list of audio sample rates (in Hz) that this model supports or is optimized for. | [optional] 
**speaker_labels** | **bool** | Indicates whether the model can provide speaker labels for the transcription. | [optional] 
**word_timestamps** | **bool** | Indicates whether the model can provide timestamps for individual words. | [optional] 
**confidence_scores** | **bool** | Indicates whether the model provides confidence scores for the transcription or individual words. | [optional] 
**language_detection** | **bool** | Indicates whether the model supports automatic language detection for input audio. | [optional] 
**custom_vocabulary_support** | **bool** | Indicates if the model can leverage a custom vocabulary or language model adaptation. | [optional] 
**profanity_filtering** | **bool** | Indicates if the model supports filtering or masking of profanity. | [optional] 
**noise_reduction** | **bool** | Indicates if the model supports noise reduction. | [optional] 
**supports_srt** | **bool** | Indicates whether the model supports SRT subtitle format output. | [default to False]
**supports_vtt** | **bool** | Indicates whether the model supports VTT subtitle format output. | [default to False]
**voice_activity_detection** | **bool** | Indicates whether the model supports voice activity detection (VAD) to identify speech segments. | [optional] 

## Example

```python
from speechall.models.speech_to_text_model import SpeechToTextModel

# TODO update the JSON string below
json = "{}"
# create an instance of SpeechToTextModel from a JSON string
speech_to_text_model_instance = SpeechToTextModel.from_json(json)
# print the JSON string representation of the object
print SpeechToTextModel.to_json()

# convert the object into a dict
speech_to_text_model_dict = speech_to_text_model_instance.to_dict()
# create an instance of SpeechToTextModel from a dict
speech_to_text_model_from_dict = SpeechToTextModel.from_dict(speech_to_text_model_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


