# step-rest-client
<h1>About</h1><p>The STEP REST API V2 provides read and write access to a set of core STEP objects using the HTTP operations GET, PUT, POST, PATCH and DELETE.</p><h1>Resource Representation</h1><p>With the exception of a few resource operations for retrieving and uploading binary data, all request and response bodies are JSON, compliant with the schema documented here.</p><h1>Context and Workspace</h1><p>All requests are handled in a specific STEP context and workspace and both can be specified via query parameters available for all resource operations. A context must always be specified while requests per default will be handled in the &quot;Main&quot; workspace.</p><h1>Polymorphism</h1><p>In STEP, attributes, reference types and data container types can all be either single- or multivalued. The STEP REST API V2 uses polymorphism to address this complexity with resources that include values, references and data containers specified to produce and consume a common &quot;abstract&quot; supertype that always will be one of either the single- or multivalued subtype.<br/>As an example, the GET /entities/{id}/values/{attributeId} resource operation is specified to return a &quot;Value&quot; but as evident from the model, the &quot;Value&quot; will always be &quot;oneOf&quot; either &quot;SingleValue&quot;, that has a &quot;value&quot; property for which the value is an object, or &quot;MultiValue&quot;, that has a &quot;values&quot; property for which the value is an array.<br/>Clients are advised to use the presence or absence of the plural array property (&quot;values&quot;, &quot;references&quot; and &quot;dataContainers&quot;) to determine the concrete type.</p><h1>Authentication</h1><p>The REST API is protected by HTTP Basic Authentication or if OAuth2-based authentication is enabled (SaaS customers only), by Bearer Authentication. With Basic Authentication, user name and password are supplied with each request and it is therefore highly recommended to only use the API in conjunction with HTTPS. For more information about OAuth2-based authentication for SaaS customers, please see the STEP Authentication Guide.</p><h1>Versioning</h1><p>The STEP REST API V2 is versioned using semantic versioning. Stibo Systems reserve the right to make non-breaking, minor / patch changes in any release without warning and clients must be coded / configured to be 'tolerant' and capable of handling such changes.</p><p>Examples of breaking, major changes:</p><ul><li>Renaming of a property</li><li>Removal of a property</li><li>Property type change</li><li>Addition of new property required for write operations</li><li>Marking existing property as required for write operations</li><li>Removal of resource or resource operation</li><li>Materially different behavior for existing resource operation</li></ul><p>Examples of non-breaking, minor / patch changes:</p><ul><li>Addition of new properties in request responses</li><li>Addition of new query parameter not required for write operations</li><li>Addition of new resource or resource operation</li><li>Bug fixes that do not change the schema or resource operations as described here</li><li>Inclusion of a response body for resource operations specified to return a 200 response with no body</li><li>Change of response &quot;Model&quot; / &quot;schema&quot; to type extending the previously specified type</li><li>Renaming a &quot;Model&quot; / &quot;schema&quot; type</li></ul><p>In addition, error message texts may change without warning within the same version. Client program logic should not depend upon the message content.</p><h1>Error Handling</h1><p>The STEP REST API V2 responds with standard HTTP status codes, with 2** responses indicating a success, 4** responses indicating a client error and 5** indicating a server error. Notice that this specification does not specify common error responses like 500 (internal server error) or 401 (unauthorized) for the individual resource operations. Clients should however be capable of handling such responses.</p><p>Error responses have a JSON response body (see Error schema below) containing HTTP status code information in addition to a message providing details about the error. As mentioned above, client program logic should not depend upon the message content.</p><p>The specific status codes used in the API are:</p><ul><li>200 (OK): Success, response may or may not have a body</li><li>201 (Created): Entity successfully created, response may or may not have a body</li><li>400 (Bad request): The server cannot or will not process the request due to an apparent client error</li><li>401 (Unauthorized): Returned only in relation to failed authentication</li><li>404 (Not Found): Returned only in relation to objects specified via path parameters (variable parts of the URL). If STEP objects referenced in request bodies or via query parameters cannot be found, the response will be 400.</li><li>429 (Too Many Requests): Clients are per default limited to 100 requests per second. Returned if the rate limit is exceeded.</li><li>500 (Internal Server Error): Unexpected error (could potentially cover an issue that rightfully should be a 400)</li></ul>

This Python package is automatically generated by the [OpenAPI Generator](https://openapi-generator.tech) project:

- API version: 1.3.0
- Package version: 1.0.0
- Generator version: 7.12.0
- Build package: org.openapitools.codegen.languages.PythonClientCodegen

## Requirements.

Python 3.8+

## Installation & Usage
### pip install

If the python package is hosted on a repository, you can install directly using:

```sh
pip install git+https://github.com/GIT_USER_ID/GIT_REPO_ID.git
```
(you may need to run `pip` with root permission: `sudo pip install git+https://github.com/GIT_USER_ID/GIT_REPO_ID.git`)

Then import the package:
```python
import step_rest_client
```

### Setuptools

Install via [Setuptools](http://pypi.python.org/pypi/setuptools).

```sh
python setup.py install --user
```
(or `sudo python setup.py install` to install the package for all users)

Then import the package:
```python
import step_rest_client
```

### Tests

Execute `pytest` to run the tests.

## Getting Started

Please follow the [installation procedure](#installation--usage) and then run the following:

```python

import step_rest_client
from step_rest_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to /restapiv2
# See configuration.py for a list of all supported configuration parameters.
configuration = step_rest_client.Configuration(
    host = "/restapiv2"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure HTTP basic authorization: basicAuth
configuration = step_rest_client.Configuration(
    username = os.environ["USERNAME"],
    password = os.environ["PASSWORD"]
)


# Enter a context with an instance of the API client
with step_rest_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = step_rest_client.AssetsApi(api_client)
    id = 'id_example' # str | ID / key value of the asset for which to get the approval status
    context = 'context_example' # str | ID of the context in which to perform the operation
    key_id = 'key_id_example' # str | ID of the key definition to be used for identifying the asset. If supplied, a key value should be supplied for the \"id\" path parameter. (optional)
    workspace = 'Main' # str | ID of the workspace in which to perform the operation. Defaults to \"Main\". (optional) (default to 'Main')

    try:
        # Returns the approval status of the asset with the specified ID / key value
        api_response = api_instance.assets_id_approval_status_get(id, context, key_id=key_id, workspace=workspace)
        print("The response of AssetsApi->assets_id_approval_status_get:\n")
        pprint(api_response)
    except ApiException as e:
        print("Exception when calling AssetsApi->assets_id_approval_status_get: %s\n" % e)

```

## Documentation for API Endpoints

All URIs are relative to */restapiv2*

Class | Method | HTTP request | Description
------------ | ------------- | ------------- | -------------
*AssetsApi* | [**assets_id_approval_status_get**](docs/AssetsApi.md#assets_id_approval_status_get) | **GET** /assets/{id}/approval-status | Returns the approval status of the asset with the specified ID / key value
*AssetsApi* | [**assets_id_approve_delete_post**](docs/AssetsApi.md#assets_id_approve_delete_post) | **POST** /assets/{id}/approve-delete | Approve deletes the asset with the specified ID
*AssetsApi* | [**assets_id_approve_post**](docs/AssetsApi.md#assets_id_approve_post) | **POST** /assets/{id}/approve | Approves the asset with the specified ID / key value
*AssetsApi* | [**assets_id_content_get**](docs/AssetsApi.md#assets_id_content_get) | **GET** /assets/{id}/content | Returns asset content for the asset with the specified ID / key value
*AssetsApi* | [**assets_id_content_put**](docs/AssetsApi.md#assets_id_content_put) | **PUT** /assets/{id}/content | Replaces asset content
*AssetsApi* | [**assets_id_delete**](docs/AssetsApi.md#assets_id_delete) | **DELETE** /assets/{id} | Deletes the asset with the specified ID / key value
*AssetsApi* | [**assets_id_get**](docs/AssetsApi.md#assets_id_get) | **GET** /assets/{id} | Returns the asset with the specified ID / key value
*AssetsApi* | [**assets_id_incoming_references_reference_type_id_get**](docs/AssetsApi.md#assets_id_incoming_references_reference_type_id_get) | **GET** /assets/{id}/incoming-references/{referenceTypeId} | Returns stream of incoming references of the specified type
*AssetsApi* | [**assets_id_patch**](docs/AssetsApi.md#assets_id_patch) | **PATCH** /assets/{id} | Partially updates an asset
*AssetsApi* | [**assets_id_purge_post**](docs/AssetsApi.md#assets_id_purge_post) | **POST** /assets/{id}/purge | Purges the asset with the specified ID from recycle bin
*AssetsApi* | [**assets_id_put**](docs/AssetsApi.md#assets_id_put) | **PUT** /assets/{id} | Creates or replaces asset with known ID
*AssetsApi* | [**assets_id_references_reference_type_id_get**](docs/AssetsApi.md#assets_id_references_reference_type_id_get) | **GET** /assets/{id}/references/{referenceTypeId} | Returns reference(s) of the specified type
*AssetsApi* | [**assets_id_references_reference_type_id_target_id_delete**](docs/AssetsApi.md#assets_id_references_reference_type_id_target_id_delete) | **DELETE** /assets/{id}/references/{referenceTypeId}/{targetId} | Deletes the reference
*AssetsApi* | [**assets_id_references_reference_type_id_target_id_get**](docs/AssetsApi.md#assets_id_references_reference_type_id_target_id_get) | **GET** /assets/{id}/references/{referenceTypeId}/{targetId} | Returns a specific reference
*AssetsApi* | [**assets_id_references_reference_type_id_target_id_put**](docs/AssetsApi.md#assets_id_references_reference_type_id_target_id_put) | **PUT** /assets/{id}/references/{referenceTypeId}/{targetId} | Replaces a reference
*AssetsApi* | [**assets_id_references_reference_type_id_target_id_values_attribute_id_delete**](docs/AssetsApi.md#assets_id_references_reference_type_id_target_id_values_attribute_id_delete) | **DELETE** /assets/{id}/references/{referenceTypeId}/{targetId}/values/{attributeId} | Deletes the value for a reference metadata attribute
*AssetsApi* | [**assets_id_references_reference_type_id_target_id_values_attribute_id_get**](docs/AssetsApi.md#assets_id_references_reference_type_id_target_id_values_attribute_id_get) | **GET** /assets/{id}/references/{referenceTypeId}/{targetId}/values/{attributeId} | Returns the value for a reference metadata attribute
*AssetsApi* | [**assets_id_references_reference_type_id_target_id_values_attribute_id_put**](docs/AssetsApi.md#assets_id_references_reference_type_id_target_id_values_attribute_id_put) | **PUT** /assets/{id}/references/{referenceTypeId}/{targetId}/values/{attributeId} | Replaces the value for a reference metadata attribute
*AssetsApi* | [**assets_id_values_attribute_id_delete**](docs/AssetsApi.md#assets_id_values_attribute_id_delete) | **DELETE** /assets/{id}/values/{attributeId} | Deletes the value for an asset attribute
*AssetsApi* | [**assets_id_values_attribute_id_get**](docs/AssetsApi.md#assets_id_values_attribute_id_get) | **GET** /assets/{id}/values/{attributeId} | Returns the value for an asset attribute
*AssetsApi* | [**assets_id_values_attribute_id_put**](docs/AssetsApi.md#assets_id_values_attribute_id_put) | **PUT** /assets/{id}/values/{attributeId} | Replaces the value for an asset attribute
*AssetsApi* | [**assets_post**](docs/AssetsApi.md#assets_post) | **POST** /assets | Creates a new asset object with autogenerated ID
*AssetsApi* | [**assets_search_post**](docs/AssetsApi.md#assets_search_post) | **POST** /assets/search | Search for / query assets
*AttributesApi* | [**attributes_id_get**](docs/AttributesApi.md#attributes_id_get) | **GET** /attributes/{id} | Returns the attribute with the specified ID
*BackgroundProcessTypesApi* | [**background_process_types_get**](docs/BackgroundProcessTypesApi.md#background_process_types_get) | **GET** /background-process-types | Returns the available background process types
*BackgroundProcessTypesApi* | [**background_process_types_type_id_processes_get**](docs/BackgroundProcessTypesApi.md#background_process_types_type_id_processes_get) | **GET** /background-process-types/{typeId}/processes | Returns background process IDs for the specified background process type
*BackgroundProcessesApi* | [**background_processes_id_attachments_attachment_id_content_get**](docs/BackgroundProcessesApi.md#background_processes_id_attachments_attachment_id_content_get) | **GET** /background-processes/{id}/attachments/{attachmentId}/content | Returns the background process attachment content
*BackgroundProcessesApi* | [**background_processes_id_attachments_attachment_id_get**](docs/BackgroundProcessesApi.md#background_processes_id_attachments_attachment_id_get) | **GET** /background-processes/{id}/attachments/{attachmentId} | Returns attachment metadata for a specific attachment
*BackgroundProcessesApi* | [**background_processes_id_attachments_get**](docs/BackgroundProcessesApi.md#background_processes_id_attachments_get) | **GET** /background-processes/{id}/attachments | Returns information about available background process attachments
*BackgroundProcessesApi* | [**background_processes_id_execution_report_get**](docs/BackgroundProcessesApi.md#background_processes_id_execution_report_get) | **GET** /background-processes/{id}/execution-report | Returns a streamed array of execution report entries (ExecutionReportEntry)
*BackgroundProcessesApi* | [**background_processes_id_get**](docs/BackgroundProcessesApi.md#background_processes_id_get) | **GET** /background-processes/{id} | Returns the background process with the specified ID
*ClassificationsApi* | [**classifications_id_approval_status_get**](docs/ClassificationsApi.md#classifications_id_approval_status_get) | **GET** /classifications/{id}/approval-status | Returns the approval status of the classification with the specified ID / key value
*ClassificationsApi* | [**classifications_id_approve_delete_post**](docs/ClassificationsApi.md#classifications_id_approve_delete_post) | **POST** /classifications/{id}/approve-delete | Approves deletes the classification with the specified ID
*ClassificationsApi* | [**classifications_id_approve_post**](docs/ClassificationsApi.md#classifications_id_approve_post) | **POST** /classifications/{id}/approve | Approves the classification with the specified ID / key value
*ClassificationsApi* | [**classifications_id_assets_get**](docs/ClassificationsApi.md#classifications_id_assets_get) | **GET** /classifications/{id}/assets | Returns a streamed array of IDs for assets linked to the classification
*ClassificationsApi* | [**classifications_id_children_get**](docs/ClassificationsApi.md#classifications_id_children_get) | **GET** /classifications/{id}/children | Returns a streamed array of IDs for classification children
*ClassificationsApi* | [**classifications_id_delete**](docs/ClassificationsApi.md#classifications_id_delete) | **DELETE** /classifications/{id} | Deletes the classification with the specified ID / key value
*ClassificationsApi* | [**classifications_id_get**](docs/ClassificationsApi.md#classifications_id_get) | **GET** /classifications/{id} | Returns the classification with the specified ID / key value
*ClassificationsApi* | [**classifications_id_incoming_references_reference_type_id_get**](docs/ClassificationsApi.md#classifications_id_incoming_references_reference_type_id_get) | **GET** /classifications/{id}/incoming-references/{referenceTypeId} | Returns stream of incoming references of the specified type
*ClassificationsApi* | [**classifications_id_patch**](docs/ClassificationsApi.md#classifications_id_patch) | **PATCH** /classifications/{id} | Partially updates a classification
*ClassificationsApi* | [**classifications_id_purge_post**](docs/ClassificationsApi.md#classifications_id_purge_post) | **POST** /classifications/{id}/purge | Purges the classification with the specified ID from recycle bin
*ClassificationsApi* | [**classifications_id_put**](docs/ClassificationsApi.md#classifications_id_put) | **PUT** /classifications/{id} | Creates or replaces classification with known ID
*ClassificationsApi* | [**classifications_id_references_reference_type_id_get**](docs/ClassificationsApi.md#classifications_id_references_reference_type_id_get) | **GET** /classifications/{id}/references/{referenceTypeId} | Returns reference(s) of the specified type
*ClassificationsApi* | [**classifications_id_references_reference_type_id_target_id_delete**](docs/ClassificationsApi.md#classifications_id_references_reference_type_id_target_id_delete) | **DELETE** /classifications/{id}/references/{referenceTypeId}/{targetId} | Deletes the reference
*ClassificationsApi* | [**classifications_id_references_reference_type_id_target_id_get**](docs/ClassificationsApi.md#classifications_id_references_reference_type_id_target_id_get) | **GET** /classifications/{id}/references/{referenceTypeId}/{targetId} | Returns a specific reference
*ClassificationsApi* | [**classifications_id_references_reference_type_id_target_id_put**](docs/ClassificationsApi.md#classifications_id_references_reference_type_id_target_id_put) | **PUT** /classifications/{id}/references/{referenceTypeId}/{targetId} | Replaces a reference
*ClassificationsApi* | [**classifications_id_references_reference_type_id_target_id_values_attribute_id_delete**](docs/ClassificationsApi.md#classifications_id_references_reference_type_id_target_id_values_attribute_id_delete) | **DELETE** /classifications/{id}/references/{referenceTypeId}/{targetId}/values/{attributeId} | Deletes the value for a reference metadata attribute
*ClassificationsApi* | [**classifications_id_references_reference_type_id_target_id_values_attribute_id_get**](docs/ClassificationsApi.md#classifications_id_references_reference_type_id_target_id_values_attribute_id_get) | **GET** /classifications/{id}/references/{referenceTypeId}/{targetId}/values/{attributeId} | Returns the value for a reference metadata attribute
*ClassificationsApi* | [**classifications_id_references_reference_type_id_target_id_values_attribute_id_put**](docs/ClassificationsApi.md#classifications_id_references_reference_type_id_target_id_values_attribute_id_put) | **PUT** /classifications/{id}/references/{referenceTypeId}/{targetId}/values/{attributeId} | Replaces the value for a reference metadata attribute
*ClassificationsApi* | [**classifications_id_values_attribute_id_delete**](docs/ClassificationsApi.md#classifications_id_values_attribute_id_delete) | **DELETE** /classifications/{id}/values/{attributeId} | Deletes the value for a classification attribute
*ClassificationsApi* | [**classifications_id_values_attribute_id_get**](docs/ClassificationsApi.md#classifications_id_values_attribute_id_get) | **GET** /classifications/{id}/values/{attributeId} | Returns the value for a classification attribute
*ClassificationsApi* | [**classifications_id_values_attribute_id_put**](docs/ClassificationsApi.md#classifications_id_values_attribute_id_put) | **PUT** /classifications/{id}/values/{attributeId} | Replaces the value for a classification attribute
*ClassificationsApi* | [**classifications_post**](docs/ClassificationsApi.md#classifications_post) | **POST** /classifications | Creates a new classification object with autogenerated ID
*ClassificationsApi* | [**classifications_search_post**](docs/ClassificationsApi.md#classifications_search_post) | **POST** /classifications/search | Search for / query classifications
*DataContainerTypesApi* | [**data_container_types_id_get**](docs/DataContainerTypesApi.md#data_container_types_id_get) | **GET** /data-container-types/{id} | Returns the data container type with the specified ID
*DataTypeGroupsApi* | [**data_type_groups_id_get**](docs/DataTypeGroupsApi.md#data_type_groups_id_get) | **GET** /data-type-groups/{id} | Returns the data type group with the specified ID
*EntitiesApi* | [**entities_find_similar_post**](docs/EntitiesApi.md#entities_find_similar_post) | **POST** /entities/find-similar | Performs a find similar operation for entities
*EntitiesApi* | [**entities_id_approval_status_get**](docs/EntitiesApi.md#entities_id_approval_status_get) | **GET** /entities/{id}/approval-status | Returns the approval status of the entity with the specified ID / key value
*EntitiesApi* | [**entities_id_approve_delete_post**](docs/EntitiesApi.md#entities_id_approve_delete_post) | **POST** /entities/{id}/approve-delete | Approve deletes the entity with the specified ID
*EntitiesApi* | [**entities_id_approve_post**](docs/EntitiesApi.md#entities_id_approve_post) | **POST** /entities/{id}/approve | Approves the entity with the specified ID / key value
*EntitiesApi* | [**entities_id_children_get**](docs/EntitiesApi.md#entities_id_children_get) | **GET** /entities/{id}/children | Returns a streamed array of IDs for entity children
*EntitiesApi* | [**entities_id_data_containers_data_container_type_id_get**](docs/EntitiesApi.md#entities_id_data_containers_data_container_type_id_get) | **GET** /entities/{id}/data-containers/{dataContainerTypeId} | Returns data container(s) of the specified type
*EntitiesApi* | [**entities_id_delete**](docs/EntitiesApi.md#entities_id_delete) | **DELETE** /entities/{id} | Deletes the entity with the specified ID
*EntitiesApi* | [**entities_id_get**](docs/EntitiesApi.md#entities_id_get) | **GET** /entities/{id} | Returns the entity with the specified ID / key value
*EntitiesApi* | [**entities_id_incoming_references_reference_type_id_get**](docs/EntitiesApi.md#entities_id_incoming_references_reference_type_id_get) | **GET** /entities/{id}/incoming-references/{referenceTypeId} | Returns stream of incoming references of the specified type
*EntitiesApi* | [**entities_id_patch**](docs/EntitiesApi.md#entities_id_patch) | **PATCH** /entities/{id} | Partially updates an entity
*EntitiesApi* | [**entities_id_purge_post**](docs/EntitiesApi.md#entities_id_purge_post) | **POST** /entities/{id}/purge | Purges the entity with the specified ID from recycle bin
*EntitiesApi* | [**entities_id_put**](docs/EntitiesApi.md#entities_id_put) | **PUT** /entities/{id} | Creates or replaces entity with known ID
*EntitiesApi* | [**entities_id_references_reference_type_id_get**](docs/EntitiesApi.md#entities_id_references_reference_type_id_get) | **GET** /entities/{id}/references/{referenceTypeId} | Returns reference(s) of the specified type
*EntitiesApi* | [**entities_id_references_reference_type_id_target_id_delete**](docs/EntitiesApi.md#entities_id_references_reference_type_id_target_id_delete) | **DELETE** /entities/{id}/references/{referenceTypeId}/{targetId} | Deletes the reference
*EntitiesApi* | [**entities_id_references_reference_type_id_target_id_get**](docs/EntitiesApi.md#entities_id_references_reference_type_id_target_id_get) | **GET** /entities/{id}/references/{referenceTypeId}/{targetId} | Returns a specific reference
*EntitiesApi* | [**entities_id_references_reference_type_id_target_id_put**](docs/EntitiesApi.md#entities_id_references_reference_type_id_target_id_put) | **PUT** /entities/{id}/references/{referenceTypeId}/{targetId} | Replaces a reference
*EntitiesApi* | [**entities_id_references_reference_type_id_target_id_values_attribute_id_delete**](docs/EntitiesApi.md#entities_id_references_reference_type_id_target_id_values_attribute_id_delete) | **DELETE** /entities/{id}/references/{referenceTypeId}/{targetId}/values/{attributeId} | Deletes the value for a reference metadata attribute
*EntitiesApi* | [**entities_id_references_reference_type_id_target_id_values_attribute_id_get**](docs/EntitiesApi.md#entities_id_references_reference_type_id_target_id_values_attribute_id_get) | **GET** /entities/{id}/references/{referenceTypeId}/{targetId}/values/{attributeId} | Returns the value for a reference metadata attribute
*EntitiesApi* | [**entities_id_references_reference_type_id_target_id_values_attribute_id_put**](docs/EntitiesApi.md#entities_id_references_reference_type_id_target_id_values_attribute_id_put) | **PUT** /entities/{id}/references/{referenceTypeId}/{targetId}/values/{attributeId} | Replaces the value for a reference metadata attribute
*EntitiesApi* | [**entities_id_values_attribute_id_delete**](docs/EntitiesApi.md#entities_id_values_attribute_id_delete) | **DELETE** /entities/{id}/values/{attributeId} | Deletes the value for an entity attribute
*EntitiesApi* | [**entities_id_values_attribute_id_get**](docs/EntitiesApi.md#entities_id_values_attribute_id_get) | **GET** /entities/{id}/values/{attributeId} | Returns the value for an entity attribute
*EntitiesApi* | [**entities_id_values_attribute_id_put**](docs/EntitiesApi.md#entities_id_values_attribute_id_put) | **PUT** /entities/{id}/values/{attributeId} | Replaces the value for an entity attribute
*EntitiesApi* | [**entities_match_and_merge_post**](docs/EntitiesApi.md#entities_match_and_merge_post) | **POST** /entities/match-and-merge | Performs a Match An Merge operation
*EntitiesApi* | [**entities_post**](docs/EntitiesApi.md#entities_post) | **POST** /entities | Creates a new entity object with autogenerated ID
*EntitiesApi* | [**entities_search_post**](docs/EntitiesApi.md#entities_search_post) | **POST** /entities/search | Search for / query entities
*EventProcessorsApi* | [**event_processors_get**](docs/EventProcessorsApi.md#event_processors_get) | **GET** /event-processors | Returns basic event processor representations
*EventProcessorsApi* | [**event_processors_id_disable_post**](docs/EventProcessorsApi.md#event_processors_id_disable_post) | **POST** /event-processors/{id}/disable | Disables the specified event processor
*EventProcessorsApi* | [**event_processors_id_enable_post**](docs/EventProcessorsApi.md#event_processors_id_enable_post) | **POST** /event-processors/{id}/enable | Enables the specified event processor
*EventProcessorsApi* | [**event_processors_id_execution_report_get**](docs/EventProcessorsApi.md#event_processors_id_execution_report_get) | **GET** /event-processors/{id}/execution-report | Returns the execution report for the specified event processor
*EventProcessorsApi* | [**event_processors_id_invoke_post**](docs/EventProcessorsApi.md#event_processors_id_invoke_post) | **POST** /event-processors/{id}/invoke | Invokes the specified event processor
*EventProcessorsApi* | [**event_processors_id_queue_disable_post**](docs/EventProcessorsApi.md#event_processors_id_queue_disable_post) | **POST** /event-processors/{id}/queue/disable | Disables the event queue associated with the event processor
*EventProcessorsApi* | [**event_processors_id_queue_enable_post**](docs/EventProcessorsApi.md#event_processors_id_queue_enable_post) | **POST** /event-processors/{id}/queue/enable | Enables the event queue associated with the event processor
*EventProcessorsApi* | [**event_processors_id_queue_number_of_unread_events_get**](docs/EventProcessorsApi.md#event_processors_id_queue_number_of_unread_events_get) | **GET** /event-processors/{id}/queue/number-of-unread-events | Returns the number of unread events for the associated event queue
*EventProcessorsApi* | [**event_processors_id_queue_status_get**](docs/EventProcessorsApi.md#event_processors_id_queue_status_get) | **GET** /event-processors/{id}/queue/status | Returns the status of the event queue associated with the event processor
*EventProcessorsApi* | [**event_processors_id_statistics_get**](docs/EventProcessorsApi.md#event_processors_id_statistics_get) | **GET** /event-processors/{id}/statistics | Returns statistics for the specified event processor
*EventProcessorsApi* | [**event_processors_id_status_get**](docs/EventProcessorsApi.md#event_processors_id_status_get) | **GET** /event-processors/{id}/status | Returns the status of the specified event processor
*ExportApi* | [**export_export_configuration_id_post**](docs/ExportApi.md#export_export_configuration_id_post) | **POST** /export/{exportConfigurationId} | Starts an export background process
*GatewayIntegrationEndpointsApi* | [**gateway_integration_endpoints_get**](docs/GatewayIntegrationEndpointsApi.md#gateway_integration_endpoints_get) | **GET** /gateway-integration-endpoints | Returns basic gateway integration endpoint representations
*GatewayIntegrationEndpointsApi* | [**gateway_integration_endpoints_id_disable_post**](docs/GatewayIntegrationEndpointsApi.md#gateway_integration_endpoints_id_disable_post) | **POST** /gateway-integration-endpoints/{id}/disable | Disables the gateway integration endpoint
*GatewayIntegrationEndpointsApi* | [**gateway_integration_endpoints_id_enable_post**](docs/GatewayIntegrationEndpointsApi.md#gateway_integration_endpoints_id_enable_post) | **POST** /gateway-integration-endpoints/{id}/enable | Enables the gateway integration endpoint
*GatewayIntegrationEndpointsApi* | [**gateway_integration_endpoints_id_status_get**](docs/GatewayIntegrationEndpointsApi.md#gateway_integration_endpoints_id_status_get) | **GET** /gateway-integration-endpoints/{id}/status | Returns the status of the specified gateway integration endpoint
*ImportApi* | [**import_import_configuration_id_post**](docs/ImportApi.md#import_import_configuration_id_post) | **POST** /import/{importConfigurationId} | Starts an import background process
*InboundIntegrationEndpointsApi* | [**inbound_integration_endpoints_get**](docs/InboundIntegrationEndpointsApi.md#inbound_integration_endpoints_get) | **GET** /inbound-integration-endpoints | Returns basic inbound integration endpoint representations
*InboundIntegrationEndpointsApi* | [**inbound_integration_endpoints_id_disable_post**](docs/InboundIntegrationEndpointsApi.md#inbound_integration_endpoints_id_disable_post) | **POST** /inbound-integration-endpoints/{id}/disable | Disables the specified inbound integration endpoint
*InboundIntegrationEndpointsApi* | [**inbound_integration_endpoints_id_enable_post**](docs/InboundIntegrationEndpointsApi.md#inbound_integration_endpoints_id_enable_post) | **POST** /inbound-integration-endpoints/{id}/enable | Enables the specified inbound integration endpoint
*InboundIntegrationEndpointsApi* | [**inbound_integration_endpoints_id_execution_report_get**](docs/InboundIntegrationEndpointsApi.md#inbound_integration_endpoints_id_execution_report_get) | **GET** /inbound-integration-endpoints/{id}/execution-report | Returns the execution report for the specified inbound integration endpoint
*InboundIntegrationEndpointsApi* | [**inbound_integration_endpoints_id_invoke_post**](docs/InboundIntegrationEndpointsApi.md#inbound_integration_endpoints_id_invoke_post) | **POST** /inbound-integration-endpoints/{id}/invoke | Invokes the specified inbound integration endpoint
*InboundIntegrationEndpointsApi* | [**inbound_integration_endpoints_id_statistics_get**](docs/InboundIntegrationEndpointsApi.md#inbound_integration_endpoints_id_statistics_get) | **GET** /inbound-integration-endpoints/{id}/statistics | Returns statistics for the specified inbound integration endpoint
*InboundIntegrationEndpointsApi* | [**inbound_integration_endpoints_id_status_get**](docs/InboundIntegrationEndpointsApi.md#inbound_integration_endpoints_id_status_get) | **GET** /inbound-integration-endpoints/{id}/status | Returns the status of the specified inbound integration endpoint
*InboundIntegrationEndpointsApi* | [**inbound_integration_endpoints_id_upload_and_invoke_post**](docs/InboundIntegrationEndpointsApi.md#inbound_integration_endpoints_id_upload_and_invoke_post) | **POST** /inbound-integration-endpoints/{id}/upload-and-invoke | Posts message/file to endpoint with REST receiver
*InboundIntegrationEndpointsApi* | [**inbound_integration_endpoints_id_worker_processes_get**](docs/InboundIntegrationEndpointsApi.md#inbound_integration_endpoints_id_worker_processes_get) | **GET** /inbound-integration-endpoints/{id}/worker-processes | Returns background process IDs for processes started by the endpoint
*ListsOfValuesApi* | [**list_of_values_id_get**](docs/ListsOfValuesApi.md#list_of_values_id_get) | **GET** /list-of-values/{id} | Returns the list of values with the specified ID
*ListsOfValuesApi* | [**list_of_values_id_value_entries_get**](docs/ListsOfValuesApi.md#list_of_values_id_value_entries_get) | **GET** /list-of-values/{id}/value-entries | Returns a streamed array of value entries (ListOfValuesEntry)
*ObjectTypesApi* | [**object_types_id_get**](docs/ObjectTypesApi.md#object_types_id_get) | **GET** /object-types/{id} | Returns the object type with the specified ID
*OutboundIntegrationEndpointsApi* | [**outbound_integration_endpoints_get**](docs/OutboundIntegrationEndpointsApi.md#outbound_integration_endpoints_get) | **GET** /outbound-integration-endpoints | Returns basic outbound integration endpoint representations
*OutboundIntegrationEndpointsApi* | [**outbound_integration_endpoints_id_disable_post**](docs/OutboundIntegrationEndpointsApi.md#outbound_integration_endpoints_id_disable_post) | **POST** /outbound-integration-endpoints/{id}/disable | Disables the specified outbound integration endpoint
*OutboundIntegrationEndpointsApi* | [**outbound_integration_endpoints_id_enable_post**](docs/OutboundIntegrationEndpointsApi.md#outbound_integration_endpoints_id_enable_post) | **POST** /outbound-integration-endpoints/{id}/enable | Enables the specified outbound integration endpoint
*OutboundIntegrationEndpointsApi* | [**outbound_integration_endpoints_id_execution_report_get**](docs/OutboundIntegrationEndpointsApi.md#outbound_integration_endpoints_id_execution_report_get) | **GET** /outbound-integration-endpoints/{id}/execution-report | Returns the execution report for the specified outbound integration endpoint
*OutboundIntegrationEndpointsApi* | [**outbound_integration_endpoints_id_invoke_post**](docs/OutboundIntegrationEndpointsApi.md#outbound_integration_endpoints_id_invoke_post) | **POST** /outbound-integration-endpoints/{id}/invoke | Invokes the specified outbound integration endpoint
*OutboundIntegrationEndpointsApi* | [**outbound_integration_endpoints_id_queue_disable_post**](docs/OutboundIntegrationEndpointsApi.md#outbound_integration_endpoints_id_queue_disable_post) | **POST** /outbound-integration-endpoints/{id}/queue/disable | Disables the event queue associated with the outbound integration endpoint
*OutboundIntegrationEndpointsApi* | [**outbound_integration_endpoints_id_queue_enable_post**](docs/OutboundIntegrationEndpointsApi.md#outbound_integration_endpoints_id_queue_enable_post) | **POST** /outbound-integration-endpoints/{id}/queue/enable | Enables the event queue associated with the outbound integration endpoint
*OutboundIntegrationEndpointsApi* | [**outbound_integration_endpoints_id_queue_number_of_unread_events_get**](docs/OutboundIntegrationEndpointsApi.md#outbound_integration_endpoints_id_queue_number_of_unread_events_get) | **GET** /outbound-integration-endpoints/{id}/queue/number-of-unread-events | Returns the number of unread events for the associated event queue
*OutboundIntegrationEndpointsApi* | [**outbound_integration_endpoints_id_queue_status_get**](docs/OutboundIntegrationEndpointsApi.md#outbound_integration_endpoints_id_queue_status_get) | **GET** /outbound-integration-endpoints/{id}/queue/status | Returns the status of the event queue associated with the outbound integration endpoint
*OutboundIntegrationEndpointsApi* | [**outbound_integration_endpoints_id_statistics_get**](docs/OutboundIntegrationEndpointsApi.md#outbound_integration_endpoints_id_statistics_get) | **GET** /outbound-integration-endpoints/{id}/statistics | Returns statistics for the specified outbound integration endpoint
*OutboundIntegrationEndpointsApi* | [**outbound_integration_endpoints_id_status_get**](docs/OutboundIntegrationEndpointsApi.md#outbound_integration_endpoints_id_status_get) | **GET** /outbound-integration-endpoints/{id}/status | Returns the status of the specified outbound integration endpoint
*OutboundIntegrationEndpointsApi* | [**outbound_integration_endpoints_id_worker_processes_get**](docs/OutboundIntegrationEndpointsApi.md#outbound_integration_endpoints_id_worker_processes_get) | **GET** /outbound-integration-endpoints/{id}/worker-processes | Returns background process IDs for processes started by the endpoint
*ProductsApi* | [**products_id_approval_status_get**](docs/ProductsApi.md#products_id_approval_status_get) | **GET** /products/{id}/approval-status | Returns the approval status of the product with the specified ID / key value
*ProductsApi* | [**products_id_approve_delete_post**](docs/ProductsApi.md#products_id_approve_delete_post) | **POST** /products/{id}/approve-delete | Approve deletes the product with the specified ID
*ProductsApi* | [**products_id_approve_post**](docs/ProductsApi.md#products_id_approve_post) | **POST** /products/{id}/approve | Approves the product with the specified ID / key value
*ProductsApi* | [**products_id_children_get**](docs/ProductsApi.md#products_id_children_get) | **GET** /products/{id}/children | Returns a streamed array of IDs for product children
*ProductsApi* | [**products_id_data_containers_data_container_type_id_get**](docs/ProductsApi.md#products_id_data_containers_data_container_type_id_get) | **GET** /products/{id}/data-containers/{dataContainerTypeId} | Returns data container(s) of the specified type
*ProductsApi* | [**products_id_delete**](docs/ProductsApi.md#products_id_delete) | **DELETE** /products/{id} | Deletes the product with the specified ID / key value
*ProductsApi* | [**products_id_get**](docs/ProductsApi.md#products_id_get) | **GET** /products/{id} | Returns the product with the specified ID / key value
*ProductsApi* | [**products_id_incoming_references_reference_type_id_get**](docs/ProductsApi.md#products_id_incoming_references_reference_type_id_get) | **GET** /products/{id}/incoming-references/{referenceTypeId} | Returns stream of incoming references of the specified type
*ProductsApi* | [**products_id_patch**](docs/ProductsApi.md#products_id_patch) | **PATCH** /products/{id} | Partially updates a product
*ProductsApi* | [**products_id_purge_post**](docs/ProductsApi.md#products_id_purge_post) | **POST** /products/{id}/purge | Purges the product with the specified ID from recycle bin
*ProductsApi* | [**products_id_put**](docs/ProductsApi.md#products_id_put) | **PUT** /products/{id} | Creates or replaces product with known ID
*ProductsApi* | [**products_id_references_reference_type_id_get**](docs/ProductsApi.md#products_id_references_reference_type_id_get) | **GET** /products/{id}/references/{referenceTypeId} | Returns reference(s) of the specified type
*ProductsApi* | [**products_id_references_reference_type_id_target_id_delete**](docs/ProductsApi.md#products_id_references_reference_type_id_target_id_delete) | **DELETE** /products/{id}/references/{referenceTypeId}/{targetId} | Deletes the reference
*ProductsApi* | [**products_id_references_reference_type_id_target_id_get**](docs/ProductsApi.md#products_id_references_reference_type_id_target_id_get) | **GET** /products/{id}/references/{referenceTypeId}/{targetId} | Returns a specific reference
*ProductsApi* | [**products_id_references_reference_type_id_target_id_put**](docs/ProductsApi.md#products_id_references_reference_type_id_target_id_put) | **PUT** /products/{id}/references/{referenceTypeId}/{targetId} | Replaces a reference
*ProductsApi* | [**products_id_references_reference_type_id_target_id_values_attribute_id_delete**](docs/ProductsApi.md#products_id_references_reference_type_id_target_id_values_attribute_id_delete) | **DELETE** /products/{id}/references/{referenceTypeId}/{targetId}/values/{attributeId} | Deletes the value for a reference metadata attribute
*ProductsApi* | [**products_id_references_reference_type_id_target_id_values_attribute_id_get**](docs/ProductsApi.md#products_id_references_reference_type_id_target_id_values_attribute_id_get) | **GET** /products/{id}/references/{referenceTypeId}/{targetId}/values/{attributeId} | Returns the value for a reference metadata attribute
*ProductsApi* | [**products_id_references_reference_type_id_target_id_values_attribute_id_put**](docs/ProductsApi.md#products_id_references_reference_type_id_target_id_values_attribute_id_put) | **PUT** /products/{id}/references/{referenceTypeId}/{targetId}/values/{attributeId} | Replaces the value for a reference metadata attribute
*ProductsApi* | [**products_id_values_attribute_id_delete**](docs/ProductsApi.md#products_id_values_attribute_id_delete) | **DELETE** /products/{id}/values/{attributeId} | Deletes the value for a product attribute
*ProductsApi* | [**products_id_values_attribute_id_get**](docs/ProductsApi.md#products_id_values_attribute_id_get) | **GET** /products/{id}/values/{attributeId} | Returns the value for a product attribute
*ProductsApi* | [**products_id_values_attribute_id_put**](docs/ProductsApi.md#products_id_values_attribute_id_put) | **PUT** /products/{id}/values/{attributeId} | Replaces the value for a product attribute
*ProductsApi* | [**products_post**](docs/ProductsApi.md#products_post) | **POST** /products | Creates a new product object with autogenerated ID
*ProductsApi* | [**products_search_post**](docs/ProductsApi.md#products_search_post) | **POST** /products/search | Search for / query products
*ReferenceTypesApi* | [**reference_types_id_get**](docs/ReferenceTypesApi.md#reference_types_id_get) | **GET** /reference-types/{id} | Returns the reference type with the specified ID
*ReportingApi* | [**reports_historic_changes_report_id_clean_up_post**](docs/ReportingApi.md#reports_historic_changes_report_id_clean_up_post) | **POST** /reports/historic-changes/{reportID}/clean-up | Deletes configuration objects specific to a report.
*ReportingApi* | [**reports_historic_changes_report_id_post**](docs/ReportingApi.md#reports_historic_changes_report_id_post) | **POST** /reports/historic-changes/{reportID} | Starts historic changes report generation
*UnitsApi* | [**units_id_get**](docs/UnitsApi.md#units_id_get) | **GET** /units/{id} | Returns the unit with the specified ID
*WorkflowTasksApi* | [**workflow_tasks_id_claim_post**](docs/WorkflowTasksApi.md#workflow_tasks_id_claim_post) | **POST** /workflow-tasks/{id}/claim | Claims a specific workflow tasks
*WorkflowTasksApi* | [**workflow_tasks_id_events_get**](docs/WorkflowTasksApi.md#workflow_tasks_id_events_get) | **GET** /workflow-tasks/{id}/events | Returns the available events for a task
*WorkflowTasksApi* | [**workflow_tasks_id_get**](docs/WorkflowTasksApi.md#workflow_tasks_id_get) | **GET** /workflow-tasks/{id} | Returns the workflow task with the specified ID
*WorkflowTasksApi* | [**workflow_tasks_id_release_post**](docs/WorkflowTasksApi.md#workflow_tasks_id_release_post) | **POST** /workflow-tasks/{id}/release | Releases a task
*WorkflowTasksApi* | [**workflow_tasks_id_trigger_event_post**](docs/WorkflowTasksApi.md#workflow_tasks_id_trigger_event_post) | **POST** /workflow-tasks/{id}/trigger-event | Triggers an event for a task
*WorkflowTasksApi* | [**workflow_tasks_search_post**](docs/WorkflowTasksApi.md#workflow_tasks_search_post) | **POST** /workflow-tasks/search | Search for / query workflow tasks
*WorkflowsApi* | [**workflows_get**](docs/WorkflowsApi.md#workflows_get) | **GET** /workflows | Returns IDs of available workflows
*WorkflowsApi* | [**workflows_id_get**](docs/WorkflowsApi.md#workflows_id_get) | **GET** /workflows/{id} | Returns the workflow with the specified ID
*WorkflowsApi* | [**workflows_id_instances_instance_id_delete**](docs/WorkflowsApi.md#workflows_id_instances_instance_id_delete) | **DELETE** /workflows/{id}/instances/{instanceId} | Deletes the workflow instance with the specified ID
*WorkflowsApi* | [**workflows_id_instances_post**](docs/WorkflowsApi.md#workflows_id_instances_post) | **POST** /workflows/{id}/instances | Starts a workflow


## Documentation For Models

 - [Amount](docs/Amount.md)
 - [AndCondition](docs/AndCondition.md)
 - [ApprovalResponse](docs/ApprovalResponse.md)
 - [ApprovalStatus](docs/ApprovalStatus.md)
 - [Asset](docs/Asset.md)
 - [Attribute](docs/Attribute.md)
 - [AttributeLink](docs/AttributeLink.md)
 - [BackgroundProcess](docs/BackgroundProcess.md)
 - [BackgroundProcessAttachmentMetadata](docs/BackgroundProcessAttachmentMetadata.md)
 - [BackgroundProcessIdentification](docs/BackgroundProcessIdentification.md)
 - [BackgroundProcessType](docs/BackgroundProcessType.md)
 - [Classification](docs/Classification.md)
 - [Condition](docs/Condition.md)
 - [DataContainer](docs/DataContainer.md)
 - [DataContainerEntry](docs/DataContainerEntry.md)
 - [DataContainerObjectCondition](docs/DataContainerObjectCondition.md)
 - [DataContainerType](docs/DataContainerType.md)
 - [DataTypeGroup](docs/DataTypeGroup.md)
 - [EndpointStatistics](docs/EndpointStatistics.md)
 - [EndpointStatus](docs/EndpointStatus.md)
 - [Entity](docs/Entity.md)
 - [Error](docs/Error.md)
 - [EventProcessor](docs/EventProcessor.md)
 - [EventProcessorStatistics](docs/EventProcessorStatistics.md)
 - [EventProcessorStatus](docs/EventProcessorStatus.md)
 - [EventQueueStatus](docs/EventQueueStatus.md)
 - [ExecutionReportEntry](docs/ExecutionReportEntry.md)
 - [ExportSpecification](docs/ExportSpecification.md)
 - [FindSimilarBusinessRuleResult](docs/FindSimilarBusinessRuleResult.md)
 - [FindSimilarEntitiesRequest](docs/FindSimilarEntitiesRequest.md)
 - [FindSimilarEntitiesResponse](docs/FindSimilarEntitiesResponse.md)
 - [FindSimilarEntitiesResponseRecord](docs/FindSimilarEntitiesResponseRecord.md)
 - [FindSimilarExecutionReport](docs/FindSimilarExecutionReport.md)
 - [GatewayIntegrationEndpoint](docs/GatewayIntegrationEndpoint.md)
 - [HasDataContainerObjectCondition](docs/HasDataContainerObjectCondition.md)
 - [HasReferenceToCondition](docs/HasReferenceToCondition.md)
 - [IdCondition](docs/IdCondition.md)
 - [InboundIntegrationEndpoint](docs/InboundIntegrationEndpoint.md)
 - [IncomingReferenceEntry](docs/IncomingReferenceEntry.md)
 - [ListOfValues](docs/ListOfValues.md)
 - [ListOfValuesEntry](docs/ListOfValuesEntry.md)
 - [LovValueCondition](docs/LovValueCondition.md)
 - [MatchAndMergeExecutionReport](docs/MatchAndMergeExecutionReport.md)
 - [MatchAndMergeGeneralExecutionReport](docs/MatchAndMergeGeneralExecutionReport.md)
 - [MatchAndMergePotentialDuplicate](docs/MatchAndMergePotentialDuplicate.md)
 - [MatchAndMergeRecordIn](docs/MatchAndMergeRecordIn.md)
 - [MatchAndMergeRecordOut](docs/MatchAndMergeRecordOut.md)
 - [MatchAndMergeResponse](docs/MatchAndMergeResponse.md)
 - [MultiDataContainer](docs/MultiDataContainer.md)
 - [MultiReference](docs/MultiReference.md)
 - [MultiValue](docs/MultiValue.md)
 - [NameCondition](docs/NameCondition.md)
 - [NumericValueCondition](docs/NumericValueCondition.md)
 - [ObjectType](docs/ObjectType.md)
 - [ObjectTypeCondition](docs/ObjectTypeCondition.md)
 - [OrCondition](docs/OrCondition.md)
 - [OutboundIntegrationEndpoint](docs/OutboundIntegrationEndpoint.md)
 - [Product](docs/Product.md)
 - [Query](docs/Query.md)
 - [QueryResult](docs/QueryResult.md)
 - [Reference](docs/Reference.md)
 - [ReferenceEntry](docs/ReferenceEntry.md)
 - [ReferenceMetadataCondition](docs/ReferenceMetadataCondition.md)
 - [ReferenceType](docs/ReferenceType.md)
 - [RejectedByBusinessCondition](docs/RejectedByBusinessCondition.md)
 - [SimpleBelowCondition](docs/SimpleBelowCondition.md)
 - [SingleDataContainer](docs/SingleDataContainer.md)
 - [SingleReference](docs/SingleReference.md)
 - [SingleValue](docs/SingleValue.md)
 - [StatusFlag](docs/StatusFlag.md)
 - [TextValueCondition](docs/TextValueCondition.md)
 - [TriggerWorkflowEvent](docs/TriggerWorkflowEvent.md)
 - [Unit](docs/Unit.md)
 - [Value](docs/Value.md)
 - [ValueEntry](docs/ValueEntry.md)
 - [Workflow](docs/Workflow.md)
 - [WorkflowEvent](docs/WorkflowEvent.md)
 - [WorkflowInstance](docs/WorkflowInstance.md)
 - [WorkflowInstanceCreation](docs/WorkflowInstanceCreation.md)
 - [WorkflowNode](docs/WorkflowNode.md)
 - [WorkflowTask](docs/WorkflowTask.md)
 - [WorkflowTaskQuery](docs/WorkflowTaskQuery.md)


<a id="documentation-for-authorization"></a>
## Documentation For Authorization


Authentication schemes defined for the API:
<a id="basicAuth"></a>
### basicAuth

- **Type**: HTTP basic authentication


## Author




