# TranscriptionSegment

Represents a time-coded segment of the transcription, typically corresponding to a phrase, sentence, or speaker turn.

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**start** | **float** | The start time of the segment in seconds from the beginning of the audio. | [optional] 
**end** | **float** | The end time of the segment in seconds from the beginning of the audio. | [optional] 
**text** | **str** | The transcribed text content of this segment. | [optional] 
**speaker** | **str** | An identifier for the speaker of this segment, present if diarization was enabled and successful. | [optional] 
**confidence** | **float** | The model&#39;s confidence score for the transcription of this segment, typically between 0 and 1 (if provided by the model). | [optional] 

## Example

```python
from speechall.models.transcription_segment import TranscriptionSegment

# TODO update the JSON string below
json = "{}"
# create an instance of TranscriptionSegment from a JSON string
transcription_segment_instance = TranscriptionSegment.from_json(json)
# print the JSON string representation of the object
print TranscriptionSegment.to_json()

# convert the object into a dict
transcription_segment_dict = transcription_segment_instance.to_dict()
# create an instance of TranscriptionSegment from a dict
transcription_segment_from_dict = TranscriptionSegment.from_dict(transcription_segment_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


