# RegexGroupRule

Defines a replacement rule that uses regex capture groups to apply different replacements to different parts of the matched text.

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**kind** | **str** | Discriminator field identifying the rule type as &#39;regex_group&#39;. | 
**pattern** | **str** | The regular expression pattern containing capture groups &#x60;(...)&#x60;. The entire pattern must match for replacements to occur. | 
**group_replacements** | **Dict[str, str]** | An object where keys are capture group numbers (as strings, e.g., \&quot;1\&quot;, \&quot;2\&quot;) and values are the respective replacement strings for those groups. Groups not listed are kept as matched. The entire match is reconstructed using these replacements. | 
**flags** | **List[str]** | An array of flags to modify the regex behavior. | [optional] 

## Example

```python
from speechall.models.regex_group_rule import RegexGroupRule

# TODO update the JSON string below
json = "{}"
# create an instance of RegexGroupRule from a JSON string
regex_group_rule_instance = RegexGroupRule.from_json(json)
# print the JSON string representation of the object
print RegexGroupRule.to_json()

# convert the object into a dict
regex_group_rule_dict = regex_group_rule_instance.to_dict()
# create an instance of RegexGroupRule from a dict
regex_group_rule_from_dict = RegexGroupRule.from_dict(regex_group_rule_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


