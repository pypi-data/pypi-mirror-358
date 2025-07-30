# TranscriptionWord

Represents a word in the transcription, providing time-coded chunks of the transcription.

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**start** | **float** | The start time of the word in seconds from the beginning of the audio. | 
**end** | **float** | The end time of the word in seconds from the beginning of the audio. | 
**word** | **str** | The transcribed word. | 
**speaker** | **str** | An identifier for the speaker of this word, present if diarization was enabled and successful. | [optional] 
**confidence** | **float** | The model&#39;s confidence score for the transcription of this word, typically between 0 and 1 (if provided by the model). | [optional] 

## Example

```python
from speechall.models.transcription_word import TranscriptionWord

# TODO update the JSON string below
json = "{}"
# create an instance of TranscriptionWord from a JSON string
transcription_word_instance = TranscriptionWord.from_json(json)
# print the JSON string representation of the object
print TranscriptionWord.to_json()

# convert the object into a dict
transcription_word_dict = transcription_word_instance.to_dict()
# create an instance of TranscriptionWord from a dict
transcription_word_from_dict = TranscriptionWord.from_dict(transcription_word_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


