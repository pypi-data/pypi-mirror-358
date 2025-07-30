# speechall.ReplacementRulesApi

All URIs are relative to *https://api.speechall.com/v1*

Method | HTTP request | Description
------------- | ------------- | -------------
[**create_replacement_ruleset**](ReplacementRulesApi.md#create_replacement_ruleset) | **POST** /replacement-rulesets | Create a reusable set of text replacement rules.


# **create_replacement_ruleset**
> CreateReplacementRuleset201Response create_replacement_ruleset(create_replacement_ruleset_request)

Create a reusable set of text replacement rules.

Defines a named set of replacement rules (exact match, regex) that can be applied during transcription requests using its `ruleset_id`.
Rules within a set are applied sequentially to the transcription text.


### Example

* Bearer (API Key) Authentication (bearerAuth):
```python
import time
import os
import speechall
from speechall.models.create_replacement_ruleset201_response import CreateReplacementRuleset201Response
from speechall.models.create_replacement_ruleset_request import CreateReplacementRulesetRequest
from speechall.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to https://api.speechall.com/v1
# See configuration.py for a list of all supported configuration parameters.
configuration = speechall.Configuration(
    host = "https://api.speechall.com/v1"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure Bearer authorization (API Key): bearerAuth
configuration = speechall.Configuration(
    access_token = os.environ["BEARER_TOKEN"]
)

# Enter a context with an instance of the API client
with speechall.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = speechall.ReplacementRulesApi(api_client)
    create_replacement_ruleset_request = {"name":"Acme Corp Corrections","rules":[{"kind":"exact","search":"speechal","replacement":"Speechall","caseSensitive":false},{"kind":"regex","pattern":"\\b(\\d{3})-(\\d{2})-(\\d{4})\\b","replacement":"[REDACTED SSN]","flags":["i"]}]} # CreateReplacementRulesetRequest | JSON object containing the name for the ruleset and an array of replacement rule objects.

    try:
        # Create a reusable set of text replacement rules.
        api_response = api_instance.create_replacement_ruleset(create_replacement_ruleset_request)
        print("The response of ReplacementRulesApi->create_replacement_ruleset:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ReplacementRulesApi->create_replacement_ruleset: %s\n" % e)
```



### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **create_replacement_ruleset_request** | [**CreateReplacementRulesetRequest**](CreateReplacementRulesetRequest.md)| JSON object containing the name for the ruleset and an array of replacement rule objects. | 

### Return type

[**CreateReplacementRuleset201Response**](CreateReplacementRuleset201Response.md)

### Authorization

[bearerAuth](../README.md#bearerAuth)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json, text/plain

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**201** | Ruleset created successfully. The response body contains the unique ID assigned to the new ruleset. |  -  |
**400** | Bad Request - The request was malformed or contained invalid parameters (e.g., invalid language code, missing required field, unsupported option). The response body provides details. |  -  |
**401** | Unauthorized - Authentication failed. The API key is missing, invalid, or expired. |  -  |
**402** | Payment Required - There is no credit left on your account. |  -  |
**429** | Too Many Requests - The client has exceeded the rate limit for API requests. Check the &#x60;Retry-After&#x60; header for guidance on when to retry. |  * Retry-After - The recommended number of seconds to wait before making another request. <br>  |
**500** | Internal Server Error - An unexpected error occurred on the server side while processing the request. Retrying the request later might succeed. If the problem persists, contact support. |  -  |
**503** | Service Unavailable - The server is temporarily unable to handle the request, possibly due to maintenance or overload. Try again later. |  -  |
**504** | Gateway Timeout - The server, while acting as a gateway or proxy, did not receive a timely response from an upstream server (e.g., the underlying STT provider). This might be a temporary issue with the provider. |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

