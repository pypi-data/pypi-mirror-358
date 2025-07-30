# TranscriptionDetailed

A detailed JSON response format containing the full text, detected language, duration, individual timed segments, and potentially speaker labels and provider-specific metadata. Returned when `output_format` is `json`.

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **str** | A unique identifier for the transcription job/request. | 
**text** | **str** | The full transcribed text as a single string. | 
**language** | **str** | The detected or specified language of the audio (ISO 639-1 code). | [optional] 
**duration** | **float** | The total duration of the processed audio file in seconds. **Deprecated**: This property may be removed in future versions as duration analysis might occur asynchronously. Rely on segment end times for duration information if needed.  | [optional] 
**segments** | [**List[TranscriptionSegment]**](TranscriptionSegment.md) | An array of transcribed segments, providing time-coded chunks of the transcription. The level of detail (word vs. segment timestamps) depends on the &#x60;timestamp_granularity&#x60; request parameter. May include speaker labels if diarization was enabled. | [optional] 
**words** | [**List[TranscriptionWord]**](TranscriptionWord.md) | An array of transcribed words, providing time-coded chunks of the transcription. The level of detail (word vs. segment timestamps) depends on the &#x60;timestamp_granularity&#x60; request parameter. May include speaker labels if diarization was enabled. | [optional] 
**provider_metadata** | **Dict[str, object]** | An optional object containing additional metadata returned directly from the underlying STT provider. The structure of this object is provider-dependent. | [optional] 

## Example

```python
from speechall.models.transcription_detailed import TranscriptionDetailed

# TODO update the JSON string below
json = "{}"
# create an instance of TranscriptionDetailed from a JSON string
transcription_detailed_instance = TranscriptionDetailed.from_json(json)
# print the JSON string representation of the object
print TranscriptionDetailed.to_json()

# convert the object into a dict
transcription_detailed_dict = transcription_detailed_instance.to_dict()
# create an instance of TranscriptionDetailed from a dict
transcription_detailed_from_dict = TranscriptionDetailed.from_dict(transcription_detailed_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


