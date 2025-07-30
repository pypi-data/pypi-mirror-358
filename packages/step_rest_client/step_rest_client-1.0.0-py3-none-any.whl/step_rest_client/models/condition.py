# coding: utf-8

"""
    STEP REST API V2

    <h1>About</h1><p>The STEP REST API V2 provides read and write access to a set of core STEP objects using the HTTP operations GET, PUT, POST, PATCH and DELETE.</p><h1>Resource Representation</h1><p>With the exception of a few resource operations for retrieving and uploading binary data, all request and response bodies are JSON, compliant with the schema documented here.</p><h1>Context and Workspace</h1><p>All requests are handled in a specific STEP context and workspace and both can be specified via query parameters available for all resource operations. A context must always be specified while requests per default will be handled in the &quot;Main&quot; workspace.</p><h1>Polymorphism</h1><p>In STEP, attributes, reference types and data container types can all be either single- or multivalued. The STEP REST API V2 uses polymorphism to address this complexity with resources that include values, references and data containers specified to produce and consume a common &quot;abstract&quot; supertype that always will be one of either the single- or multivalued subtype.<br/>As an example, the GET /entities/{id}/values/{attributeId} resource operation is specified to return a &quot;Value&quot; but as evident from the model, the &quot;Value&quot; will always be &quot;oneOf&quot; either &quot;SingleValue&quot;, that has a &quot;value&quot; property for which the value is an object, or &quot;MultiValue&quot;, that has a &quot;values&quot; property for which the value is an array.<br/>Clients are advised to use the presence or absence of the plural array property (&quot;values&quot;, &quot;references&quot; and &quot;dataContainers&quot;) to determine the concrete type.</p><h1>Authentication</h1><p>The REST API is protected by HTTP Basic Authentication or if OAuth2-based authentication is enabled (SaaS customers only), by Bearer Authentication. With Basic Authentication, user name and password are supplied with each request and it is therefore highly recommended to only use the API in conjunction with HTTPS. For more information about OAuth2-based authentication for SaaS customers, please see the STEP Authentication Guide.</p><h1>Versioning</h1><p>The STEP REST API V2 is versioned using semantic versioning. Stibo Systems reserve the right to make non-breaking, minor / patch changes in any release without warning and clients must be coded / configured to be 'tolerant' and capable of handling such changes.</p><p>Examples of breaking, major changes:</p><ul><li>Renaming of a property</li><li>Removal of a property</li><li>Property type change</li><li>Addition of new property required for write operations</li><li>Marking existing property as required for write operations</li><li>Removal of resource or resource operation</li><li>Materially different behavior for existing resource operation</li></ul><p>Examples of non-breaking, minor / patch changes:</p><ul><li>Addition of new properties in request responses</li><li>Addition of new query parameter not required for write operations</li><li>Addition of new resource or resource operation</li><li>Bug fixes that do not change the schema or resource operations as described here</li><li>Inclusion of a response body for resource operations specified to return a 200 response with no body</li><li>Change of response &quot;Model&quot; / &quot;schema&quot; to type extending the previously specified type</li><li>Renaming a &quot;Model&quot; / &quot;schema&quot; type</li></ul><p>In addition, error message texts may change without warning within the same version. Client program logic should not depend upon the message content.</p><h1>Error Handling</h1><p>The STEP REST API V2 responds with standard HTTP status codes, with 2** responses indicating a success, 4** responses indicating a client error and 5** indicating a server error. Notice that this specification does not specify common error responses like 500 (internal server error) or 401 (unauthorized) for the individual resource operations. Clients should however be capable of handling such responses.</p><p>Error responses have a JSON response body (see Error schema below) containing HTTP status code information in addition to a message providing details about the error. As mentioned above, client program logic should not depend upon the message content.</p><p>The specific status codes used in the API are:</p><ul><li>200 (OK): Success, response may or may not have a body</li><li>201 (Created): Entity successfully created, response may or may not have a body</li><li>400 (Bad request): The server cannot or will not process the request due to an apparent client error</li><li>401 (Unauthorized): Returned only in relation to failed authentication</li><li>404 (Not Found): Returned only in relation to objects specified via path parameters (variable parts of the URL). If STEP objects referenced in request bodies or via query parameters cannot be found, the response will be 400.</li><li>429 (Too Many Requests): Clients are per default limited to 100 requests per second. Returned if the rate limit is exceeded.</li><li>500 (Internal Server Error): Unexpected error (could potentially cover an issue that rightfully should be a 400)</li></ul>

    The version of the OpenAPI document: 1.3.0
    Generated by OpenAPI Generator (https://openapi-generator.tech)

    Do not edit the class manually.
"""  # noqa: E501


from __future__ import annotations
import json
import pprint
from pydantic import BaseModel, ConfigDict, Field, StrictStr, ValidationError, field_validator
from typing import Any, List, Optional
from step_rest_client.models.id_condition import IdCondition
from step_rest_client.models.lov_value_condition import LovValueCondition
from step_rest_client.models.name_condition import NameCondition
from step_rest_client.models.numeric_value_condition import NumericValueCondition
from step_rest_client.models.object_type_condition import ObjectTypeCondition
from step_rest_client.models.simple_below_condition import SimpleBelowCondition
from step_rest_client.models.text_value_condition import TextValueCondition
from pydantic import StrictStr, Field
from typing import Union, List, Set, Optional, Dict
from typing_extensions import Literal, Self

CONDITION_ONE_OF_SCHEMAS = ["AndCondition", "HasDataContainerObjectCondition", "HasReferenceToCondition", "IdCondition", "LovValueCondition", "NameCondition", "NumericValueCondition", "ObjectTypeCondition", "OrCondition", "SimpleBelowCondition", "TextValueCondition"]

class Condition(BaseModel):
    """
    An \"abstract\" representation of a condition. Must always either be an AndCondition, an OrCondition, an IdCondition, a NameCondition, a TextValueCondition, a NumericValueCondition, an ObjectTypeCondition, a SimpleBelowCondition, an LovValueCondition, a HasReferenceToCondition or a HasDataContainerObjectCondition.
    """
    # data type: AndCondition
    oneof_schema_1_validator: Optional[AndCondition] = None
    # data type: OrCondition
    oneof_schema_2_validator: Optional[OrCondition] = None
    # data type: IdCondition
    oneof_schema_3_validator: Optional[IdCondition] = None
    # data type: NameCondition
    oneof_schema_4_validator: Optional[NameCondition] = None
    # data type: TextValueCondition
    oneof_schema_5_validator: Optional[TextValueCondition] = None
    # data type: NumericValueCondition
    oneof_schema_6_validator: Optional[NumericValueCondition] = None
    # data type: ObjectTypeCondition
    oneof_schema_7_validator: Optional[ObjectTypeCondition] = None
    # data type: SimpleBelowCondition
    oneof_schema_8_validator: Optional[SimpleBelowCondition] = None
    # data type: LovValueCondition
    oneof_schema_9_validator: Optional[LovValueCondition] = None
    # data type: HasReferenceToCondition
    oneof_schema_10_validator: Optional[HasReferenceToCondition] = None
    # data type: HasDataContainerObjectCondition
    oneof_schema_11_validator: Optional[HasDataContainerObjectCondition] = None
    actual_instance: Optional[Union[AndCondition, HasDataContainerObjectCondition, HasReferenceToCondition, IdCondition, LovValueCondition, NameCondition, NumericValueCondition, ObjectTypeCondition, OrCondition, SimpleBelowCondition, TextValueCondition]] = None
    one_of_schemas: Set[str] = { "AndCondition", "HasDataContainerObjectCondition", "HasReferenceToCondition", "IdCondition", "LovValueCondition", "NameCondition", "NumericValueCondition", "ObjectTypeCondition", "OrCondition", "SimpleBelowCondition", "TextValueCondition" }

    model_config = ConfigDict(
        validate_assignment=True,
        protected_namespaces=(),
    )


    def __init__(self, *args, **kwargs) -> None:
        if args:
            if len(args) > 1:
                raise ValueError("If a position argument is used, only 1 is allowed to set `actual_instance`")
            if kwargs:
                raise ValueError("If a position argument is used, keyword arguments cannot be used.")
            super().__init__(actual_instance=args[0])
        else:
            super().__init__(**kwargs)

    @field_validator('actual_instance')
    def actual_instance_must_validate_oneof(cls, v):
        instance = Condition.model_construct()
        error_messages = []
        match = 0
        # validate data type: AndCondition
        if not isinstance(v, AndCondition):
            error_messages.append(f"Error! Input type `{type(v)}` is not `AndCondition`")
        else:
            match += 1
        # validate data type: OrCondition
        if not isinstance(v, OrCondition):
            error_messages.append(f"Error! Input type `{type(v)}` is not `OrCondition`")
        else:
            match += 1
        # validate data type: IdCondition
        if not isinstance(v, IdCondition):
            error_messages.append(f"Error! Input type `{type(v)}` is not `IdCondition`")
        else:
            match += 1
        # validate data type: NameCondition
        if not isinstance(v, NameCondition):
            error_messages.append(f"Error! Input type `{type(v)}` is not `NameCondition`")
        else:
            match += 1
        # validate data type: TextValueCondition
        if not isinstance(v, TextValueCondition):
            error_messages.append(f"Error! Input type `{type(v)}` is not `TextValueCondition`")
        else:
            match += 1
        # validate data type: NumericValueCondition
        if not isinstance(v, NumericValueCondition):
            error_messages.append(f"Error! Input type `{type(v)}` is not `NumericValueCondition`")
        else:
            match += 1
        # validate data type: ObjectTypeCondition
        if not isinstance(v, ObjectTypeCondition):
            error_messages.append(f"Error! Input type `{type(v)}` is not `ObjectTypeCondition`")
        else:
            match += 1
        # validate data type: SimpleBelowCondition
        if not isinstance(v, SimpleBelowCondition):
            error_messages.append(f"Error! Input type `{type(v)}` is not `SimpleBelowCondition`")
        else:
            match += 1
        # validate data type: LovValueCondition
        if not isinstance(v, LovValueCondition):
            error_messages.append(f"Error! Input type `{type(v)}` is not `LovValueCondition`")
        else:
            match += 1
        # validate data type: HasReferenceToCondition
        if not isinstance(v, HasReferenceToCondition):
            error_messages.append(f"Error! Input type `{type(v)}` is not `HasReferenceToCondition`")
        else:
            match += 1
        # validate data type: HasDataContainerObjectCondition
        if not isinstance(v, HasDataContainerObjectCondition):
            error_messages.append(f"Error! Input type `{type(v)}` is not `HasDataContainerObjectCondition`")
        else:
            match += 1
        if match > 1:
            # more than 1 match
            raise ValueError("Multiple matches found when setting `actual_instance` in Condition with oneOf schemas: AndCondition, HasDataContainerObjectCondition, HasReferenceToCondition, IdCondition, LovValueCondition, NameCondition, NumericValueCondition, ObjectTypeCondition, OrCondition, SimpleBelowCondition, TextValueCondition. Details: " + ", ".join(error_messages))
        elif match == 0:
            # no match
            raise ValueError("No match found when setting `actual_instance` in Condition with oneOf schemas: AndCondition, HasDataContainerObjectCondition, HasReferenceToCondition, IdCondition, LovValueCondition, NameCondition, NumericValueCondition, ObjectTypeCondition, OrCondition, SimpleBelowCondition, TextValueCondition. Details: " + ", ".join(error_messages))
        else:
            return v

    @classmethod
    def from_dict(cls, obj: Union[str, Dict[str, Any]]) -> Self:
        return cls.from_json(json.dumps(obj))

    @classmethod
    def from_json(cls, json_str: str) -> Self:
        """Returns the object represented by the json string"""
        instance = cls.model_construct()
        error_messages = []
        match = 0

        # deserialize data into AndCondition
        try:
            instance.actual_instance = AndCondition.from_json(json_str)
            match += 1
        except (ValidationError, ValueError) as e:
            error_messages.append(str(e))
        # deserialize data into OrCondition
        try:
            instance.actual_instance = OrCondition.from_json(json_str)
            match += 1
        except (ValidationError, ValueError) as e:
            error_messages.append(str(e))
        # deserialize data into IdCondition
        try:
            instance.actual_instance = IdCondition.from_json(json_str)
            match += 1
        except (ValidationError, ValueError) as e:
            error_messages.append(str(e))
        # deserialize data into NameCondition
        try:
            instance.actual_instance = NameCondition.from_json(json_str)
            match += 1
        except (ValidationError, ValueError) as e:
            error_messages.append(str(e))
        # deserialize data into TextValueCondition
        try:
            instance.actual_instance = TextValueCondition.from_json(json_str)
            match += 1
        except (ValidationError, ValueError) as e:
            error_messages.append(str(e))
        # deserialize data into NumericValueCondition
        try:
            instance.actual_instance = NumericValueCondition.from_json(json_str)
            match += 1
        except (ValidationError, ValueError) as e:
            error_messages.append(str(e))
        # deserialize data into ObjectTypeCondition
        try:
            instance.actual_instance = ObjectTypeCondition.from_json(json_str)
            match += 1
        except (ValidationError, ValueError) as e:
            error_messages.append(str(e))
        # deserialize data into SimpleBelowCondition
        try:
            instance.actual_instance = SimpleBelowCondition.from_json(json_str)
            match += 1
        except (ValidationError, ValueError) as e:
            error_messages.append(str(e))
        # deserialize data into LovValueCondition
        try:
            instance.actual_instance = LovValueCondition.from_json(json_str)
            match += 1
        except (ValidationError, ValueError) as e:
            error_messages.append(str(e))
        # deserialize data into HasReferenceToCondition
        try:
            instance.actual_instance = HasReferenceToCondition.from_json(json_str)
            match += 1
        except (ValidationError, ValueError) as e:
            error_messages.append(str(e))
        # deserialize data into HasDataContainerObjectCondition
        try:
            instance.actual_instance = HasDataContainerObjectCondition.from_json(json_str)
            match += 1
        except (ValidationError, ValueError) as e:
            error_messages.append(str(e))

        if match > 1:
            # more than 1 match
            raise ValueError("Multiple matches found when deserializing the JSON string into Condition with oneOf schemas: AndCondition, HasDataContainerObjectCondition, HasReferenceToCondition, IdCondition, LovValueCondition, NameCondition, NumericValueCondition, ObjectTypeCondition, OrCondition, SimpleBelowCondition, TextValueCondition. Details: " + ", ".join(error_messages))
        elif match == 0:
            # no match
            raise ValueError("No match found when deserializing the JSON string into Condition with oneOf schemas: AndCondition, HasDataContainerObjectCondition, HasReferenceToCondition, IdCondition, LovValueCondition, NameCondition, NumericValueCondition, ObjectTypeCondition, OrCondition, SimpleBelowCondition, TextValueCondition. Details: " + ", ".join(error_messages))
        else:
            return instance

    def to_json(self) -> str:
        """Returns the JSON representation of the actual instance"""
        if self.actual_instance is None:
            return "null"

        if hasattr(self.actual_instance, "to_json") and callable(self.actual_instance.to_json):
            return self.actual_instance.to_json()
        else:
            return json.dumps(self.actual_instance)

    def to_dict(self) -> Optional[Union[Dict[str, Any], AndCondition, HasDataContainerObjectCondition, HasReferenceToCondition, IdCondition, LovValueCondition, NameCondition, NumericValueCondition, ObjectTypeCondition, OrCondition, SimpleBelowCondition, TextValueCondition]]:
        """Returns the dict representation of the actual instance"""
        if self.actual_instance is None:
            return None

        if hasattr(self.actual_instance, "to_dict") and callable(self.actual_instance.to_dict):
            return self.actual_instance.to_dict()
        else:
            # primitive type
            return self.actual_instance

    def to_str(self) -> str:
        """Returns the string representation of the actual instance"""
        return pprint.pformat(self.model_dump())

from step_rest_client.models.and_condition import AndCondition
from step_rest_client.models.has_data_container_object_condition import HasDataContainerObjectCondition
from step_rest_client.models.has_reference_to_condition import HasReferenceToCondition
from step_rest_client.models.or_condition import OrCondition
# TODO: Rewrite to not use raise_errors
Condition.model_rebuild(raise_errors=False)

