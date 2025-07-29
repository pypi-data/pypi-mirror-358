# mypy: ignore-errors
# This file has a lot of type based creation of models, which mypy is flagging as errors.
# Turning off type checking for this file.

import inspect
import sys
from typing import (
    Annotated,
    Any,
    Callable,
    Final,
    ForwardRef,
    Literal,
    NewType,
    Optional,
    TypedDict,
    TypeVar,
    Union,
    get_args,
    get_origin,
    get_type_hints,
)

from pydantic import BaseModel, Field, create_model


def is_pydantic_model(obj: Any) -> bool:
    return inspect.isclass(obj) and issubclass(obj, BaseModel)


def serialize_type(typ):
    """Serialize a type annotation to a structured representation"""
    if isinstance(typ, type) and issubclass(typ, BaseModel):
        # For Pydantic models, reference by name
        return {"kind": "model", "name": typ.__name__}

    elif get_origin(typ) is not None:
        # Handle generic types like list, dict, etc.
        origin = get_origin(typ)
        args = get_args(typ)

        origin_name = origin.__name__ if hasattr(origin, "__name__") else str(origin)

        if origin in (list, list[Any]):
            return {"kind": "list", "item_type": serialize_type(args[0])}
        elif origin in (dict, dict[Any, Any]):
            return {
                "kind": "dict",
                "key_type": serialize_type(args[0]),
                "value_type": serialize_type(args[1]),
            }
        elif origin in (set, set[Any]):
            return {"kind": "set", "item_type": serialize_type(args[0])}
        elif origin in (tuple, tuple[Any, ...]):
            return {"kind": "tuple", "item_types": [serialize_type(arg) for arg in args]}
        elif origin in (Union, Union[Any, ...]):
            # Special handling for Optional[T] which is Union[T, None]
            if len(args) == 2 and args[1] is type(None):
                return {"kind": "optional", "type": serialize_type(args[0])}
            return {"kind": "union", "types": [serialize_type(arg) for arg in args]}
        elif origin is Literal:
            return {"kind": "literal", "values": args}
        elif origin is Annotated:
            return {
                "kind": "annotated",
                "type": serialize_type(args[0]),
                "metadata": [str(arg) for arg in args[1:]],
            }
        elif origin is Callable:
            if len(args) == 2 and args[0] is Ellipsis:
                return {"kind": "callable", "return_type": serialize_type(args[1])}
            return {
                "kind": "callable",
                "arg_types": [serialize_type(arg) for arg in args[:-1]],
                "return_type": serialize_type(args[-1]),
            }
        elif origin is type:
            return {"kind": "type", "type": serialize_type(args[0])}
        elif origin is Final:
            return {"kind": "final", "type": serialize_type(args[0])}
        else:
            return {
                "kind": "generic",
                "origin": origin_name,
                "args": [serialize_type(arg) for arg in args],
            }

    elif isinstance(typ, ForwardRef):
        # Handle forward references
        return {"kind": "forward_ref", "name": typ.__forward_arg__}

    elif isinstance(typ, TypeVar):
        # Handle type variables
        return {
            "kind": "typevar",
            "name": typ.__name__,
            "constraints": [serialize_type(c) for c in typ.__constraints__]
            if typ.__constraints__
            else None,
            "bound": serialize_type(typ.__bound__) if typ.__bound__ is not None else None,
        }
    elif hasattr(typ, "__supertype__"):  # Handle NewType
        return {
            "kind": "newtype",
            "name": typ.__name__,
            "supertype": serialize_type(typ.__supertype__),
        }

    else:
        # Handle simple types
        try:
            return {
                "kind": "simple",
                "name": typ.__name__ if hasattr(typ, "__name__") else str(typ),
            }
        except AttributeError:
            return {"kind": "simple", "name": str(typ)}


def deserialize_type(
    type_info: dict[str, Any], model_registry: Optional[dict[str, Any]] = None
) -> Any:
    """Deserialize a type from its structured representation"""
    if model_registry is None:
        model_registry = {}

    kind = type_info.get("kind")

    if kind == "model":
        # Handle Pydantic model references
        model_name = type_info["name"]
        if model_name in model_registry:
            return model_registry[model_name]
        else:
            # Return a ForwardRef if model not yet defined
            return ForwardRef(model_name)

    elif kind == "list":
        # Handle List types
        item_type = deserialize_type(type_info["item_type"], model_registry)
        return list[item_type]

    elif kind == "dict":
        # Handle Dict types
        key_type = deserialize_type(type_info["key_type"], model_registry)
        value_type = deserialize_type(type_info["value_type"], model_registry)
        return dict[key_type, value_type]

    elif kind == "set":
        # Handle Set types
        item_type = deserialize_type(type_info["item_type"], model_registry)
        return set[item_type]

    elif kind == "tuple":
        # Handle Tuple types
        item_types = [
            deserialize_type(t, model_registry) for t in type_info["item_types"]
        ]
        return tuple[tuple(item_types)]

    elif kind == "optional":
        # Handle Optional types
        inner_type = deserialize_type(type_info["type"], model_registry)
        return Optional[inner_type]

    elif kind == "union":
        # Handle Union types
        types = [deserialize_type(t, model_registry) for t in type_info["types"]]
        return Union[tuple(types)]
    elif kind == "type":
        # Handle Type types
        inner_type = deserialize_type(type_info["type"], model_registry)
        return type[inner_type]

    elif kind == "final":
        # Handle Final types
        inner_type = deserialize_type(type_info["type"], model_registry)
        return Final[inner_type]

    elif kind == "typevar":
        # Handle TypeVar
        constraints = None
        if type_info["constraints"]:
            constraints = tuple(
                deserialize_type(c, model_registry) for c in type_info["constraints"]
            )
        bound = None
        if type_info["bound"]:
            bound = deserialize_type(type_info["bound"], model_registry)
        return TypeVar(type_info["name"], constraints=constraints, bound=bound)

    elif kind == "protocol":
        # Handle Protocol
        return ForwardRef(type_info["name"])

    elif kind == "typeddict":
        # Handle TypedDict
        fields = {
            k: deserialize_type(v, model_registry) for k, v in type_info["fields"].items()
        }
        return TypedDict(type_info["name"], fields)

    elif kind == "newtype":
        # Handle NewType
        supertype = deserialize_type(type_info["supertype"], model_registry)
        return NewType(type_info["name"], supertype)

    elif kind == "forward_ref":
        # Handle forward references
        return ForwardRef(type_info["name"])

    elif kind == "simple":
        # Handle simple types
        type_name = type_info["name"]
        if type_name == "str":
            return str
        elif type_name == "int":
            return int
        elif type_name == "float":
            return float
        elif type_name == "bool":
            return bool
        elif type_name == "None" or type_name == "NoneType":
            return type(None)
        else:
            # Try to resolve from built-in types
            if hasattr(sys.modules["builtins"], type_name):
                return getattr(sys.modules["builtins"], type_name)
            # Default to Any if type can't be resolved
            return Any

    else:
        # Default case
        return Any


def serialize_model_definition(model_class: type[BaseModel]) -> dict[str, Any]:
    """Serialize a Pydantic model class definition to a dictionary."""
    # Get field information including types
    fields = {}
    type_hints = get_type_hints(model_class)

    for field_name, field_info in model_class.model_fields.items():
        field_type = type_hints.get(field_name, Any)

        # Serialize field information
        field_data = {
            "type": serialize_type(field_type),
            "required": field_info.is_required(),
            "default": None,  # Will be updated if not required
            "description": field_info.description,
        }

        # Handle default values
        if not field_info.is_required():
            default_value = field_info.get_default()
            if default_value is not None and hasattr(default_value, "model_dump"):
                # Handle default value that is a Pydantic model
                field_data["default"] = {
                    "is_model": True,
                    "value": default_value.model_dump(),
                }
            else:
                # Simple default value
                field_data["default"] = default_value

        fields[field_name] = field_data

    # Include any validators and extra model info
    model_config = {}
    if hasattr(model_class, "model_config"):
        for key, value in model_class.model_config.items():
            if isinstance(value, (str, int, float, bool, list, dict)) or value is None:
                model_config[key] = value

    # Generate a basic schema without using model_json_schema
    schema = {"type": "object", "properties": {}, "required": []}

    for field_name, field_info in fields.items():
        # Add to properties
        schema["properties"][field_name] = {
            "type": "object" if field_info["type"]["kind"] == "model" else "string",
            "description": field_info["description"] or "",
        }

        # Add to required if needed
        if field_info["required"]:
            schema["required"].append(field_name)

    return {
        "name": model_class.__name__,
        "fields": fields,
        "schema": schema,
        "config": model_config,
    }


def collect_model_dependencies(
    model_class: type[BaseModel], collected_models=None, localns=None
):
    """Recursively collect all model dependencies."""
    if collected_models is None:
        collected_models = {}

    # Skip if already collected
    if model_class.__name__ in collected_models:
        return collected_models

    # Add current model
    collected_models[model_class.__name__] = model_class

    # Get the module's globals and locals for type resolution
    if localns is None:
        localns = sys.modules[model_class.__module__].__dict__

    # Find all field types that are Pydantic models
    type_hints = get_type_hints(model_class, localns=localns)

    for field_type in type_hints.values():
        # Process the type to find nested models
        def process_type(typ):
            if isinstance(typ, type) and issubclass(typ, BaseModel):
                collect_model_dependencies(typ, collected_models, localns)
            elif get_origin(typ) is not None:
                # Handle container types
                for arg in get_args(typ):
                    process_type(arg)
            elif isinstance(typ, ForwardRef):
                # Try to resolve the forward reference
                try:
                    resolved_type = typ._evaluate(localns, None, set())
                    if isinstance(resolved_type, type) and issubclass(
                        resolved_type, BaseModel
                    ):
                        collect_model_dependencies(
                            resolved_type, collected_models, localns
                        )
                except (NameError, AttributeError):
                    # If we can't resolve it yet, that's okay
                    # - it will be handled during deserialization
                    pass

        process_type(field_type)

    return collected_models


def serialize_all_models(root_model: type[BaseModel]) -> dict[str, Any]:
    """Serialize a model and all its dependencies into a single dictionary"""
    # First collect all models
    all_models = collect_model_dependencies(root_model)

    # Then serialize each model
    serialized_models = {}
    for model_name, model_class in all_models.items():
        serialized_models[model_name] = serialize_model_definition(model_class)

    return {"models": serialized_models, "root_model": root_model.__name__}


def get_model_dependencies(model_def: dict[str, Any]) -> set[str]:
    """Get all model dependencies for a given model definition."""
    dependencies = set()

    def process_type_info(type_info: dict[str, Any]):
        if type_info["kind"] == "model":
            dependencies.add(type_info["name"])
        elif type_info["kind"] in ["list", "set"]:
            process_type_info(type_info["item_type"])
        elif type_info["kind"] == "dict":
            process_type_info(type_info["key_type"])
            process_type_info(type_info["value_type"])
        elif type_info["kind"] == "union":
            for t in type_info["types"]:
                process_type_info(t)
        elif type_info["kind"] == "generic":
            for arg in type_info["args"]:
                process_type_info(arg)

    for field_info in model_def["fields"].values():
        process_type_info(field_info["type"])

    return dependencies


def topological_sort(serialized_models: dict[str, dict[str, Any]]) -> list[str]:
    """Sort model names in dependency order."""
    # Build dependency graph
    graph = {
        name: get_model_dependencies(model_def)
        for name, model_def in serialized_models.items()
    }

    # Topological sort using DFS
    visited = set()
    temp = set()
    order = []

    def visit(node: str):
        if node in temp:
            raise ValueError(f"Circular dependency detected involving {node}")
        if node in visited:
            return

        temp.add(node)
        for dep in graph[node]:
            if dep in graph:  # Only process dependencies that are in our models
                visit(dep)
        temp.remove(node)
        visited.add(node)
        order.append(node)

    for node in graph:
        if node not in visited:
            visit(node)

    return order


def deserialize_all_models(serialized_data: dict[str, Any]) -> dict[str, type[BaseModel]]:
    """Deserialize all models from a single dictionary"""
    serialized_models = serialized_data["models"]
    model_registry = {}

    # First pass: create placeholder classes for all models
    for model_name in serialized_models:
        placeholder = type(model_name, (BaseModel,), {})
        model_registry[model_name] = placeholder

    # Sort models by dependency order
    model_order = topological_sort(serialized_models)

    # Second pass: fill in the actual definitions in dependency order
    for model_name in model_order:
        deserialize_model_definition(serialized_models[model_name], model_registry)

    # Return the complete registry of models
    return model_registry


def deserialize_model_definition(
    model_def: dict[str, Any], model_registry: dict[str, type[BaseModel]]
) -> type[BaseModel]:
    """Recreate a Pydantic model class from its serialized definition."""
    model_name = model_def["name"]

    # Process fields
    fields = {}
    for field_name, field_info in model_def["fields"].items():
        # Deserialize field type
        field_type = deserialize_type(field_info["type"], model_registry)

        # Process field parameters
        field_params = {}
        if not field_info["required"]:
            default_value = field_info["default"]

            # Handle default value that is a model
            if isinstance(default_value, dict) and default_value.get("is_model"):
                model_type = field_type
                if hasattr(model_type, "__origin__"):  # Handle Optional[Model] etc.
                    for arg in get_args(model_type):
                        if isinstance(arg, type) and issubclass(arg, BaseModel):
                            model_type = arg
                            break

                if model_type in model_registry:
                    model_class = model_registry[model_type]
                    field_params["default"] = model_class(**default_value["value"])
                else:
                    # Skip default if model not yet available
                    pass
            else:
                field_params["default"] = default_value

        if field_info["description"]:
            field_params["description"] = field_info["description"]

        # Add validation to accept instances of original model classes
        if isinstance(field_type, type) and issubclass(field_type, BaseModel):
            # Ensure the model type is properly registered
            if field_type.__name__ in model_registry:
                field_type = model_registry[field_type.__name__]

            def validate_model(value):
                if isinstance(value, field_type):
                    return value
                if isinstance(value, dict):
                    return field_type(**value)
                raise ValueError(
                    f"Expected {field_type.__name__} or dict, got {type(value)}"
                )

            field_params["validator"] = validate_model

        fields[field_name] = (field_type, Field(**field_params))

    # Create the model with appropriate configuration
    config_dict = model_def.get("config", {})

    # Create actual model class
    if config_dict:
        actual_model = create_model(
            model_name, **fields, __config__=type("Config", (), config_dict)
        )
    else:
        actual_model = create_model(model_name, **fields)

    model_registry[model_name] = actual_model

    return actual_model


# Simplified API functions for serializing and deserializing
def serialize_model(model_class: type[Any]) -> dict[str, Any]:
    """Serialize a model class and all its dependencies to JSON"""
    return serialize_all_models(model_class)


def deserialize_model(model_dict: dict[str, Any]) -> type[Any]:
    """Deserialize model classes from JSON"""
    root_model = model_dict["root_model"]
    model_dict = deserialize_all_models(model_dict)
    return model_dict[root_model]
