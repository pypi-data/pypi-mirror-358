# RegexRule

Defines a replacement rule based on matching a regular expression pattern.

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**kind** | **str** | Discriminator field identifying the rule type as &#39;regex&#39;. | 
**pattern** | **str** | The regular expression pattern to search for. Uses standard regex syntax (implementation specific, often PCRE-like). Remember to escape special characters if needed (e.g., &#x60;\\\\.&#x60; for a literal dot). | 
**replacement** | **str** | The replacement text. Can include backreferences to capture groups from the pattern, like &#x60;$1&#x60;, &#x60;$2&#x60;, etc. A literal &#x60;$&#x60; should be escaped (e.g., &#x60;$$&#x60;). | 
**flags** | **List[str]** | An array of flags to modify the regex behavior (e.g., &#39;i&#39; for case-insensitivity). | [optional] 

## Example

```python
from speechall.models.regex_rule import RegexRule

# TODO update the JSON string below
json = "{}"
# create an instance of RegexRule from a JSON string
regex_rule_instance = RegexRule.from_json(json)
# print the JSON string representation of the object
print RegexRule.to_json()

# convert the object into a dict
regex_rule_dict = regex_rule_instance.to_dict()
# create an instance of RegexRule from a dict
regex_rule_from_dict = RegexRule.from_dict(regex_rule_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


