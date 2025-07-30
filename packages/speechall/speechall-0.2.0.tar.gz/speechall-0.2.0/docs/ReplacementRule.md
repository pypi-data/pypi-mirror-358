# ReplacementRule

Defines a single rule for finding and replacing text in a transcription. Use one of the specific rule types (`ExactRule`, `RegexRule`, `RegexGroupRule`). The `kind` property acts as a discriminator.

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**kind** | **str** | Discriminator field identifying the rule type as &#39;regex_group&#39;. | 
**search** | **str** | The exact text string to search for within the transcription. | 
**replacement** | **str** | The replacement text. Can include backreferences to capture groups from the pattern, like &#x60;$1&#x60;, &#x60;$2&#x60;, etc. A literal &#x60;$&#x60; should be escaped (e.g., &#x60;$$&#x60;). | 
**case_sensitive** | **bool** | If true, the search will match only if the case is identical. If false (default), the search ignores case. | [optional] [default to False]
**pattern** | **str** | The regular expression pattern containing capture groups &#x60;(...)&#x60;. The entire pattern must match for replacements to occur. | 
**flags** | **List[str]** | An array of flags to modify the regex behavior. | [optional] 
**group_replacements** | **Dict[str, str]** | An object where keys are capture group numbers (as strings, e.g., \&quot;1\&quot;, \&quot;2\&quot;) and values are the respective replacement strings for those groups. Groups not listed are kept as matched. The entire match is reconstructed using these replacements. | 

## Example

```python
from speechall.models.replacement_rule import ReplacementRule

# TODO update the JSON string below
json = "{}"
# create an instance of ReplacementRule from a JSON string
replacement_rule_instance = ReplacementRule.from_json(json)
# print the JSON string representation of the object
print ReplacementRule.to_json()

# convert the object into a dict
replacement_rule_dict = replacement_rule_instance.to_dict()
# create an instance of ReplacementRule from a dict
replacement_rule_from_dict = ReplacementRule.from_dict(replacement_rule_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


