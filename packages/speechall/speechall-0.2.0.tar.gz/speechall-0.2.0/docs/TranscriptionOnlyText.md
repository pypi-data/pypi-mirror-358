# TranscriptionOnlyText

A simplified JSON response format containing only the transcription ID and the full transcribed text. Returned when `output_format` is `json_text`.

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **str** | A unique identifier for the transcription job/request. | 
**text** | **str** | The full transcribed text as a single string. | 

## Example

```python
from speechall.models.transcription_only_text import TranscriptionOnlyText

# TODO update the JSON string below
json = "{}"
# create an instance of TranscriptionOnlyText from a JSON string
transcription_only_text_instance = TranscriptionOnlyText.from_json(json)
# print the JSON string representation of the object
print TranscriptionOnlyText.to_json()

# convert the object into a dict
transcription_only_text_dict = transcription_only_text_instance.to_dict()
# create an instance of TranscriptionOnlyText from a dict
transcription_only_text_from_dict = TranscriptionOnlyText.from_dict(transcription_only_text_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


