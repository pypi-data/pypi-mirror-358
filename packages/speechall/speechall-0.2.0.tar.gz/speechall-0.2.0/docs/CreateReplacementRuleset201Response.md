# CreateReplacementRuleset201Response


## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **str** | The unique identifier (UUID) generated for this ruleset. Use this ID in the &#x60;ruleset_id&#x60; parameter of transcription requests. | 

## Example

```python
from speechall.models.create_replacement_ruleset201_response import CreateReplacementRuleset201Response

# TODO update the JSON string below
json = "{}"
# create an instance of CreateReplacementRuleset201Response from a JSON string
create_replacement_ruleset201_response_instance = CreateReplacementRuleset201Response.from_json(json)
# print the JSON string representation of the object
print CreateReplacementRuleset201Response.to_json()

# convert the object into a dict
create_replacement_ruleset201_response_dict = create_replacement_ruleset201_response_instance.to_dict()
# create an instance of CreateReplacementRuleset201Response from a dict
create_replacement_ruleset201_response_from_dict = CreateReplacementRuleset201Response.from_dict(create_replacement_ruleset201_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


