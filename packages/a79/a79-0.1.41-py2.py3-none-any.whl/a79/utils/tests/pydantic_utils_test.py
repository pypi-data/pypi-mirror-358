from typing import Optional

import pytest
from pydantic import BaseModel

from ..pydantic_utils import deserialize_model, serialize_model


class SimpleModel(BaseModel):
    name: str
    age: int
    is_active: bool = True
    description: Optional[str] = None


class NestedModel(BaseModel):
    simple: SimpleModel
    extra_field: str


class ComplexModel(BaseModel):
    nested: NestedModel
    numbers: list[int]
    tags: set[str]
    coordinates: tuple[float, float]
    optional_nested: Optional[NestedModel] = None


def assert_field_types_match(original_field, deserialized_field):
    """Helper function to compare field types, handling nested models by name"""
    original_type = original_field.annotation
    deserialized_type = deserialized_field.annotation

    # Handle Optional types
    if hasattr(original_type, "__origin__") and original_type.__origin__ is Optional:
        assert (
            hasattr(deserialized_type, "__origin__")
            and deserialized_type.__origin__ is Optional
        )
        original_type = original_type.__args__[0]
        deserialized_type = deserialized_type.__args__[0]

    # Handle container types (list, dict, set, tuple)
    if hasattr(original_type, "__origin__"):
        assert hasattr(deserialized_type, "__origin__")
        assert original_type.__origin__ == deserialized_type.__origin__

        # Compare container item types
        for orig_arg, deser_arg in zip(
            original_type.__args__, deserialized_type.__args__
        ):
            if isinstance(orig_arg, type) and issubclass(orig_arg, BaseModel):
                assert isinstance(deser_arg, type) and issubclass(deser_arg, BaseModel)
                assert orig_arg.__name__ == deser_arg.__name__
                for field_name in orig_arg.model_fields:
                    assert_field_types_match(
                        orig_arg.model_fields[field_name],
                        deser_arg.model_fields[field_name],
                    )
            else:
                assert orig_arg == deser_arg
    # Handle Pydantic models
    elif isinstance(original_type, type) and issubclass(original_type, BaseModel):
        assert isinstance(deserialized_type, type) and issubclass(
            deserialized_type, BaseModel
        )
        assert original_type.__name__ == deserialized_type.__name__
        for field_name in original_type.model_fields:
            assert_field_types_match(
                original_type.model_fields[field_name],
                deserialized_type.model_fields[field_name],
            )
    # Handle simple types
    else:
        assert original_type == deserialized_type


def test_simple_model_serialization():
    # Test serialization
    serialized = serialize_model(SimpleModel)

    # Test deserialization
    deserialized = deserialize_model(serialized)

    # Verify field properties are preserved
    for field_name in SimpleModel.model_fields:
        assert_field_types_match(
            SimpleModel.model_fields[field_name], deserialized.model_fields[field_name]
        )

    # Verify default values are preserved
    assert deserialized.model_fields["is_active"].default is True
    assert deserialized.model_fields["description"].default is None

    # Verify field requirements are preserved
    assert deserialized.model_fields["name"].is_required()
    assert deserialized.model_fields["age"].is_required()
    assert not deserialized.model_fields["is_active"].is_required()
    assert not deserialized.model_fields["description"].is_required()


def test_nested_model_serialization():
    # Test serialization
    serialized = serialize_model(NestedModel)

    # Test deserialization
    deserialized = deserialize_model(serialized)

    # Verify field properties are preserved
    for field_name in NestedModel.model_fields:
        assert_field_types_match(
            NestedModel.model_fields[field_name], deserialized.model_fields[field_name]
        )

    # Verify field requirements are preserved
    assert deserialized.model_fields["simple"].is_required()
    assert deserialized.model_fields["extra_field"].is_required()

    # Verify nested model field properties
    simple_field = deserialized.model_fields["simple"].annotation
    for field_name in SimpleModel.model_fields:
        assert_field_types_match(
            SimpleModel.model_fields[field_name], simple_field.model_fields[field_name]
        )


def test_complex_model_serialization():
    # Test serialization
    serialized = serialize_model(ComplexModel)

    # Test deserialization
    deserialized = deserialize_model(serialized)

    # Verify field properties are preserved
    for field_name in ComplexModel.model_fields:
        assert_field_types_match(
            ComplexModel.model_fields[field_name], deserialized.model_fields[field_name]
        )

    # Verify field requirements are preserved
    assert deserialized.model_fields["nested"].is_required()
    assert deserialized.model_fields["numbers"].is_required()
    assert deserialized.model_fields["tags"].is_required()
    assert deserialized.model_fields["coordinates"].is_required()
    assert not deserialized.model_fields["optional_nested"].is_required()

    # Verify nested model field properties
    nested_field = deserialized.model_fields["nested"].annotation
    for field_name in NestedModel.model_fields:
        assert_field_types_match(
            NestedModel.model_fields[field_name], nested_field.model_fields[field_name]
        )


@pytest.mark.skip(reason="Circular references are not supported yet")
def test_circular_reference():
    class ModelA(BaseModel):
        name: str
        b: Optional["ModelB"] = None

    class ModelB(BaseModel):
        name: str
        a: Optional[ModelA] = None

    # Test serialization
    serialized = serialize_model(ModelA)

    # Test deserialization
    deserialized = deserialize_model(serialized)

    # Verify field properties are preserved
    for field_name in ModelA.model_fields:
        assert_field_types_match(
            ModelA.model_fields[field_name], deserialized.model_fields[field_name]
        )

    # Verify nested model field properties
    model_b_field = deserialized.model_fields["b"].annotation.__args__[0]
    for field_name in ModelB.model_fields:
        assert_field_types_match(
            ModelB.model_fields[field_name], model_b_field.model_fields[field_name]
        )


def test_model_with_config():
    class ConfigModel(BaseModel):
        name: str

        model_config = {"extra": "forbid", "validate_assignment": True}

    # Test serialization
    serialized = serialize_model(ConfigModel)

    # Test deserialization
    deserialized = deserialize_model(serialized)

    # Verify field properties are preserved
    for field_name in ConfigModel.model_fields:
        assert_field_types_match(
            ConfigModel.model_fields[field_name], deserialized.model_fields[field_name]
        )

    # Verify model config is preserved
    assert deserialized.model_config == ConfigModel.model_config


def test_invalid_input():
    class NotAModel:
        pass

    with pytest.raises(AttributeError):
        serialize_model(NotAModel)


def test_nested_model_type_preservation():
    class Level3Model(BaseModel):
        value: int
        description: str
        metadata: dict[str, str]
        tags: set[str]

    class Level2Model(BaseModel):
        level3: Level3Model
        level3_list: list[Level3Model]
        level3_optional: Optional[Level3Model] = None
        level3_dict: dict[str, Level3Model]
        level3_set: set[Level3Model]

    class Level1Model(BaseModel):
        level2: Level2Model
        level2_list: list[Level2Model]
        level2_optional: Optional[Level2Model] = None
        level2_dict: dict[str, Level2Model]
        level2_set: set[Level2Model]

    # Test serialization
    serialized = serialize_model(Level1Model)

    # Test deserialization
    deserialized = deserialize_model(serialized)

    # Verify field types at each level
    for field_name in Level1Model.model_fields:
        assert_field_types_match(
            Level1Model.model_fields[field_name], deserialized.model_fields[field_name]
        )

    # Verify field requirements
    assert deserialized.model_fields["level2"].is_required()
    assert deserialized.model_fields["level2_list"].is_required()
    assert not deserialized.model_fields["level2_optional"].is_required()
    assert deserialized.model_fields["level2_dict"].is_required()
    assert deserialized.model_fields["level2_set"].is_required()

    # Verify default values
    assert deserialized.model_fields["level2_optional"].default is None
    level2_field = deserialized.model_fields["level2"].annotation
    assert level2_field.model_fields["level3_optional"].default is None
