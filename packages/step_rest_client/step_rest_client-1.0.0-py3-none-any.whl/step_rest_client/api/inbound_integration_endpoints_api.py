# coding: utf-8

"""
    STEP REST API V2

    <h1>About</h1><p>The STEP REST API V2 provides read and write access to a set of core STEP objects using the HTTP operations GET, PUT, POST, PATCH and DELETE.</p><h1>Resource Representation</h1><p>With the exception of a few resource operations for retrieving and uploading binary data, all request and response bodies are JSON, compliant with the schema documented here.</p><h1>Context and Workspace</h1><p>All requests are handled in a specific STEP context and workspace and both can be specified via query parameters available for all resource operations. A context must always be specified while requests per default will be handled in the &quot;Main&quot; workspace.</p><h1>Polymorphism</h1><p>In STEP, attributes, reference types and data container types can all be either single- or multivalued. The STEP REST API V2 uses polymorphism to address this complexity with resources that include values, references and data containers specified to produce and consume a common &quot;abstract&quot; supertype that always will be one of either the single- or multivalued subtype.<br/>As an example, the GET /entities/{id}/values/{attributeId} resource operation is specified to return a &quot;Value&quot; but as evident from the model, the &quot;Value&quot; will always be &quot;oneOf&quot; either &quot;SingleValue&quot;, that has a &quot;value&quot; property for which the value is an object, or &quot;MultiValue&quot;, that has a &quot;values&quot; property for which the value is an array.<br/>Clients are advised to use the presence or absence of the plural array property (&quot;values&quot;, &quot;references&quot; and &quot;dataContainers&quot;) to determine the concrete type.</p><h1>Authentication</h1><p>The REST API is protected by HTTP Basic Authentication or if OAuth2-based authentication is enabled (SaaS customers only), by Bearer Authentication. With Basic Authentication, user name and password are supplied with each request and it is therefore highly recommended to only use the API in conjunction with HTTPS. For more information about OAuth2-based authentication for SaaS customers, please see the STEP Authentication Guide.</p><h1>Versioning</h1><p>The STEP REST API V2 is versioned using semantic versioning. Stibo Systems reserve the right to make non-breaking, minor / patch changes in any release without warning and clients must be coded / configured to be 'tolerant' and capable of handling such changes.</p><p>Examples of breaking, major changes:</p><ul><li>Renaming of a property</li><li>Removal of a property</li><li>Property type change</li><li>Addition of new property required for write operations</li><li>Marking existing property as required for write operations</li><li>Removal of resource or resource operation</li><li>Materially different behavior for existing resource operation</li></ul><p>Examples of non-breaking, minor / patch changes:</p><ul><li>Addition of new properties in request responses</li><li>Addition of new query parameter not required for write operations</li><li>Addition of new resource or resource operation</li><li>Bug fixes that do not change the schema or resource operations as described here</li><li>Inclusion of a response body for resource operations specified to return a 200 response with no body</li><li>Change of response &quot;Model&quot; / &quot;schema&quot; to type extending the previously specified type</li><li>Renaming a &quot;Model&quot; / &quot;schema&quot; type</li></ul><p>In addition, error message texts may change without warning within the same version. Client program logic should not depend upon the message content.</p><h1>Error Handling</h1><p>The STEP REST API V2 responds with standard HTTP status codes, with 2** responses indicating a success, 4** responses indicating a client error and 5** indicating a server error. Notice that this specification does not specify common error responses like 500 (internal server error) or 401 (unauthorized) for the individual resource operations. Clients should however be capable of handling such responses.</p><p>Error responses have a JSON response body (see Error schema below) containing HTTP status code information in addition to a message providing details about the error. As mentioned above, client program logic should not depend upon the message content.</p><p>The specific status codes used in the API are:</p><ul><li>200 (OK): Success, response may or may not have a body</li><li>201 (Created): Entity successfully created, response may or may not have a body</li><li>400 (Bad request): The server cannot or will not process the request due to an apparent client error</li><li>401 (Unauthorized): Returned only in relation to failed authentication</li><li>404 (Not Found): Returned only in relation to objects specified via path parameters (variable parts of the URL). If STEP objects referenced in request bodies or via query parameters cannot be found, the response will be 400.</li><li>429 (Too Many Requests): Clients are per default limited to 100 requests per second. Returned if the rate limit is exceeded.</li><li>500 (Internal Server Error): Unexpected error (could potentially cover an issue that rightfully should be a 400)</li></ul>

    The version of the OpenAPI document: 1.3.0
    Generated by OpenAPI Generator (https://openapi-generator.tech)

    Do not edit the class manually.
"""  # noqa: E501

import warnings
from pydantic import validate_call, Field, StrictFloat, StrictStr, StrictInt
from typing import Any, Dict, List, Optional, Tuple, Union
from typing_extensions import Annotated

from pydantic import Field, StrictBytes, StrictStr, field_validator
from typing import List, Optional, Tuple, Union
from typing_extensions import Annotated
from step_rest_client.models.endpoint_statistics import EndpointStatistics
from step_rest_client.models.endpoint_status import EndpointStatus
from step_rest_client.models.execution_report_entry import ExecutionReportEntry
from step_rest_client.models.inbound_integration_endpoint import InboundIntegrationEndpoint

from step_rest_client.api_client import ApiClient, RequestSerialized
from step_rest_client.api_response import ApiResponse
from step_rest_client.rest import RESTResponseType


class InboundIntegrationEndpointsApi:
    """NOTE: This class is auto generated by OpenAPI Generator
    Ref: https://openapi-generator.tech

    Do not edit the class manually.
    """

    def __init__(self, api_client=None) -> None:
        if api_client is None:
            api_client = ApiClient.get_default()
        self.api_client = api_client


    @validate_call
    def inbound_integration_endpoints_get(
        self,
        context: Annotated[StrictStr, Field(description="ID of the context in which to perform the operation")],
        workspace: Annotated[Optional[StrictStr], Field(description="ID of the workspace in which to perform the operation. Defaults to \"Main\".")] = None,
        _request_timeout: Union[
            None,
            Annotated[StrictFloat, Field(gt=0)],
            Tuple[
                Annotated[StrictFloat, Field(gt=0)],
                Annotated[StrictFloat, Field(gt=0)]
            ]
        ] = None,
        _request_auth: Optional[Dict[StrictStr, Any]] = None,
        _content_type: Optional[StrictStr] = None,
        _headers: Optional[Dict[StrictStr, Any]] = None,
        _host_index: Annotated[StrictInt, Field(ge=0, le=0)] = 0,
    ) -> List[InboundIntegrationEndpoint]:
        """Returns basic inbound integration endpoint representations

        Operation for retrieving an array of basic inbound integration endpoint representations for all accessible endpoints

        :param context: ID of the context in which to perform the operation (required)
        :type context: str
        :param workspace: ID of the workspace in which to perform the operation. Defaults to \"Main\".
        :type workspace: str
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :type _request_timeout: int, tuple(int, int), optional
        :param _request_auth: set to override the auth_settings for an a single
                              request; this effectively ignores the
                              authentication in the spec for a single request.
        :type _request_auth: dict, optional
        :param _content_type: force content-type for the request.
        :type _content_type: str, Optional
        :param _headers: set to override the headers for a single
                         request; this effectively ignores the headers
                         in the spec for a single request.
        :type _headers: dict, optional
        :param _host_index: set to override the host_index for a single
                            request; this effectively ignores the host_index
                            in the spec for a single request.
        :type _host_index: int, optional
        :return: Returns the result object.
        """ # noqa: E501

        _param = self._inbound_integration_endpoints_get_serialize(
            context=context,
            workspace=workspace,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "List[InboundIntegrationEndpoint]",
            '400': "Error",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        response_data.read()
        return self.api_client.response_deserialize(
            response_data=response_data,
            response_types_map=_response_types_map,
        ).data


    @validate_call
    def inbound_integration_endpoints_get_with_http_info(
        self,
        context: Annotated[StrictStr, Field(description="ID of the context in which to perform the operation")],
        workspace: Annotated[Optional[StrictStr], Field(description="ID of the workspace in which to perform the operation. Defaults to \"Main\".")] = None,
        _request_timeout: Union[
            None,
            Annotated[StrictFloat, Field(gt=0)],
            Tuple[
                Annotated[StrictFloat, Field(gt=0)],
                Annotated[StrictFloat, Field(gt=0)]
            ]
        ] = None,
        _request_auth: Optional[Dict[StrictStr, Any]] = None,
        _content_type: Optional[StrictStr] = None,
        _headers: Optional[Dict[StrictStr, Any]] = None,
        _host_index: Annotated[StrictInt, Field(ge=0, le=0)] = 0,
    ) -> ApiResponse[List[InboundIntegrationEndpoint]]:
        """Returns basic inbound integration endpoint representations

        Operation for retrieving an array of basic inbound integration endpoint representations for all accessible endpoints

        :param context: ID of the context in which to perform the operation (required)
        :type context: str
        :param workspace: ID of the workspace in which to perform the operation. Defaults to \"Main\".
        :type workspace: str
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :type _request_timeout: int, tuple(int, int), optional
        :param _request_auth: set to override the auth_settings for an a single
                              request; this effectively ignores the
                              authentication in the spec for a single request.
        :type _request_auth: dict, optional
        :param _content_type: force content-type for the request.
        :type _content_type: str, Optional
        :param _headers: set to override the headers for a single
                         request; this effectively ignores the headers
                         in the spec for a single request.
        :type _headers: dict, optional
        :param _host_index: set to override the host_index for a single
                            request; this effectively ignores the host_index
                            in the spec for a single request.
        :type _host_index: int, optional
        :return: Returns the result object.
        """ # noqa: E501

        _param = self._inbound_integration_endpoints_get_serialize(
            context=context,
            workspace=workspace,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "List[InboundIntegrationEndpoint]",
            '400': "Error",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        response_data.read()
        return self.api_client.response_deserialize(
            response_data=response_data,
            response_types_map=_response_types_map,
        )


    @validate_call
    def inbound_integration_endpoints_get_without_preload_content(
        self,
        context: Annotated[StrictStr, Field(description="ID of the context in which to perform the operation")],
        workspace: Annotated[Optional[StrictStr], Field(description="ID of the workspace in which to perform the operation. Defaults to \"Main\".")] = None,
        _request_timeout: Union[
            None,
            Annotated[StrictFloat, Field(gt=0)],
            Tuple[
                Annotated[StrictFloat, Field(gt=0)],
                Annotated[StrictFloat, Field(gt=0)]
            ]
        ] = None,
        _request_auth: Optional[Dict[StrictStr, Any]] = None,
        _content_type: Optional[StrictStr] = None,
        _headers: Optional[Dict[StrictStr, Any]] = None,
        _host_index: Annotated[StrictInt, Field(ge=0, le=0)] = 0,
    ) -> RESTResponseType:
        """Returns basic inbound integration endpoint representations

        Operation for retrieving an array of basic inbound integration endpoint representations for all accessible endpoints

        :param context: ID of the context in which to perform the operation (required)
        :type context: str
        :param workspace: ID of the workspace in which to perform the operation. Defaults to \"Main\".
        :type workspace: str
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :type _request_timeout: int, tuple(int, int), optional
        :param _request_auth: set to override the auth_settings for an a single
                              request; this effectively ignores the
                              authentication in the spec for a single request.
        :type _request_auth: dict, optional
        :param _content_type: force content-type for the request.
        :type _content_type: str, Optional
        :param _headers: set to override the headers for a single
                         request; this effectively ignores the headers
                         in the spec for a single request.
        :type _headers: dict, optional
        :param _host_index: set to override the host_index for a single
                            request; this effectively ignores the host_index
                            in the spec for a single request.
        :type _host_index: int, optional
        :return: Returns the result object.
        """ # noqa: E501

        _param = self._inbound_integration_endpoints_get_serialize(
            context=context,
            workspace=workspace,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "List[InboundIntegrationEndpoint]",
            '400': "Error",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        return response_data.response


    def _inbound_integration_endpoints_get_serialize(
        self,
        context,
        workspace,
        _request_auth,
        _content_type,
        _headers,
        _host_index,
    ) -> RequestSerialized:

        _host = None

        _collection_formats: Dict[str, str] = {
        }

        _path_params: Dict[str, str] = {}
        _query_params: List[Tuple[str, str]] = []
        _header_params: Dict[str, Optional[str]] = _headers or {}
        _form_params: List[Tuple[str, str]] = []
        _files: Dict[
            str, Union[str, bytes, List[str], List[bytes], List[Tuple[str, bytes]]]
        ] = {}
        _body_params: Optional[bytes] = None

        # process the path parameters
        # process the query parameters
        if context is not None:
            
            _query_params.append(('context', context))
            
        if workspace is not None:
            
            _query_params.append(('workspace', workspace))
            
        # process the header parameters
        # process the form parameters
        # process the body parameter


        # set the HTTP header `Accept`
        if 'Accept' not in _header_params:
            _header_params['Accept'] = self.api_client.select_header_accept(
                [
                    'application/json'
                ]
            )


        # authentication setting
        _auth_settings: List[str] = [
            'basicAuth'
        ]

        return self.api_client.param_serialize(
            method='GET',
            resource_path='/inbound-integration-endpoints',
            path_params=_path_params,
            query_params=_query_params,
            header_params=_header_params,
            body=_body_params,
            post_params=_form_params,
            files=_files,
            auth_settings=_auth_settings,
            collection_formats=_collection_formats,
            _host=_host,
            _request_auth=_request_auth
        )




    @validate_call
    def inbound_integration_endpoints_id_disable_post(
        self,
        id: Annotated[StrictStr, Field(description="ID of the inbound integration endpoint to disable")],
        context: Annotated[StrictStr, Field(description="ID of the context in which to perform the operation")],
        workspace: Annotated[Optional[StrictStr], Field(description="ID of the workspace in which to perform the operation. Defaults to \"Main\".")] = None,
        _request_timeout: Union[
            None,
            Annotated[StrictFloat, Field(gt=0)],
            Tuple[
                Annotated[StrictFloat, Field(gt=0)],
                Annotated[StrictFloat, Field(gt=0)]
            ]
        ] = None,
        _request_auth: Optional[Dict[StrictStr, Any]] = None,
        _content_type: Optional[StrictStr] = None,
        _headers: Optional[Dict[StrictStr, Any]] = None,
        _host_index: Annotated[StrictInt, Field(ge=0, le=0)] = 0,
    ) -> None:
        """Disables the specified inbound integration endpoint

        Operation for disabling an inbound integration endpoint. Can be called regardless of the endpoint status.

        :param id: ID of the inbound integration endpoint to disable (required)
        :type id: str
        :param context: ID of the context in which to perform the operation (required)
        :type context: str
        :param workspace: ID of the workspace in which to perform the operation. Defaults to \"Main\".
        :type workspace: str
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :type _request_timeout: int, tuple(int, int), optional
        :param _request_auth: set to override the auth_settings for an a single
                              request; this effectively ignores the
                              authentication in the spec for a single request.
        :type _request_auth: dict, optional
        :param _content_type: force content-type for the request.
        :type _content_type: str, Optional
        :param _headers: set to override the headers for a single
                         request; this effectively ignores the headers
                         in the spec for a single request.
        :type _headers: dict, optional
        :param _host_index: set to override the host_index for a single
                            request; this effectively ignores the host_index
                            in the spec for a single request.
        :type _host_index: int, optional
        :return: Returns the result object.
        """ # noqa: E501

        _param = self._inbound_integration_endpoints_id_disable_post_serialize(
            id=id,
            context=context,
            workspace=workspace,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': None,
            '400': "Error",
            '404': "Error",
            '503': "Error",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        response_data.read()
        return self.api_client.response_deserialize(
            response_data=response_data,
            response_types_map=_response_types_map,
        ).data


    @validate_call
    def inbound_integration_endpoints_id_disable_post_with_http_info(
        self,
        id: Annotated[StrictStr, Field(description="ID of the inbound integration endpoint to disable")],
        context: Annotated[StrictStr, Field(description="ID of the context in which to perform the operation")],
        workspace: Annotated[Optional[StrictStr], Field(description="ID of the workspace in which to perform the operation. Defaults to \"Main\".")] = None,
        _request_timeout: Union[
            None,
            Annotated[StrictFloat, Field(gt=0)],
            Tuple[
                Annotated[StrictFloat, Field(gt=0)],
                Annotated[StrictFloat, Field(gt=0)]
            ]
        ] = None,
        _request_auth: Optional[Dict[StrictStr, Any]] = None,
        _content_type: Optional[StrictStr] = None,
        _headers: Optional[Dict[StrictStr, Any]] = None,
        _host_index: Annotated[StrictInt, Field(ge=0, le=0)] = 0,
    ) -> ApiResponse[None]:
        """Disables the specified inbound integration endpoint

        Operation for disabling an inbound integration endpoint. Can be called regardless of the endpoint status.

        :param id: ID of the inbound integration endpoint to disable (required)
        :type id: str
        :param context: ID of the context in which to perform the operation (required)
        :type context: str
        :param workspace: ID of the workspace in which to perform the operation. Defaults to \"Main\".
        :type workspace: str
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :type _request_timeout: int, tuple(int, int), optional
        :param _request_auth: set to override the auth_settings for an a single
                              request; this effectively ignores the
                              authentication in the spec for a single request.
        :type _request_auth: dict, optional
        :param _content_type: force content-type for the request.
        :type _content_type: str, Optional
        :param _headers: set to override the headers for a single
                         request; this effectively ignores the headers
                         in the spec for a single request.
        :type _headers: dict, optional
        :param _host_index: set to override the host_index for a single
                            request; this effectively ignores the host_index
                            in the spec for a single request.
        :type _host_index: int, optional
        :return: Returns the result object.
        """ # noqa: E501

        _param = self._inbound_integration_endpoints_id_disable_post_serialize(
            id=id,
            context=context,
            workspace=workspace,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': None,
            '400': "Error",
            '404': "Error",
            '503': "Error",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        response_data.read()
        return self.api_client.response_deserialize(
            response_data=response_data,
            response_types_map=_response_types_map,
        )


    @validate_call
    def inbound_integration_endpoints_id_disable_post_without_preload_content(
        self,
        id: Annotated[StrictStr, Field(description="ID of the inbound integration endpoint to disable")],
        context: Annotated[StrictStr, Field(description="ID of the context in which to perform the operation")],
        workspace: Annotated[Optional[StrictStr], Field(description="ID of the workspace in which to perform the operation. Defaults to \"Main\".")] = None,
        _request_timeout: Union[
            None,
            Annotated[StrictFloat, Field(gt=0)],
            Tuple[
                Annotated[StrictFloat, Field(gt=0)],
                Annotated[StrictFloat, Field(gt=0)]
            ]
        ] = None,
        _request_auth: Optional[Dict[StrictStr, Any]] = None,
        _content_type: Optional[StrictStr] = None,
        _headers: Optional[Dict[StrictStr, Any]] = None,
        _host_index: Annotated[StrictInt, Field(ge=0, le=0)] = 0,
    ) -> RESTResponseType:
        """Disables the specified inbound integration endpoint

        Operation for disabling an inbound integration endpoint. Can be called regardless of the endpoint status.

        :param id: ID of the inbound integration endpoint to disable (required)
        :type id: str
        :param context: ID of the context in which to perform the operation (required)
        :type context: str
        :param workspace: ID of the workspace in which to perform the operation. Defaults to \"Main\".
        :type workspace: str
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :type _request_timeout: int, tuple(int, int), optional
        :param _request_auth: set to override the auth_settings for an a single
                              request; this effectively ignores the
                              authentication in the spec for a single request.
        :type _request_auth: dict, optional
        :param _content_type: force content-type for the request.
        :type _content_type: str, Optional
        :param _headers: set to override the headers for a single
                         request; this effectively ignores the headers
                         in the spec for a single request.
        :type _headers: dict, optional
        :param _host_index: set to override the host_index for a single
                            request; this effectively ignores the host_index
                            in the spec for a single request.
        :type _host_index: int, optional
        :return: Returns the result object.
        """ # noqa: E501

        _param = self._inbound_integration_endpoints_id_disable_post_serialize(
            id=id,
            context=context,
            workspace=workspace,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': None,
            '400': "Error",
            '404': "Error",
            '503': "Error",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        return response_data.response


    def _inbound_integration_endpoints_id_disable_post_serialize(
        self,
        id,
        context,
        workspace,
        _request_auth,
        _content_type,
        _headers,
        _host_index,
    ) -> RequestSerialized:

        _host = None

        _collection_formats: Dict[str, str] = {
        }

        _path_params: Dict[str, str] = {}
        _query_params: List[Tuple[str, str]] = []
        _header_params: Dict[str, Optional[str]] = _headers or {}
        _form_params: List[Tuple[str, str]] = []
        _files: Dict[
            str, Union[str, bytes, List[str], List[bytes], List[Tuple[str, bytes]]]
        ] = {}
        _body_params: Optional[bytes] = None

        # process the path parameters
        if id is not None:
            _path_params['id'] = id
        # process the query parameters
        if context is not None:
            
            _query_params.append(('context', context))
            
        if workspace is not None:
            
            _query_params.append(('workspace', workspace))
            
        # process the header parameters
        # process the form parameters
        # process the body parameter


        # set the HTTP header `Accept`
        if 'Accept' not in _header_params:
            _header_params['Accept'] = self.api_client.select_header_accept(
                [
                    'application/json'
                ]
            )


        # authentication setting
        _auth_settings: List[str] = [
            'basicAuth'
        ]

        return self.api_client.param_serialize(
            method='POST',
            resource_path='/inbound-integration-endpoints/{id}/disable',
            path_params=_path_params,
            query_params=_query_params,
            header_params=_header_params,
            body=_body_params,
            post_params=_form_params,
            files=_files,
            auth_settings=_auth_settings,
            collection_formats=_collection_formats,
            _host=_host,
            _request_auth=_request_auth
        )




    @validate_call
    def inbound_integration_endpoints_id_enable_post(
        self,
        id: Annotated[StrictStr, Field(description="ID of the inbound integration endpoint to enable")],
        context: Annotated[StrictStr, Field(description="ID of the context in which to perform the operation")],
        workspace: Annotated[Optional[StrictStr], Field(description="ID of the workspace in which to perform the operation. Defaults to \"Main\".")] = None,
        _request_timeout: Union[
            None,
            Annotated[StrictFloat, Field(gt=0)],
            Tuple[
                Annotated[StrictFloat, Field(gt=0)],
                Annotated[StrictFloat, Field(gt=0)]
            ]
        ] = None,
        _request_auth: Optional[Dict[StrictStr, Any]] = None,
        _content_type: Optional[StrictStr] = None,
        _headers: Optional[Dict[StrictStr, Any]] = None,
        _host_index: Annotated[StrictInt, Field(ge=0, le=0)] = 0,
    ) -> None:
        """Enables the specified inbound integration endpoint

        Operation for enabling an inbound integration endpoint. Can be called regardless of the endpoint status. Endpoints with status 'failed' will be resumed.

        :param id: ID of the inbound integration endpoint to enable (required)
        :type id: str
        :param context: ID of the context in which to perform the operation (required)
        :type context: str
        :param workspace: ID of the workspace in which to perform the operation. Defaults to \"Main\".
        :type workspace: str
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :type _request_timeout: int, tuple(int, int), optional
        :param _request_auth: set to override the auth_settings for an a single
                              request; this effectively ignores the
                              authentication in the spec for a single request.
        :type _request_auth: dict, optional
        :param _content_type: force content-type for the request.
        :type _content_type: str, Optional
        :param _headers: set to override the headers for a single
                         request; this effectively ignores the headers
                         in the spec for a single request.
        :type _headers: dict, optional
        :param _host_index: set to override the host_index for a single
                            request; this effectively ignores the host_index
                            in the spec for a single request.
        :type _host_index: int, optional
        :return: Returns the result object.
        """ # noqa: E501

        _param = self._inbound_integration_endpoints_id_enable_post_serialize(
            id=id,
            context=context,
            workspace=workspace,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': None,
            '400': "Error",
            '404': "Error",
            '503': "Error",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        response_data.read()
        return self.api_client.response_deserialize(
            response_data=response_data,
            response_types_map=_response_types_map,
        ).data


    @validate_call
    def inbound_integration_endpoints_id_enable_post_with_http_info(
        self,
        id: Annotated[StrictStr, Field(description="ID of the inbound integration endpoint to enable")],
        context: Annotated[StrictStr, Field(description="ID of the context in which to perform the operation")],
        workspace: Annotated[Optional[StrictStr], Field(description="ID of the workspace in which to perform the operation. Defaults to \"Main\".")] = None,
        _request_timeout: Union[
            None,
            Annotated[StrictFloat, Field(gt=0)],
            Tuple[
                Annotated[StrictFloat, Field(gt=0)],
                Annotated[StrictFloat, Field(gt=0)]
            ]
        ] = None,
        _request_auth: Optional[Dict[StrictStr, Any]] = None,
        _content_type: Optional[StrictStr] = None,
        _headers: Optional[Dict[StrictStr, Any]] = None,
        _host_index: Annotated[StrictInt, Field(ge=0, le=0)] = 0,
    ) -> ApiResponse[None]:
        """Enables the specified inbound integration endpoint

        Operation for enabling an inbound integration endpoint. Can be called regardless of the endpoint status. Endpoints with status 'failed' will be resumed.

        :param id: ID of the inbound integration endpoint to enable (required)
        :type id: str
        :param context: ID of the context in which to perform the operation (required)
        :type context: str
        :param workspace: ID of the workspace in which to perform the operation. Defaults to \"Main\".
        :type workspace: str
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :type _request_timeout: int, tuple(int, int), optional
        :param _request_auth: set to override the auth_settings for an a single
                              request; this effectively ignores the
                              authentication in the spec for a single request.
        :type _request_auth: dict, optional
        :param _content_type: force content-type for the request.
        :type _content_type: str, Optional
        :param _headers: set to override the headers for a single
                         request; this effectively ignores the headers
                         in the spec for a single request.
        :type _headers: dict, optional
        :param _host_index: set to override the host_index for a single
                            request; this effectively ignores the host_index
                            in the spec for a single request.
        :type _host_index: int, optional
        :return: Returns the result object.
        """ # noqa: E501

        _param = self._inbound_integration_endpoints_id_enable_post_serialize(
            id=id,
            context=context,
            workspace=workspace,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': None,
            '400': "Error",
            '404': "Error",
            '503': "Error",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        response_data.read()
        return self.api_client.response_deserialize(
            response_data=response_data,
            response_types_map=_response_types_map,
        )


    @validate_call
    def inbound_integration_endpoints_id_enable_post_without_preload_content(
        self,
        id: Annotated[StrictStr, Field(description="ID of the inbound integration endpoint to enable")],
        context: Annotated[StrictStr, Field(description="ID of the context in which to perform the operation")],
        workspace: Annotated[Optional[StrictStr], Field(description="ID of the workspace in which to perform the operation. Defaults to \"Main\".")] = None,
        _request_timeout: Union[
            None,
            Annotated[StrictFloat, Field(gt=0)],
            Tuple[
                Annotated[StrictFloat, Field(gt=0)],
                Annotated[StrictFloat, Field(gt=0)]
            ]
        ] = None,
        _request_auth: Optional[Dict[StrictStr, Any]] = None,
        _content_type: Optional[StrictStr] = None,
        _headers: Optional[Dict[StrictStr, Any]] = None,
        _host_index: Annotated[StrictInt, Field(ge=0, le=0)] = 0,
    ) -> RESTResponseType:
        """Enables the specified inbound integration endpoint

        Operation for enabling an inbound integration endpoint. Can be called regardless of the endpoint status. Endpoints with status 'failed' will be resumed.

        :param id: ID of the inbound integration endpoint to enable (required)
        :type id: str
        :param context: ID of the context in which to perform the operation (required)
        :type context: str
        :param workspace: ID of the workspace in which to perform the operation. Defaults to \"Main\".
        :type workspace: str
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :type _request_timeout: int, tuple(int, int), optional
        :param _request_auth: set to override the auth_settings for an a single
                              request; this effectively ignores the
                              authentication in the spec for a single request.
        :type _request_auth: dict, optional
        :param _content_type: force content-type for the request.
        :type _content_type: str, Optional
        :param _headers: set to override the headers for a single
                         request; this effectively ignores the headers
                         in the spec for a single request.
        :type _headers: dict, optional
        :param _host_index: set to override the host_index for a single
                            request; this effectively ignores the host_index
                            in the spec for a single request.
        :type _host_index: int, optional
        :return: Returns the result object.
        """ # noqa: E501

        _param = self._inbound_integration_endpoints_id_enable_post_serialize(
            id=id,
            context=context,
            workspace=workspace,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': None,
            '400': "Error",
            '404': "Error",
            '503': "Error",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        return response_data.response


    def _inbound_integration_endpoints_id_enable_post_serialize(
        self,
        id,
        context,
        workspace,
        _request_auth,
        _content_type,
        _headers,
        _host_index,
    ) -> RequestSerialized:

        _host = None

        _collection_formats: Dict[str, str] = {
        }

        _path_params: Dict[str, str] = {}
        _query_params: List[Tuple[str, str]] = []
        _header_params: Dict[str, Optional[str]] = _headers or {}
        _form_params: List[Tuple[str, str]] = []
        _files: Dict[
            str, Union[str, bytes, List[str], List[bytes], List[Tuple[str, bytes]]]
        ] = {}
        _body_params: Optional[bytes] = None

        # process the path parameters
        if id is not None:
            _path_params['id'] = id
        # process the query parameters
        if context is not None:
            
            _query_params.append(('context', context))
            
        if workspace is not None:
            
            _query_params.append(('workspace', workspace))
            
        # process the header parameters
        # process the form parameters
        # process the body parameter


        # set the HTTP header `Accept`
        if 'Accept' not in _header_params:
            _header_params['Accept'] = self.api_client.select_header_accept(
                [
                    'application/json'
                ]
            )


        # authentication setting
        _auth_settings: List[str] = [
            'basicAuth'
        ]

        return self.api_client.param_serialize(
            method='POST',
            resource_path='/inbound-integration-endpoints/{id}/enable',
            path_params=_path_params,
            query_params=_query_params,
            header_params=_header_params,
            body=_body_params,
            post_params=_form_params,
            files=_files,
            auth_settings=_auth_settings,
            collection_formats=_collection_formats,
            _host=_host,
            _request_auth=_request_auth
        )




    @validate_call
    def inbound_integration_endpoints_id_execution_report_get(
        self,
        id: Annotated[StrictStr, Field(description="ID of the inbound integration endpoint for which to retrieve the execution report")],
        context: Annotated[StrictStr, Field(description="ID of the context in which to perform the operation")],
        workspace: Annotated[Optional[StrictStr], Field(description="ID of the workspace in which to perform the operation. Defaults to \"Main\".")] = None,
        _request_timeout: Union[
            None,
            Annotated[StrictFloat, Field(gt=0)],
            Tuple[
                Annotated[StrictFloat, Field(gt=0)],
                Annotated[StrictFloat, Field(gt=0)]
            ]
        ] = None,
        _request_auth: Optional[Dict[StrictStr, Any]] = None,
        _content_type: Optional[StrictStr] = None,
        _headers: Optional[Dict[StrictStr, Any]] = None,
        _host_index: Annotated[StrictInt, Field(ge=0, le=0)] = 0,
    ) -> List[ExecutionReportEntry]:
        """Returns the execution report for the specified inbound integration endpoint

        Operation for retrieving the execution report for the main process of a specific inbound integration endpoint

        :param id: ID of the inbound integration endpoint for which to retrieve the execution report (required)
        :type id: str
        :param context: ID of the context in which to perform the operation (required)
        :type context: str
        :param workspace: ID of the workspace in which to perform the operation. Defaults to \"Main\".
        :type workspace: str
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :type _request_timeout: int, tuple(int, int), optional
        :param _request_auth: set to override the auth_settings for an a single
                              request; this effectively ignores the
                              authentication in the spec for a single request.
        :type _request_auth: dict, optional
        :param _content_type: force content-type for the request.
        :type _content_type: str, Optional
        :param _headers: set to override the headers for a single
                         request; this effectively ignores the headers
                         in the spec for a single request.
        :type _headers: dict, optional
        :param _host_index: set to override the host_index for a single
                            request; this effectively ignores the host_index
                            in the spec for a single request.
        :type _host_index: int, optional
        :return: Returns the result object.
        """ # noqa: E501

        _param = self._inbound_integration_endpoints_id_execution_report_get_serialize(
            id=id,
            context=context,
            workspace=workspace,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "List[ExecutionReportEntry]",
            '400': "Error",
            '404': "Error",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        response_data.read()
        return self.api_client.response_deserialize(
            response_data=response_data,
            response_types_map=_response_types_map,
        ).data


    @validate_call
    def inbound_integration_endpoints_id_execution_report_get_with_http_info(
        self,
        id: Annotated[StrictStr, Field(description="ID of the inbound integration endpoint for which to retrieve the execution report")],
        context: Annotated[StrictStr, Field(description="ID of the context in which to perform the operation")],
        workspace: Annotated[Optional[StrictStr], Field(description="ID of the workspace in which to perform the operation. Defaults to \"Main\".")] = None,
        _request_timeout: Union[
            None,
            Annotated[StrictFloat, Field(gt=0)],
            Tuple[
                Annotated[StrictFloat, Field(gt=0)],
                Annotated[StrictFloat, Field(gt=0)]
            ]
        ] = None,
        _request_auth: Optional[Dict[StrictStr, Any]] = None,
        _content_type: Optional[StrictStr] = None,
        _headers: Optional[Dict[StrictStr, Any]] = None,
        _host_index: Annotated[StrictInt, Field(ge=0, le=0)] = 0,
    ) -> ApiResponse[List[ExecutionReportEntry]]:
        """Returns the execution report for the specified inbound integration endpoint

        Operation for retrieving the execution report for the main process of a specific inbound integration endpoint

        :param id: ID of the inbound integration endpoint for which to retrieve the execution report (required)
        :type id: str
        :param context: ID of the context in which to perform the operation (required)
        :type context: str
        :param workspace: ID of the workspace in which to perform the operation. Defaults to \"Main\".
        :type workspace: str
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :type _request_timeout: int, tuple(int, int), optional
        :param _request_auth: set to override the auth_settings for an a single
                              request; this effectively ignores the
                              authentication in the spec for a single request.
        :type _request_auth: dict, optional
        :param _content_type: force content-type for the request.
        :type _content_type: str, Optional
        :param _headers: set to override the headers for a single
                         request; this effectively ignores the headers
                         in the spec for a single request.
        :type _headers: dict, optional
        :param _host_index: set to override the host_index for a single
                            request; this effectively ignores the host_index
                            in the spec for a single request.
        :type _host_index: int, optional
        :return: Returns the result object.
        """ # noqa: E501

        _param = self._inbound_integration_endpoints_id_execution_report_get_serialize(
            id=id,
            context=context,
            workspace=workspace,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "List[ExecutionReportEntry]",
            '400': "Error",
            '404': "Error",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        response_data.read()
        return self.api_client.response_deserialize(
            response_data=response_data,
            response_types_map=_response_types_map,
        )


    @validate_call
    def inbound_integration_endpoints_id_execution_report_get_without_preload_content(
        self,
        id: Annotated[StrictStr, Field(description="ID of the inbound integration endpoint for which to retrieve the execution report")],
        context: Annotated[StrictStr, Field(description="ID of the context in which to perform the operation")],
        workspace: Annotated[Optional[StrictStr], Field(description="ID of the workspace in which to perform the operation. Defaults to \"Main\".")] = None,
        _request_timeout: Union[
            None,
            Annotated[StrictFloat, Field(gt=0)],
            Tuple[
                Annotated[StrictFloat, Field(gt=0)],
                Annotated[StrictFloat, Field(gt=0)]
            ]
        ] = None,
        _request_auth: Optional[Dict[StrictStr, Any]] = None,
        _content_type: Optional[StrictStr] = None,
        _headers: Optional[Dict[StrictStr, Any]] = None,
        _host_index: Annotated[StrictInt, Field(ge=0, le=0)] = 0,
    ) -> RESTResponseType:
        """Returns the execution report for the specified inbound integration endpoint

        Operation for retrieving the execution report for the main process of a specific inbound integration endpoint

        :param id: ID of the inbound integration endpoint for which to retrieve the execution report (required)
        :type id: str
        :param context: ID of the context in which to perform the operation (required)
        :type context: str
        :param workspace: ID of the workspace in which to perform the operation. Defaults to \"Main\".
        :type workspace: str
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :type _request_timeout: int, tuple(int, int), optional
        :param _request_auth: set to override the auth_settings for an a single
                              request; this effectively ignores the
                              authentication in the spec for a single request.
        :type _request_auth: dict, optional
        :param _content_type: force content-type for the request.
        :type _content_type: str, Optional
        :param _headers: set to override the headers for a single
                         request; this effectively ignores the headers
                         in the spec for a single request.
        :type _headers: dict, optional
        :param _host_index: set to override the host_index for a single
                            request; this effectively ignores the host_index
                            in the spec for a single request.
        :type _host_index: int, optional
        :return: Returns the result object.
        """ # noqa: E501

        _param = self._inbound_integration_endpoints_id_execution_report_get_serialize(
            id=id,
            context=context,
            workspace=workspace,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "List[ExecutionReportEntry]",
            '400': "Error",
            '404': "Error",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        return response_data.response


    def _inbound_integration_endpoints_id_execution_report_get_serialize(
        self,
        id,
        context,
        workspace,
        _request_auth,
        _content_type,
        _headers,
        _host_index,
    ) -> RequestSerialized:

        _host = None

        _collection_formats: Dict[str, str] = {
        }

        _path_params: Dict[str, str] = {}
        _query_params: List[Tuple[str, str]] = []
        _header_params: Dict[str, Optional[str]] = _headers or {}
        _form_params: List[Tuple[str, str]] = []
        _files: Dict[
            str, Union[str, bytes, List[str], List[bytes], List[Tuple[str, bytes]]]
        ] = {}
        _body_params: Optional[bytes] = None

        # process the path parameters
        if id is not None:
            _path_params['id'] = id
        # process the query parameters
        if context is not None:
            
            _query_params.append(('context', context))
            
        if workspace is not None:
            
            _query_params.append(('workspace', workspace))
            
        # process the header parameters
        # process the form parameters
        # process the body parameter


        # set the HTTP header `Accept`
        if 'Accept' not in _header_params:
            _header_params['Accept'] = self.api_client.select_header_accept(
                [
                    'application/json'
                ]
            )


        # authentication setting
        _auth_settings: List[str] = [
            'basicAuth'
        ]

        return self.api_client.param_serialize(
            method='GET',
            resource_path='/inbound-integration-endpoints/{id}/execution-report',
            path_params=_path_params,
            query_params=_query_params,
            header_params=_header_params,
            body=_body_params,
            post_params=_form_params,
            files=_files,
            auth_settings=_auth_settings,
            collection_formats=_collection_formats,
            _host=_host,
            _request_auth=_request_auth
        )




    @validate_call
    def inbound_integration_endpoints_id_invoke_post(
        self,
        id: Annotated[StrictStr, Field(description="ID of the inbound integration endpoint to invoke")],
        context: Annotated[StrictStr, Field(description="ID of the context in which to perform the operation")],
        workspace: Annotated[Optional[StrictStr], Field(description="ID of the workspace in which to perform the operation. Defaults to \"Main\".")] = None,
        _request_timeout: Union[
            None,
            Annotated[StrictFloat, Field(gt=0)],
            Tuple[
                Annotated[StrictFloat, Field(gt=0)],
                Annotated[StrictFloat, Field(gt=0)]
            ]
        ] = None,
        _request_auth: Optional[Dict[StrictStr, Any]] = None,
        _content_type: Optional[StrictStr] = None,
        _headers: Optional[Dict[StrictStr, Any]] = None,
        _host_index: Annotated[StrictInt, Field(ge=0, le=0)] = 0,
    ) -> None:
        """Invokes the specified inbound integration endpoint

        Operation for invoking an inbound integration endpoint. Can be called only for endpoints with status 'enabled'.

        :param id: ID of the inbound integration endpoint to invoke (required)
        :type id: str
        :param context: ID of the context in which to perform the operation (required)
        :type context: str
        :param workspace: ID of the workspace in which to perform the operation. Defaults to \"Main\".
        :type workspace: str
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :type _request_timeout: int, tuple(int, int), optional
        :param _request_auth: set to override the auth_settings for an a single
                              request; this effectively ignores the
                              authentication in the spec for a single request.
        :type _request_auth: dict, optional
        :param _content_type: force content-type for the request.
        :type _content_type: str, Optional
        :param _headers: set to override the headers for a single
                         request; this effectively ignores the headers
                         in the spec for a single request.
        :type _headers: dict, optional
        :param _host_index: set to override the host_index for a single
                            request; this effectively ignores the host_index
                            in the spec for a single request.
        :type _host_index: int, optional
        :return: Returns the result object.
        """ # noqa: E501

        _param = self._inbound_integration_endpoints_id_invoke_post_serialize(
            id=id,
            context=context,
            workspace=workspace,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': None,
            '400': "Error",
            '404': "Error",
            '503': "Error",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        response_data.read()
        return self.api_client.response_deserialize(
            response_data=response_data,
            response_types_map=_response_types_map,
        ).data


    @validate_call
    def inbound_integration_endpoints_id_invoke_post_with_http_info(
        self,
        id: Annotated[StrictStr, Field(description="ID of the inbound integration endpoint to invoke")],
        context: Annotated[StrictStr, Field(description="ID of the context in which to perform the operation")],
        workspace: Annotated[Optional[StrictStr], Field(description="ID of the workspace in which to perform the operation. Defaults to \"Main\".")] = None,
        _request_timeout: Union[
            None,
            Annotated[StrictFloat, Field(gt=0)],
            Tuple[
                Annotated[StrictFloat, Field(gt=0)],
                Annotated[StrictFloat, Field(gt=0)]
            ]
        ] = None,
        _request_auth: Optional[Dict[StrictStr, Any]] = None,
        _content_type: Optional[StrictStr] = None,
        _headers: Optional[Dict[StrictStr, Any]] = None,
        _host_index: Annotated[StrictInt, Field(ge=0, le=0)] = 0,
    ) -> ApiResponse[None]:
        """Invokes the specified inbound integration endpoint

        Operation for invoking an inbound integration endpoint. Can be called only for endpoints with status 'enabled'.

        :param id: ID of the inbound integration endpoint to invoke (required)
        :type id: str
        :param context: ID of the context in which to perform the operation (required)
        :type context: str
        :param workspace: ID of the workspace in which to perform the operation. Defaults to \"Main\".
        :type workspace: str
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :type _request_timeout: int, tuple(int, int), optional
        :param _request_auth: set to override the auth_settings for an a single
                              request; this effectively ignores the
                              authentication in the spec for a single request.
        :type _request_auth: dict, optional
        :param _content_type: force content-type for the request.
        :type _content_type: str, Optional
        :param _headers: set to override the headers for a single
                         request; this effectively ignores the headers
                         in the spec for a single request.
        :type _headers: dict, optional
        :param _host_index: set to override the host_index for a single
                            request; this effectively ignores the host_index
                            in the spec for a single request.
        :type _host_index: int, optional
        :return: Returns the result object.
        """ # noqa: E501

        _param = self._inbound_integration_endpoints_id_invoke_post_serialize(
            id=id,
            context=context,
            workspace=workspace,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': None,
            '400': "Error",
            '404': "Error",
            '503': "Error",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        response_data.read()
        return self.api_client.response_deserialize(
            response_data=response_data,
            response_types_map=_response_types_map,
        )


    @validate_call
    def inbound_integration_endpoints_id_invoke_post_without_preload_content(
        self,
        id: Annotated[StrictStr, Field(description="ID of the inbound integration endpoint to invoke")],
        context: Annotated[StrictStr, Field(description="ID of the context in which to perform the operation")],
        workspace: Annotated[Optional[StrictStr], Field(description="ID of the workspace in which to perform the operation. Defaults to \"Main\".")] = None,
        _request_timeout: Union[
            None,
            Annotated[StrictFloat, Field(gt=0)],
            Tuple[
                Annotated[StrictFloat, Field(gt=0)],
                Annotated[StrictFloat, Field(gt=0)]
            ]
        ] = None,
        _request_auth: Optional[Dict[StrictStr, Any]] = None,
        _content_type: Optional[StrictStr] = None,
        _headers: Optional[Dict[StrictStr, Any]] = None,
        _host_index: Annotated[StrictInt, Field(ge=0, le=0)] = 0,
    ) -> RESTResponseType:
        """Invokes the specified inbound integration endpoint

        Operation for invoking an inbound integration endpoint. Can be called only for endpoints with status 'enabled'.

        :param id: ID of the inbound integration endpoint to invoke (required)
        :type id: str
        :param context: ID of the context in which to perform the operation (required)
        :type context: str
        :param workspace: ID of the workspace in which to perform the operation. Defaults to \"Main\".
        :type workspace: str
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :type _request_timeout: int, tuple(int, int), optional
        :param _request_auth: set to override the auth_settings for an a single
                              request; this effectively ignores the
                              authentication in the spec for a single request.
        :type _request_auth: dict, optional
        :param _content_type: force content-type for the request.
        :type _content_type: str, Optional
        :param _headers: set to override the headers for a single
                         request; this effectively ignores the headers
                         in the spec for a single request.
        :type _headers: dict, optional
        :param _host_index: set to override the host_index for a single
                            request; this effectively ignores the host_index
                            in the spec for a single request.
        :type _host_index: int, optional
        :return: Returns the result object.
        """ # noqa: E501

        _param = self._inbound_integration_endpoints_id_invoke_post_serialize(
            id=id,
            context=context,
            workspace=workspace,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': None,
            '400': "Error",
            '404': "Error",
            '503': "Error",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        return response_data.response


    def _inbound_integration_endpoints_id_invoke_post_serialize(
        self,
        id,
        context,
        workspace,
        _request_auth,
        _content_type,
        _headers,
        _host_index,
    ) -> RequestSerialized:

        _host = None

        _collection_formats: Dict[str, str] = {
        }

        _path_params: Dict[str, str] = {}
        _query_params: List[Tuple[str, str]] = []
        _header_params: Dict[str, Optional[str]] = _headers or {}
        _form_params: List[Tuple[str, str]] = []
        _files: Dict[
            str, Union[str, bytes, List[str], List[bytes], List[Tuple[str, bytes]]]
        ] = {}
        _body_params: Optional[bytes] = None

        # process the path parameters
        if id is not None:
            _path_params['id'] = id
        # process the query parameters
        if context is not None:
            
            _query_params.append(('context', context))
            
        if workspace is not None:
            
            _query_params.append(('workspace', workspace))
            
        # process the header parameters
        # process the form parameters
        # process the body parameter


        # set the HTTP header `Accept`
        if 'Accept' not in _header_params:
            _header_params['Accept'] = self.api_client.select_header_accept(
                [
                    'application/json'
                ]
            )


        # authentication setting
        _auth_settings: List[str] = [
            'basicAuth'
        ]

        return self.api_client.param_serialize(
            method='POST',
            resource_path='/inbound-integration-endpoints/{id}/invoke',
            path_params=_path_params,
            query_params=_query_params,
            header_params=_header_params,
            body=_body_params,
            post_params=_form_params,
            files=_files,
            auth_settings=_auth_settings,
            collection_formats=_collection_formats,
            _host=_host,
            _request_auth=_request_auth
        )




    @validate_call
    def inbound_integration_endpoints_id_statistics_get(
        self,
        id: Annotated[StrictStr, Field(description="ID of the inbound integration endpoint for which to retrieve the statistics")],
        context: Annotated[StrictStr, Field(description="ID of the context in which to perform the operation")],
        workspace: Annotated[Optional[StrictStr], Field(description="ID of the workspace in which to perform the operation. Defaults to \"Main\".")] = None,
        _request_timeout: Union[
            None,
            Annotated[StrictFloat, Field(gt=0)],
            Tuple[
                Annotated[StrictFloat, Field(gt=0)],
                Annotated[StrictFloat, Field(gt=0)]
            ]
        ] = None,
        _request_auth: Optional[Dict[StrictStr, Any]] = None,
        _content_type: Optional[StrictStr] = None,
        _headers: Optional[Dict[StrictStr, Any]] = None,
        _host_index: Annotated[StrictInt, Field(ge=0, le=0)] = 0,
    ) -> EndpointStatistics:
        """Returns statistics for the specified inbound integration endpoint

        Operation for retrieving statistics for a specific inbound integration endpoint

        :param id: ID of the inbound integration endpoint for which to retrieve the statistics (required)
        :type id: str
        :param context: ID of the context in which to perform the operation (required)
        :type context: str
        :param workspace: ID of the workspace in which to perform the operation. Defaults to \"Main\".
        :type workspace: str
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :type _request_timeout: int, tuple(int, int), optional
        :param _request_auth: set to override the auth_settings for an a single
                              request; this effectively ignores the
                              authentication in the spec for a single request.
        :type _request_auth: dict, optional
        :param _content_type: force content-type for the request.
        :type _content_type: str, Optional
        :param _headers: set to override the headers for a single
                         request; this effectively ignores the headers
                         in the spec for a single request.
        :type _headers: dict, optional
        :param _host_index: set to override the host_index for a single
                            request; this effectively ignores the host_index
                            in the spec for a single request.
        :type _host_index: int, optional
        :return: Returns the result object.
        """ # noqa: E501

        _param = self._inbound_integration_endpoints_id_statistics_get_serialize(
            id=id,
            context=context,
            workspace=workspace,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "EndpointStatistics",
            '400': "Error",
            '404': "Error",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        response_data.read()
        return self.api_client.response_deserialize(
            response_data=response_data,
            response_types_map=_response_types_map,
        ).data


    @validate_call
    def inbound_integration_endpoints_id_statistics_get_with_http_info(
        self,
        id: Annotated[StrictStr, Field(description="ID of the inbound integration endpoint for which to retrieve the statistics")],
        context: Annotated[StrictStr, Field(description="ID of the context in which to perform the operation")],
        workspace: Annotated[Optional[StrictStr], Field(description="ID of the workspace in which to perform the operation. Defaults to \"Main\".")] = None,
        _request_timeout: Union[
            None,
            Annotated[StrictFloat, Field(gt=0)],
            Tuple[
                Annotated[StrictFloat, Field(gt=0)],
                Annotated[StrictFloat, Field(gt=0)]
            ]
        ] = None,
        _request_auth: Optional[Dict[StrictStr, Any]] = None,
        _content_type: Optional[StrictStr] = None,
        _headers: Optional[Dict[StrictStr, Any]] = None,
        _host_index: Annotated[StrictInt, Field(ge=0, le=0)] = 0,
    ) -> ApiResponse[EndpointStatistics]:
        """Returns statistics for the specified inbound integration endpoint

        Operation for retrieving statistics for a specific inbound integration endpoint

        :param id: ID of the inbound integration endpoint for which to retrieve the statistics (required)
        :type id: str
        :param context: ID of the context in which to perform the operation (required)
        :type context: str
        :param workspace: ID of the workspace in which to perform the operation. Defaults to \"Main\".
        :type workspace: str
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :type _request_timeout: int, tuple(int, int), optional
        :param _request_auth: set to override the auth_settings for an a single
                              request; this effectively ignores the
                              authentication in the spec for a single request.
        :type _request_auth: dict, optional
        :param _content_type: force content-type for the request.
        :type _content_type: str, Optional
        :param _headers: set to override the headers for a single
                         request; this effectively ignores the headers
                         in the spec for a single request.
        :type _headers: dict, optional
        :param _host_index: set to override the host_index for a single
                            request; this effectively ignores the host_index
                            in the spec for a single request.
        :type _host_index: int, optional
        :return: Returns the result object.
        """ # noqa: E501

        _param = self._inbound_integration_endpoints_id_statistics_get_serialize(
            id=id,
            context=context,
            workspace=workspace,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "EndpointStatistics",
            '400': "Error",
            '404': "Error",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        response_data.read()
        return self.api_client.response_deserialize(
            response_data=response_data,
            response_types_map=_response_types_map,
        )


    @validate_call
    def inbound_integration_endpoints_id_statistics_get_without_preload_content(
        self,
        id: Annotated[StrictStr, Field(description="ID of the inbound integration endpoint for which to retrieve the statistics")],
        context: Annotated[StrictStr, Field(description="ID of the context in which to perform the operation")],
        workspace: Annotated[Optional[StrictStr], Field(description="ID of the workspace in which to perform the operation. Defaults to \"Main\".")] = None,
        _request_timeout: Union[
            None,
            Annotated[StrictFloat, Field(gt=0)],
            Tuple[
                Annotated[StrictFloat, Field(gt=0)],
                Annotated[StrictFloat, Field(gt=0)]
            ]
        ] = None,
        _request_auth: Optional[Dict[StrictStr, Any]] = None,
        _content_type: Optional[StrictStr] = None,
        _headers: Optional[Dict[StrictStr, Any]] = None,
        _host_index: Annotated[StrictInt, Field(ge=0, le=0)] = 0,
    ) -> RESTResponseType:
        """Returns statistics for the specified inbound integration endpoint

        Operation for retrieving statistics for a specific inbound integration endpoint

        :param id: ID of the inbound integration endpoint for which to retrieve the statistics (required)
        :type id: str
        :param context: ID of the context in which to perform the operation (required)
        :type context: str
        :param workspace: ID of the workspace in which to perform the operation. Defaults to \"Main\".
        :type workspace: str
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :type _request_timeout: int, tuple(int, int), optional
        :param _request_auth: set to override the auth_settings for an a single
                              request; this effectively ignores the
                              authentication in the spec for a single request.
        :type _request_auth: dict, optional
        :param _content_type: force content-type for the request.
        :type _content_type: str, Optional
        :param _headers: set to override the headers for a single
                         request; this effectively ignores the headers
                         in the spec for a single request.
        :type _headers: dict, optional
        :param _host_index: set to override the host_index for a single
                            request; this effectively ignores the host_index
                            in the spec for a single request.
        :type _host_index: int, optional
        :return: Returns the result object.
        """ # noqa: E501

        _param = self._inbound_integration_endpoints_id_statistics_get_serialize(
            id=id,
            context=context,
            workspace=workspace,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "EndpointStatistics",
            '400': "Error",
            '404': "Error",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        return response_data.response


    def _inbound_integration_endpoints_id_statistics_get_serialize(
        self,
        id,
        context,
        workspace,
        _request_auth,
        _content_type,
        _headers,
        _host_index,
    ) -> RequestSerialized:

        _host = None

        _collection_formats: Dict[str, str] = {
        }

        _path_params: Dict[str, str] = {}
        _query_params: List[Tuple[str, str]] = []
        _header_params: Dict[str, Optional[str]] = _headers or {}
        _form_params: List[Tuple[str, str]] = []
        _files: Dict[
            str, Union[str, bytes, List[str], List[bytes], List[Tuple[str, bytes]]]
        ] = {}
        _body_params: Optional[bytes] = None

        # process the path parameters
        if id is not None:
            _path_params['id'] = id
        # process the query parameters
        if context is not None:
            
            _query_params.append(('context', context))
            
        if workspace is not None:
            
            _query_params.append(('workspace', workspace))
            
        # process the header parameters
        # process the form parameters
        # process the body parameter


        # set the HTTP header `Accept`
        if 'Accept' not in _header_params:
            _header_params['Accept'] = self.api_client.select_header_accept(
                [
                    'application/json'
                ]
            )


        # authentication setting
        _auth_settings: List[str] = [
            'basicAuth'
        ]

        return self.api_client.param_serialize(
            method='GET',
            resource_path='/inbound-integration-endpoints/{id}/statistics',
            path_params=_path_params,
            query_params=_query_params,
            header_params=_header_params,
            body=_body_params,
            post_params=_form_params,
            files=_files,
            auth_settings=_auth_settings,
            collection_formats=_collection_formats,
            _host=_host,
            _request_auth=_request_auth
        )




    @validate_call
    def inbound_integration_endpoints_id_status_get(
        self,
        id: Annotated[StrictStr, Field(description="ID of the inbound integration endpoint for which to retrieve the status")],
        context: Annotated[StrictStr, Field(description="ID of the context in which to perform the operation")],
        workspace: Annotated[Optional[StrictStr], Field(description="ID of the workspace in which to perform the operation. Defaults to \"Main\".")] = None,
        _request_timeout: Union[
            None,
            Annotated[StrictFloat, Field(gt=0)],
            Tuple[
                Annotated[StrictFloat, Field(gt=0)],
                Annotated[StrictFloat, Field(gt=0)]
            ]
        ] = None,
        _request_auth: Optional[Dict[StrictStr, Any]] = None,
        _content_type: Optional[StrictStr] = None,
        _headers: Optional[Dict[StrictStr, Any]] = None,
        _host_index: Annotated[StrictInt, Field(ge=0, le=0)] = 0,
    ) -> EndpointStatus:
        """Returns the status of the specified inbound integration endpoint

        Operation for retrieving status information for a specific inbound integration endpoint

        :param id: ID of the inbound integration endpoint for which to retrieve the status (required)
        :type id: str
        :param context: ID of the context in which to perform the operation (required)
        :type context: str
        :param workspace: ID of the workspace in which to perform the operation. Defaults to \"Main\".
        :type workspace: str
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :type _request_timeout: int, tuple(int, int), optional
        :param _request_auth: set to override the auth_settings for an a single
                              request; this effectively ignores the
                              authentication in the spec for a single request.
        :type _request_auth: dict, optional
        :param _content_type: force content-type for the request.
        :type _content_type: str, Optional
        :param _headers: set to override the headers for a single
                         request; this effectively ignores the headers
                         in the spec for a single request.
        :type _headers: dict, optional
        :param _host_index: set to override the host_index for a single
                            request; this effectively ignores the host_index
                            in the spec for a single request.
        :type _host_index: int, optional
        :return: Returns the result object.
        """ # noqa: E501

        _param = self._inbound_integration_endpoints_id_status_get_serialize(
            id=id,
            context=context,
            workspace=workspace,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "EndpointStatus",
            '400': "Error",
            '404': "Error",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        response_data.read()
        return self.api_client.response_deserialize(
            response_data=response_data,
            response_types_map=_response_types_map,
        ).data


    @validate_call
    def inbound_integration_endpoints_id_status_get_with_http_info(
        self,
        id: Annotated[StrictStr, Field(description="ID of the inbound integration endpoint for which to retrieve the status")],
        context: Annotated[StrictStr, Field(description="ID of the context in which to perform the operation")],
        workspace: Annotated[Optional[StrictStr], Field(description="ID of the workspace in which to perform the operation. Defaults to \"Main\".")] = None,
        _request_timeout: Union[
            None,
            Annotated[StrictFloat, Field(gt=0)],
            Tuple[
                Annotated[StrictFloat, Field(gt=0)],
                Annotated[StrictFloat, Field(gt=0)]
            ]
        ] = None,
        _request_auth: Optional[Dict[StrictStr, Any]] = None,
        _content_type: Optional[StrictStr] = None,
        _headers: Optional[Dict[StrictStr, Any]] = None,
        _host_index: Annotated[StrictInt, Field(ge=0, le=0)] = 0,
    ) -> ApiResponse[EndpointStatus]:
        """Returns the status of the specified inbound integration endpoint

        Operation for retrieving status information for a specific inbound integration endpoint

        :param id: ID of the inbound integration endpoint for which to retrieve the status (required)
        :type id: str
        :param context: ID of the context in which to perform the operation (required)
        :type context: str
        :param workspace: ID of the workspace in which to perform the operation. Defaults to \"Main\".
        :type workspace: str
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :type _request_timeout: int, tuple(int, int), optional
        :param _request_auth: set to override the auth_settings for an a single
                              request; this effectively ignores the
                              authentication in the spec for a single request.
        :type _request_auth: dict, optional
        :param _content_type: force content-type for the request.
        :type _content_type: str, Optional
        :param _headers: set to override the headers for a single
                         request; this effectively ignores the headers
                         in the spec for a single request.
        :type _headers: dict, optional
        :param _host_index: set to override the host_index for a single
                            request; this effectively ignores the host_index
                            in the spec for a single request.
        :type _host_index: int, optional
        :return: Returns the result object.
        """ # noqa: E501

        _param = self._inbound_integration_endpoints_id_status_get_serialize(
            id=id,
            context=context,
            workspace=workspace,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "EndpointStatus",
            '400': "Error",
            '404': "Error",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        response_data.read()
        return self.api_client.response_deserialize(
            response_data=response_data,
            response_types_map=_response_types_map,
        )


    @validate_call
    def inbound_integration_endpoints_id_status_get_without_preload_content(
        self,
        id: Annotated[StrictStr, Field(description="ID of the inbound integration endpoint for which to retrieve the status")],
        context: Annotated[StrictStr, Field(description="ID of the context in which to perform the operation")],
        workspace: Annotated[Optional[StrictStr], Field(description="ID of the workspace in which to perform the operation. Defaults to \"Main\".")] = None,
        _request_timeout: Union[
            None,
            Annotated[StrictFloat, Field(gt=0)],
            Tuple[
                Annotated[StrictFloat, Field(gt=0)],
                Annotated[StrictFloat, Field(gt=0)]
            ]
        ] = None,
        _request_auth: Optional[Dict[StrictStr, Any]] = None,
        _content_type: Optional[StrictStr] = None,
        _headers: Optional[Dict[StrictStr, Any]] = None,
        _host_index: Annotated[StrictInt, Field(ge=0, le=0)] = 0,
    ) -> RESTResponseType:
        """Returns the status of the specified inbound integration endpoint

        Operation for retrieving status information for a specific inbound integration endpoint

        :param id: ID of the inbound integration endpoint for which to retrieve the status (required)
        :type id: str
        :param context: ID of the context in which to perform the operation (required)
        :type context: str
        :param workspace: ID of the workspace in which to perform the operation. Defaults to \"Main\".
        :type workspace: str
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :type _request_timeout: int, tuple(int, int), optional
        :param _request_auth: set to override the auth_settings for an a single
                              request; this effectively ignores the
                              authentication in the spec for a single request.
        :type _request_auth: dict, optional
        :param _content_type: force content-type for the request.
        :type _content_type: str, Optional
        :param _headers: set to override the headers for a single
                         request; this effectively ignores the headers
                         in the spec for a single request.
        :type _headers: dict, optional
        :param _host_index: set to override the host_index for a single
                            request; this effectively ignores the host_index
                            in the spec for a single request.
        :type _host_index: int, optional
        :return: Returns the result object.
        """ # noqa: E501

        _param = self._inbound_integration_endpoints_id_status_get_serialize(
            id=id,
            context=context,
            workspace=workspace,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "EndpointStatus",
            '400': "Error",
            '404': "Error",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        return response_data.response


    def _inbound_integration_endpoints_id_status_get_serialize(
        self,
        id,
        context,
        workspace,
        _request_auth,
        _content_type,
        _headers,
        _host_index,
    ) -> RequestSerialized:

        _host = None

        _collection_formats: Dict[str, str] = {
        }

        _path_params: Dict[str, str] = {}
        _query_params: List[Tuple[str, str]] = []
        _header_params: Dict[str, Optional[str]] = _headers or {}
        _form_params: List[Tuple[str, str]] = []
        _files: Dict[
            str, Union[str, bytes, List[str], List[bytes], List[Tuple[str, bytes]]]
        ] = {}
        _body_params: Optional[bytes] = None

        # process the path parameters
        if id is not None:
            _path_params['id'] = id
        # process the query parameters
        if context is not None:
            
            _query_params.append(('context', context))
            
        if workspace is not None:
            
            _query_params.append(('workspace', workspace))
            
        # process the header parameters
        # process the form parameters
        # process the body parameter


        # set the HTTP header `Accept`
        if 'Accept' not in _header_params:
            _header_params['Accept'] = self.api_client.select_header_accept(
                [
                    'application/json'
                ]
            )


        # authentication setting
        _auth_settings: List[str] = [
            'basicAuth'
        ]

        return self.api_client.param_serialize(
            method='GET',
            resource_path='/inbound-integration-endpoints/{id}/status',
            path_params=_path_params,
            query_params=_query_params,
            header_params=_header_params,
            body=_body_params,
            post_params=_form_params,
            files=_files,
            auth_settings=_auth_settings,
            collection_formats=_collection_formats,
            _host=_host,
            _request_auth=_request_auth
        )




    @validate_call
    def inbound_integration_endpoints_id_upload_and_invoke_post(
        self,
        id: Annotated[StrictStr, Field(description="ID of the inbound integration endpoint")],
        context: Annotated[StrictStr, Field(description="ID of the context in which to perform the operation")],
        file_name: Annotated[Optional[StrictStr], Field(description="Optional file name (including extension) for the supplied binary data")] = None,
        workspace: Annotated[Optional[StrictStr], Field(description="ID of the workspace in which to perform the operation. Defaults to \"Main\".")] = None,
        body: Optional[Union[StrictBytes, StrictStr, Tuple[StrictStr, StrictBytes]]] = None,
        _request_timeout: Union[
            None,
            Annotated[StrictFloat, Field(gt=0)],
            Tuple[
                Annotated[StrictFloat, Field(gt=0)],
                Annotated[StrictFloat, Field(gt=0)]
            ]
        ] = None,
        _request_auth: Optional[Dict[StrictStr, Any]] = None,
        _content_type: Optional[StrictStr] = None,
        _headers: Optional[Dict[StrictStr, Any]] = None,
        _host_index: Annotated[StrictInt, Field(ge=0, le=0)] = 0,
    ) -> None:
        """Posts message/file to endpoint with REST receiver

        Operation for posting a message/file to an inbound integration endpoint with a configured REST receiver and invoking the endpoint. A 400 response is returned if the endpoint does not have a REST-enabled receiver plugin or if the endpoint is not enabled.

        :param id: ID of the inbound integration endpoint (required)
        :type id: str
        :param context: ID of the context in which to perform the operation (required)
        :type context: str
        :param file_name: Optional file name (including extension) for the supplied binary data
        :type file_name: str
        :param workspace: ID of the workspace in which to perform the operation. Defaults to \"Main\".
        :type workspace: str
        :param body:
        :type body: bytearray
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :type _request_timeout: int, tuple(int, int), optional
        :param _request_auth: set to override the auth_settings for an a single
                              request; this effectively ignores the
                              authentication in the spec for a single request.
        :type _request_auth: dict, optional
        :param _content_type: force content-type for the request.
        :type _content_type: str, Optional
        :param _headers: set to override the headers for a single
                         request; this effectively ignores the headers
                         in the spec for a single request.
        :type _headers: dict, optional
        :param _host_index: set to override the host_index for a single
                            request; this effectively ignores the host_index
                            in the spec for a single request.
        :type _host_index: int, optional
        :return: Returns the result object.
        """ # noqa: E501

        _param = self._inbound_integration_endpoints_id_upload_and_invoke_post_serialize(
            id=id,
            context=context,
            file_name=file_name,
            workspace=workspace,
            body=body,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': None,
            '400': "Error",
            '404': "Error",
            '503': "Error",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        response_data.read()
        return self.api_client.response_deserialize(
            response_data=response_data,
            response_types_map=_response_types_map,
        ).data


    @validate_call
    def inbound_integration_endpoints_id_upload_and_invoke_post_with_http_info(
        self,
        id: Annotated[StrictStr, Field(description="ID of the inbound integration endpoint")],
        context: Annotated[StrictStr, Field(description="ID of the context in which to perform the operation")],
        file_name: Annotated[Optional[StrictStr], Field(description="Optional file name (including extension) for the supplied binary data")] = None,
        workspace: Annotated[Optional[StrictStr], Field(description="ID of the workspace in which to perform the operation. Defaults to \"Main\".")] = None,
        body: Optional[Union[StrictBytes, StrictStr, Tuple[StrictStr, StrictBytes]]] = None,
        _request_timeout: Union[
            None,
            Annotated[StrictFloat, Field(gt=0)],
            Tuple[
                Annotated[StrictFloat, Field(gt=0)],
                Annotated[StrictFloat, Field(gt=0)]
            ]
        ] = None,
        _request_auth: Optional[Dict[StrictStr, Any]] = None,
        _content_type: Optional[StrictStr] = None,
        _headers: Optional[Dict[StrictStr, Any]] = None,
        _host_index: Annotated[StrictInt, Field(ge=0, le=0)] = 0,
    ) -> ApiResponse[None]:
        """Posts message/file to endpoint with REST receiver

        Operation for posting a message/file to an inbound integration endpoint with a configured REST receiver and invoking the endpoint. A 400 response is returned if the endpoint does not have a REST-enabled receiver plugin or if the endpoint is not enabled.

        :param id: ID of the inbound integration endpoint (required)
        :type id: str
        :param context: ID of the context in which to perform the operation (required)
        :type context: str
        :param file_name: Optional file name (including extension) for the supplied binary data
        :type file_name: str
        :param workspace: ID of the workspace in which to perform the operation. Defaults to \"Main\".
        :type workspace: str
        :param body:
        :type body: bytearray
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :type _request_timeout: int, tuple(int, int), optional
        :param _request_auth: set to override the auth_settings for an a single
                              request; this effectively ignores the
                              authentication in the spec for a single request.
        :type _request_auth: dict, optional
        :param _content_type: force content-type for the request.
        :type _content_type: str, Optional
        :param _headers: set to override the headers for a single
                         request; this effectively ignores the headers
                         in the spec for a single request.
        :type _headers: dict, optional
        :param _host_index: set to override the host_index for a single
                            request; this effectively ignores the host_index
                            in the spec for a single request.
        :type _host_index: int, optional
        :return: Returns the result object.
        """ # noqa: E501

        _param = self._inbound_integration_endpoints_id_upload_and_invoke_post_serialize(
            id=id,
            context=context,
            file_name=file_name,
            workspace=workspace,
            body=body,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': None,
            '400': "Error",
            '404': "Error",
            '503': "Error",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        response_data.read()
        return self.api_client.response_deserialize(
            response_data=response_data,
            response_types_map=_response_types_map,
        )


    @validate_call
    def inbound_integration_endpoints_id_upload_and_invoke_post_without_preload_content(
        self,
        id: Annotated[StrictStr, Field(description="ID of the inbound integration endpoint")],
        context: Annotated[StrictStr, Field(description="ID of the context in which to perform the operation")],
        file_name: Annotated[Optional[StrictStr], Field(description="Optional file name (including extension) for the supplied binary data")] = None,
        workspace: Annotated[Optional[StrictStr], Field(description="ID of the workspace in which to perform the operation. Defaults to \"Main\".")] = None,
        body: Optional[Union[StrictBytes, StrictStr, Tuple[StrictStr, StrictBytes]]] = None,
        _request_timeout: Union[
            None,
            Annotated[StrictFloat, Field(gt=0)],
            Tuple[
                Annotated[StrictFloat, Field(gt=0)],
                Annotated[StrictFloat, Field(gt=0)]
            ]
        ] = None,
        _request_auth: Optional[Dict[StrictStr, Any]] = None,
        _content_type: Optional[StrictStr] = None,
        _headers: Optional[Dict[StrictStr, Any]] = None,
        _host_index: Annotated[StrictInt, Field(ge=0, le=0)] = 0,
    ) -> RESTResponseType:
        """Posts message/file to endpoint with REST receiver

        Operation for posting a message/file to an inbound integration endpoint with a configured REST receiver and invoking the endpoint. A 400 response is returned if the endpoint does not have a REST-enabled receiver plugin or if the endpoint is not enabled.

        :param id: ID of the inbound integration endpoint (required)
        :type id: str
        :param context: ID of the context in which to perform the operation (required)
        :type context: str
        :param file_name: Optional file name (including extension) for the supplied binary data
        :type file_name: str
        :param workspace: ID of the workspace in which to perform the operation. Defaults to \"Main\".
        :type workspace: str
        :param body:
        :type body: bytearray
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :type _request_timeout: int, tuple(int, int), optional
        :param _request_auth: set to override the auth_settings for an a single
                              request; this effectively ignores the
                              authentication in the spec for a single request.
        :type _request_auth: dict, optional
        :param _content_type: force content-type for the request.
        :type _content_type: str, Optional
        :param _headers: set to override the headers for a single
                         request; this effectively ignores the headers
                         in the spec for a single request.
        :type _headers: dict, optional
        :param _host_index: set to override the host_index for a single
                            request; this effectively ignores the host_index
                            in the spec for a single request.
        :type _host_index: int, optional
        :return: Returns the result object.
        """ # noqa: E501

        _param = self._inbound_integration_endpoints_id_upload_and_invoke_post_serialize(
            id=id,
            context=context,
            file_name=file_name,
            workspace=workspace,
            body=body,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': None,
            '400': "Error",
            '404': "Error",
            '503': "Error",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        return response_data.response


    def _inbound_integration_endpoints_id_upload_and_invoke_post_serialize(
        self,
        id,
        context,
        file_name,
        workspace,
        body,
        _request_auth,
        _content_type,
        _headers,
        _host_index,
    ) -> RequestSerialized:

        _host = None

        _collection_formats: Dict[str, str] = {
        }

        _path_params: Dict[str, str] = {}
        _query_params: List[Tuple[str, str]] = []
        _header_params: Dict[str, Optional[str]] = _headers or {}
        _form_params: List[Tuple[str, str]] = []
        _files: Dict[
            str, Union[str, bytes, List[str], List[bytes], List[Tuple[str, bytes]]]
        ] = {}
        _body_params: Optional[bytes] = None

        # process the path parameters
        if id is not None:
            _path_params['id'] = id
        # process the query parameters
        if file_name is not None:
            
            _query_params.append(('fileName', file_name))
            
        if context is not None:
            
            _query_params.append(('context', context))
            
        if workspace is not None:
            
            _query_params.append(('workspace', workspace))
            
        # process the header parameters
        # process the form parameters
        # process the body parameter
        if body is not None:
            # convert to byte array if the input is a file name (str)
            if isinstance(body, str):
                with open(body, "rb") as _fp:
                    _body_params = _fp.read()
            elif isinstance(body, tuple):
                # drop the filename from the tuple
                _body_params = body[1]
            else:
                _body_params = body


        # set the HTTP header `Accept`
        if 'Accept' not in _header_params:
            _header_params['Accept'] = self.api_client.select_header_accept(
                [
                    'application/json'
                ]
            )

        # set the HTTP header `Content-Type`
        if _content_type:
            _header_params['Content-Type'] = _content_type
        else:
            _default_content_type = (
                self.api_client.select_header_content_type(
                    [
                        'application/octet-stream'
                    ]
                )
            )
            if _default_content_type is not None:
                _header_params['Content-Type'] = _default_content_type

        # authentication setting
        _auth_settings: List[str] = [
            'basicAuth'
        ]

        return self.api_client.param_serialize(
            method='POST',
            resource_path='/inbound-integration-endpoints/{id}/upload-and-invoke',
            path_params=_path_params,
            query_params=_query_params,
            header_params=_header_params,
            body=_body_params,
            post_params=_form_params,
            files=_files,
            auth_settings=_auth_settings,
            collection_formats=_collection_formats,
            _host=_host,
            _request_auth=_request_auth
        )




    @validate_call
    def inbound_integration_endpoints_id_worker_processes_get(
        self,
        id: Annotated[StrictStr, Field(description="ID of the inbound integration endpoint for which to retrieve processes")],
        context: Annotated[StrictStr, Field(description="ID of the context in which to perform the operation")],
        workspace: Annotated[Optional[StrictStr], Field(description="ID of the workspace in which to perform the operation. Defaults to \"Main\".")] = None,
        status: Annotated[Optional[StrictStr], Field(description="Background process status filter")] = None,
        _request_timeout: Union[
            None,
            Annotated[StrictFloat, Field(gt=0)],
            Tuple[
                Annotated[StrictFloat, Field(gt=0)],
                Annotated[StrictFloat, Field(gt=0)]
            ]
        ] = None,
        _request_auth: Optional[Dict[StrictStr, Any]] = None,
        _content_type: Optional[StrictStr] = None,
        _headers: Optional[Dict[StrictStr, Any]] = None,
        _host_index: Annotated[StrictInt, Field(ge=0, le=0)] = 0,
    ) -> List[str]:
        """Returns background process IDs for processes started by the endpoint

        Operation for retrieving background process IDs for processes started by the endpoint. Can be filtered on process status.

        :param id: ID of the inbound integration endpoint for which to retrieve processes (required)
        :type id: str
        :param context: ID of the context in which to perform the operation (required)
        :type context: str
        :param workspace: ID of the workspace in which to perform the operation. Defaults to \"Main\".
        :type workspace: str
        :param status: Background process status filter
        :type status: str
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :type _request_timeout: int, tuple(int, int), optional
        :param _request_auth: set to override the auth_settings for an a single
                              request; this effectively ignores the
                              authentication in the spec for a single request.
        :type _request_auth: dict, optional
        :param _content_type: force content-type for the request.
        :type _content_type: str, Optional
        :param _headers: set to override the headers for a single
                         request; this effectively ignores the headers
                         in the spec for a single request.
        :type _headers: dict, optional
        :param _host_index: set to override the host_index for a single
                            request; this effectively ignores the host_index
                            in the spec for a single request.
        :type _host_index: int, optional
        :return: Returns the result object.
        """ # noqa: E501

        _param = self._inbound_integration_endpoints_id_worker_processes_get_serialize(
            id=id,
            context=context,
            workspace=workspace,
            status=status,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "List[str]",
            '400': "Error",
            '404': "Error",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        response_data.read()
        return self.api_client.response_deserialize(
            response_data=response_data,
            response_types_map=_response_types_map,
        ).data


    @validate_call
    def inbound_integration_endpoints_id_worker_processes_get_with_http_info(
        self,
        id: Annotated[StrictStr, Field(description="ID of the inbound integration endpoint for which to retrieve processes")],
        context: Annotated[StrictStr, Field(description="ID of the context in which to perform the operation")],
        workspace: Annotated[Optional[StrictStr], Field(description="ID of the workspace in which to perform the operation. Defaults to \"Main\".")] = None,
        status: Annotated[Optional[StrictStr], Field(description="Background process status filter")] = None,
        _request_timeout: Union[
            None,
            Annotated[StrictFloat, Field(gt=0)],
            Tuple[
                Annotated[StrictFloat, Field(gt=0)],
                Annotated[StrictFloat, Field(gt=0)]
            ]
        ] = None,
        _request_auth: Optional[Dict[StrictStr, Any]] = None,
        _content_type: Optional[StrictStr] = None,
        _headers: Optional[Dict[StrictStr, Any]] = None,
        _host_index: Annotated[StrictInt, Field(ge=0, le=0)] = 0,
    ) -> ApiResponse[List[str]]:
        """Returns background process IDs for processes started by the endpoint

        Operation for retrieving background process IDs for processes started by the endpoint. Can be filtered on process status.

        :param id: ID of the inbound integration endpoint for which to retrieve processes (required)
        :type id: str
        :param context: ID of the context in which to perform the operation (required)
        :type context: str
        :param workspace: ID of the workspace in which to perform the operation. Defaults to \"Main\".
        :type workspace: str
        :param status: Background process status filter
        :type status: str
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :type _request_timeout: int, tuple(int, int), optional
        :param _request_auth: set to override the auth_settings for an a single
                              request; this effectively ignores the
                              authentication in the spec for a single request.
        :type _request_auth: dict, optional
        :param _content_type: force content-type for the request.
        :type _content_type: str, Optional
        :param _headers: set to override the headers for a single
                         request; this effectively ignores the headers
                         in the spec for a single request.
        :type _headers: dict, optional
        :param _host_index: set to override the host_index for a single
                            request; this effectively ignores the host_index
                            in the spec for a single request.
        :type _host_index: int, optional
        :return: Returns the result object.
        """ # noqa: E501

        _param = self._inbound_integration_endpoints_id_worker_processes_get_serialize(
            id=id,
            context=context,
            workspace=workspace,
            status=status,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "List[str]",
            '400': "Error",
            '404': "Error",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        response_data.read()
        return self.api_client.response_deserialize(
            response_data=response_data,
            response_types_map=_response_types_map,
        )


    @validate_call
    def inbound_integration_endpoints_id_worker_processes_get_without_preload_content(
        self,
        id: Annotated[StrictStr, Field(description="ID of the inbound integration endpoint for which to retrieve processes")],
        context: Annotated[StrictStr, Field(description="ID of the context in which to perform the operation")],
        workspace: Annotated[Optional[StrictStr], Field(description="ID of the workspace in which to perform the operation. Defaults to \"Main\".")] = None,
        status: Annotated[Optional[StrictStr], Field(description="Background process status filter")] = None,
        _request_timeout: Union[
            None,
            Annotated[StrictFloat, Field(gt=0)],
            Tuple[
                Annotated[StrictFloat, Field(gt=0)],
                Annotated[StrictFloat, Field(gt=0)]
            ]
        ] = None,
        _request_auth: Optional[Dict[StrictStr, Any]] = None,
        _content_type: Optional[StrictStr] = None,
        _headers: Optional[Dict[StrictStr, Any]] = None,
        _host_index: Annotated[StrictInt, Field(ge=0, le=0)] = 0,
    ) -> RESTResponseType:
        """Returns background process IDs for processes started by the endpoint

        Operation for retrieving background process IDs for processes started by the endpoint. Can be filtered on process status.

        :param id: ID of the inbound integration endpoint for which to retrieve processes (required)
        :type id: str
        :param context: ID of the context in which to perform the operation (required)
        :type context: str
        :param workspace: ID of the workspace in which to perform the operation. Defaults to \"Main\".
        :type workspace: str
        :param status: Background process status filter
        :type status: str
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :type _request_timeout: int, tuple(int, int), optional
        :param _request_auth: set to override the auth_settings for an a single
                              request; this effectively ignores the
                              authentication in the spec for a single request.
        :type _request_auth: dict, optional
        :param _content_type: force content-type for the request.
        :type _content_type: str, Optional
        :param _headers: set to override the headers for a single
                         request; this effectively ignores the headers
                         in the spec for a single request.
        :type _headers: dict, optional
        :param _host_index: set to override the host_index for a single
                            request; this effectively ignores the host_index
                            in the spec for a single request.
        :type _host_index: int, optional
        :return: Returns the result object.
        """ # noqa: E501

        _param = self._inbound_integration_endpoints_id_worker_processes_get_serialize(
            id=id,
            context=context,
            workspace=workspace,
            status=status,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "List[str]",
            '400': "Error",
            '404': "Error",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        return response_data.response


    def _inbound_integration_endpoints_id_worker_processes_get_serialize(
        self,
        id,
        context,
        workspace,
        status,
        _request_auth,
        _content_type,
        _headers,
        _host_index,
    ) -> RequestSerialized:

        _host = None

        _collection_formats: Dict[str, str] = {
        }

        _path_params: Dict[str, str] = {}
        _query_params: List[Tuple[str, str]] = []
        _header_params: Dict[str, Optional[str]] = _headers or {}
        _form_params: List[Tuple[str, str]] = []
        _files: Dict[
            str, Union[str, bytes, List[str], List[bytes], List[Tuple[str, bytes]]]
        ] = {}
        _body_params: Optional[bytes] = None

        # process the path parameters
        if id is not None:
            _path_params['id'] = id
        # process the query parameters
        if context is not None:
            
            _query_params.append(('context', context))
            
        if workspace is not None:
            
            _query_params.append(('workspace', workspace))
            
        if status is not None:
            
            _query_params.append(('status', status))
            
        # process the header parameters
        # process the form parameters
        # process the body parameter


        # set the HTTP header `Accept`
        if 'Accept' not in _header_params:
            _header_params['Accept'] = self.api_client.select_header_accept(
                [
                    'application/json'
                ]
            )


        # authentication setting
        _auth_settings: List[str] = [
            'basicAuth'
        ]

        return self.api_client.param_serialize(
            method='GET',
            resource_path='/inbound-integration-endpoints/{id}/worker-processes',
            path_params=_path_params,
            query_params=_query_params,
            header_params=_header_params,
            body=_body_params,
            post_params=_form_params,
            files=_files,
            auth_settings=_auth_settings,
            collection_formats=_collection_formats,
            _host=_host,
            _request_auth=_request_auth
        )


