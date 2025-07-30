# ExactRule

Defines a replacement rule based on finding an exact string match.

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**kind** | **str** | Discriminator field identifying the rule type as &#39;exact&#39;. | 
**search** | **str** | The exact text string to search for within the transcription. | 
**replacement** | **str** | The text string to replace the found &#39;search&#39; text with. | 
**case_sensitive** | **bool** | If true, the search will match only if the case is identical. If false (default), the search ignores case. | [optional] [default to False]

## Example

```python
from speechall.models.exact_rule import ExactRule

# TODO update the JSON string below
json = "{}"
# create an instance of ExactRule from a JSON string
exact_rule_instance = ExactRule.from_json(json)
# print the JSON string representation of the object
print ExactRule.to_json()

# convert the object into a dict
exact_rule_dict = exact_rule_instance.to_dict()
# create an instance of ExactRule from a dict
exact_rule_from_dict = ExactRule.from_dict(exact_rule_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


