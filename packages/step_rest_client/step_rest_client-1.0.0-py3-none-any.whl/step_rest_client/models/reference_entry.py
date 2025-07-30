# coding: utf-8

"""
    STEP REST API V2

    <h1>About</h1><p>The STEP REST API V2 provides read and write access to a set of core STEP objects using the HTTP operations GET, PUT, POST, PATCH and DELETE.</p><h1>Resource Representation</h1><p>With the exception of a few resource operations for retrieving and uploading binary data, all request and response bodies are JSON, compliant with the schema documented here.</p><h1>Context and Workspace</h1><p>All requests are handled in a specific STEP context and workspace and both can be specified via query parameters available for all resource operations. A context must always be specified while requests per default will be handled in the &quot;Main&quot; workspace.</p><h1>Polymorphism</h1><p>In STEP, attributes, reference types and data container types can all be either single- or multivalued. The STEP REST API V2 uses polymorphism to address this complexity with resources that include values, references and data containers specified to produce and consume a common &quot;abstract&quot; supertype that always will be one of either the single- or multivalued subtype.<br/>As an example, the GET /entities/{id}/values/{attributeId} resource operation is specified to return a &quot;Value&quot; but as evident from the model, the &quot;Value&quot; will always be &quot;oneOf&quot; either &quot;SingleValue&quot;, that has a &quot;value&quot; property for which the value is an object, or &quot;MultiValue&quot;, that has a &quot;values&quot; property for which the value is an array.<br/>Clients are advised to use the presence or absence of the plural array property (&quot;values&quot;, &quot;references&quot; and &quot;dataContainers&quot;) to determine the concrete type.</p><h1>Authentication</h1><p>The REST API is protected by HTTP Basic Authentication or if OAuth2-based authentication is enabled (SaaS customers only), by Bearer Authentication. With Basic Authentication, user name and password are supplied with each request and it is therefore highly recommended to only use the API in conjunction with HTTPS. For more information about OAuth2-based authentication for SaaS customers, please see the STEP Authentication Guide.</p><h1>Versioning</h1><p>The STEP REST API V2 is versioned using semantic versioning. Stibo Systems reserve the right to make non-breaking, minor / patch changes in any release without warning and clients must be coded / configured to be 'tolerant' and capable of handling such changes.</p><p>Examples of breaking, major changes:</p><ul><li>Renaming of a property</li><li>Removal of a property</li><li>Property type change</li><li>Addition of new property required for write operations</li><li>Marking existing property as required for write operations</li><li>Removal of resource or resource operation</li><li>Materially different behavior for existing resource operation</li></ul><p>Examples of non-breaking, minor / patch changes:</p><ul><li>Addition of new properties in request responses</li><li>Addition of new query parameter not required for write operations</li><li>Addition of new resource or resource operation</li><li>Bug fixes that do not change the schema or resource operations as described here</li><li>Inclusion of a response body for resource operations specified to return a 200 response with no body</li><li>Change of response &quot;Model&quot; / &quot;schema&quot; to type extending the previously specified type</li><li>Renaming a &quot;Model&quot; / &quot;schema&quot; type</li></ul><p>In addition, error message texts may change without warning within the same version. Client program logic should not depend upon the message content.</p><h1>Error Handling</h1><p>The STEP REST API V2 responds with standard HTTP status codes, with 2** responses indicating a success, 4** responses indicating a client error and 5** indicating a server error. Notice that this specification does not specify common error responses like 500 (internal server error) or 401 (unauthorized) for the individual resource operations. Clients should however be capable of handling such responses.</p><p>Error responses have a JSON response body (see Error schema below) containing HTTP status code information in addition to a message providing details about the error. As mentioned above, client program logic should not depend upon the message content.</p><p>The specific status codes used in the API are:</p><ul><li>200 (OK): Success, response may or may not have a body</li><li>201 (Created): Entity successfully created, response may or may not have a body</li><li>400 (Bad request): The server cannot or will not process the request due to an apparent client error</li><li>401 (Unauthorized): Returned only in relation to failed authentication</li><li>404 (Not Found): Returned only in relation to objects specified via path parameters (variable parts of the URL). If STEP objects referenced in request bodies or via query parameters cannot be found, the response will be 400.</li><li>429 (Too Many Requests): Clients are per default limited to 100 requests per second. Returned if the rate limit is exceeded.</li><li>500 (Internal Server Error): Unexpected error (could potentially cover an issue that rightfully should be a 400)</li></ul>

    The version of the OpenAPI document: 1.3.0
    Generated by OpenAPI Generator (https://openapi-generator.tech)

    Do not edit the class manually.
"""  # noqa: E501


from __future__ import annotations
import pprint
import re  # noqa: F401
import json

from pydantic import BaseModel, ConfigDict, Field, StrictBool, StrictStr, field_validator
from typing import Any, ClassVar, Dict, List, Optional
from step_rest_client.models.value import Value
from typing import Optional, Set
from typing_extensions import Self

class ReferenceEntry(BaseModel):
    """
    An atomic reference. Can represent both a \"cross reference\" and a \"classification product link\".
    """ # noqa: E501
    context_local: Optional[StrictBool] = Field(default=None, description="Indicates whether the reference is set locally or inherited from a dimension point / a combination dimension points different from the ones used for current context. Should not be supplied for reference updates. If supplied with the value \"false\", the update will be skipped.", alias="contextLocal")
    inherited: Optional[StrictBool] = Field(default=None, description="Indicates whether the reference entry is inherited from parent node.")
    target: Optional[StrictStr] = Field(default=None, description="ID of the target object")
    target_type: Optional[StrictStr] = Field(default=None, description="Target \"supertype\"", alias="targetType")
    values: Optional[Dict[str, Value]] = Field(default=None, description="Reference metadata values. Keys are attribute IDs and values either a SingleValue or a MultiValue depending on whether the attribute is multivalued.")
    entity: Optional[Dict[str, Entity]] = Field(default=None, description="The encapsulating reference should point to the specified entity. Only supported by find-similar and match-and-merge and the targetType of the reference must be entity. The embedded entity should be denoted by source information, i.e. it should have a source relation where source system id and source record id is known to originator of the JSON request. The supplied source information will be used for looking up actual target record of the encapsulating relation. Cannot be applied together with target id.")
    __properties: ClassVar[List[str]] = ["contextLocal", "inherited", "target", "targetType", "values", "entity"]

    @field_validator('target_type')
    def target_type_validate_enum(cls, value):
        """Validates the enum"""
        if value is None:
            return value

        if value not in set(['product', 'classification', 'asset', 'entity']):
            raise ValueError("must be one of enum values ('product', 'classification', 'asset', 'entity')")
        return value

    model_config = ConfigDict(
        populate_by_name=True,
        validate_assignment=True,
        protected_namespaces=(),
    )


    def to_str(self) -> str:
        """Returns the string representation of the model using alias"""
        return pprint.pformat(self.model_dump(by_alias=True))

    def to_json(self) -> str:
        """Returns the JSON representation of the model using alias"""
        # TODO: pydantic v2: use .model_dump_json(by_alias=True, exclude_unset=True) instead
        return json.dumps(self.to_dict())

    @classmethod
    def from_json(cls, json_str: str) -> Optional[Self]:
        """Create an instance of ReferenceEntry from a JSON string"""
        return cls.from_dict(json.loads(json_str))

    def to_dict(self) -> Dict[str, Any]:
        """Return the dictionary representation of the model using alias.

        This has the following differences from calling pydantic's
        `self.model_dump(by_alias=True)`:

        * `None` is only added to the output dict for nullable fields that
          were set at model initialization. Other fields with value `None`
          are ignored.
        * OpenAPI `readOnly` fields are excluded.
        * OpenAPI `readOnly` fields are excluded.
        * OpenAPI `readOnly` fields are excluded.
        """
        excluded_fields: Set[str] = set([
            "context_local",
            "inherited",
            "target_type",
        ])

        _dict = self.model_dump(
            by_alias=True,
            exclude=excluded_fields,
            exclude_none=True,
        )
        # override the default output from pydantic by calling `to_dict()` of each value in values (dict)
        _field_dict = {}
        if self.values:
            for _key_values in self.values:
                if self.values[_key_values]:
                    _field_dict[_key_values] = self.values[_key_values].to_dict()
            _dict['values'] = _field_dict
        # override the default output from pydantic by calling `to_dict()` of each value in entity (dict)
        _field_dict = {}
        if self.entity:
            for _key_entity in self.entity:
                if self.entity[_key_entity]:
                    _field_dict[_key_entity] = self.entity[_key_entity].to_dict()
            _dict['entity'] = _field_dict
        return _dict

    @classmethod
    def from_dict(cls, obj: Optional[Dict[str, Any]]) -> Optional[Self]:
        """Create an instance of ReferenceEntry from a dict"""
        if obj is None:
            return None

        if not isinstance(obj, dict):
            return cls.model_validate(obj)

        _obj = cls.model_validate({
            "contextLocal": obj.get("contextLocal"),
            "inherited": obj.get("inherited"),
            "target": obj.get("target"),
            "targetType": obj.get("targetType"),
            "values": dict(
                (_k, Value.from_dict(_v))
                for _k, _v in obj["values"].items()
            )
            if obj.get("values") is not None
            else None,
            "entity": dict(
                (_k, Entity.from_dict(_v))
                for _k, _v in obj["entity"].items()
            )
            if obj.get("entity") is not None
            else None
        })
        return _obj

from step_rest_client.models.entity import Entity
# TODO: Rewrite to not use raise_errors
ReferenceEntry.model_rebuild(raise_errors=False)

