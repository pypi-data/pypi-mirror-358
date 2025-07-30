# RemoteTranscriptionConfiguration

Configuration options for transcribing audio specified by a remote URL via the `/transcribe-remote` endpoint.

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**model** | [**TranscriptionModelIdentifier**](TranscriptionModelIdentifier.md) |  | 
**language** | [**TranscriptLanguageCode**](TranscriptLanguageCode.md) |  | [optional] 
**output_format** | [**TranscriptOutputFormat**](TranscriptOutputFormat.md) |  | [optional] 
**ruleset_id** | **str** | The unique identifier (UUID) of a pre-defined replacement ruleset to apply to the final transcription text. | [optional] 
**punctuation** | **bool** | Whether to add punctuation. Support varies by model (e.g., Deepgram, AssemblyAI). Defaults to &#x60;true&#x60;. | [optional] [default to True]
**timestamp_granularity** | **str** | Level of timestamp detail (&#x60;word&#x60; or &#x60;segment&#x60;). Defaults to &#x60;segment&#x60;. | [optional] [default to 'segment']
**diarization** | **bool** | Enable speaker diarization. Defaults to &#x60;false&#x60;. | [optional] [default to False]
**initial_prompt** | **str** | Optional text prompt to guide the transcription model. Support varies (e.g., OpenAI). | [optional] 
**temperature** | **float** | Controls output randomness for supported models (e.g., OpenAI). Value between 0 and 1. | [optional] 
**smart_format** | **bool** | Enable provider-specific smart formatting (e.g., Deepgram). Defaults vary. | [optional] 
**speakers_expected** | **int** | Hint for the number of expected speakers for diarization (e.g., RevAI, Deepgram). | [optional] 
**custom_vocabulary** | **List[str]** | List of custom words/phrases to improve recognition (e.g., Deepgram, AssemblyAI). | [optional] 
**file_url** | **str** | The publicly accessible URL of the audio file to transcribe. The API server must be able to fetch the audio from this URL. | 
**replacement_ruleset** | [**List[ReplacementRule]**](ReplacementRule.md) | An array of replacement rules to be applied directly to this transcription request, in order. This allows defining rules inline instead of (or in addition to) using a pre-saved &#x60;ruleset_id&#x60;. | [optional] 

## Example

```python
from speechall.models.remote_transcription_configuration import RemoteTranscriptionConfiguration

# TODO update the JSON string below
json = "{}"
# create an instance of RemoteTranscriptionConfiguration from a JSON string
remote_transcription_configuration_instance = RemoteTranscriptionConfiguration.from_json(json)
# print the JSON string representation of the object
print RemoteTranscriptionConfiguration.to_json()

# convert the object into a dict
remote_transcription_configuration_dict = remote_transcription_configuration_instance.to_dict()
# create an instance of RemoteTranscriptionConfiguration from a dict
remote_transcription_configuration_from_dict = RemoteTranscriptionConfiguration.from_dict(remote_transcription_configuration_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


