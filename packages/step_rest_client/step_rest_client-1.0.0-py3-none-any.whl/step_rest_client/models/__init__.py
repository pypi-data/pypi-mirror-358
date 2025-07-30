# coding: utf-8

# flake8: noqa
"""
    STEP REST API V2

    <h1>About</h1><p>The STEP REST API V2 provides read and write access to a set of core STEP objects using the HTTP operations GET, PUT, POST, PATCH and DELETE.</p><h1>Resource Representation</h1><p>With the exception of a few resource operations for retrieving and uploading binary data, all request and response bodies are JSON, compliant with the schema documented here.</p><h1>Context and Workspace</h1><p>All requests are handled in a specific STEP context and workspace and both can be specified via query parameters available for all resource operations. A context must always be specified while requests per default will be handled in the &quot;Main&quot; workspace.</p><h1>Polymorphism</h1><p>In STEP, attributes, reference types and data container types can all be either single- or multivalued. The STEP REST API V2 uses polymorphism to address this complexity with resources that include values, references and data containers specified to produce and consume a common &quot;abstract&quot; supertype that always will be one of either the single- or multivalued subtype.<br/>As an example, the GET /entities/{id}/values/{attributeId} resource operation is specified to return a &quot;Value&quot; but as evident from the model, the &quot;Value&quot; will always be &quot;oneOf&quot; either &quot;SingleValue&quot;, that has a &quot;value&quot; property for which the value is an object, or &quot;MultiValue&quot;, that has a &quot;values&quot; property for which the value is an array.<br/>Clients are advised to use the presence or absence of the plural array property (&quot;values&quot;, &quot;references&quot; and &quot;dataContainers&quot;) to determine the concrete type.</p><h1>Authentication</h1><p>The REST API is protected by HTTP Basic Authentication or if OAuth2-based authentication is enabled (SaaS customers only), by Bearer Authentication. With Basic Authentication, user name and password are supplied with each request and it is therefore highly recommended to only use the API in conjunction with HTTPS. For more information about OAuth2-based authentication for SaaS customers, please see the STEP Authentication Guide.</p><h1>Versioning</h1><p>The STEP REST API V2 is versioned using semantic versioning. Stibo Systems reserve the right to make non-breaking, minor / patch changes in any release without warning and clients must be coded / configured to be 'tolerant' and capable of handling such changes.</p><p>Examples of breaking, major changes:</p><ul><li>Renaming of a property</li><li>Removal of a property</li><li>Property type change</li><li>Addition of new property required for write operations</li><li>Marking existing property as required for write operations</li><li>Removal of resource or resource operation</li><li>Materially different behavior for existing resource operation</li></ul><p>Examples of non-breaking, minor / patch changes:</p><ul><li>Addition of new properties in request responses</li><li>Addition of new query parameter not required for write operations</li><li>Addition of new resource or resource operation</li><li>Bug fixes that do not change the schema or resource operations as described here</li><li>Inclusion of a response body for resource operations specified to return a 200 response with no body</li><li>Change of response &quot;Model&quot; / &quot;schema&quot; to type extending the previously specified type</li><li>Renaming a &quot;Model&quot; / &quot;schema&quot; type</li></ul><p>In addition, error message texts may change without warning within the same version. Client program logic should not depend upon the message content.</p><h1>Error Handling</h1><p>The STEP REST API V2 responds with standard HTTP status codes, with 2** responses indicating a success, 4** responses indicating a client error and 5** indicating a server error. Notice that this specification does not specify common error responses like 500 (internal server error) or 401 (unauthorized) for the individual resource operations. Clients should however be capable of handling such responses.</p><p>Error responses have a JSON response body (see Error schema below) containing HTTP status code information in addition to a message providing details about the error. As mentioned above, client program logic should not depend upon the message content.</p><p>The specific status codes used in the API are:</p><ul><li>200 (OK): Success, response may or may not have a body</li><li>201 (Created): Entity successfully created, response may or may not have a body</li><li>400 (Bad request): The server cannot or will not process the request due to an apparent client error</li><li>401 (Unauthorized): Returned only in relation to failed authentication</li><li>404 (Not Found): Returned only in relation to objects specified via path parameters (variable parts of the URL). If STEP objects referenced in request bodies or via query parameters cannot be found, the response will be 400.</li><li>429 (Too Many Requests): Clients are per default limited to 100 requests per second. Returned if the rate limit is exceeded.</li><li>500 (Internal Server Error): Unexpected error (could potentially cover an issue that rightfully should be a 400)</li></ul>

    The version of the OpenAPI document: 1.3.0
    Generated by OpenAPI Generator (https://openapi-generator.tech)

    Do not edit the class manually.
"""  # noqa: E501


# import models into model package
from step_rest_client.models.amount import Amount
from step_rest_client.models.and_condition import AndCondition
from step_rest_client.models.approval_response import ApprovalResponse
from step_rest_client.models.approval_status import ApprovalStatus
from step_rest_client.models.asset import Asset
from step_rest_client.models.attribute import Attribute
from step_rest_client.models.attribute_link import AttributeLink
from step_rest_client.models.background_process import BackgroundProcess
from step_rest_client.models.background_process_attachment_metadata import BackgroundProcessAttachmentMetadata
from step_rest_client.models.background_process_identification import BackgroundProcessIdentification
from step_rest_client.models.background_process_type import BackgroundProcessType
from step_rest_client.models.classification import Classification
from step_rest_client.models.condition import Condition
from step_rest_client.models.data_container import DataContainer
from step_rest_client.models.data_container_entry import DataContainerEntry
from step_rest_client.models.data_container_object_condition import DataContainerObjectCondition
from step_rest_client.models.data_container_type import DataContainerType
from step_rest_client.models.data_type_group import DataTypeGroup
from step_rest_client.models.endpoint_statistics import EndpointStatistics
from step_rest_client.models.endpoint_status import EndpointStatus
from step_rest_client.models.entity import Entity
from step_rest_client.models.error import Error
from step_rest_client.models.event_processor import EventProcessor
from step_rest_client.models.event_processor_statistics import EventProcessorStatistics
from step_rest_client.models.event_processor_status import EventProcessorStatus
from step_rest_client.models.event_queue_status import EventQueueStatus
from step_rest_client.models.execution_report_entry import ExecutionReportEntry
from step_rest_client.models.export_specification import ExportSpecification
from step_rest_client.models.find_similar_business_rule_result import FindSimilarBusinessRuleResult
from step_rest_client.models.find_similar_entities_request import FindSimilarEntitiesRequest
from step_rest_client.models.find_similar_entities_response import FindSimilarEntitiesResponse
from step_rest_client.models.find_similar_entities_response_record import FindSimilarEntitiesResponseRecord
from step_rest_client.models.find_similar_execution_report import FindSimilarExecutionReport
from step_rest_client.models.gateway_integration_endpoint import GatewayIntegrationEndpoint
from step_rest_client.models.has_data_container_object_condition import HasDataContainerObjectCondition
from step_rest_client.models.has_reference_to_condition import HasReferenceToCondition
from step_rest_client.models.id_condition import IdCondition
from step_rest_client.models.inbound_integration_endpoint import InboundIntegrationEndpoint
from step_rest_client.models.incoming_reference_entry import IncomingReferenceEntry
from step_rest_client.models.list_of_values import ListOfValues
from step_rest_client.models.list_of_values_entry import ListOfValuesEntry
from step_rest_client.models.lov_value_condition import LovValueCondition
from step_rest_client.models.match_and_merge_execution_report import MatchAndMergeExecutionReport
from step_rest_client.models.match_and_merge_general_execution_report import MatchAndMergeGeneralExecutionReport
from step_rest_client.models.match_and_merge_potential_duplicate import MatchAndMergePotentialDuplicate
from step_rest_client.models.match_and_merge_record_in import MatchAndMergeRecordIn
from step_rest_client.models.match_and_merge_record_out import MatchAndMergeRecordOut
from step_rest_client.models.match_and_merge_response import MatchAndMergeResponse
from step_rest_client.models.multi_data_container import MultiDataContainer
from step_rest_client.models.multi_reference import MultiReference
from step_rest_client.models.multi_value import MultiValue
from step_rest_client.models.name_condition import NameCondition
from step_rest_client.models.numeric_value_condition import NumericValueCondition
from step_rest_client.models.object_type import ObjectType
from step_rest_client.models.object_type_condition import ObjectTypeCondition
from step_rest_client.models.or_condition import OrCondition
from step_rest_client.models.outbound_integration_endpoint import OutboundIntegrationEndpoint
from step_rest_client.models.product import Product
from step_rest_client.models.query import Query
from step_rest_client.models.query_result import QueryResult
from step_rest_client.models.reference import Reference
from step_rest_client.models.reference_entry import ReferenceEntry
from step_rest_client.models.reference_metadata_condition import ReferenceMetadataCondition
from step_rest_client.models.reference_type import ReferenceType
from step_rest_client.models.rejected_by_business_condition import RejectedByBusinessCondition
from step_rest_client.models.simple_below_condition import SimpleBelowCondition
from step_rest_client.models.single_data_container import SingleDataContainer
from step_rest_client.models.single_reference import SingleReference
from step_rest_client.models.single_value import SingleValue
from step_rest_client.models.status_flag import StatusFlag
from step_rest_client.models.text_value_condition import TextValueCondition
from step_rest_client.models.trigger_workflow_event import TriggerWorkflowEvent
from step_rest_client.models.unit import Unit
from step_rest_client.models.value import Value
from step_rest_client.models.value_entry import ValueEntry
from step_rest_client.models.workflow import Workflow
from step_rest_client.models.workflow_event import WorkflowEvent
from step_rest_client.models.workflow_instance import WorkflowInstance
from step_rest_client.models.workflow_instance_creation import WorkflowInstanceCreation
from step_rest_client.models.workflow_node import WorkflowNode
from step_rest_client.models.workflow_task import WorkflowTask
from step_rest_client.models.workflow_task_query import WorkflowTaskQuery
