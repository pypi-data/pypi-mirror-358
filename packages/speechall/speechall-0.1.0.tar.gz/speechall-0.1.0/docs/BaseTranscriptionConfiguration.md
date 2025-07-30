# BaseTranscriptionConfiguration

Common configuration options for transcription, applicable to both direct uploads and remote URLs.

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

## Example

```python
from speechall.models.base_transcription_configuration import BaseTranscriptionConfiguration

# TODO update the JSON string below
json = "{}"
# create an instance of BaseTranscriptionConfiguration from a JSON string
base_transcription_configuration_instance = BaseTranscriptionConfiguration.from_json(json)
# print the JSON string representation of the object
print BaseTranscriptionConfiguration.to_json()

# convert the object into a dict
base_transcription_configuration_dict = base_transcription_configuration_instance.to_dict()
# create an instance of BaseTranscriptionConfiguration from a dict
base_transcription_configuration_from_dict = BaseTranscriptionConfiguration.from_dict(base_transcription_configuration_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


