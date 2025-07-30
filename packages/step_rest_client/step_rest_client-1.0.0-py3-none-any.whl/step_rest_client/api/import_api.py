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

from pydantic import Field, StrictBytes, StrictStr
from typing import Optional, Tuple, Union
from typing_extensions import Annotated
from step_rest_client.models.background_process_identification import BackgroundProcessIdentification

from step_rest_client.api_client import ApiClient, RequestSerialized
from step_rest_client.api_response import ApiResponse
from step_rest_client.rest import RESTResponseType


class ImportApi:
    """NOTE: This class is auto generated by OpenAPI Generator
    Ref: https://openapi-generator.tech

    Do not edit the class manually.
    """

    def __init__(self, api_client=None) -> None:
        if api_client is None:
            api_client = ApiClient.get_default()
        self.api_client = api_client


    @validate_call
    def import_import_configuration_id_post(
        self,
        import_configuration_id: Annotated[StrictStr, Field(description="ID of the import configuration to use")],
        context: Annotated[StrictStr, Field(description="ID of the context in which to perform the operation")],
        process_description: Annotated[Optional[StrictStr], Field(description="Optional process description")] = None,
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
    ) -> BackgroundProcessIdentification:
        """Starts an import background process

        Operation for starting an import background process. For STEPXML imports, the process will be run in the context/workspace specified in the STEPXML file. For other imports, the request context/workspace will be used.

        :param import_configuration_id: ID of the import configuration to use (required)
        :type import_configuration_id: str
        :param context: ID of the context in which to perform the operation (required)
        :type context: str
        :param process_description: Optional process description
        :type process_description: str
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

        _param = self._import_import_configuration_id_post_serialize(
            import_configuration_id=import_configuration_id,
            context=context,
            process_description=process_description,
            workspace=workspace,
            body=body,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "BackgroundProcessIdentification",
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
    def import_import_configuration_id_post_with_http_info(
        self,
        import_configuration_id: Annotated[StrictStr, Field(description="ID of the import configuration to use")],
        context: Annotated[StrictStr, Field(description="ID of the context in which to perform the operation")],
        process_description: Annotated[Optional[StrictStr], Field(description="Optional process description")] = None,
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
    ) -> ApiResponse[BackgroundProcessIdentification]:
        """Starts an import background process

        Operation for starting an import background process. For STEPXML imports, the process will be run in the context/workspace specified in the STEPXML file. For other imports, the request context/workspace will be used.

        :param import_configuration_id: ID of the import configuration to use (required)
        :type import_configuration_id: str
        :param context: ID of the context in which to perform the operation (required)
        :type context: str
        :param process_description: Optional process description
        :type process_description: str
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

        _param = self._import_import_configuration_id_post_serialize(
            import_configuration_id=import_configuration_id,
            context=context,
            process_description=process_description,
            workspace=workspace,
            body=body,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "BackgroundProcessIdentification",
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
    def import_import_configuration_id_post_without_preload_content(
        self,
        import_configuration_id: Annotated[StrictStr, Field(description="ID of the import configuration to use")],
        context: Annotated[StrictStr, Field(description="ID of the context in which to perform the operation")],
        process_description: Annotated[Optional[StrictStr], Field(description="Optional process description")] = None,
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
        """Starts an import background process

        Operation for starting an import background process. For STEPXML imports, the process will be run in the context/workspace specified in the STEPXML file. For other imports, the request context/workspace will be used.

        :param import_configuration_id: ID of the import configuration to use (required)
        :type import_configuration_id: str
        :param context: ID of the context in which to perform the operation (required)
        :type context: str
        :param process_description: Optional process description
        :type process_description: str
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

        _param = self._import_import_configuration_id_post_serialize(
            import_configuration_id=import_configuration_id,
            context=context,
            process_description=process_description,
            workspace=workspace,
            body=body,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "BackgroundProcessIdentification",
            '400': "Error",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        return response_data.response


    def _import_import_configuration_id_post_serialize(
        self,
        import_configuration_id,
        context,
        process_description,
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
        if import_configuration_id is not None:
            _path_params['importConfigurationId'] = import_configuration_id
        # process the query parameters
        if process_description is not None:
            
            _query_params.append(('processDescription', process_description))
            
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
            resource_path='/import/{importConfigurationId}',
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


