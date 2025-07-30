# OpenaiCompatibleCreateTranscription200Response


## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**language** | **str** | The language of the input audio. | 
**duration** | **float** | The duration of the input audio. | 
**text** | **str** | The transcribed text. | 
**words** | [**List[OpenAITranscriptionWord]**](OpenAITranscriptionWord.md) | Extracted words and their corresponding timestamps. | [optional] 
**segments** | [**List[OpenAITranscriptionSegment]**](OpenAITranscriptionSegment.md) | Segments of the transcribed text and their corresponding details. | [optional] 

## Example

```python
from speechall.models.openai_compatible_create_transcription200_response import OpenaiCompatibleCreateTranscription200Response

# TODO update the JSON string below
json = "{}"
# create an instance of OpenaiCompatibleCreateTranscription200Response from a JSON string
openai_compatible_create_transcription200_response_instance = OpenaiCompatibleCreateTranscription200Response.from_json(json)
# print the JSON string representation of the object
print OpenaiCompatibleCreateTranscription200Response.to_json()

# convert the object into a dict
openai_compatible_create_transcription200_response_dict = openai_compatible_create_transcription200_response_instance.to_dict()
# create an instance of OpenaiCompatibleCreateTranscription200Response from a dict
openai_compatible_create_transcription200_response_from_dict = OpenaiCompatibleCreateTranscription200Response.from_dict(openai_compatible_create_transcription200_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


