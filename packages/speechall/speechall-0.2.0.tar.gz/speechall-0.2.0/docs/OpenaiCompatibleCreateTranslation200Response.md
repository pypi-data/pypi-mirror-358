# OpenaiCompatibleCreateTranslation200Response


## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**language** | **str** | The language of the output translation (always &#x60;english&#x60;). | 
**duration** | **str** | The duration of the input audio. | 
**text** | **str** |  | 
**segments** | [**List[OpenAITranscriptionSegment]**](OpenAITranscriptionSegment.md) | Segments of the translated text and their corresponding details. | [optional] 

## Example

```python
from speechall.models.openai_compatible_create_translation200_response import OpenaiCompatibleCreateTranslation200Response

# TODO update the JSON string below
json = "{}"
# create an instance of OpenaiCompatibleCreateTranslation200Response from a JSON string
openai_compatible_create_translation200_response_instance = OpenaiCompatibleCreateTranslation200Response.from_json(json)
# print the JSON string representation of the object
print OpenaiCompatibleCreateTranslation200Response.to_json()

# convert the object into a dict
openai_compatible_create_translation200_response_dict = openai_compatible_create_translation200_response_instance.to_dict()
# create an instance of OpenaiCompatibleCreateTranslation200Response from a dict
openai_compatible_create_translation200_response_from_dict = OpenaiCompatibleCreateTranslation200Response.from_dict(openai_compatible_create_translation200_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


