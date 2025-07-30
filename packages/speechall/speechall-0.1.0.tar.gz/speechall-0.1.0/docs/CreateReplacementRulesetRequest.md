# CreateReplacementRulesetRequest


## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**name** | **str** | A user-defined name for this ruleset for easier identification. | 
**rules** | [**List[ReplacementRule]**](ReplacementRule.md) | An ordered array of replacement rules. Rules are applied in the order they appear in this list. See the &#x60;ReplacementRule&#x60; schema for different rule types (exact, regex, regex_group). | 

## Example

```python
from speechall.models.create_replacement_ruleset_request import CreateReplacementRulesetRequest

# TODO update the JSON string below
json = "{}"
# create an instance of CreateReplacementRulesetRequest from a JSON string
create_replacement_ruleset_request_instance = CreateReplacementRulesetRequest.from_json(json)
# print the JSON string representation of the object
print CreateReplacementRulesetRequest.to_json()

# convert the object into a dict
create_replacement_ruleset_request_dict = create_replacement_ruleset_request_instance.to_dict()
# create an instance of CreateReplacementRulesetRequest from a dict
create_replacement_ruleset_request_from_dict = CreateReplacementRulesetRequest.from_dict(create_replacement_ruleset_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


