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

from pydantic import Field, StrictBool, StrictStr
from typing import List, Optional
from typing_extensions import Annotated
from step_rest_client.models.approval_response import ApprovalResponse
from step_rest_client.models.approval_status import ApprovalStatus
from step_rest_client.models.data_container import DataContainer
from step_rest_client.models.incoming_reference_entry import IncomingReferenceEntry
from step_rest_client.models.product import Product
from step_rest_client.models.query import Query
from step_rest_client.models.query_result import QueryResult
from step_rest_client.models.reference import Reference
from step_rest_client.models.reference_entry import ReferenceEntry
from step_rest_client.models.value import Value

from step_rest_client.api_client import ApiClient, RequestSerialized
from step_rest_client.api_response import ApiResponse
from step_rest_client.rest import RESTResponseType


class ProductsApi:
    """NOTE: This class is auto generated by OpenAPI Generator
    Ref: https://openapi-generator.tech

    Do not edit the class manually.
    """

    def __init__(self, api_client=None) -> None:
        if api_client is None:
            api_client = ApiClient.get_default()
        self.api_client = api_client


    @validate_call
    def products_id_approval_status_get(
        self,
        id: Annotated[StrictStr, Field(description="ID / key value of the product for which to get the approval status")],
        context: Annotated[StrictStr, Field(description="ID of the context in which to perform the operation")],
        key_id: Annotated[Optional[StrictStr], Field(description="ID of the key definition to be used for identifying the product. If supplied, a key value should be supplied for the \"id\" path parameter.")] = None,
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
    ) -> ApprovalStatus:
        """Returns the approval status of the product with the specified ID / key value

        Operation for retrieving the approval status of a product. The product can be identified either by its STEP ID or if a value for the \"keyId\" query parameter is supplied, by its key value for the specified key.

        :param id: ID / key value of the product for which to get the approval status (required)
        :type id: str
        :param context: ID of the context in which to perform the operation (required)
        :type context: str
        :param key_id: ID of the key definition to be used for identifying the product. If supplied, a key value should be supplied for the \"id\" path parameter.
        :type key_id: str
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

        _param = self._products_id_approval_status_get_serialize(
            id=id,
            context=context,
            key_id=key_id,
            workspace=workspace,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "ApprovalStatus",
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
    def products_id_approval_status_get_with_http_info(
        self,
        id: Annotated[StrictStr, Field(description="ID / key value of the product for which to get the approval status")],
        context: Annotated[StrictStr, Field(description="ID of the context in which to perform the operation")],
        key_id: Annotated[Optional[StrictStr], Field(description="ID of the key definition to be used for identifying the product. If supplied, a key value should be supplied for the \"id\" path parameter.")] = None,
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
    ) -> ApiResponse[ApprovalStatus]:
        """Returns the approval status of the product with the specified ID / key value

        Operation for retrieving the approval status of a product. The product can be identified either by its STEP ID or if a value for the \"keyId\" query parameter is supplied, by its key value for the specified key.

        :param id: ID / key value of the product for which to get the approval status (required)
        :type id: str
        :param context: ID of the context in which to perform the operation (required)
        :type context: str
        :param key_id: ID of the key definition to be used for identifying the product. If supplied, a key value should be supplied for the \"id\" path parameter.
        :type key_id: str
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

        _param = self._products_id_approval_status_get_serialize(
            id=id,
            context=context,
            key_id=key_id,
            workspace=workspace,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "ApprovalStatus",
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
    def products_id_approval_status_get_without_preload_content(
        self,
        id: Annotated[StrictStr, Field(description="ID / key value of the product for which to get the approval status")],
        context: Annotated[StrictStr, Field(description="ID of the context in which to perform the operation")],
        key_id: Annotated[Optional[StrictStr], Field(description="ID of the key definition to be used for identifying the product. If supplied, a key value should be supplied for the \"id\" path parameter.")] = None,
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
        """Returns the approval status of the product with the specified ID / key value

        Operation for retrieving the approval status of a product. The product can be identified either by its STEP ID or if a value for the \"keyId\" query parameter is supplied, by its key value for the specified key.

        :param id: ID / key value of the product for which to get the approval status (required)
        :type id: str
        :param context: ID of the context in which to perform the operation (required)
        :type context: str
        :param key_id: ID of the key definition to be used for identifying the product. If supplied, a key value should be supplied for the \"id\" path parameter.
        :type key_id: str
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

        _param = self._products_id_approval_status_get_serialize(
            id=id,
            context=context,
            key_id=key_id,
            workspace=workspace,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "ApprovalStatus",
            '400': "Error",
            '404': "Error",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        return response_data.response


    def _products_id_approval_status_get_serialize(
        self,
        id,
        context,
        key_id,
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
        if key_id is not None:
            
            _query_params.append(('keyId', key_id))
            
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
            resource_path='/products/{id}/approval-status',
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
    def products_id_approve_delete_post(
        self,
        id: Annotated[StrictStr, Field(description="ID of the product to approve delete")],
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
        """Approve deletes the product with the specified ID

        Operation for approving a product. A 400 response is returned if the product could not be approved deleted.

        :param id: ID of the product to approve delete (required)
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

        _param = self._products_id_approve_delete_post_serialize(
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
    def products_id_approve_delete_post_with_http_info(
        self,
        id: Annotated[StrictStr, Field(description="ID of the product to approve delete")],
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
        """Approve deletes the product with the specified ID

        Operation for approving a product. A 400 response is returned if the product could not be approved deleted.

        :param id: ID of the product to approve delete (required)
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

        _param = self._products_id_approve_delete_post_serialize(
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
    def products_id_approve_delete_post_without_preload_content(
        self,
        id: Annotated[StrictStr, Field(description="ID of the product to approve delete")],
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
        """Approve deletes the product with the specified ID

        Operation for approving a product. A 400 response is returned if the product could not be approved deleted.

        :param id: ID of the product to approve delete (required)
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

        _param = self._products_id_approve_delete_post_serialize(
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
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        return response_data.response


    def _products_id_approve_delete_post_serialize(
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
            resource_path='/products/{id}/approve-delete',
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
    def products_id_approve_post(
        self,
        id: Annotated[StrictStr, Field(description="ID / key value of the product to approve")],
        context: Annotated[StrictStr, Field(description="ID of the context in which to perform the operation")],
        key_id: Annotated[Optional[StrictStr], Field(description="ID of the key definition to be used for identifying the product. If supplied, a key value should be supplied for the \"id\" path parameter.")] = None,
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
    ) -> ApprovalResponse:
        """Approves the product with the specified ID / key value

        Operation for approving a product. The operation can only be invoked in the Main workspace and a 400 response will be returned if the operation is invoked in another workspace. A 400 response is also returned if the product could not be approved, for instance due to a constraint (e.g. parent not present in Approved) or due to the approval being rejected by a business condition. The product to approve can be identified either by its STEP ID or if a value for the \"keyId\" query parameter is supplied, by its key value for the specified key.

        :param id: ID / key value of the product to approve (required)
        :type id: str
        :param context: ID of the context in which to perform the operation (required)
        :type context: str
        :param key_id: ID of the key definition to be used for identifying the product. If supplied, a key value should be supplied for the \"id\" path parameter.
        :type key_id: str
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

        _param = self._products_id_approve_post_serialize(
            id=id,
            context=context,
            key_id=key_id,
            workspace=workspace,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "ApprovalResponse",
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
    def products_id_approve_post_with_http_info(
        self,
        id: Annotated[StrictStr, Field(description="ID / key value of the product to approve")],
        context: Annotated[StrictStr, Field(description="ID of the context in which to perform the operation")],
        key_id: Annotated[Optional[StrictStr], Field(description="ID of the key definition to be used for identifying the product. If supplied, a key value should be supplied for the \"id\" path parameter.")] = None,
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
    ) -> ApiResponse[ApprovalResponse]:
        """Approves the product with the specified ID / key value

        Operation for approving a product. The operation can only be invoked in the Main workspace and a 400 response will be returned if the operation is invoked in another workspace. A 400 response is also returned if the product could not be approved, for instance due to a constraint (e.g. parent not present in Approved) or due to the approval being rejected by a business condition. The product to approve can be identified either by its STEP ID or if a value for the \"keyId\" query parameter is supplied, by its key value for the specified key.

        :param id: ID / key value of the product to approve (required)
        :type id: str
        :param context: ID of the context in which to perform the operation (required)
        :type context: str
        :param key_id: ID of the key definition to be used for identifying the product. If supplied, a key value should be supplied for the \"id\" path parameter.
        :type key_id: str
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

        _param = self._products_id_approve_post_serialize(
            id=id,
            context=context,
            key_id=key_id,
            workspace=workspace,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "ApprovalResponse",
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
    def products_id_approve_post_without_preload_content(
        self,
        id: Annotated[StrictStr, Field(description="ID / key value of the product to approve")],
        context: Annotated[StrictStr, Field(description="ID of the context in which to perform the operation")],
        key_id: Annotated[Optional[StrictStr], Field(description="ID of the key definition to be used for identifying the product. If supplied, a key value should be supplied for the \"id\" path parameter.")] = None,
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
        """Approves the product with the specified ID / key value

        Operation for approving a product. The operation can only be invoked in the Main workspace and a 400 response will be returned if the operation is invoked in another workspace. A 400 response is also returned if the product could not be approved, for instance due to a constraint (e.g. parent not present in Approved) or due to the approval being rejected by a business condition. The product to approve can be identified either by its STEP ID or if a value for the \"keyId\" query parameter is supplied, by its key value for the specified key.

        :param id: ID / key value of the product to approve (required)
        :type id: str
        :param context: ID of the context in which to perform the operation (required)
        :type context: str
        :param key_id: ID of the key definition to be used for identifying the product. If supplied, a key value should be supplied for the \"id\" path parameter.
        :type key_id: str
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

        _param = self._products_id_approve_post_serialize(
            id=id,
            context=context,
            key_id=key_id,
            workspace=workspace,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "ApprovalResponse",
            '400': "Error",
            '404': "Error",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        return response_data.response


    def _products_id_approve_post_serialize(
        self,
        id,
        context,
        key_id,
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
        if key_id is not None:
            
            _query_params.append(('keyId', key_id))
            
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
            resource_path='/products/{id}/approve',
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
    def products_id_children_get(
        self,
        id: Annotated[StrictStr, Field(description="ID / key value of the product for which to retrieve children information")],
        context: Annotated[StrictStr, Field(description="ID of the context in which to perform the operation")],
        key_id: Annotated[Optional[StrictStr], Field(description="ID of the key definition to be used for identifying the product. If supplied, a key value should be supplied for the \"id\" path parameter.")] = None,
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
    ) -> List[str]:
        """Returns a streamed array of IDs for product children

        Returns a streamed array of IDs for products directly below the specified product. The product can be identified either by its STEP ID or if a value for the \"keyId\" query parameter is supplied, by its key value for the specified key.

        :param id: ID / key value of the product for which to retrieve children information (required)
        :type id: str
        :param context: ID of the context in which to perform the operation (required)
        :type context: str
        :param key_id: ID of the key definition to be used for identifying the product. If supplied, a key value should be supplied for the \"id\" path parameter.
        :type key_id: str
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

        _param = self._products_id_children_get_serialize(
            id=id,
            context=context,
            key_id=key_id,
            workspace=workspace,
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
    def products_id_children_get_with_http_info(
        self,
        id: Annotated[StrictStr, Field(description="ID / key value of the product for which to retrieve children information")],
        context: Annotated[StrictStr, Field(description="ID of the context in which to perform the operation")],
        key_id: Annotated[Optional[StrictStr], Field(description="ID of the key definition to be used for identifying the product. If supplied, a key value should be supplied for the \"id\" path parameter.")] = None,
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
    ) -> ApiResponse[List[str]]:
        """Returns a streamed array of IDs for product children

        Returns a streamed array of IDs for products directly below the specified product. The product can be identified either by its STEP ID or if a value for the \"keyId\" query parameter is supplied, by its key value for the specified key.

        :param id: ID / key value of the product for which to retrieve children information (required)
        :type id: str
        :param context: ID of the context in which to perform the operation (required)
        :type context: str
        :param key_id: ID of the key definition to be used for identifying the product. If supplied, a key value should be supplied for the \"id\" path parameter.
        :type key_id: str
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

        _param = self._products_id_children_get_serialize(
            id=id,
            context=context,
            key_id=key_id,
            workspace=workspace,
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
    def products_id_children_get_without_preload_content(
        self,
        id: Annotated[StrictStr, Field(description="ID / key value of the product for which to retrieve children information")],
        context: Annotated[StrictStr, Field(description="ID of the context in which to perform the operation")],
        key_id: Annotated[Optional[StrictStr], Field(description="ID of the key definition to be used for identifying the product. If supplied, a key value should be supplied for the \"id\" path parameter.")] = None,
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
        """Returns a streamed array of IDs for product children

        Returns a streamed array of IDs for products directly below the specified product. The product can be identified either by its STEP ID or if a value for the \"keyId\" query parameter is supplied, by its key value for the specified key.

        :param id: ID / key value of the product for which to retrieve children information (required)
        :type id: str
        :param context: ID of the context in which to perform the operation (required)
        :type context: str
        :param key_id: ID of the key definition to be used for identifying the product. If supplied, a key value should be supplied for the \"id\" path parameter.
        :type key_id: str
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

        _param = self._products_id_children_get_serialize(
            id=id,
            context=context,
            key_id=key_id,
            workspace=workspace,
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


    def _products_id_children_get_serialize(
        self,
        id,
        context,
        key_id,
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
        if key_id is not None:
            
            _query_params.append(('keyId', key_id))
            
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
            resource_path='/products/{id}/children',
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
    def products_id_data_containers_data_container_type_id_get(
        self,
        id: Annotated[StrictStr, Field(description="ID / key value of the product to retrieve data container(s) for")],
        data_container_type_id: Annotated[StrictStr, Field(description="ID of the data container type")],
        context: Annotated[StrictStr, Field(description="ID of the context in which to perform the operation")],
        key_id: Annotated[Optional[StrictStr], Field(description="ID of the key definition to be used for identifying the product. If supplied, a key value should be supplied for the \"id\" path parameter.")] = None,
        workspace: Annotated[Optional[StrictStr], Field(description="ID of the workspace in which to perform the operation. Defaults to \"Main\".")] = None,
        include_inherited_data: Annotated[Optional[StrictBool], Field(description="Endpoint returns inherited data when parameter is supplied with the value true. Defaults to \"false\".")] = None,
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
    ) -> DataContainer:
        """Returns data container(s) of the specified type

        Returns data container(s) of the specified type. Response will either be a SingleDataContainer or a MultiDataContainer depending on whether the data container type is multivalued. The product can be identified either by its STEP ID or if a value for the \"keyId\" query parameter is supplied, by its key value for the specified key.

        :param id: ID / key value of the product to retrieve data container(s) for (required)
        :type id: str
        :param data_container_type_id: ID of the data container type (required)
        :type data_container_type_id: str
        :param context: ID of the context in which to perform the operation (required)
        :type context: str
        :param key_id: ID of the key definition to be used for identifying the product. If supplied, a key value should be supplied for the \"id\" path parameter.
        :type key_id: str
        :param workspace: ID of the workspace in which to perform the operation. Defaults to \"Main\".
        :type workspace: str
        :param include_inherited_data: Endpoint returns inherited data when parameter is supplied with the value true. Defaults to \"false\".
        :type include_inherited_data: bool
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

        _param = self._products_id_data_containers_data_container_type_id_get_serialize(
            id=id,
            data_container_type_id=data_container_type_id,
            context=context,
            key_id=key_id,
            workspace=workspace,
            include_inherited_data=include_inherited_data,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "DataContainer",
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
    def products_id_data_containers_data_container_type_id_get_with_http_info(
        self,
        id: Annotated[StrictStr, Field(description="ID / key value of the product to retrieve data container(s) for")],
        data_container_type_id: Annotated[StrictStr, Field(description="ID of the data container type")],
        context: Annotated[StrictStr, Field(description="ID of the context in which to perform the operation")],
        key_id: Annotated[Optional[StrictStr], Field(description="ID of the key definition to be used for identifying the product. If supplied, a key value should be supplied for the \"id\" path parameter.")] = None,
        workspace: Annotated[Optional[StrictStr], Field(description="ID of the workspace in which to perform the operation. Defaults to \"Main\".")] = None,
        include_inherited_data: Annotated[Optional[StrictBool], Field(description="Endpoint returns inherited data when parameter is supplied with the value true. Defaults to \"false\".")] = None,
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
    ) -> ApiResponse[DataContainer]:
        """Returns data container(s) of the specified type

        Returns data container(s) of the specified type. Response will either be a SingleDataContainer or a MultiDataContainer depending on whether the data container type is multivalued. The product can be identified either by its STEP ID or if a value for the \"keyId\" query parameter is supplied, by its key value for the specified key.

        :param id: ID / key value of the product to retrieve data container(s) for (required)
        :type id: str
        :param data_container_type_id: ID of the data container type (required)
        :type data_container_type_id: str
        :param context: ID of the context in which to perform the operation (required)
        :type context: str
        :param key_id: ID of the key definition to be used for identifying the product. If supplied, a key value should be supplied for the \"id\" path parameter.
        :type key_id: str
        :param workspace: ID of the workspace in which to perform the operation. Defaults to \"Main\".
        :type workspace: str
        :param include_inherited_data: Endpoint returns inherited data when parameter is supplied with the value true. Defaults to \"false\".
        :type include_inherited_data: bool
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

        _param = self._products_id_data_containers_data_container_type_id_get_serialize(
            id=id,
            data_container_type_id=data_container_type_id,
            context=context,
            key_id=key_id,
            workspace=workspace,
            include_inherited_data=include_inherited_data,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "DataContainer",
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
    def products_id_data_containers_data_container_type_id_get_without_preload_content(
        self,
        id: Annotated[StrictStr, Field(description="ID / key value of the product to retrieve data container(s) for")],
        data_container_type_id: Annotated[StrictStr, Field(description="ID of the data container type")],
        context: Annotated[StrictStr, Field(description="ID of the context in which to perform the operation")],
        key_id: Annotated[Optional[StrictStr], Field(description="ID of the key definition to be used for identifying the product. If supplied, a key value should be supplied for the \"id\" path parameter.")] = None,
        workspace: Annotated[Optional[StrictStr], Field(description="ID of the workspace in which to perform the operation. Defaults to \"Main\".")] = None,
        include_inherited_data: Annotated[Optional[StrictBool], Field(description="Endpoint returns inherited data when parameter is supplied with the value true. Defaults to \"false\".")] = None,
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
        """Returns data container(s) of the specified type

        Returns data container(s) of the specified type. Response will either be a SingleDataContainer or a MultiDataContainer depending on whether the data container type is multivalued. The product can be identified either by its STEP ID or if a value for the \"keyId\" query parameter is supplied, by its key value for the specified key.

        :param id: ID / key value of the product to retrieve data container(s) for (required)
        :type id: str
        :param data_container_type_id: ID of the data container type (required)
        :type data_container_type_id: str
        :param context: ID of the context in which to perform the operation (required)
        :type context: str
        :param key_id: ID of the key definition to be used for identifying the product. If supplied, a key value should be supplied for the \"id\" path parameter.
        :type key_id: str
        :param workspace: ID of the workspace in which to perform the operation. Defaults to \"Main\".
        :type workspace: str
        :param include_inherited_data: Endpoint returns inherited data when parameter is supplied with the value true. Defaults to \"false\".
        :type include_inherited_data: bool
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

        _param = self._products_id_data_containers_data_container_type_id_get_serialize(
            id=id,
            data_container_type_id=data_container_type_id,
            context=context,
            key_id=key_id,
            workspace=workspace,
            include_inherited_data=include_inherited_data,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "DataContainer",
            '400': "Error",
            '404': "Error",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        return response_data.response


    def _products_id_data_containers_data_container_type_id_get_serialize(
        self,
        id,
        data_container_type_id,
        context,
        key_id,
        workspace,
        include_inherited_data,
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
        if data_container_type_id is not None:
            _path_params['dataContainerTypeId'] = data_container_type_id
        # process the query parameters
        if key_id is not None:
            
            _query_params.append(('keyId', key_id))
            
        if context is not None:
            
            _query_params.append(('context', context))
            
        if workspace is not None:
            
            _query_params.append(('workspace', workspace))
            
        if include_inherited_data is not None:
            
            _query_params.append(('includeInheritedData', include_inherited_data))
            
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
            resource_path='/products/{id}/data-containers/{dataContainerTypeId}',
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
    def products_id_delete(
        self,
        id: Annotated[StrictStr, Field(description="ID / key value of the product to delete")],
        context: Annotated[StrictStr, Field(description="ID of the context in which to perform the operation")],
        key_id: Annotated[Optional[StrictStr], Field(description="ID of the key definition to be used for identifying the product. If supplied, a key value should be supplied for the \"id\" path parameter.")] = None,
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
        """Deletes the product with the specified ID / key value

        Operation for deleting a specific product. Operation can only be invoked in editable workspaces and will if successful move the product to the recycle bin. The product can be identified either by its STEP ID or if a value for the \"keyId\" query parameter is supplied, by its key value for the specified key.

        :param id: ID / key value of the product to delete (required)
        :type id: str
        :param context: ID of the context in which to perform the operation (required)
        :type context: str
        :param key_id: ID of the key definition to be used for identifying the product. If supplied, a key value should be supplied for the \"id\" path parameter.
        :type key_id: str
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

        _param = self._products_id_delete_serialize(
            id=id,
            context=context,
            key_id=key_id,
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
    def products_id_delete_with_http_info(
        self,
        id: Annotated[StrictStr, Field(description="ID / key value of the product to delete")],
        context: Annotated[StrictStr, Field(description="ID of the context in which to perform the operation")],
        key_id: Annotated[Optional[StrictStr], Field(description="ID of the key definition to be used for identifying the product. If supplied, a key value should be supplied for the \"id\" path parameter.")] = None,
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
        """Deletes the product with the specified ID / key value

        Operation for deleting a specific product. Operation can only be invoked in editable workspaces and will if successful move the product to the recycle bin. The product can be identified either by its STEP ID or if a value for the \"keyId\" query parameter is supplied, by its key value for the specified key.

        :param id: ID / key value of the product to delete (required)
        :type id: str
        :param context: ID of the context in which to perform the operation (required)
        :type context: str
        :param key_id: ID of the key definition to be used for identifying the product. If supplied, a key value should be supplied for the \"id\" path parameter.
        :type key_id: str
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

        _param = self._products_id_delete_serialize(
            id=id,
            context=context,
            key_id=key_id,
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
    def products_id_delete_without_preload_content(
        self,
        id: Annotated[StrictStr, Field(description="ID / key value of the product to delete")],
        context: Annotated[StrictStr, Field(description="ID of the context in which to perform the operation")],
        key_id: Annotated[Optional[StrictStr], Field(description="ID of the key definition to be used for identifying the product. If supplied, a key value should be supplied for the \"id\" path parameter.")] = None,
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
        """Deletes the product with the specified ID / key value

        Operation for deleting a specific product. Operation can only be invoked in editable workspaces and will if successful move the product to the recycle bin. The product can be identified either by its STEP ID or if a value for the \"keyId\" query parameter is supplied, by its key value for the specified key.

        :param id: ID / key value of the product to delete (required)
        :type id: str
        :param context: ID of the context in which to perform the operation (required)
        :type context: str
        :param key_id: ID of the key definition to be used for identifying the product. If supplied, a key value should be supplied for the \"id\" path parameter.
        :type key_id: str
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

        _param = self._products_id_delete_serialize(
            id=id,
            context=context,
            key_id=key_id,
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
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        return response_data.response


    def _products_id_delete_serialize(
        self,
        id,
        context,
        key_id,
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
        if key_id is not None:
            
            _query_params.append(('keyId', key_id))
            
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
            method='DELETE',
            resource_path='/products/{id}',
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
    def products_id_get(
        self,
        id: Annotated[StrictStr, Field(description="ID / key value of the product for which to retrieve data")],
        context: Annotated[StrictStr, Field(description="ID of the context in which to perform the operation")],
        key_id: Annotated[Optional[StrictStr], Field(description="ID of the key definition to be used for identifying the product. If supplied, a key value should be supplied for the \"id\" path parameter.")] = None,
        workspace: Annotated[Optional[StrictStr], Field(description="ID of the workspace in which to perform the operation. Defaults to \"Main\".")] = None,
        include_inherited_data: Annotated[Optional[StrictBool], Field(description="Endpoint returns inherited data when parameter is supplied with the value true. Defaults to \"false\".")] = None,
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
    ) -> Product:
        """Returns the product with the specified ID / key value

        Operation for retrieving information about a specific product object. The product can be identified either by its STEP ID or if a value for the \"keyId\" query parameter is supplied, by its key value for the specified key.

        :param id: ID / key value of the product for which to retrieve data (required)
        :type id: str
        :param context: ID of the context in which to perform the operation (required)
        :type context: str
        :param key_id: ID of the key definition to be used for identifying the product. If supplied, a key value should be supplied for the \"id\" path parameter.
        :type key_id: str
        :param workspace: ID of the workspace in which to perform the operation. Defaults to \"Main\".
        :type workspace: str
        :param include_inherited_data: Endpoint returns inherited data when parameter is supplied with the value true. Defaults to \"false\".
        :type include_inherited_data: bool
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

        _param = self._products_id_get_serialize(
            id=id,
            context=context,
            key_id=key_id,
            workspace=workspace,
            include_inherited_data=include_inherited_data,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "Product",
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
    def products_id_get_with_http_info(
        self,
        id: Annotated[StrictStr, Field(description="ID / key value of the product for which to retrieve data")],
        context: Annotated[StrictStr, Field(description="ID of the context in which to perform the operation")],
        key_id: Annotated[Optional[StrictStr], Field(description="ID of the key definition to be used for identifying the product. If supplied, a key value should be supplied for the \"id\" path parameter.")] = None,
        workspace: Annotated[Optional[StrictStr], Field(description="ID of the workspace in which to perform the operation. Defaults to \"Main\".")] = None,
        include_inherited_data: Annotated[Optional[StrictBool], Field(description="Endpoint returns inherited data when parameter is supplied with the value true. Defaults to \"false\".")] = None,
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
    ) -> ApiResponse[Product]:
        """Returns the product with the specified ID / key value

        Operation for retrieving information about a specific product object. The product can be identified either by its STEP ID or if a value for the \"keyId\" query parameter is supplied, by its key value for the specified key.

        :param id: ID / key value of the product for which to retrieve data (required)
        :type id: str
        :param context: ID of the context in which to perform the operation (required)
        :type context: str
        :param key_id: ID of the key definition to be used for identifying the product. If supplied, a key value should be supplied for the \"id\" path parameter.
        :type key_id: str
        :param workspace: ID of the workspace in which to perform the operation. Defaults to \"Main\".
        :type workspace: str
        :param include_inherited_data: Endpoint returns inherited data when parameter is supplied with the value true. Defaults to \"false\".
        :type include_inherited_data: bool
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

        _param = self._products_id_get_serialize(
            id=id,
            context=context,
            key_id=key_id,
            workspace=workspace,
            include_inherited_data=include_inherited_data,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "Product",
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
    def products_id_get_without_preload_content(
        self,
        id: Annotated[StrictStr, Field(description="ID / key value of the product for which to retrieve data")],
        context: Annotated[StrictStr, Field(description="ID of the context in which to perform the operation")],
        key_id: Annotated[Optional[StrictStr], Field(description="ID of the key definition to be used for identifying the product. If supplied, a key value should be supplied for the \"id\" path parameter.")] = None,
        workspace: Annotated[Optional[StrictStr], Field(description="ID of the workspace in which to perform the operation. Defaults to \"Main\".")] = None,
        include_inherited_data: Annotated[Optional[StrictBool], Field(description="Endpoint returns inherited data when parameter is supplied with the value true. Defaults to \"false\".")] = None,
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
        """Returns the product with the specified ID / key value

        Operation for retrieving information about a specific product object. The product can be identified either by its STEP ID or if a value for the \"keyId\" query parameter is supplied, by its key value for the specified key.

        :param id: ID / key value of the product for which to retrieve data (required)
        :type id: str
        :param context: ID of the context in which to perform the operation (required)
        :type context: str
        :param key_id: ID of the key definition to be used for identifying the product. If supplied, a key value should be supplied for the \"id\" path parameter.
        :type key_id: str
        :param workspace: ID of the workspace in which to perform the operation. Defaults to \"Main\".
        :type workspace: str
        :param include_inherited_data: Endpoint returns inherited data when parameter is supplied with the value true. Defaults to \"false\".
        :type include_inherited_data: bool
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

        _param = self._products_id_get_serialize(
            id=id,
            context=context,
            key_id=key_id,
            workspace=workspace,
            include_inherited_data=include_inherited_data,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "Product",
            '400': "Error",
            '404': "Error",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        return response_data.response


    def _products_id_get_serialize(
        self,
        id,
        context,
        key_id,
        workspace,
        include_inherited_data,
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
        if key_id is not None:
            
            _query_params.append(('keyId', key_id))
            
        if context is not None:
            
            _query_params.append(('context', context))
            
        if workspace is not None:
            
            _query_params.append(('workspace', workspace))
            
        if include_inherited_data is not None:
            
            _query_params.append(('includeInheritedData', include_inherited_data))
            
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
            resource_path='/products/{id}',
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
    def products_id_incoming_references_reference_type_id_get(
        self,
        id: Annotated[StrictStr, Field(description="ID / key value of the product for which to retrieve incoming references")],
        reference_type_id: Annotated[StrictStr, Field(description="ID of the reference type for which to retrieve incoming references")],
        context: Annotated[StrictStr, Field(description="ID of the context in which to perform the operation")],
        key_id: Annotated[Optional[StrictStr], Field(description="ID of the key definition to be used for identifying the product. If supplied, a key value should be supplied for the \"id\" path parameter.")] = None,
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
    ) -> List[IncomingReferenceEntry]:
        """Returns stream of incoming references of the specified type

        Returns an array of incoming references (IncomingReferenceEntry) of the specified type as a stream. Notice that this resource covers both \"cross references\" and \"classification product links\" owned by the product side. The product can be identified either by its STEP ID or if a value for the \"keyId\" query parameter is supplied, by its key value for the specified key.

        :param id: ID / key value of the product for which to retrieve incoming references (required)
        :type id: str
        :param reference_type_id: ID of the reference type for which to retrieve incoming references (required)
        :type reference_type_id: str
        :param context: ID of the context in which to perform the operation (required)
        :type context: str
        :param key_id: ID of the key definition to be used for identifying the product. If supplied, a key value should be supplied for the \"id\" path parameter.
        :type key_id: str
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

        _param = self._products_id_incoming_references_reference_type_id_get_serialize(
            id=id,
            reference_type_id=reference_type_id,
            context=context,
            key_id=key_id,
            workspace=workspace,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "List[IncomingReferenceEntry]",
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
    def products_id_incoming_references_reference_type_id_get_with_http_info(
        self,
        id: Annotated[StrictStr, Field(description="ID / key value of the product for which to retrieve incoming references")],
        reference_type_id: Annotated[StrictStr, Field(description="ID of the reference type for which to retrieve incoming references")],
        context: Annotated[StrictStr, Field(description="ID of the context in which to perform the operation")],
        key_id: Annotated[Optional[StrictStr], Field(description="ID of the key definition to be used for identifying the product. If supplied, a key value should be supplied for the \"id\" path parameter.")] = None,
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
    ) -> ApiResponse[List[IncomingReferenceEntry]]:
        """Returns stream of incoming references of the specified type

        Returns an array of incoming references (IncomingReferenceEntry) of the specified type as a stream. Notice that this resource covers both \"cross references\" and \"classification product links\" owned by the product side. The product can be identified either by its STEP ID or if a value for the \"keyId\" query parameter is supplied, by its key value for the specified key.

        :param id: ID / key value of the product for which to retrieve incoming references (required)
        :type id: str
        :param reference_type_id: ID of the reference type for which to retrieve incoming references (required)
        :type reference_type_id: str
        :param context: ID of the context in which to perform the operation (required)
        :type context: str
        :param key_id: ID of the key definition to be used for identifying the product. If supplied, a key value should be supplied for the \"id\" path parameter.
        :type key_id: str
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

        _param = self._products_id_incoming_references_reference_type_id_get_serialize(
            id=id,
            reference_type_id=reference_type_id,
            context=context,
            key_id=key_id,
            workspace=workspace,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "List[IncomingReferenceEntry]",
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
    def products_id_incoming_references_reference_type_id_get_without_preload_content(
        self,
        id: Annotated[StrictStr, Field(description="ID / key value of the product for which to retrieve incoming references")],
        reference_type_id: Annotated[StrictStr, Field(description="ID of the reference type for which to retrieve incoming references")],
        context: Annotated[StrictStr, Field(description="ID of the context in which to perform the operation")],
        key_id: Annotated[Optional[StrictStr], Field(description="ID of the key definition to be used for identifying the product. If supplied, a key value should be supplied for the \"id\" path parameter.")] = None,
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
        """Returns stream of incoming references of the specified type

        Returns an array of incoming references (IncomingReferenceEntry) of the specified type as a stream. Notice that this resource covers both \"cross references\" and \"classification product links\" owned by the product side. The product can be identified either by its STEP ID or if a value for the \"keyId\" query parameter is supplied, by its key value for the specified key.

        :param id: ID / key value of the product for which to retrieve incoming references (required)
        :type id: str
        :param reference_type_id: ID of the reference type for which to retrieve incoming references (required)
        :type reference_type_id: str
        :param context: ID of the context in which to perform the operation (required)
        :type context: str
        :param key_id: ID of the key definition to be used for identifying the product. If supplied, a key value should be supplied for the \"id\" path parameter.
        :type key_id: str
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

        _param = self._products_id_incoming_references_reference_type_id_get_serialize(
            id=id,
            reference_type_id=reference_type_id,
            context=context,
            key_id=key_id,
            workspace=workspace,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "List[IncomingReferenceEntry]",
            '400': "Error",
            '404': "Error",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        return response_data.response


    def _products_id_incoming_references_reference_type_id_get_serialize(
        self,
        id,
        reference_type_id,
        context,
        key_id,
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
        if reference_type_id is not None:
            _path_params['referenceTypeId'] = reference_type_id
        # process the query parameters
        if key_id is not None:
            
            _query_params.append(('keyId', key_id))
            
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
            resource_path='/products/{id}/incoming-references/{referenceTypeId}',
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
    def products_id_patch(
        self,
        id: Annotated[StrictStr, Field(description="ID / key value of the product to update")],
        context: Annotated[StrictStr, Field(description="ID of the context in which to perform the operation")],
        key_id: Annotated[Optional[StrictStr], Field(description="ID of the key definition to be used for identifying the product to update. If supplied, a key value should be supplied for the \"id\" path parameter.")] = None,
        workspace: Annotated[Optional[StrictStr], Field(description="ID of the workspace in which to perform the operation. Defaults to \"Main\".")] = None,
        product: Optional[Product] = None,
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
    ) -> Product:
        """Partially updates a product

        Operation for updating multiple properties with a single request. The product to update can be identified either by its STEP ID or if a value for the \"keyId\" query parameter is supplied, by its value for the specified key. Contrary to the PUT /products/{id} replace operation, this operation will only modify data present in the supplied request body.<br/>For both single and multivalued attributes, if a value representation is present in the request body, the existing value will be overwritten. Notice however that supplying the property \"contextLocal\" with the value \"false\" or the SingleValue \"calculated\" property with the value \"true\" will cause a value update to be ignored.<br/>For single valued reference types (incl. classification product link types owned by the product side), existing references will be replaced with those provided in the request body. For multivalued reference types, if references in the request body match existing references, these will be replaced. Otherwise references in the request body will be added (i.e. existing references not in the request body will not be removed). As with values, if the property \"contextLocal\" is supplied with the value \"false\" for a reference, the update will be ignored.<br/>If \"parent\" information is supplied, the product will be moved below the specified parent given that it differs from the current.<br/>Data containers can only be updated if auto IDs are configured for the data container type. For single valued data container types, existing data container objects will be replaced with the data container object in the request body. For multi valued data container types, data container objects in the request body will be added if the data container type does not have a key definition. If a data container key definition is present data container objects in the request body will replace existing data containers that matches the data container key, otherwise new data container objects will be added to the multi valued data container.<br/>For attribute links, supplied attribute links will either be added or will replace existing links.<br/>This resource operation does not allow for the product object type to be updated. If an ID is supplied in the request body, it must match the ID of the product identified via the URL.

        :param id: ID / key value of the product to update (required)
        :type id: str
        :param context: ID of the context in which to perform the operation (required)
        :type context: str
        :param key_id: ID of the key definition to be used for identifying the product to update. If supplied, a key value should be supplied for the \"id\" path parameter.
        :type key_id: str
        :param workspace: ID of the workspace in which to perform the operation. Defaults to \"Main\".
        :type workspace: str
        :param product:
        :type product: Product
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

        _param = self._products_id_patch_serialize(
            id=id,
            context=context,
            key_id=key_id,
            workspace=workspace,
            product=product,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "Product",
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
    def products_id_patch_with_http_info(
        self,
        id: Annotated[StrictStr, Field(description="ID / key value of the product to update")],
        context: Annotated[StrictStr, Field(description="ID of the context in which to perform the operation")],
        key_id: Annotated[Optional[StrictStr], Field(description="ID of the key definition to be used for identifying the product to update. If supplied, a key value should be supplied for the \"id\" path parameter.")] = None,
        workspace: Annotated[Optional[StrictStr], Field(description="ID of the workspace in which to perform the operation. Defaults to \"Main\".")] = None,
        product: Optional[Product] = None,
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
    ) -> ApiResponse[Product]:
        """Partially updates a product

        Operation for updating multiple properties with a single request. The product to update can be identified either by its STEP ID or if a value for the \"keyId\" query parameter is supplied, by its value for the specified key. Contrary to the PUT /products/{id} replace operation, this operation will only modify data present in the supplied request body.<br/>For both single and multivalued attributes, if a value representation is present in the request body, the existing value will be overwritten. Notice however that supplying the property \"contextLocal\" with the value \"false\" or the SingleValue \"calculated\" property with the value \"true\" will cause a value update to be ignored.<br/>For single valued reference types (incl. classification product link types owned by the product side), existing references will be replaced with those provided in the request body. For multivalued reference types, if references in the request body match existing references, these will be replaced. Otherwise references in the request body will be added (i.e. existing references not in the request body will not be removed). As with values, if the property \"contextLocal\" is supplied with the value \"false\" for a reference, the update will be ignored.<br/>If \"parent\" information is supplied, the product will be moved below the specified parent given that it differs from the current.<br/>Data containers can only be updated if auto IDs are configured for the data container type. For single valued data container types, existing data container objects will be replaced with the data container object in the request body. For multi valued data container types, data container objects in the request body will be added if the data container type does not have a key definition. If a data container key definition is present data container objects in the request body will replace existing data containers that matches the data container key, otherwise new data container objects will be added to the multi valued data container.<br/>For attribute links, supplied attribute links will either be added or will replace existing links.<br/>This resource operation does not allow for the product object type to be updated. If an ID is supplied in the request body, it must match the ID of the product identified via the URL.

        :param id: ID / key value of the product to update (required)
        :type id: str
        :param context: ID of the context in which to perform the operation (required)
        :type context: str
        :param key_id: ID of the key definition to be used for identifying the product to update. If supplied, a key value should be supplied for the \"id\" path parameter.
        :type key_id: str
        :param workspace: ID of the workspace in which to perform the operation. Defaults to \"Main\".
        :type workspace: str
        :param product:
        :type product: Product
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

        _param = self._products_id_patch_serialize(
            id=id,
            context=context,
            key_id=key_id,
            workspace=workspace,
            product=product,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "Product",
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
    def products_id_patch_without_preload_content(
        self,
        id: Annotated[StrictStr, Field(description="ID / key value of the product to update")],
        context: Annotated[StrictStr, Field(description="ID of the context in which to perform the operation")],
        key_id: Annotated[Optional[StrictStr], Field(description="ID of the key definition to be used for identifying the product to update. If supplied, a key value should be supplied for the \"id\" path parameter.")] = None,
        workspace: Annotated[Optional[StrictStr], Field(description="ID of the workspace in which to perform the operation. Defaults to \"Main\".")] = None,
        product: Optional[Product] = None,
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
        """Partially updates a product

        Operation for updating multiple properties with a single request. The product to update can be identified either by its STEP ID or if a value for the \"keyId\" query parameter is supplied, by its value for the specified key. Contrary to the PUT /products/{id} replace operation, this operation will only modify data present in the supplied request body.<br/>For both single and multivalued attributes, if a value representation is present in the request body, the existing value will be overwritten. Notice however that supplying the property \"contextLocal\" with the value \"false\" or the SingleValue \"calculated\" property with the value \"true\" will cause a value update to be ignored.<br/>For single valued reference types (incl. classification product link types owned by the product side), existing references will be replaced with those provided in the request body. For multivalued reference types, if references in the request body match existing references, these will be replaced. Otherwise references in the request body will be added (i.e. existing references not in the request body will not be removed). As with values, if the property \"contextLocal\" is supplied with the value \"false\" for a reference, the update will be ignored.<br/>If \"parent\" information is supplied, the product will be moved below the specified parent given that it differs from the current.<br/>Data containers can only be updated if auto IDs are configured for the data container type. For single valued data container types, existing data container objects will be replaced with the data container object in the request body. For multi valued data container types, data container objects in the request body will be added if the data container type does not have a key definition. If a data container key definition is present data container objects in the request body will replace existing data containers that matches the data container key, otherwise new data container objects will be added to the multi valued data container.<br/>For attribute links, supplied attribute links will either be added or will replace existing links.<br/>This resource operation does not allow for the product object type to be updated. If an ID is supplied in the request body, it must match the ID of the product identified via the URL.

        :param id: ID / key value of the product to update (required)
        :type id: str
        :param context: ID of the context in which to perform the operation (required)
        :type context: str
        :param key_id: ID of the key definition to be used for identifying the product to update. If supplied, a key value should be supplied for the \"id\" path parameter.
        :type key_id: str
        :param workspace: ID of the workspace in which to perform the operation. Defaults to \"Main\".
        :type workspace: str
        :param product:
        :type product: Product
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

        _param = self._products_id_patch_serialize(
            id=id,
            context=context,
            key_id=key_id,
            workspace=workspace,
            product=product,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "Product",
            '400': "Error",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        return response_data.response


    def _products_id_patch_serialize(
        self,
        id,
        context,
        key_id,
        workspace,
        product,
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
        if key_id is not None:
            
            _query_params.append(('keyId', key_id))
            
        if context is not None:
            
            _query_params.append(('context', context))
            
        if workspace is not None:
            
            _query_params.append(('workspace', workspace))
            
        # process the header parameters
        # process the form parameters
        # process the body parameter
        if product is not None:
            _body_params = product


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
                        'application/json'
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
            method='PATCH',
            resource_path='/products/{id}',
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
    def products_id_purge_post(
        self,
        id: Annotated[StrictStr, Field(description="ID of the product to delete")],
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
        """Purges the product with the specified ID from recycle bin

        Operation for purging a specific product. Operation can only be invoked if the product is already approve deleted.

        :param id: ID of the product to delete (required)
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

        _param = self._products_id_purge_post_serialize(
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
    def products_id_purge_post_with_http_info(
        self,
        id: Annotated[StrictStr, Field(description="ID of the product to delete")],
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
        """Purges the product with the specified ID from recycle bin

        Operation for purging a specific product. Operation can only be invoked if the product is already approve deleted.

        :param id: ID of the product to delete (required)
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

        _param = self._products_id_purge_post_serialize(
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
    def products_id_purge_post_without_preload_content(
        self,
        id: Annotated[StrictStr, Field(description="ID of the product to delete")],
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
        """Purges the product with the specified ID from recycle bin

        Operation for purging a specific product. Operation can only be invoked if the product is already approve deleted.

        :param id: ID of the product to delete (required)
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

        _param = self._products_id_purge_post_serialize(
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
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        return response_data.response


    def _products_id_purge_post_serialize(
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
            resource_path='/products/{id}/purge',
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
    def products_id_put(
        self,
        id: Annotated[StrictStr, Field(description="ID / key value of the product to create or replace")],
        context: Annotated[StrictStr, Field(description="ID of the context in which to perform the operation")],
        allow_overwrite: Annotated[Optional[StrictBool], Field(description="Specifies whether the product may be overwritten / replaced if it already exists. Defaults to \"false\".")] = None,
        key_id: Annotated[Optional[StrictStr], Field(description="ID of the key definition to be used for identifying the product to replace. If supplied, a key value should be supplied for the \"id\" path parameter. Cannot be used in combination with \"allow-overwrite=true\".")] = None,
        workspace: Annotated[Optional[StrictStr], Field(description="ID of the workspace in which to perform the operation. Defaults to \"Main\".")] = None,
        product: Optional[Product] = None,
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
    ) -> Product:
        """Creates or replaces product with known ID

        Operation for replacing an existing product or creating a new product with known ID. To avoid accidental replacement of existing products, replacement will only be performed if the value \"true\" is supplied for the \"allow-overwrite\" query parameter. A 400 response is returned if the value for \"allow-overwrite\" is \"false\" and a product with the specified ID already exists. When replacing, any data that is local to the working context (or not dimension dependent) and for which the client has write permissions will be overwritten and replaced with the data provided in the request body. Object type and parent must always be specified in the request body. For the replace case, the product can be identified either by its STEP ID or if a value for the \"keyId\" query parameter is supplied, by its value for the specified key. A STEP ID is required for creating a new product via this resource operation and a 400 response will therefore be returned if a \"keyId\" is supplied and the object does not exist in advance. If an ID is supplied in the request body, it must match the ID of the product identified via the URL.

        :param id: ID / key value of the product to create or replace (required)
        :type id: str
        :param context: ID of the context in which to perform the operation (required)
        :type context: str
        :param allow_overwrite: Specifies whether the product may be overwritten / replaced if it already exists. Defaults to \"false\".
        :type allow_overwrite: bool
        :param key_id: ID of the key definition to be used for identifying the product to replace. If supplied, a key value should be supplied for the \"id\" path parameter. Cannot be used in combination with \"allow-overwrite=true\".
        :type key_id: str
        :param workspace: ID of the workspace in which to perform the operation. Defaults to \"Main\".
        :type workspace: str
        :param product:
        :type product: Product
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

        _param = self._products_id_put_serialize(
            id=id,
            context=context,
            allow_overwrite=allow_overwrite,
            key_id=key_id,
            workspace=workspace,
            product=product,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "Product",
            '201': "Product",
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
    def products_id_put_with_http_info(
        self,
        id: Annotated[StrictStr, Field(description="ID / key value of the product to create or replace")],
        context: Annotated[StrictStr, Field(description="ID of the context in which to perform the operation")],
        allow_overwrite: Annotated[Optional[StrictBool], Field(description="Specifies whether the product may be overwritten / replaced if it already exists. Defaults to \"false\".")] = None,
        key_id: Annotated[Optional[StrictStr], Field(description="ID of the key definition to be used for identifying the product to replace. If supplied, a key value should be supplied for the \"id\" path parameter. Cannot be used in combination with \"allow-overwrite=true\".")] = None,
        workspace: Annotated[Optional[StrictStr], Field(description="ID of the workspace in which to perform the operation. Defaults to \"Main\".")] = None,
        product: Optional[Product] = None,
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
    ) -> ApiResponse[Product]:
        """Creates or replaces product with known ID

        Operation for replacing an existing product or creating a new product with known ID. To avoid accidental replacement of existing products, replacement will only be performed if the value \"true\" is supplied for the \"allow-overwrite\" query parameter. A 400 response is returned if the value for \"allow-overwrite\" is \"false\" and a product with the specified ID already exists. When replacing, any data that is local to the working context (or not dimension dependent) and for which the client has write permissions will be overwritten and replaced with the data provided in the request body. Object type and parent must always be specified in the request body. For the replace case, the product can be identified either by its STEP ID or if a value for the \"keyId\" query parameter is supplied, by its value for the specified key. A STEP ID is required for creating a new product via this resource operation and a 400 response will therefore be returned if a \"keyId\" is supplied and the object does not exist in advance. If an ID is supplied in the request body, it must match the ID of the product identified via the URL.

        :param id: ID / key value of the product to create or replace (required)
        :type id: str
        :param context: ID of the context in which to perform the operation (required)
        :type context: str
        :param allow_overwrite: Specifies whether the product may be overwritten / replaced if it already exists. Defaults to \"false\".
        :type allow_overwrite: bool
        :param key_id: ID of the key definition to be used for identifying the product to replace. If supplied, a key value should be supplied for the \"id\" path parameter. Cannot be used in combination with \"allow-overwrite=true\".
        :type key_id: str
        :param workspace: ID of the workspace in which to perform the operation. Defaults to \"Main\".
        :type workspace: str
        :param product:
        :type product: Product
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

        _param = self._products_id_put_serialize(
            id=id,
            context=context,
            allow_overwrite=allow_overwrite,
            key_id=key_id,
            workspace=workspace,
            product=product,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "Product",
            '201': "Product",
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
    def products_id_put_without_preload_content(
        self,
        id: Annotated[StrictStr, Field(description="ID / key value of the product to create or replace")],
        context: Annotated[StrictStr, Field(description="ID of the context in which to perform the operation")],
        allow_overwrite: Annotated[Optional[StrictBool], Field(description="Specifies whether the product may be overwritten / replaced if it already exists. Defaults to \"false\".")] = None,
        key_id: Annotated[Optional[StrictStr], Field(description="ID of the key definition to be used for identifying the product to replace. If supplied, a key value should be supplied for the \"id\" path parameter. Cannot be used in combination with \"allow-overwrite=true\".")] = None,
        workspace: Annotated[Optional[StrictStr], Field(description="ID of the workspace in which to perform the operation. Defaults to \"Main\".")] = None,
        product: Optional[Product] = None,
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
        """Creates or replaces product with known ID

        Operation for replacing an existing product or creating a new product with known ID. To avoid accidental replacement of existing products, replacement will only be performed if the value \"true\" is supplied for the \"allow-overwrite\" query parameter. A 400 response is returned if the value for \"allow-overwrite\" is \"false\" and a product with the specified ID already exists. When replacing, any data that is local to the working context (or not dimension dependent) and for which the client has write permissions will be overwritten and replaced with the data provided in the request body. Object type and parent must always be specified in the request body. For the replace case, the product can be identified either by its STEP ID or if a value for the \"keyId\" query parameter is supplied, by its value for the specified key. A STEP ID is required for creating a new product via this resource operation and a 400 response will therefore be returned if a \"keyId\" is supplied and the object does not exist in advance. If an ID is supplied in the request body, it must match the ID of the product identified via the URL.

        :param id: ID / key value of the product to create or replace (required)
        :type id: str
        :param context: ID of the context in which to perform the operation (required)
        :type context: str
        :param allow_overwrite: Specifies whether the product may be overwritten / replaced if it already exists. Defaults to \"false\".
        :type allow_overwrite: bool
        :param key_id: ID of the key definition to be used for identifying the product to replace. If supplied, a key value should be supplied for the \"id\" path parameter. Cannot be used in combination with \"allow-overwrite=true\".
        :type key_id: str
        :param workspace: ID of the workspace in which to perform the operation. Defaults to \"Main\".
        :type workspace: str
        :param product:
        :type product: Product
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

        _param = self._products_id_put_serialize(
            id=id,
            context=context,
            allow_overwrite=allow_overwrite,
            key_id=key_id,
            workspace=workspace,
            product=product,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "Product",
            '201': "Product",
            '400': "Error",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        return response_data.response


    def _products_id_put_serialize(
        self,
        id,
        context,
        allow_overwrite,
        key_id,
        workspace,
        product,
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
        if allow_overwrite is not None:
            
            _query_params.append(('allow-overwrite', allow_overwrite))
            
        if key_id is not None:
            
            _query_params.append(('keyId', key_id))
            
        if context is not None:
            
            _query_params.append(('context', context))
            
        if workspace is not None:
            
            _query_params.append(('workspace', workspace))
            
        # process the header parameters
        # process the form parameters
        # process the body parameter
        if product is not None:
            _body_params = product


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
                        'application/json'
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
            method='PUT',
            resource_path='/products/{id}',
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
    def products_id_references_reference_type_id_get(
        self,
        id: Annotated[StrictStr, Field(description="ID / key value of the product for which to retrieve references")],
        reference_type_id: Annotated[StrictStr, Field(description="ID of the reference type for which to retrieve references")],
        context: Annotated[StrictStr, Field(description="ID of the context in which to perform the operation")],
        key_id: Annotated[Optional[StrictStr], Field(description="ID of the key definition to be used for identifying the product. If supplied, a key value should be supplied for the \"id\" path parameter.")] = None,
        workspace: Annotated[Optional[StrictStr], Field(description="ID of the workspace in which to perform the operation. Defaults to \"Main\".")] = None,
        include_inherited_data: Annotated[Optional[StrictBool], Field(description="Endpoint returns inherited data when parameter is supplied with the value true. Defaults to \"false\".")] = None,
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
    ) -> Reference:
        """Returns reference(s) of the specified type

        Returns local reference(s) of the specified type owned by the product. Response will either be a SingleReference or a MultiReference depending on whether the reference type is multivalued. Notice that this resource covers both \"cross references\" and  \"classification product links\" owned by the product side. The product can be identified either by its STEP ID or if a value for the \"keyId\" query parameter is supplied, by its key value for the specified key.

        :param id: ID / key value of the product for which to retrieve references (required)
        :type id: str
        :param reference_type_id: ID of the reference type for which to retrieve references (required)
        :type reference_type_id: str
        :param context: ID of the context in which to perform the operation (required)
        :type context: str
        :param key_id: ID of the key definition to be used for identifying the product. If supplied, a key value should be supplied for the \"id\" path parameter.
        :type key_id: str
        :param workspace: ID of the workspace in which to perform the operation. Defaults to \"Main\".
        :type workspace: str
        :param include_inherited_data: Endpoint returns inherited data when parameter is supplied with the value true. Defaults to \"false\".
        :type include_inherited_data: bool
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

        _param = self._products_id_references_reference_type_id_get_serialize(
            id=id,
            reference_type_id=reference_type_id,
            context=context,
            key_id=key_id,
            workspace=workspace,
            include_inherited_data=include_inherited_data,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "Reference",
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
    def products_id_references_reference_type_id_get_with_http_info(
        self,
        id: Annotated[StrictStr, Field(description="ID / key value of the product for which to retrieve references")],
        reference_type_id: Annotated[StrictStr, Field(description="ID of the reference type for which to retrieve references")],
        context: Annotated[StrictStr, Field(description="ID of the context in which to perform the operation")],
        key_id: Annotated[Optional[StrictStr], Field(description="ID of the key definition to be used for identifying the product. If supplied, a key value should be supplied for the \"id\" path parameter.")] = None,
        workspace: Annotated[Optional[StrictStr], Field(description="ID of the workspace in which to perform the operation. Defaults to \"Main\".")] = None,
        include_inherited_data: Annotated[Optional[StrictBool], Field(description="Endpoint returns inherited data when parameter is supplied with the value true. Defaults to \"false\".")] = None,
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
    ) -> ApiResponse[Reference]:
        """Returns reference(s) of the specified type

        Returns local reference(s) of the specified type owned by the product. Response will either be a SingleReference or a MultiReference depending on whether the reference type is multivalued. Notice that this resource covers both \"cross references\" and  \"classification product links\" owned by the product side. The product can be identified either by its STEP ID or if a value for the \"keyId\" query parameter is supplied, by its key value for the specified key.

        :param id: ID / key value of the product for which to retrieve references (required)
        :type id: str
        :param reference_type_id: ID of the reference type for which to retrieve references (required)
        :type reference_type_id: str
        :param context: ID of the context in which to perform the operation (required)
        :type context: str
        :param key_id: ID of the key definition to be used for identifying the product. If supplied, a key value should be supplied for the \"id\" path parameter.
        :type key_id: str
        :param workspace: ID of the workspace in which to perform the operation. Defaults to \"Main\".
        :type workspace: str
        :param include_inherited_data: Endpoint returns inherited data when parameter is supplied with the value true. Defaults to \"false\".
        :type include_inherited_data: bool
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

        _param = self._products_id_references_reference_type_id_get_serialize(
            id=id,
            reference_type_id=reference_type_id,
            context=context,
            key_id=key_id,
            workspace=workspace,
            include_inherited_data=include_inherited_data,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "Reference",
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
    def products_id_references_reference_type_id_get_without_preload_content(
        self,
        id: Annotated[StrictStr, Field(description="ID / key value of the product for which to retrieve references")],
        reference_type_id: Annotated[StrictStr, Field(description="ID of the reference type for which to retrieve references")],
        context: Annotated[StrictStr, Field(description="ID of the context in which to perform the operation")],
        key_id: Annotated[Optional[StrictStr], Field(description="ID of the key definition to be used for identifying the product. If supplied, a key value should be supplied for the \"id\" path parameter.")] = None,
        workspace: Annotated[Optional[StrictStr], Field(description="ID of the workspace in which to perform the operation. Defaults to \"Main\".")] = None,
        include_inherited_data: Annotated[Optional[StrictBool], Field(description="Endpoint returns inherited data when parameter is supplied with the value true. Defaults to \"false\".")] = None,
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
        """Returns reference(s) of the specified type

        Returns local reference(s) of the specified type owned by the product. Response will either be a SingleReference or a MultiReference depending on whether the reference type is multivalued. Notice that this resource covers both \"cross references\" and  \"classification product links\" owned by the product side. The product can be identified either by its STEP ID or if a value for the \"keyId\" query parameter is supplied, by its key value for the specified key.

        :param id: ID / key value of the product for which to retrieve references (required)
        :type id: str
        :param reference_type_id: ID of the reference type for which to retrieve references (required)
        :type reference_type_id: str
        :param context: ID of the context in which to perform the operation (required)
        :type context: str
        :param key_id: ID of the key definition to be used for identifying the product. If supplied, a key value should be supplied for the \"id\" path parameter.
        :type key_id: str
        :param workspace: ID of the workspace in which to perform the operation. Defaults to \"Main\".
        :type workspace: str
        :param include_inherited_data: Endpoint returns inherited data when parameter is supplied with the value true. Defaults to \"false\".
        :type include_inherited_data: bool
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

        _param = self._products_id_references_reference_type_id_get_serialize(
            id=id,
            reference_type_id=reference_type_id,
            context=context,
            key_id=key_id,
            workspace=workspace,
            include_inherited_data=include_inherited_data,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "Reference",
            '400': "Error",
            '404': "Error",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        return response_data.response


    def _products_id_references_reference_type_id_get_serialize(
        self,
        id,
        reference_type_id,
        context,
        key_id,
        workspace,
        include_inherited_data,
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
        if reference_type_id is not None:
            _path_params['referenceTypeId'] = reference_type_id
        # process the query parameters
        if key_id is not None:
            
            _query_params.append(('keyId', key_id))
            
        if context is not None:
            
            _query_params.append(('context', context))
            
        if workspace is not None:
            
            _query_params.append(('workspace', workspace))
            
        if include_inherited_data is not None:
            
            _query_params.append(('includeInheritedData', include_inherited_data))
            
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
            resource_path='/products/{id}/references/{referenceTypeId}',
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
    def products_id_references_reference_type_id_target_id_delete(
        self,
        id: Annotated[StrictStr, Field(description="ID / key value of the product that owns the reference")],
        reference_type_id: Annotated[StrictStr, Field(description="ID of the reference type")],
        target_id: Annotated[StrictStr, Field(description="ID / key value of the reference target")],
        context: Annotated[StrictStr, Field(description="ID of the context in which to perform the operation")],
        key_id: Annotated[Optional[StrictStr], Field(description="ID of the key definition to be used for identifying the product that owns the reference. If supplied, a key value should be supplied for the \"id\" path parameter.")] = None,
        target_key_id: Annotated[Optional[StrictStr], Field(description="ID of the key definition to be used for identifying the reference target. If supplied, a key value should be supplied for the \"targetId\" path parameter.")] = None,
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
        """Deletes the reference

        Deletes the specified reference. Notice that it is only possible to delete references that are defined locally (\"contextLocal\": true). Further notice that this resource covers both \"cross references\" and \"classification product links\" owned by the product side. The product that owns the reference can be identified either by its STEP ID or if a value for the \"keyId\" query parameter is supplied, by its key value for the specified key. Likewise, the reference target can be identified either by its STEP ID or if a value for the \"targetKeyId\" query parameter is supplied, by its key value for the specified key.

        :param id: ID / key value of the product that owns the reference (required)
        :type id: str
        :param reference_type_id: ID of the reference type (required)
        :type reference_type_id: str
        :param target_id: ID / key value of the reference target (required)
        :type target_id: str
        :param context: ID of the context in which to perform the operation (required)
        :type context: str
        :param key_id: ID of the key definition to be used for identifying the product that owns the reference. If supplied, a key value should be supplied for the \"id\" path parameter.
        :type key_id: str
        :param target_key_id: ID of the key definition to be used for identifying the reference target. If supplied, a key value should be supplied for the \"targetId\" path parameter.
        :type target_key_id: str
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

        _param = self._products_id_references_reference_type_id_target_id_delete_serialize(
            id=id,
            reference_type_id=reference_type_id,
            target_id=target_id,
            context=context,
            key_id=key_id,
            target_key_id=target_key_id,
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
    def products_id_references_reference_type_id_target_id_delete_with_http_info(
        self,
        id: Annotated[StrictStr, Field(description="ID / key value of the product that owns the reference")],
        reference_type_id: Annotated[StrictStr, Field(description="ID of the reference type")],
        target_id: Annotated[StrictStr, Field(description="ID / key value of the reference target")],
        context: Annotated[StrictStr, Field(description="ID of the context in which to perform the operation")],
        key_id: Annotated[Optional[StrictStr], Field(description="ID of the key definition to be used for identifying the product that owns the reference. If supplied, a key value should be supplied for the \"id\" path parameter.")] = None,
        target_key_id: Annotated[Optional[StrictStr], Field(description="ID of the key definition to be used for identifying the reference target. If supplied, a key value should be supplied for the \"targetId\" path parameter.")] = None,
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
        """Deletes the reference

        Deletes the specified reference. Notice that it is only possible to delete references that are defined locally (\"contextLocal\": true). Further notice that this resource covers both \"cross references\" and \"classification product links\" owned by the product side. The product that owns the reference can be identified either by its STEP ID or if a value for the \"keyId\" query parameter is supplied, by its key value for the specified key. Likewise, the reference target can be identified either by its STEP ID or if a value for the \"targetKeyId\" query parameter is supplied, by its key value for the specified key.

        :param id: ID / key value of the product that owns the reference (required)
        :type id: str
        :param reference_type_id: ID of the reference type (required)
        :type reference_type_id: str
        :param target_id: ID / key value of the reference target (required)
        :type target_id: str
        :param context: ID of the context in which to perform the operation (required)
        :type context: str
        :param key_id: ID of the key definition to be used for identifying the product that owns the reference. If supplied, a key value should be supplied for the \"id\" path parameter.
        :type key_id: str
        :param target_key_id: ID of the key definition to be used for identifying the reference target. If supplied, a key value should be supplied for the \"targetId\" path parameter.
        :type target_key_id: str
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

        _param = self._products_id_references_reference_type_id_target_id_delete_serialize(
            id=id,
            reference_type_id=reference_type_id,
            target_id=target_id,
            context=context,
            key_id=key_id,
            target_key_id=target_key_id,
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
    def products_id_references_reference_type_id_target_id_delete_without_preload_content(
        self,
        id: Annotated[StrictStr, Field(description="ID / key value of the product that owns the reference")],
        reference_type_id: Annotated[StrictStr, Field(description="ID of the reference type")],
        target_id: Annotated[StrictStr, Field(description="ID / key value of the reference target")],
        context: Annotated[StrictStr, Field(description="ID of the context in which to perform the operation")],
        key_id: Annotated[Optional[StrictStr], Field(description="ID of the key definition to be used for identifying the product that owns the reference. If supplied, a key value should be supplied for the \"id\" path parameter.")] = None,
        target_key_id: Annotated[Optional[StrictStr], Field(description="ID of the key definition to be used for identifying the reference target. If supplied, a key value should be supplied for the \"targetId\" path parameter.")] = None,
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
        """Deletes the reference

        Deletes the specified reference. Notice that it is only possible to delete references that are defined locally (\"contextLocal\": true). Further notice that this resource covers both \"cross references\" and \"classification product links\" owned by the product side. The product that owns the reference can be identified either by its STEP ID or if a value for the \"keyId\" query parameter is supplied, by its key value for the specified key. Likewise, the reference target can be identified either by its STEP ID or if a value for the \"targetKeyId\" query parameter is supplied, by its key value for the specified key.

        :param id: ID / key value of the product that owns the reference (required)
        :type id: str
        :param reference_type_id: ID of the reference type (required)
        :type reference_type_id: str
        :param target_id: ID / key value of the reference target (required)
        :type target_id: str
        :param context: ID of the context in which to perform the operation (required)
        :type context: str
        :param key_id: ID of the key definition to be used for identifying the product that owns the reference. If supplied, a key value should be supplied for the \"id\" path parameter.
        :type key_id: str
        :param target_key_id: ID of the key definition to be used for identifying the reference target. If supplied, a key value should be supplied for the \"targetId\" path parameter.
        :type target_key_id: str
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

        _param = self._products_id_references_reference_type_id_target_id_delete_serialize(
            id=id,
            reference_type_id=reference_type_id,
            target_id=target_id,
            context=context,
            key_id=key_id,
            target_key_id=target_key_id,
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
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        return response_data.response


    def _products_id_references_reference_type_id_target_id_delete_serialize(
        self,
        id,
        reference_type_id,
        target_id,
        context,
        key_id,
        target_key_id,
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
        if reference_type_id is not None:
            _path_params['referenceTypeId'] = reference_type_id
        if target_id is not None:
            _path_params['targetId'] = target_id
        # process the query parameters
        if key_id is not None:
            
            _query_params.append(('keyId', key_id))
            
        if target_key_id is not None:
            
            _query_params.append(('targetKeyId', target_key_id))
            
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
            method='DELETE',
            resource_path='/products/{id}/references/{referenceTypeId}/{targetId}',
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
    def products_id_references_reference_type_id_target_id_get(
        self,
        id: Annotated[StrictStr, Field(description="ID / key value of the product that owns the reference")],
        reference_type_id: Annotated[StrictStr, Field(description="ID of the reference type")],
        target_id: Annotated[StrictStr, Field(description="ID / key value of the reference target")],
        context: Annotated[StrictStr, Field(description="ID of the context in which to perform the operation")],
        key_id: Annotated[Optional[StrictStr], Field(description="ID of the key definition to be used for identifying the product that owns the reference. If supplied, a key value should be supplied for the \"id\" path parameter.")] = None,
        target_key_id: Annotated[Optional[StrictStr], Field(description="ID of the key definition to be used for identifying the reference target. If supplied, a key value should be supplied for the \"targetId\" path parameter.")] = None,
        workspace: Annotated[Optional[StrictStr], Field(description="ID of the workspace in which to perform the operation. Defaults to \"Main\".")] = None,
        include_inherited_data: Annotated[Optional[StrictBool], Field(description="Endpoint returns inherited data when parameter is supplied with the value true. Defaults to \"false\".")] = None,
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
    ) -> ReferenceEntry:
        """Returns a specific reference

        Returns the local reference (ReferenceEntry) of specified type from specified product to specified target. Notice that this resource covers both \"cross references\" and \"classification product links\" owned by the product side. The product that owns the reference can be identified either by its STEP ID or if a value for the \"keyId\" query parameter is supplied, by its key value for the specified key. Likewise, the reference target can be identified either by its STEP ID or if a value for the \"targetKeyId\" query parameter is supplied, by its key value for the specified key.

        :param id: ID / key value of the product that owns the reference (required)
        :type id: str
        :param reference_type_id: ID of the reference type (required)
        :type reference_type_id: str
        :param target_id: ID / key value of the reference target (required)
        :type target_id: str
        :param context: ID of the context in which to perform the operation (required)
        :type context: str
        :param key_id: ID of the key definition to be used for identifying the product that owns the reference. If supplied, a key value should be supplied for the \"id\" path parameter.
        :type key_id: str
        :param target_key_id: ID of the key definition to be used for identifying the reference target. If supplied, a key value should be supplied for the \"targetId\" path parameter.
        :type target_key_id: str
        :param workspace: ID of the workspace in which to perform the operation. Defaults to \"Main\".
        :type workspace: str
        :param include_inherited_data: Endpoint returns inherited data when parameter is supplied with the value true. Defaults to \"false\".
        :type include_inherited_data: bool
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

        _param = self._products_id_references_reference_type_id_target_id_get_serialize(
            id=id,
            reference_type_id=reference_type_id,
            target_id=target_id,
            context=context,
            key_id=key_id,
            target_key_id=target_key_id,
            workspace=workspace,
            include_inherited_data=include_inherited_data,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "ReferenceEntry",
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
    def products_id_references_reference_type_id_target_id_get_with_http_info(
        self,
        id: Annotated[StrictStr, Field(description="ID / key value of the product that owns the reference")],
        reference_type_id: Annotated[StrictStr, Field(description="ID of the reference type")],
        target_id: Annotated[StrictStr, Field(description="ID / key value of the reference target")],
        context: Annotated[StrictStr, Field(description="ID of the context in which to perform the operation")],
        key_id: Annotated[Optional[StrictStr], Field(description="ID of the key definition to be used for identifying the product that owns the reference. If supplied, a key value should be supplied for the \"id\" path parameter.")] = None,
        target_key_id: Annotated[Optional[StrictStr], Field(description="ID of the key definition to be used for identifying the reference target. If supplied, a key value should be supplied for the \"targetId\" path parameter.")] = None,
        workspace: Annotated[Optional[StrictStr], Field(description="ID of the workspace in which to perform the operation. Defaults to \"Main\".")] = None,
        include_inherited_data: Annotated[Optional[StrictBool], Field(description="Endpoint returns inherited data when parameter is supplied with the value true. Defaults to \"false\".")] = None,
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
    ) -> ApiResponse[ReferenceEntry]:
        """Returns a specific reference

        Returns the local reference (ReferenceEntry) of specified type from specified product to specified target. Notice that this resource covers both \"cross references\" and \"classification product links\" owned by the product side. The product that owns the reference can be identified either by its STEP ID or if a value for the \"keyId\" query parameter is supplied, by its key value for the specified key. Likewise, the reference target can be identified either by its STEP ID or if a value for the \"targetKeyId\" query parameter is supplied, by its key value for the specified key.

        :param id: ID / key value of the product that owns the reference (required)
        :type id: str
        :param reference_type_id: ID of the reference type (required)
        :type reference_type_id: str
        :param target_id: ID / key value of the reference target (required)
        :type target_id: str
        :param context: ID of the context in which to perform the operation (required)
        :type context: str
        :param key_id: ID of the key definition to be used for identifying the product that owns the reference. If supplied, a key value should be supplied for the \"id\" path parameter.
        :type key_id: str
        :param target_key_id: ID of the key definition to be used for identifying the reference target. If supplied, a key value should be supplied for the \"targetId\" path parameter.
        :type target_key_id: str
        :param workspace: ID of the workspace in which to perform the operation. Defaults to \"Main\".
        :type workspace: str
        :param include_inherited_data: Endpoint returns inherited data when parameter is supplied with the value true. Defaults to \"false\".
        :type include_inherited_data: bool
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

        _param = self._products_id_references_reference_type_id_target_id_get_serialize(
            id=id,
            reference_type_id=reference_type_id,
            target_id=target_id,
            context=context,
            key_id=key_id,
            target_key_id=target_key_id,
            workspace=workspace,
            include_inherited_data=include_inherited_data,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "ReferenceEntry",
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
    def products_id_references_reference_type_id_target_id_get_without_preload_content(
        self,
        id: Annotated[StrictStr, Field(description="ID / key value of the product that owns the reference")],
        reference_type_id: Annotated[StrictStr, Field(description="ID of the reference type")],
        target_id: Annotated[StrictStr, Field(description="ID / key value of the reference target")],
        context: Annotated[StrictStr, Field(description="ID of the context in which to perform the operation")],
        key_id: Annotated[Optional[StrictStr], Field(description="ID of the key definition to be used for identifying the product that owns the reference. If supplied, a key value should be supplied for the \"id\" path parameter.")] = None,
        target_key_id: Annotated[Optional[StrictStr], Field(description="ID of the key definition to be used for identifying the reference target. If supplied, a key value should be supplied for the \"targetId\" path parameter.")] = None,
        workspace: Annotated[Optional[StrictStr], Field(description="ID of the workspace in which to perform the operation. Defaults to \"Main\".")] = None,
        include_inherited_data: Annotated[Optional[StrictBool], Field(description="Endpoint returns inherited data when parameter is supplied with the value true. Defaults to \"false\".")] = None,
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
        """Returns a specific reference

        Returns the local reference (ReferenceEntry) of specified type from specified product to specified target. Notice that this resource covers both \"cross references\" and \"classification product links\" owned by the product side. The product that owns the reference can be identified either by its STEP ID or if a value for the \"keyId\" query parameter is supplied, by its key value for the specified key. Likewise, the reference target can be identified either by its STEP ID or if a value for the \"targetKeyId\" query parameter is supplied, by its key value for the specified key.

        :param id: ID / key value of the product that owns the reference (required)
        :type id: str
        :param reference_type_id: ID of the reference type (required)
        :type reference_type_id: str
        :param target_id: ID / key value of the reference target (required)
        :type target_id: str
        :param context: ID of the context in which to perform the operation (required)
        :type context: str
        :param key_id: ID of the key definition to be used for identifying the product that owns the reference. If supplied, a key value should be supplied for the \"id\" path parameter.
        :type key_id: str
        :param target_key_id: ID of the key definition to be used for identifying the reference target. If supplied, a key value should be supplied for the \"targetId\" path parameter.
        :type target_key_id: str
        :param workspace: ID of the workspace in which to perform the operation. Defaults to \"Main\".
        :type workspace: str
        :param include_inherited_data: Endpoint returns inherited data when parameter is supplied with the value true. Defaults to \"false\".
        :type include_inherited_data: bool
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

        _param = self._products_id_references_reference_type_id_target_id_get_serialize(
            id=id,
            reference_type_id=reference_type_id,
            target_id=target_id,
            context=context,
            key_id=key_id,
            target_key_id=target_key_id,
            workspace=workspace,
            include_inherited_data=include_inherited_data,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "ReferenceEntry",
            '400': "Error",
            '404': "Error",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        return response_data.response


    def _products_id_references_reference_type_id_target_id_get_serialize(
        self,
        id,
        reference_type_id,
        target_id,
        context,
        key_id,
        target_key_id,
        workspace,
        include_inherited_data,
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
        if reference_type_id is not None:
            _path_params['referenceTypeId'] = reference_type_id
        if target_id is not None:
            _path_params['targetId'] = target_id
        # process the query parameters
        if key_id is not None:
            
            _query_params.append(('keyId', key_id))
            
        if target_key_id is not None:
            
            _query_params.append(('targetKeyId', target_key_id))
            
        if context is not None:
            
            _query_params.append(('context', context))
            
        if workspace is not None:
            
            _query_params.append(('workspace', workspace))
            
        if include_inherited_data is not None:
            
            _query_params.append(('includeInheritedData', include_inherited_data))
            
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
            resource_path='/products/{id}/references/{referenceTypeId}/{targetId}',
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
    def products_id_references_reference_type_id_target_id_put(
        self,
        id: Annotated[StrictStr, Field(description="ID / key value of the product that should own the reference")],
        reference_type_id: Annotated[StrictStr, Field(description="ID of the reference type")],
        target_id: Annotated[StrictStr, Field(description="ID / key value of the desired reference target")],
        context: Annotated[StrictStr, Field(description="ID of the context in which to perform the operation")],
        key_id: Annotated[Optional[StrictStr], Field(description="ID of the key definition to be used for identifying the product that owns / will own the reference. If supplied, a key value should be supplied for the \"id\" path parameter.")] = None,
        target_key_id: Annotated[Optional[StrictStr], Field(description="ID of the key definition to be used for identifying the reference target. If supplied, a key value should be supplied for the \"targetId\" path parameter.")] = None,
        allow_overwrite: Annotated[Optional[StrictBool], Field(description="Specifies whether existing references may be overwritten. This includes references of the same type to the same target and for single-valued reference types, references of the same type to any target. Defaults to \"false\".")] = None,
        workspace: Annotated[Optional[StrictStr], Field(description="ID of the workspace in which to perform the operation. Defaults to \"Main\".")] = None,
        reference_entry: Optional[ReferenceEntry] = None,
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
    ) -> ReferenceEntry:
        """Replaces a reference

        Replaces the specified reference. If a locally defined reference to the same target already exists or if the reference type is single-valued and a locally defined reference from the source already exists, the \"allow-overwrite\" query parameter must be set to \"true\" in order for the existing reference to be replaced. Notice that this resource covers both \"cross references\" and \"classification product links\" owned by the product side. The product that owns / will own the reference can be identified either by its STEP ID or if a value for the \"keyId\" query parameter is supplied, by its key value for the specified key. Likewise, the reference target can be identified either by its STEP ID or if a value for the \"targetKeyId\" query parameter is supplied, by its key value for the specified key. Notice that if \"target\" or \"targetType\" is supplied in the request body, the values must match the reference type and the STEP ID of the target specified in the URL. If the property \"contextLocal\" is supplied with the value \"false\", the update will be ignored.

        :param id: ID / key value of the product that should own the reference (required)
        :type id: str
        :param reference_type_id: ID of the reference type (required)
        :type reference_type_id: str
        :param target_id: ID / key value of the desired reference target (required)
        :type target_id: str
        :param context: ID of the context in which to perform the operation (required)
        :type context: str
        :param key_id: ID of the key definition to be used for identifying the product that owns / will own the reference. If supplied, a key value should be supplied for the \"id\" path parameter.
        :type key_id: str
        :param target_key_id: ID of the key definition to be used for identifying the reference target. If supplied, a key value should be supplied for the \"targetId\" path parameter.
        :type target_key_id: str
        :param allow_overwrite: Specifies whether existing references may be overwritten. This includes references of the same type to the same target and for single-valued reference types, references of the same type to any target. Defaults to \"false\".
        :type allow_overwrite: bool
        :param workspace: ID of the workspace in which to perform the operation. Defaults to \"Main\".
        :type workspace: str
        :param reference_entry:
        :type reference_entry: ReferenceEntry
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

        _param = self._products_id_references_reference_type_id_target_id_put_serialize(
            id=id,
            reference_type_id=reference_type_id,
            target_id=target_id,
            context=context,
            key_id=key_id,
            target_key_id=target_key_id,
            allow_overwrite=allow_overwrite,
            workspace=workspace,
            reference_entry=reference_entry,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "ReferenceEntry",
            '201': "ReferenceEntry",
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
    def products_id_references_reference_type_id_target_id_put_with_http_info(
        self,
        id: Annotated[StrictStr, Field(description="ID / key value of the product that should own the reference")],
        reference_type_id: Annotated[StrictStr, Field(description="ID of the reference type")],
        target_id: Annotated[StrictStr, Field(description="ID / key value of the desired reference target")],
        context: Annotated[StrictStr, Field(description="ID of the context in which to perform the operation")],
        key_id: Annotated[Optional[StrictStr], Field(description="ID of the key definition to be used for identifying the product that owns / will own the reference. If supplied, a key value should be supplied for the \"id\" path parameter.")] = None,
        target_key_id: Annotated[Optional[StrictStr], Field(description="ID of the key definition to be used for identifying the reference target. If supplied, a key value should be supplied for the \"targetId\" path parameter.")] = None,
        allow_overwrite: Annotated[Optional[StrictBool], Field(description="Specifies whether existing references may be overwritten. This includes references of the same type to the same target and for single-valued reference types, references of the same type to any target. Defaults to \"false\".")] = None,
        workspace: Annotated[Optional[StrictStr], Field(description="ID of the workspace in which to perform the operation. Defaults to \"Main\".")] = None,
        reference_entry: Optional[ReferenceEntry] = None,
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
    ) -> ApiResponse[ReferenceEntry]:
        """Replaces a reference

        Replaces the specified reference. If a locally defined reference to the same target already exists or if the reference type is single-valued and a locally defined reference from the source already exists, the \"allow-overwrite\" query parameter must be set to \"true\" in order for the existing reference to be replaced. Notice that this resource covers both \"cross references\" and \"classification product links\" owned by the product side. The product that owns / will own the reference can be identified either by its STEP ID or if a value for the \"keyId\" query parameter is supplied, by its key value for the specified key. Likewise, the reference target can be identified either by its STEP ID or if a value for the \"targetKeyId\" query parameter is supplied, by its key value for the specified key. Notice that if \"target\" or \"targetType\" is supplied in the request body, the values must match the reference type and the STEP ID of the target specified in the URL. If the property \"contextLocal\" is supplied with the value \"false\", the update will be ignored.

        :param id: ID / key value of the product that should own the reference (required)
        :type id: str
        :param reference_type_id: ID of the reference type (required)
        :type reference_type_id: str
        :param target_id: ID / key value of the desired reference target (required)
        :type target_id: str
        :param context: ID of the context in which to perform the operation (required)
        :type context: str
        :param key_id: ID of the key definition to be used for identifying the product that owns / will own the reference. If supplied, a key value should be supplied for the \"id\" path parameter.
        :type key_id: str
        :param target_key_id: ID of the key definition to be used for identifying the reference target. If supplied, a key value should be supplied for the \"targetId\" path parameter.
        :type target_key_id: str
        :param allow_overwrite: Specifies whether existing references may be overwritten. This includes references of the same type to the same target and for single-valued reference types, references of the same type to any target. Defaults to \"false\".
        :type allow_overwrite: bool
        :param workspace: ID of the workspace in which to perform the operation. Defaults to \"Main\".
        :type workspace: str
        :param reference_entry:
        :type reference_entry: ReferenceEntry
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

        _param = self._products_id_references_reference_type_id_target_id_put_serialize(
            id=id,
            reference_type_id=reference_type_id,
            target_id=target_id,
            context=context,
            key_id=key_id,
            target_key_id=target_key_id,
            allow_overwrite=allow_overwrite,
            workspace=workspace,
            reference_entry=reference_entry,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "ReferenceEntry",
            '201': "ReferenceEntry",
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
    def products_id_references_reference_type_id_target_id_put_without_preload_content(
        self,
        id: Annotated[StrictStr, Field(description="ID / key value of the product that should own the reference")],
        reference_type_id: Annotated[StrictStr, Field(description="ID of the reference type")],
        target_id: Annotated[StrictStr, Field(description="ID / key value of the desired reference target")],
        context: Annotated[StrictStr, Field(description="ID of the context in which to perform the operation")],
        key_id: Annotated[Optional[StrictStr], Field(description="ID of the key definition to be used for identifying the product that owns / will own the reference. If supplied, a key value should be supplied for the \"id\" path parameter.")] = None,
        target_key_id: Annotated[Optional[StrictStr], Field(description="ID of the key definition to be used for identifying the reference target. If supplied, a key value should be supplied for the \"targetId\" path parameter.")] = None,
        allow_overwrite: Annotated[Optional[StrictBool], Field(description="Specifies whether existing references may be overwritten. This includes references of the same type to the same target and for single-valued reference types, references of the same type to any target. Defaults to \"false\".")] = None,
        workspace: Annotated[Optional[StrictStr], Field(description="ID of the workspace in which to perform the operation. Defaults to \"Main\".")] = None,
        reference_entry: Optional[ReferenceEntry] = None,
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
        """Replaces a reference

        Replaces the specified reference. If a locally defined reference to the same target already exists or if the reference type is single-valued and a locally defined reference from the source already exists, the \"allow-overwrite\" query parameter must be set to \"true\" in order for the existing reference to be replaced. Notice that this resource covers both \"cross references\" and \"classification product links\" owned by the product side. The product that owns / will own the reference can be identified either by its STEP ID or if a value for the \"keyId\" query parameter is supplied, by its key value for the specified key. Likewise, the reference target can be identified either by its STEP ID or if a value for the \"targetKeyId\" query parameter is supplied, by its key value for the specified key. Notice that if \"target\" or \"targetType\" is supplied in the request body, the values must match the reference type and the STEP ID of the target specified in the URL. If the property \"contextLocal\" is supplied with the value \"false\", the update will be ignored.

        :param id: ID / key value of the product that should own the reference (required)
        :type id: str
        :param reference_type_id: ID of the reference type (required)
        :type reference_type_id: str
        :param target_id: ID / key value of the desired reference target (required)
        :type target_id: str
        :param context: ID of the context in which to perform the operation (required)
        :type context: str
        :param key_id: ID of the key definition to be used for identifying the product that owns / will own the reference. If supplied, a key value should be supplied for the \"id\" path parameter.
        :type key_id: str
        :param target_key_id: ID of the key definition to be used for identifying the reference target. If supplied, a key value should be supplied for the \"targetId\" path parameter.
        :type target_key_id: str
        :param allow_overwrite: Specifies whether existing references may be overwritten. This includes references of the same type to the same target and for single-valued reference types, references of the same type to any target. Defaults to \"false\".
        :type allow_overwrite: bool
        :param workspace: ID of the workspace in which to perform the operation. Defaults to \"Main\".
        :type workspace: str
        :param reference_entry:
        :type reference_entry: ReferenceEntry
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

        _param = self._products_id_references_reference_type_id_target_id_put_serialize(
            id=id,
            reference_type_id=reference_type_id,
            target_id=target_id,
            context=context,
            key_id=key_id,
            target_key_id=target_key_id,
            allow_overwrite=allow_overwrite,
            workspace=workspace,
            reference_entry=reference_entry,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "ReferenceEntry",
            '201': "ReferenceEntry",
            '400': "Error",
            '404': "Error",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        return response_data.response


    def _products_id_references_reference_type_id_target_id_put_serialize(
        self,
        id,
        reference_type_id,
        target_id,
        context,
        key_id,
        target_key_id,
        allow_overwrite,
        workspace,
        reference_entry,
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
        if reference_type_id is not None:
            _path_params['referenceTypeId'] = reference_type_id
        if target_id is not None:
            _path_params['targetId'] = target_id
        # process the query parameters
        if key_id is not None:
            
            _query_params.append(('keyId', key_id))
            
        if target_key_id is not None:
            
            _query_params.append(('targetKeyId', target_key_id))
            
        if allow_overwrite is not None:
            
            _query_params.append(('allow-overwrite', allow_overwrite))
            
        if context is not None:
            
            _query_params.append(('context', context))
            
        if workspace is not None:
            
            _query_params.append(('workspace', workspace))
            
        # process the header parameters
        # process the form parameters
        # process the body parameter
        if reference_entry is not None:
            _body_params = reference_entry


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
                        'application/json'
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
            method='PUT',
            resource_path='/products/{id}/references/{referenceTypeId}/{targetId}',
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
    def products_id_references_reference_type_id_target_id_values_attribute_id_delete(
        self,
        id: Annotated[StrictStr, Field(description="ID / key value of the product owning the reference for which to delete the attribute value")],
        reference_type_id: Annotated[StrictStr, Field(description="ID of the reference type")],
        target_id: Annotated[StrictStr, Field(description="ID / key value of the reference target")],
        attribute_id: Annotated[StrictStr, Field(description="ID of the attribute for which to delete the value")],
        context: Annotated[StrictStr, Field(description="ID of the context in which to perform the operation")],
        key_id: Annotated[Optional[StrictStr], Field(description="ID of the key definition to be used for identifying the product that owns the reference. If supplied, a key value should be supplied for the \"id\" path parameter.")] = None,
        target_key_id: Annotated[Optional[StrictStr], Field(description="ID of the key definition to be used for identifying the reference target. If supplied, a key value should be supplied for the \"targetId\" path parameter.")] = None,
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
    ) -> Value:
        """Deletes the value for a reference metadata attribute

        Operation for deleting the value of an attribute on a reference. Notice that it is only possible to delete non-calculated values on references that are defined locally (\"contextLocal\": true). Further notice that this resource covers values on both \"cross references\" and \"classification product links\" owned by the product side. The product that owns the reference can be identified either by its STEP ID or if a value for the \"keyId\" query parameter is supplied, by its key value for the specified key. Likewise, the reference target can be identified either by its STEP ID or if a value for the \"targetKeyId\" query parameter is supplied, by its key value for the specified key.

        :param id: ID / key value of the product owning the reference for which to delete the attribute value (required)
        :type id: str
        :param reference_type_id: ID of the reference type (required)
        :type reference_type_id: str
        :param target_id: ID / key value of the reference target (required)
        :type target_id: str
        :param attribute_id: ID of the attribute for which to delete the value (required)
        :type attribute_id: str
        :param context: ID of the context in which to perform the operation (required)
        :type context: str
        :param key_id: ID of the key definition to be used for identifying the product that owns the reference. If supplied, a key value should be supplied for the \"id\" path parameter.
        :type key_id: str
        :param target_key_id: ID of the key definition to be used for identifying the reference target. If supplied, a key value should be supplied for the \"targetId\" path parameter.
        :type target_key_id: str
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

        _param = self._products_id_references_reference_type_id_target_id_values_attribute_id_delete_serialize(
            id=id,
            reference_type_id=reference_type_id,
            target_id=target_id,
            attribute_id=attribute_id,
            context=context,
            key_id=key_id,
            target_key_id=target_key_id,
            workspace=workspace,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "Value",
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
    def products_id_references_reference_type_id_target_id_values_attribute_id_delete_with_http_info(
        self,
        id: Annotated[StrictStr, Field(description="ID / key value of the product owning the reference for which to delete the attribute value")],
        reference_type_id: Annotated[StrictStr, Field(description="ID of the reference type")],
        target_id: Annotated[StrictStr, Field(description="ID / key value of the reference target")],
        attribute_id: Annotated[StrictStr, Field(description="ID of the attribute for which to delete the value")],
        context: Annotated[StrictStr, Field(description="ID of the context in which to perform the operation")],
        key_id: Annotated[Optional[StrictStr], Field(description="ID of the key definition to be used for identifying the product that owns the reference. If supplied, a key value should be supplied for the \"id\" path parameter.")] = None,
        target_key_id: Annotated[Optional[StrictStr], Field(description="ID of the key definition to be used for identifying the reference target. If supplied, a key value should be supplied for the \"targetId\" path parameter.")] = None,
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
    ) -> ApiResponse[Value]:
        """Deletes the value for a reference metadata attribute

        Operation for deleting the value of an attribute on a reference. Notice that it is only possible to delete non-calculated values on references that are defined locally (\"contextLocal\": true). Further notice that this resource covers values on both \"cross references\" and \"classification product links\" owned by the product side. The product that owns the reference can be identified either by its STEP ID or if a value for the \"keyId\" query parameter is supplied, by its key value for the specified key. Likewise, the reference target can be identified either by its STEP ID or if a value for the \"targetKeyId\" query parameter is supplied, by its key value for the specified key.

        :param id: ID / key value of the product owning the reference for which to delete the attribute value (required)
        :type id: str
        :param reference_type_id: ID of the reference type (required)
        :type reference_type_id: str
        :param target_id: ID / key value of the reference target (required)
        :type target_id: str
        :param attribute_id: ID of the attribute for which to delete the value (required)
        :type attribute_id: str
        :param context: ID of the context in which to perform the operation (required)
        :type context: str
        :param key_id: ID of the key definition to be used for identifying the product that owns the reference. If supplied, a key value should be supplied for the \"id\" path parameter.
        :type key_id: str
        :param target_key_id: ID of the key definition to be used for identifying the reference target. If supplied, a key value should be supplied for the \"targetId\" path parameter.
        :type target_key_id: str
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

        _param = self._products_id_references_reference_type_id_target_id_values_attribute_id_delete_serialize(
            id=id,
            reference_type_id=reference_type_id,
            target_id=target_id,
            attribute_id=attribute_id,
            context=context,
            key_id=key_id,
            target_key_id=target_key_id,
            workspace=workspace,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "Value",
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
    def products_id_references_reference_type_id_target_id_values_attribute_id_delete_without_preload_content(
        self,
        id: Annotated[StrictStr, Field(description="ID / key value of the product owning the reference for which to delete the attribute value")],
        reference_type_id: Annotated[StrictStr, Field(description="ID of the reference type")],
        target_id: Annotated[StrictStr, Field(description="ID / key value of the reference target")],
        attribute_id: Annotated[StrictStr, Field(description="ID of the attribute for which to delete the value")],
        context: Annotated[StrictStr, Field(description="ID of the context in which to perform the operation")],
        key_id: Annotated[Optional[StrictStr], Field(description="ID of the key definition to be used for identifying the product that owns the reference. If supplied, a key value should be supplied for the \"id\" path parameter.")] = None,
        target_key_id: Annotated[Optional[StrictStr], Field(description="ID of the key definition to be used for identifying the reference target. If supplied, a key value should be supplied for the \"targetId\" path parameter.")] = None,
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
        """Deletes the value for a reference metadata attribute

        Operation for deleting the value of an attribute on a reference. Notice that it is only possible to delete non-calculated values on references that are defined locally (\"contextLocal\": true). Further notice that this resource covers values on both \"cross references\" and \"classification product links\" owned by the product side. The product that owns the reference can be identified either by its STEP ID or if a value for the \"keyId\" query parameter is supplied, by its key value for the specified key. Likewise, the reference target can be identified either by its STEP ID or if a value for the \"targetKeyId\" query parameter is supplied, by its key value for the specified key.

        :param id: ID / key value of the product owning the reference for which to delete the attribute value (required)
        :type id: str
        :param reference_type_id: ID of the reference type (required)
        :type reference_type_id: str
        :param target_id: ID / key value of the reference target (required)
        :type target_id: str
        :param attribute_id: ID of the attribute for which to delete the value (required)
        :type attribute_id: str
        :param context: ID of the context in which to perform the operation (required)
        :type context: str
        :param key_id: ID of the key definition to be used for identifying the product that owns the reference. If supplied, a key value should be supplied for the \"id\" path parameter.
        :type key_id: str
        :param target_key_id: ID of the key definition to be used for identifying the reference target. If supplied, a key value should be supplied for the \"targetId\" path parameter.
        :type target_key_id: str
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

        _param = self._products_id_references_reference_type_id_target_id_values_attribute_id_delete_serialize(
            id=id,
            reference_type_id=reference_type_id,
            target_id=target_id,
            attribute_id=attribute_id,
            context=context,
            key_id=key_id,
            target_key_id=target_key_id,
            workspace=workspace,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "Value",
            '400': "Error",
            '404': "Error",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        return response_data.response


    def _products_id_references_reference_type_id_target_id_values_attribute_id_delete_serialize(
        self,
        id,
        reference_type_id,
        target_id,
        attribute_id,
        context,
        key_id,
        target_key_id,
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
        if reference_type_id is not None:
            _path_params['referenceTypeId'] = reference_type_id
        if target_id is not None:
            _path_params['targetId'] = target_id
        if attribute_id is not None:
            _path_params['attributeId'] = attribute_id
        # process the query parameters
        if key_id is not None:
            
            _query_params.append(('keyId', key_id))
            
        if target_key_id is not None:
            
            _query_params.append(('targetKeyId', target_key_id))
            
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
            method='DELETE',
            resource_path='/products/{id}/references/{referenceTypeId}/{targetId}/values/{attributeId}',
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
    def products_id_references_reference_type_id_target_id_values_attribute_id_get(
        self,
        id: Annotated[StrictStr, Field(description="ID / key value of the product that owns the reference")],
        reference_type_id: Annotated[StrictStr, Field(description="ID of the reference type")],
        target_id: Annotated[StrictStr, Field(description="ID / key value of the reference target")],
        attribute_id: Annotated[StrictStr, Field(description="ID of the attribute for which to retrieve the value")],
        context: Annotated[StrictStr, Field(description="ID of the context in which to perform the operation")],
        key_id: Annotated[Optional[StrictStr], Field(description="ID of the key definition to be used for identifying the product that owns the reference. If supplied, a key value should be supplied for the \"id\" path parameter.")] = None,
        target_key_id: Annotated[Optional[StrictStr], Field(description="ID of the key definition to be used for identifying the reference target. If supplied, a key value should be supplied for the \"targetId\" path parameter.")] = None,
        workspace: Annotated[Optional[StrictStr], Field(description="ID of the workspace in which to perform the operation. Defaults to \"Main\".")] = None,
        include_inherited_data: Annotated[Optional[StrictBool], Field(description="Endpoint returns inherited data when parameter is supplied with the value true. Defaults to \"false\".")] = None,
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
    ) -> Value:
        """Returns the value for a reference metadata attribute

        Returns the value for the specified attribute for the specified local reference. Will either be an instance of SingleValue or MultiValue depending on whether the attribute is multivalued. Notice that this resource covers both \"cross references\" and \"classification product links\" owned by the product side. The product that owns the reference can be identified either by its STEP ID or if a value for the \"keyId\" query parameter is supplied, by its key value for the specified key. Likewise, the reference target can be identified either by its STEP ID or if a value for the \"targetKeyId\" query parameter is supplied, by its key value for the specified key.

        :param id: ID / key value of the product that owns the reference (required)
        :type id: str
        :param reference_type_id: ID of the reference type (required)
        :type reference_type_id: str
        :param target_id: ID / key value of the reference target (required)
        :type target_id: str
        :param attribute_id: ID of the attribute for which to retrieve the value (required)
        :type attribute_id: str
        :param context: ID of the context in which to perform the operation (required)
        :type context: str
        :param key_id: ID of the key definition to be used for identifying the product that owns the reference. If supplied, a key value should be supplied for the \"id\" path parameter.
        :type key_id: str
        :param target_key_id: ID of the key definition to be used for identifying the reference target. If supplied, a key value should be supplied for the \"targetId\" path parameter.
        :type target_key_id: str
        :param workspace: ID of the workspace in which to perform the operation. Defaults to \"Main\".
        :type workspace: str
        :param include_inherited_data: Endpoint returns inherited data when parameter is supplied with the value true. Defaults to \"false\".
        :type include_inherited_data: bool
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

        _param = self._products_id_references_reference_type_id_target_id_values_attribute_id_get_serialize(
            id=id,
            reference_type_id=reference_type_id,
            target_id=target_id,
            attribute_id=attribute_id,
            context=context,
            key_id=key_id,
            target_key_id=target_key_id,
            workspace=workspace,
            include_inherited_data=include_inherited_data,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "Value",
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
    def products_id_references_reference_type_id_target_id_values_attribute_id_get_with_http_info(
        self,
        id: Annotated[StrictStr, Field(description="ID / key value of the product that owns the reference")],
        reference_type_id: Annotated[StrictStr, Field(description="ID of the reference type")],
        target_id: Annotated[StrictStr, Field(description="ID / key value of the reference target")],
        attribute_id: Annotated[StrictStr, Field(description="ID of the attribute for which to retrieve the value")],
        context: Annotated[StrictStr, Field(description="ID of the context in which to perform the operation")],
        key_id: Annotated[Optional[StrictStr], Field(description="ID of the key definition to be used for identifying the product that owns the reference. If supplied, a key value should be supplied for the \"id\" path parameter.")] = None,
        target_key_id: Annotated[Optional[StrictStr], Field(description="ID of the key definition to be used for identifying the reference target. If supplied, a key value should be supplied for the \"targetId\" path parameter.")] = None,
        workspace: Annotated[Optional[StrictStr], Field(description="ID of the workspace in which to perform the operation. Defaults to \"Main\".")] = None,
        include_inherited_data: Annotated[Optional[StrictBool], Field(description="Endpoint returns inherited data when parameter is supplied with the value true. Defaults to \"false\".")] = None,
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
    ) -> ApiResponse[Value]:
        """Returns the value for a reference metadata attribute

        Returns the value for the specified attribute for the specified local reference. Will either be an instance of SingleValue or MultiValue depending on whether the attribute is multivalued. Notice that this resource covers both \"cross references\" and \"classification product links\" owned by the product side. The product that owns the reference can be identified either by its STEP ID or if a value for the \"keyId\" query parameter is supplied, by its key value for the specified key. Likewise, the reference target can be identified either by its STEP ID or if a value for the \"targetKeyId\" query parameter is supplied, by its key value for the specified key.

        :param id: ID / key value of the product that owns the reference (required)
        :type id: str
        :param reference_type_id: ID of the reference type (required)
        :type reference_type_id: str
        :param target_id: ID / key value of the reference target (required)
        :type target_id: str
        :param attribute_id: ID of the attribute for which to retrieve the value (required)
        :type attribute_id: str
        :param context: ID of the context in which to perform the operation (required)
        :type context: str
        :param key_id: ID of the key definition to be used for identifying the product that owns the reference. If supplied, a key value should be supplied for the \"id\" path parameter.
        :type key_id: str
        :param target_key_id: ID of the key definition to be used for identifying the reference target. If supplied, a key value should be supplied for the \"targetId\" path parameter.
        :type target_key_id: str
        :param workspace: ID of the workspace in which to perform the operation. Defaults to \"Main\".
        :type workspace: str
        :param include_inherited_data: Endpoint returns inherited data when parameter is supplied with the value true. Defaults to \"false\".
        :type include_inherited_data: bool
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

        _param = self._products_id_references_reference_type_id_target_id_values_attribute_id_get_serialize(
            id=id,
            reference_type_id=reference_type_id,
            target_id=target_id,
            attribute_id=attribute_id,
            context=context,
            key_id=key_id,
            target_key_id=target_key_id,
            workspace=workspace,
            include_inherited_data=include_inherited_data,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "Value",
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
    def products_id_references_reference_type_id_target_id_values_attribute_id_get_without_preload_content(
        self,
        id: Annotated[StrictStr, Field(description="ID / key value of the product that owns the reference")],
        reference_type_id: Annotated[StrictStr, Field(description="ID of the reference type")],
        target_id: Annotated[StrictStr, Field(description="ID / key value of the reference target")],
        attribute_id: Annotated[StrictStr, Field(description="ID of the attribute for which to retrieve the value")],
        context: Annotated[StrictStr, Field(description="ID of the context in which to perform the operation")],
        key_id: Annotated[Optional[StrictStr], Field(description="ID of the key definition to be used for identifying the product that owns the reference. If supplied, a key value should be supplied for the \"id\" path parameter.")] = None,
        target_key_id: Annotated[Optional[StrictStr], Field(description="ID of the key definition to be used for identifying the reference target. If supplied, a key value should be supplied for the \"targetId\" path parameter.")] = None,
        workspace: Annotated[Optional[StrictStr], Field(description="ID of the workspace in which to perform the operation. Defaults to \"Main\".")] = None,
        include_inherited_data: Annotated[Optional[StrictBool], Field(description="Endpoint returns inherited data when parameter is supplied with the value true. Defaults to \"false\".")] = None,
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
        """Returns the value for a reference metadata attribute

        Returns the value for the specified attribute for the specified local reference. Will either be an instance of SingleValue or MultiValue depending on whether the attribute is multivalued. Notice that this resource covers both \"cross references\" and \"classification product links\" owned by the product side. The product that owns the reference can be identified either by its STEP ID or if a value for the \"keyId\" query parameter is supplied, by its key value for the specified key. Likewise, the reference target can be identified either by its STEP ID or if a value for the \"targetKeyId\" query parameter is supplied, by its key value for the specified key.

        :param id: ID / key value of the product that owns the reference (required)
        :type id: str
        :param reference_type_id: ID of the reference type (required)
        :type reference_type_id: str
        :param target_id: ID / key value of the reference target (required)
        :type target_id: str
        :param attribute_id: ID of the attribute for which to retrieve the value (required)
        :type attribute_id: str
        :param context: ID of the context in which to perform the operation (required)
        :type context: str
        :param key_id: ID of the key definition to be used for identifying the product that owns the reference. If supplied, a key value should be supplied for the \"id\" path parameter.
        :type key_id: str
        :param target_key_id: ID of the key definition to be used for identifying the reference target. If supplied, a key value should be supplied for the \"targetId\" path parameter.
        :type target_key_id: str
        :param workspace: ID of the workspace in which to perform the operation. Defaults to \"Main\".
        :type workspace: str
        :param include_inherited_data: Endpoint returns inherited data when parameter is supplied with the value true. Defaults to \"false\".
        :type include_inherited_data: bool
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

        _param = self._products_id_references_reference_type_id_target_id_values_attribute_id_get_serialize(
            id=id,
            reference_type_id=reference_type_id,
            target_id=target_id,
            attribute_id=attribute_id,
            context=context,
            key_id=key_id,
            target_key_id=target_key_id,
            workspace=workspace,
            include_inherited_data=include_inherited_data,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "Value",
            '400': "Error",
            '404': "Error",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        return response_data.response


    def _products_id_references_reference_type_id_target_id_values_attribute_id_get_serialize(
        self,
        id,
        reference_type_id,
        target_id,
        attribute_id,
        context,
        key_id,
        target_key_id,
        workspace,
        include_inherited_data,
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
        if reference_type_id is not None:
            _path_params['referenceTypeId'] = reference_type_id
        if target_id is not None:
            _path_params['targetId'] = target_id
        if attribute_id is not None:
            _path_params['attributeId'] = attribute_id
        # process the query parameters
        if key_id is not None:
            
            _query_params.append(('keyId', key_id))
            
        if target_key_id is not None:
            
            _query_params.append(('targetKeyId', target_key_id))
            
        if context is not None:
            
            _query_params.append(('context', context))
            
        if workspace is not None:
            
            _query_params.append(('workspace', workspace))
            
        if include_inherited_data is not None:
            
            _query_params.append(('includeInheritedData', include_inherited_data))
            
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
            resource_path='/products/{id}/references/{referenceTypeId}/{targetId}/values/{attributeId}',
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
    def products_id_references_reference_type_id_target_id_values_attribute_id_put(
        self,
        id: Annotated[StrictStr, Field(description="ID / key value of the product that owns the reference")],
        reference_type_id: Annotated[StrictStr, Field(description="ID of the reference type")],
        target_id: Annotated[StrictStr, Field(description="ID / key value of the reference target")],
        attribute_id: Annotated[StrictStr, Field(description="ID of the attribute for which to replace the value")],
        context: Annotated[StrictStr, Field(description="ID of the context in which to perform the operation")],
        key_id: Annotated[Optional[StrictStr], Field(description="ID of the key definition to be used for identifying the product that owns the reference. If supplied, a key value should be supplied for the \"id\" path parameter.")] = None,
        target_key_id: Annotated[Optional[StrictStr], Field(description="ID of the key definition to be used for identifying the reference target. If supplied, a key value should be supplied for the \"targetId\" path parameter.")] = None,
        workspace: Annotated[Optional[StrictStr], Field(description="ID of the workspace in which to perform the operation. Defaults to \"Main\".")] = None,
        value: Optional[Value] = None,
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
    ) -> Value:
        """Replaces the value for a reference metadata attribute

        Operation for replacing the value of an attribute on a local reference. It is only possible to replace values on references that are defined locally (\"contextLocal\": true). Request body must be either a SingleValue or a MultiValue depending on whether the attribute is multivalued. Notice that supplying the property \"contextLocal\" with the value \"false\" or the SingleValue \"calculated\" property with the value \"true\" will cause the value update to be ignored. Further notice that this resource covers values on both \"cross references\" and \"classification product links\" owned by the product side. The product that owns the reference can be identified either by its STEP ID or if a value for the \"keyId\" query parameter is supplied, by its key value for the specified key. Likewise, the reference target can be identified either by its STEP ID or if a value for the \"targetKeyId\" query parameter is supplied, by its key value for the specified key.

        :param id: ID / key value of the product that owns the reference (required)
        :type id: str
        :param reference_type_id: ID of the reference type (required)
        :type reference_type_id: str
        :param target_id: ID / key value of the reference target (required)
        :type target_id: str
        :param attribute_id: ID of the attribute for which to replace the value (required)
        :type attribute_id: str
        :param context: ID of the context in which to perform the operation (required)
        :type context: str
        :param key_id: ID of the key definition to be used for identifying the product that owns the reference. If supplied, a key value should be supplied for the \"id\" path parameter.
        :type key_id: str
        :param target_key_id: ID of the key definition to be used for identifying the reference target. If supplied, a key value should be supplied for the \"targetId\" path parameter.
        :type target_key_id: str
        :param workspace: ID of the workspace in which to perform the operation. Defaults to \"Main\".
        :type workspace: str
        :param value:
        :type value: Value
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

        _param = self._products_id_references_reference_type_id_target_id_values_attribute_id_put_serialize(
            id=id,
            reference_type_id=reference_type_id,
            target_id=target_id,
            attribute_id=attribute_id,
            context=context,
            key_id=key_id,
            target_key_id=target_key_id,
            workspace=workspace,
            value=value,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "Value",
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
    def products_id_references_reference_type_id_target_id_values_attribute_id_put_with_http_info(
        self,
        id: Annotated[StrictStr, Field(description="ID / key value of the product that owns the reference")],
        reference_type_id: Annotated[StrictStr, Field(description="ID of the reference type")],
        target_id: Annotated[StrictStr, Field(description="ID / key value of the reference target")],
        attribute_id: Annotated[StrictStr, Field(description="ID of the attribute for which to replace the value")],
        context: Annotated[StrictStr, Field(description="ID of the context in which to perform the operation")],
        key_id: Annotated[Optional[StrictStr], Field(description="ID of the key definition to be used for identifying the product that owns the reference. If supplied, a key value should be supplied for the \"id\" path parameter.")] = None,
        target_key_id: Annotated[Optional[StrictStr], Field(description="ID of the key definition to be used for identifying the reference target. If supplied, a key value should be supplied for the \"targetId\" path parameter.")] = None,
        workspace: Annotated[Optional[StrictStr], Field(description="ID of the workspace in which to perform the operation. Defaults to \"Main\".")] = None,
        value: Optional[Value] = None,
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
    ) -> ApiResponse[Value]:
        """Replaces the value for a reference metadata attribute

        Operation for replacing the value of an attribute on a local reference. It is only possible to replace values on references that are defined locally (\"contextLocal\": true). Request body must be either a SingleValue or a MultiValue depending on whether the attribute is multivalued. Notice that supplying the property \"contextLocal\" with the value \"false\" or the SingleValue \"calculated\" property with the value \"true\" will cause the value update to be ignored. Further notice that this resource covers values on both \"cross references\" and \"classification product links\" owned by the product side. The product that owns the reference can be identified either by its STEP ID or if a value for the \"keyId\" query parameter is supplied, by its key value for the specified key. Likewise, the reference target can be identified either by its STEP ID or if a value for the \"targetKeyId\" query parameter is supplied, by its key value for the specified key.

        :param id: ID / key value of the product that owns the reference (required)
        :type id: str
        :param reference_type_id: ID of the reference type (required)
        :type reference_type_id: str
        :param target_id: ID / key value of the reference target (required)
        :type target_id: str
        :param attribute_id: ID of the attribute for which to replace the value (required)
        :type attribute_id: str
        :param context: ID of the context in which to perform the operation (required)
        :type context: str
        :param key_id: ID of the key definition to be used for identifying the product that owns the reference. If supplied, a key value should be supplied for the \"id\" path parameter.
        :type key_id: str
        :param target_key_id: ID of the key definition to be used for identifying the reference target. If supplied, a key value should be supplied for the \"targetId\" path parameter.
        :type target_key_id: str
        :param workspace: ID of the workspace in which to perform the operation. Defaults to \"Main\".
        :type workspace: str
        :param value:
        :type value: Value
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

        _param = self._products_id_references_reference_type_id_target_id_values_attribute_id_put_serialize(
            id=id,
            reference_type_id=reference_type_id,
            target_id=target_id,
            attribute_id=attribute_id,
            context=context,
            key_id=key_id,
            target_key_id=target_key_id,
            workspace=workspace,
            value=value,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "Value",
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
    def products_id_references_reference_type_id_target_id_values_attribute_id_put_without_preload_content(
        self,
        id: Annotated[StrictStr, Field(description="ID / key value of the product that owns the reference")],
        reference_type_id: Annotated[StrictStr, Field(description="ID of the reference type")],
        target_id: Annotated[StrictStr, Field(description="ID / key value of the reference target")],
        attribute_id: Annotated[StrictStr, Field(description="ID of the attribute for which to replace the value")],
        context: Annotated[StrictStr, Field(description="ID of the context in which to perform the operation")],
        key_id: Annotated[Optional[StrictStr], Field(description="ID of the key definition to be used for identifying the product that owns the reference. If supplied, a key value should be supplied for the \"id\" path parameter.")] = None,
        target_key_id: Annotated[Optional[StrictStr], Field(description="ID of the key definition to be used for identifying the reference target. If supplied, a key value should be supplied for the \"targetId\" path parameter.")] = None,
        workspace: Annotated[Optional[StrictStr], Field(description="ID of the workspace in which to perform the operation. Defaults to \"Main\".")] = None,
        value: Optional[Value] = None,
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
        """Replaces the value for a reference metadata attribute

        Operation for replacing the value of an attribute on a local reference. It is only possible to replace values on references that are defined locally (\"contextLocal\": true). Request body must be either a SingleValue or a MultiValue depending on whether the attribute is multivalued. Notice that supplying the property \"contextLocal\" with the value \"false\" or the SingleValue \"calculated\" property with the value \"true\" will cause the value update to be ignored. Further notice that this resource covers values on both \"cross references\" and \"classification product links\" owned by the product side. The product that owns the reference can be identified either by its STEP ID or if a value for the \"keyId\" query parameter is supplied, by its key value for the specified key. Likewise, the reference target can be identified either by its STEP ID or if a value for the \"targetKeyId\" query parameter is supplied, by its key value for the specified key.

        :param id: ID / key value of the product that owns the reference (required)
        :type id: str
        :param reference_type_id: ID of the reference type (required)
        :type reference_type_id: str
        :param target_id: ID / key value of the reference target (required)
        :type target_id: str
        :param attribute_id: ID of the attribute for which to replace the value (required)
        :type attribute_id: str
        :param context: ID of the context in which to perform the operation (required)
        :type context: str
        :param key_id: ID of the key definition to be used for identifying the product that owns the reference. If supplied, a key value should be supplied for the \"id\" path parameter.
        :type key_id: str
        :param target_key_id: ID of the key definition to be used for identifying the reference target. If supplied, a key value should be supplied for the \"targetId\" path parameter.
        :type target_key_id: str
        :param workspace: ID of the workspace in which to perform the operation. Defaults to \"Main\".
        :type workspace: str
        :param value:
        :type value: Value
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

        _param = self._products_id_references_reference_type_id_target_id_values_attribute_id_put_serialize(
            id=id,
            reference_type_id=reference_type_id,
            target_id=target_id,
            attribute_id=attribute_id,
            context=context,
            key_id=key_id,
            target_key_id=target_key_id,
            workspace=workspace,
            value=value,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "Value",
            '400': "Error",
            '404': "Error",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        return response_data.response


    def _products_id_references_reference_type_id_target_id_values_attribute_id_put_serialize(
        self,
        id,
        reference_type_id,
        target_id,
        attribute_id,
        context,
        key_id,
        target_key_id,
        workspace,
        value,
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
        if reference_type_id is not None:
            _path_params['referenceTypeId'] = reference_type_id
        if target_id is not None:
            _path_params['targetId'] = target_id
        if attribute_id is not None:
            _path_params['attributeId'] = attribute_id
        # process the query parameters
        if key_id is not None:
            
            _query_params.append(('keyId', key_id))
            
        if target_key_id is not None:
            
            _query_params.append(('targetKeyId', target_key_id))
            
        if context is not None:
            
            _query_params.append(('context', context))
            
        if workspace is not None:
            
            _query_params.append(('workspace', workspace))
            
        # process the header parameters
        # process the form parameters
        # process the body parameter
        if value is not None:
            _body_params = value


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
                        'application/json'
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
            method='PUT',
            resource_path='/products/{id}/references/{referenceTypeId}/{targetId}/values/{attributeId}',
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
    def products_id_values_attribute_id_delete(
        self,
        id: Annotated[StrictStr, Field(description="ID / key value of the product for which to delete the attribute value")],
        attribute_id: Annotated[StrictStr, Field(description="ID of the attribute for which to delete the value")],
        context: Annotated[StrictStr, Field(description="ID of the context in which to perform the operation")],
        key_id: Annotated[Optional[StrictStr], Field(description="ID of the key definition to be used for identifying the product. If supplied, a key value should be supplied for the \"id\" path parameter.")] = None,
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
    ) -> Value:
        """Deletes the value for a product attribute

        Operation for deleting a product attribute value. Notice that it is only possible to delete non-calculated, locally defined values. The product can be identified either by its STEP ID or if a value for the \"keyId\" query parameter is supplied, by its key value for the specified key.

        :param id: ID / key value of the product for which to delete the attribute value (required)
        :type id: str
        :param attribute_id: ID of the attribute for which to delete the value (required)
        :type attribute_id: str
        :param context: ID of the context in which to perform the operation (required)
        :type context: str
        :param key_id: ID of the key definition to be used for identifying the product. If supplied, a key value should be supplied for the \"id\" path parameter.
        :type key_id: str
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

        _param = self._products_id_values_attribute_id_delete_serialize(
            id=id,
            attribute_id=attribute_id,
            context=context,
            key_id=key_id,
            workspace=workspace,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "Value",
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
    def products_id_values_attribute_id_delete_with_http_info(
        self,
        id: Annotated[StrictStr, Field(description="ID / key value of the product for which to delete the attribute value")],
        attribute_id: Annotated[StrictStr, Field(description="ID of the attribute for which to delete the value")],
        context: Annotated[StrictStr, Field(description="ID of the context in which to perform the operation")],
        key_id: Annotated[Optional[StrictStr], Field(description="ID of the key definition to be used for identifying the product. If supplied, a key value should be supplied for the \"id\" path parameter.")] = None,
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
    ) -> ApiResponse[Value]:
        """Deletes the value for a product attribute

        Operation for deleting a product attribute value. Notice that it is only possible to delete non-calculated, locally defined values. The product can be identified either by its STEP ID or if a value for the \"keyId\" query parameter is supplied, by its key value for the specified key.

        :param id: ID / key value of the product for which to delete the attribute value (required)
        :type id: str
        :param attribute_id: ID of the attribute for which to delete the value (required)
        :type attribute_id: str
        :param context: ID of the context in which to perform the operation (required)
        :type context: str
        :param key_id: ID of the key definition to be used for identifying the product. If supplied, a key value should be supplied for the \"id\" path parameter.
        :type key_id: str
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

        _param = self._products_id_values_attribute_id_delete_serialize(
            id=id,
            attribute_id=attribute_id,
            context=context,
            key_id=key_id,
            workspace=workspace,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "Value",
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
    def products_id_values_attribute_id_delete_without_preload_content(
        self,
        id: Annotated[StrictStr, Field(description="ID / key value of the product for which to delete the attribute value")],
        attribute_id: Annotated[StrictStr, Field(description="ID of the attribute for which to delete the value")],
        context: Annotated[StrictStr, Field(description="ID of the context in which to perform the operation")],
        key_id: Annotated[Optional[StrictStr], Field(description="ID of the key definition to be used for identifying the product. If supplied, a key value should be supplied for the \"id\" path parameter.")] = None,
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
        """Deletes the value for a product attribute

        Operation for deleting a product attribute value. Notice that it is only possible to delete non-calculated, locally defined values. The product can be identified either by its STEP ID or if a value for the \"keyId\" query parameter is supplied, by its key value for the specified key.

        :param id: ID / key value of the product for which to delete the attribute value (required)
        :type id: str
        :param attribute_id: ID of the attribute for which to delete the value (required)
        :type attribute_id: str
        :param context: ID of the context in which to perform the operation (required)
        :type context: str
        :param key_id: ID of the key definition to be used for identifying the product. If supplied, a key value should be supplied for the \"id\" path parameter.
        :type key_id: str
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

        _param = self._products_id_values_attribute_id_delete_serialize(
            id=id,
            attribute_id=attribute_id,
            context=context,
            key_id=key_id,
            workspace=workspace,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "Value",
            '400': "Error",
            '404': "Error",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        return response_data.response


    def _products_id_values_attribute_id_delete_serialize(
        self,
        id,
        attribute_id,
        context,
        key_id,
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
        if attribute_id is not None:
            _path_params['attributeId'] = attribute_id
        # process the query parameters
        if key_id is not None:
            
            _query_params.append(('keyId', key_id))
            
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
            method='DELETE',
            resource_path='/products/{id}/values/{attributeId}',
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
    def products_id_values_attribute_id_get(
        self,
        id: Annotated[StrictStr, Field(description="ID / key value of the product for which to retrieve the attribute value")],
        attribute_id: Annotated[StrictStr, Field(description="ID of the attribute for which to retrieve the value")],
        context: Annotated[StrictStr, Field(description="ID of the context in which to perform the operation")],
        key_id: Annotated[Optional[StrictStr], Field(description="ID of the key definition to be used for identifying the product. If supplied, a key value should be supplied for the \"id\" path parameter.")] = None,
        workspace: Annotated[Optional[StrictStr], Field(description="ID of the workspace in which to perform the operation. Defaults to \"Main\".")] = None,
        include_inherited_data: Annotated[Optional[StrictBool], Field(description="Endpoint returns inherited data when parameter is supplied with the value true. Defaults to \"false\".")] = None,
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
    ) -> Value:
        """Returns the value for a product attribute

        Returns the value for the specified attribute. Will either be an instance of SingleValue or MultiValue depending on whether the attribute is multivalued. The product can be identified either by its STEP ID or if a value for the \"keyId\" query parameter is supplied, by its key value for the specified key.

        :param id: ID / key value of the product for which to retrieve the attribute value (required)
        :type id: str
        :param attribute_id: ID of the attribute for which to retrieve the value (required)
        :type attribute_id: str
        :param context: ID of the context in which to perform the operation (required)
        :type context: str
        :param key_id: ID of the key definition to be used for identifying the product. If supplied, a key value should be supplied for the \"id\" path parameter.
        :type key_id: str
        :param workspace: ID of the workspace in which to perform the operation. Defaults to \"Main\".
        :type workspace: str
        :param include_inherited_data: Endpoint returns inherited data when parameter is supplied with the value true. Defaults to \"false\".
        :type include_inherited_data: bool
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

        _param = self._products_id_values_attribute_id_get_serialize(
            id=id,
            attribute_id=attribute_id,
            context=context,
            key_id=key_id,
            workspace=workspace,
            include_inherited_data=include_inherited_data,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "Value",
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
    def products_id_values_attribute_id_get_with_http_info(
        self,
        id: Annotated[StrictStr, Field(description="ID / key value of the product for which to retrieve the attribute value")],
        attribute_id: Annotated[StrictStr, Field(description="ID of the attribute for which to retrieve the value")],
        context: Annotated[StrictStr, Field(description="ID of the context in which to perform the operation")],
        key_id: Annotated[Optional[StrictStr], Field(description="ID of the key definition to be used for identifying the product. If supplied, a key value should be supplied for the \"id\" path parameter.")] = None,
        workspace: Annotated[Optional[StrictStr], Field(description="ID of the workspace in which to perform the operation. Defaults to \"Main\".")] = None,
        include_inherited_data: Annotated[Optional[StrictBool], Field(description="Endpoint returns inherited data when parameter is supplied with the value true. Defaults to \"false\".")] = None,
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
    ) -> ApiResponse[Value]:
        """Returns the value for a product attribute

        Returns the value for the specified attribute. Will either be an instance of SingleValue or MultiValue depending on whether the attribute is multivalued. The product can be identified either by its STEP ID or if a value for the \"keyId\" query parameter is supplied, by its key value for the specified key.

        :param id: ID / key value of the product for which to retrieve the attribute value (required)
        :type id: str
        :param attribute_id: ID of the attribute for which to retrieve the value (required)
        :type attribute_id: str
        :param context: ID of the context in which to perform the operation (required)
        :type context: str
        :param key_id: ID of the key definition to be used for identifying the product. If supplied, a key value should be supplied for the \"id\" path parameter.
        :type key_id: str
        :param workspace: ID of the workspace in which to perform the operation. Defaults to \"Main\".
        :type workspace: str
        :param include_inherited_data: Endpoint returns inherited data when parameter is supplied with the value true. Defaults to \"false\".
        :type include_inherited_data: bool
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

        _param = self._products_id_values_attribute_id_get_serialize(
            id=id,
            attribute_id=attribute_id,
            context=context,
            key_id=key_id,
            workspace=workspace,
            include_inherited_data=include_inherited_data,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "Value",
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
    def products_id_values_attribute_id_get_without_preload_content(
        self,
        id: Annotated[StrictStr, Field(description="ID / key value of the product for which to retrieve the attribute value")],
        attribute_id: Annotated[StrictStr, Field(description="ID of the attribute for which to retrieve the value")],
        context: Annotated[StrictStr, Field(description="ID of the context in which to perform the operation")],
        key_id: Annotated[Optional[StrictStr], Field(description="ID of the key definition to be used for identifying the product. If supplied, a key value should be supplied for the \"id\" path parameter.")] = None,
        workspace: Annotated[Optional[StrictStr], Field(description="ID of the workspace in which to perform the operation. Defaults to \"Main\".")] = None,
        include_inherited_data: Annotated[Optional[StrictBool], Field(description="Endpoint returns inherited data when parameter is supplied with the value true. Defaults to \"false\".")] = None,
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
        """Returns the value for a product attribute

        Returns the value for the specified attribute. Will either be an instance of SingleValue or MultiValue depending on whether the attribute is multivalued. The product can be identified either by its STEP ID or if a value for the \"keyId\" query parameter is supplied, by its key value for the specified key.

        :param id: ID / key value of the product for which to retrieve the attribute value (required)
        :type id: str
        :param attribute_id: ID of the attribute for which to retrieve the value (required)
        :type attribute_id: str
        :param context: ID of the context in which to perform the operation (required)
        :type context: str
        :param key_id: ID of the key definition to be used for identifying the product. If supplied, a key value should be supplied for the \"id\" path parameter.
        :type key_id: str
        :param workspace: ID of the workspace in which to perform the operation. Defaults to \"Main\".
        :type workspace: str
        :param include_inherited_data: Endpoint returns inherited data when parameter is supplied with the value true. Defaults to \"false\".
        :type include_inherited_data: bool
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

        _param = self._products_id_values_attribute_id_get_serialize(
            id=id,
            attribute_id=attribute_id,
            context=context,
            key_id=key_id,
            workspace=workspace,
            include_inherited_data=include_inherited_data,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "Value",
            '400': "Error",
            '404': "Error",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        return response_data.response


    def _products_id_values_attribute_id_get_serialize(
        self,
        id,
        attribute_id,
        context,
        key_id,
        workspace,
        include_inherited_data,
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
        if attribute_id is not None:
            _path_params['attributeId'] = attribute_id
        # process the query parameters
        if key_id is not None:
            
            _query_params.append(('keyId', key_id))
            
        if context is not None:
            
            _query_params.append(('context', context))
            
        if workspace is not None:
            
            _query_params.append(('workspace', workspace))
            
        if include_inherited_data is not None:
            
            _query_params.append(('includeInheritedData', include_inherited_data))
            
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
            resource_path='/products/{id}/values/{attributeId}',
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
    def products_id_values_attribute_id_put(
        self,
        id: Annotated[StrictStr, Field(description="ID / key value of the product for which to replace the attribute value")],
        attribute_id: Annotated[StrictStr, Field(description="ID of the attribute for which to replace the value")],
        context: Annotated[StrictStr, Field(description="ID of the context in which to perform the operation")],
        key_id: Annotated[Optional[StrictStr], Field(description="ID of the key definition to be used for identifying the product. If supplied, a key value should be supplied for the \"id\" path parameter.")] = None,
        workspace: Annotated[Optional[StrictStr], Field(description="ID of the workspace in which to perform the operation. Defaults to \"Main\".")] = None,
        value: Optional[Value] = None,
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
    ) -> Value:
        """Replaces the value for a product attribute

        Operation for replacing a product attribute value. Request body must be either a SingleValue or a MultiValue depending on whether the attribute is multivalued. Notice that supplying the property \"contextLocal\" with the value \"false\" or the SingleValue \"calculated\" property with the value \"true\" will cause the value update to be ignored. The product can be identified either by its STEP ID or if a value for the \"keyId\" query parameter is supplied, by its key value for the specified key.

        :param id: ID / key value of the product for which to replace the attribute value (required)
        :type id: str
        :param attribute_id: ID of the attribute for which to replace the value (required)
        :type attribute_id: str
        :param context: ID of the context in which to perform the operation (required)
        :type context: str
        :param key_id: ID of the key definition to be used for identifying the product. If supplied, a key value should be supplied for the \"id\" path parameter.
        :type key_id: str
        :param workspace: ID of the workspace in which to perform the operation. Defaults to \"Main\".
        :type workspace: str
        :param value:
        :type value: Value
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

        _param = self._products_id_values_attribute_id_put_serialize(
            id=id,
            attribute_id=attribute_id,
            context=context,
            key_id=key_id,
            workspace=workspace,
            value=value,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "Value",
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
    def products_id_values_attribute_id_put_with_http_info(
        self,
        id: Annotated[StrictStr, Field(description="ID / key value of the product for which to replace the attribute value")],
        attribute_id: Annotated[StrictStr, Field(description="ID of the attribute for which to replace the value")],
        context: Annotated[StrictStr, Field(description="ID of the context in which to perform the operation")],
        key_id: Annotated[Optional[StrictStr], Field(description="ID of the key definition to be used for identifying the product. If supplied, a key value should be supplied for the \"id\" path parameter.")] = None,
        workspace: Annotated[Optional[StrictStr], Field(description="ID of the workspace in which to perform the operation. Defaults to \"Main\".")] = None,
        value: Optional[Value] = None,
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
    ) -> ApiResponse[Value]:
        """Replaces the value for a product attribute

        Operation for replacing a product attribute value. Request body must be either a SingleValue or a MultiValue depending on whether the attribute is multivalued. Notice that supplying the property \"contextLocal\" with the value \"false\" or the SingleValue \"calculated\" property with the value \"true\" will cause the value update to be ignored. The product can be identified either by its STEP ID or if a value for the \"keyId\" query parameter is supplied, by its key value for the specified key.

        :param id: ID / key value of the product for which to replace the attribute value (required)
        :type id: str
        :param attribute_id: ID of the attribute for which to replace the value (required)
        :type attribute_id: str
        :param context: ID of the context in which to perform the operation (required)
        :type context: str
        :param key_id: ID of the key definition to be used for identifying the product. If supplied, a key value should be supplied for the \"id\" path parameter.
        :type key_id: str
        :param workspace: ID of the workspace in which to perform the operation. Defaults to \"Main\".
        :type workspace: str
        :param value:
        :type value: Value
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

        _param = self._products_id_values_attribute_id_put_serialize(
            id=id,
            attribute_id=attribute_id,
            context=context,
            key_id=key_id,
            workspace=workspace,
            value=value,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "Value",
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
    def products_id_values_attribute_id_put_without_preload_content(
        self,
        id: Annotated[StrictStr, Field(description="ID / key value of the product for which to replace the attribute value")],
        attribute_id: Annotated[StrictStr, Field(description="ID of the attribute for which to replace the value")],
        context: Annotated[StrictStr, Field(description="ID of the context in which to perform the operation")],
        key_id: Annotated[Optional[StrictStr], Field(description="ID of the key definition to be used for identifying the product. If supplied, a key value should be supplied for the \"id\" path parameter.")] = None,
        workspace: Annotated[Optional[StrictStr], Field(description="ID of the workspace in which to perform the operation. Defaults to \"Main\".")] = None,
        value: Optional[Value] = None,
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
        """Replaces the value for a product attribute

        Operation for replacing a product attribute value. Request body must be either a SingleValue or a MultiValue depending on whether the attribute is multivalued. Notice that supplying the property \"contextLocal\" with the value \"false\" or the SingleValue \"calculated\" property with the value \"true\" will cause the value update to be ignored. The product can be identified either by its STEP ID or if a value for the \"keyId\" query parameter is supplied, by its key value for the specified key.

        :param id: ID / key value of the product for which to replace the attribute value (required)
        :type id: str
        :param attribute_id: ID of the attribute for which to replace the value (required)
        :type attribute_id: str
        :param context: ID of the context in which to perform the operation (required)
        :type context: str
        :param key_id: ID of the key definition to be used for identifying the product. If supplied, a key value should be supplied for the \"id\" path parameter.
        :type key_id: str
        :param workspace: ID of the workspace in which to perform the operation. Defaults to \"Main\".
        :type workspace: str
        :param value:
        :type value: Value
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

        _param = self._products_id_values_attribute_id_put_serialize(
            id=id,
            attribute_id=attribute_id,
            context=context,
            key_id=key_id,
            workspace=workspace,
            value=value,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "Value",
            '400': "Error",
            '404': "Error",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        return response_data.response


    def _products_id_values_attribute_id_put_serialize(
        self,
        id,
        attribute_id,
        context,
        key_id,
        workspace,
        value,
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
        if attribute_id is not None:
            _path_params['attributeId'] = attribute_id
        # process the query parameters
        if key_id is not None:
            
            _query_params.append(('keyId', key_id))
            
        if context is not None:
            
            _query_params.append(('context', context))
            
        if workspace is not None:
            
            _query_params.append(('workspace', workspace))
            
        # process the header parameters
        # process the form parameters
        # process the body parameter
        if value is not None:
            _body_params = value


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
                        'application/json'
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
            method='PUT',
            resource_path='/products/{id}/values/{attributeId}',
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
    def products_post(
        self,
        context: Annotated[StrictStr, Field(description="ID of the context in which to perform the operation")],
        workspace: Annotated[Optional[StrictStr], Field(description="ID of the workspace in which to perform the operation. Defaults to \"Main\".")] = None,
        product: Optional[Product] = None,
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
    ) -> Product:
        """Creates a new product object with autogenerated ID

        Operation for creating a new product object with autogenerated ID. Object type and a parent product must be specified in the request body. Further, an auto ID pattern must be configured for the object type. An \"id\" must not be supplied in the request body.

        :param context: ID of the context in which to perform the operation (required)
        :type context: str
        :param workspace: ID of the workspace in which to perform the operation. Defaults to \"Main\".
        :type workspace: str
        :param product:
        :type product: Product
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

        _param = self._products_post_serialize(
            context=context,
            workspace=workspace,
            product=product,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '201': "Product",
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
    def products_post_with_http_info(
        self,
        context: Annotated[StrictStr, Field(description="ID of the context in which to perform the operation")],
        workspace: Annotated[Optional[StrictStr], Field(description="ID of the workspace in which to perform the operation. Defaults to \"Main\".")] = None,
        product: Optional[Product] = None,
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
    ) -> ApiResponse[Product]:
        """Creates a new product object with autogenerated ID

        Operation for creating a new product object with autogenerated ID. Object type and a parent product must be specified in the request body. Further, an auto ID pattern must be configured for the object type. An \"id\" must not be supplied in the request body.

        :param context: ID of the context in which to perform the operation (required)
        :type context: str
        :param workspace: ID of the workspace in which to perform the operation. Defaults to \"Main\".
        :type workspace: str
        :param product:
        :type product: Product
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

        _param = self._products_post_serialize(
            context=context,
            workspace=workspace,
            product=product,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '201': "Product",
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
    def products_post_without_preload_content(
        self,
        context: Annotated[StrictStr, Field(description="ID of the context in which to perform the operation")],
        workspace: Annotated[Optional[StrictStr], Field(description="ID of the workspace in which to perform the operation. Defaults to \"Main\".")] = None,
        product: Optional[Product] = None,
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
        """Creates a new product object with autogenerated ID

        Operation for creating a new product object with autogenerated ID. Object type and a parent product must be specified in the request body. Further, an auto ID pattern must be configured for the object type. An \"id\" must not be supplied in the request body.

        :param context: ID of the context in which to perform the operation (required)
        :type context: str
        :param workspace: ID of the workspace in which to perform the operation. Defaults to \"Main\".
        :type workspace: str
        :param product:
        :type product: Product
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

        _param = self._products_post_serialize(
            context=context,
            workspace=workspace,
            product=product,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '201': "Product",
            '400': "Error",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        return response_data.response


    def _products_post_serialize(
        self,
        context,
        workspace,
        product,
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
        if product is not None:
            _body_params = product


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
                        'application/json'
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
            resource_path='/products',
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
    def products_search_post(
        self,
        context: Annotated[StrictStr, Field(description="ID of the context in which to perform the operation")],
        workspace: Annotated[Optional[StrictStr], Field(description="ID of the workspace in which to perform the operation. Defaults to \"Main\".")] = None,
        query: Optional[Query] = None,
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
    ) -> List[QueryResult]:
        """Search for / query products

        Operation for querying products. Resource operation will return a maximum of 1000 results. Notice that while the query can be made arbitrarily complex with multiple levels of nested AND and OR conditions, such complex queries will not perform well.

        :param context: ID of the context in which to perform the operation (required)
        :type context: str
        :param workspace: ID of the workspace in which to perform the operation. Defaults to \"Main\".
        :type workspace: str
        :param query:
        :type query: Query
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

        _param = self._products_search_post_serialize(
            context=context,
            workspace=workspace,
            query=query,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "List[QueryResult]",
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
    def products_search_post_with_http_info(
        self,
        context: Annotated[StrictStr, Field(description="ID of the context in which to perform the operation")],
        workspace: Annotated[Optional[StrictStr], Field(description="ID of the workspace in which to perform the operation. Defaults to \"Main\".")] = None,
        query: Optional[Query] = None,
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
    ) -> ApiResponse[List[QueryResult]]:
        """Search for / query products

        Operation for querying products. Resource operation will return a maximum of 1000 results. Notice that while the query can be made arbitrarily complex with multiple levels of nested AND and OR conditions, such complex queries will not perform well.

        :param context: ID of the context in which to perform the operation (required)
        :type context: str
        :param workspace: ID of the workspace in which to perform the operation. Defaults to \"Main\".
        :type workspace: str
        :param query:
        :type query: Query
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

        _param = self._products_search_post_serialize(
            context=context,
            workspace=workspace,
            query=query,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "List[QueryResult]",
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
    def products_search_post_without_preload_content(
        self,
        context: Annotated[StrictStr, Field(description="ID of the context in which to perform the operation")],
        workspace: Annotated[Optional[StrictStr], Field(description="ID of the workspace in which to perform the operation. Defaults to \"Main\".")] = None,
        query: Optional[Query] = None,
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
        """Search for / query products

        Operation for querying products. Resource operation will return a maximum of 1000 results. Notice that while the query can be made arbitrarily complex with multiple levels of nested AND and OR conditions, such complex queries will not perform well.

        :param context: ID of the context in which to perform the operation (required)
        :type context: str
        :param workspace: ID of the workspace in which to perform the operation. Defaults to \"Main\".
        :type workspace: str
        :param query:
        :type query: Query
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

        _param = self._products_search_post_serialize(
            context=context,
            workspace=workspace,
            query=query,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "List[QueryResult]",
            '400': "Error",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        return response_data.response


    def _products_search_post_serialize(
        self,
        context,
        workspace,
        query,
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
        if query is not None:
            _body_params = query


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
                        'application/json'
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
            resource_path='/products/search',
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


