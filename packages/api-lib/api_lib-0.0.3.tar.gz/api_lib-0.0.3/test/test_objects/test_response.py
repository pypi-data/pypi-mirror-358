from decimal import Decimal
from test.config.response import (
    MetricResponseClass,
    Repository,
    ResponseClass,
    ResponseWithList,
    ResponseWithNestedObjects,
    User,
    UserWithObject,
)

import pytest

from api_lib.objects.response import APIfield, APIobject, JsonResponse


def test_api_field():
    obj = ResponseClass({"field": "test_value"})
    assert isinstance(obj.field, str)
    assert obj.field == "test_value"


def test_api_field_with_path():
    obj = ResponseClass({"path": {"to": {"field": "test_value"}}})
    assert isinstance(obj.path_field, str)
    assert obj.path_field == "test_value"


def test_api_field_with_default():
    obj = ResponseClass({"default_field": None})

    assert isinstance(obj.default_field, str)
    assert obj.default_field == "default_value"


def test_api_field_with_wrong_default_type():
    @APIobject
    class WrongDefaultResponseClass(JsonResponse):
        default_field: str = APIfield(default=12)

    with pytest.raises(TypeError):
        WrongDefaultResponseClass({})


def test_is_null():
    obj = ResponseClass({})
    assert not obj.is_null

    obj.default_field = None  # ty: ignore[invalid-assignment]
    assert obj.is_null


def test_as_dict():
    obj = ResponseClass({"field": "test_value", "path": {"to": {"field": "test_path_value"}}})
    expected_dict = {
        "field": "test_value",
        "path_field": "test_path_value",
        "default_field": "default_value",
    }
    assert obj.as_dict == expected_dict


def test_equality():
    obj1 = ResponseClass(
        {
            "field": "test_value",
            "path": {"to": {"field": "test_path_value"}},
            "default_field": "default_value",
        }
    )
    obj2 = ResponseClass({"field": "test_value", "path": {"to": {"field": "test_path_value"}}})
    obj3 = ResponseClass({"field": "different_value"})

    assert obj1 == obj2
    assert obj1 != obj3
    assert obj2 != obj3
    assert not (obj1 == "not an object")


def test_metric_response():
    response = MetricResponseClass(
        """
    # MetricResponseClass Test
    metric_one{label_name="label_1"} 123.45
    metric_two{label_name="label_1"} 42.42
    metric_two{label_name="label_2"} 24.24
    metric_three{label_name="label_1"} 100
    metric_three{label_name="label_2"} 200
    metric_three{label_name="label_3"} 300
    metric_not_useful 1

    # Rest of the metrics
    metric_four{label_name="label_1", other_label_name="other_label_1"} 50
    """
    )

    assert response.metric_one == 123.45
    assert response.metric_two["label_1"] == Decimal("42.42")
    assert response.metric_two["label_2"] == Decimal("24.24")
    assert response.metric_three == 600


def test_metric_response_multiple_labels_sum():
    response = MetricResponseClass(
        """
    # MetricResponseClass Test
    metric_two{label_name="label_1", other_label_name="other_label_1"} 42.42
    metric_two{label_name="label_1", other_label_name="other_label_2"} 10.10
    metric_two{label_name="label_2"} 24.24
    """
    )

    assert response.metric_two["label_1"] == Decimal("52.52")
    assert response.metric_two["label_2"] == Decimal("24.24")


def test_metric_response_multiple_labels_distinct():
    response = MetricResponseClass(
        """
    # MetricResponseClass Test
    metric_four{label_name="label_1",other_label_name="other_label_1"} 42.42
    metric_four{label_name="label_1",other_label_name="other_label_2"} 10.10
    metric_four{label_name="label_2"} 24.24
    """
    )

    assert response.metric_four["label_1"]["other_label_1"] == Decimal("42.42")
    assert response.metric_four["label_1"]["other_label_2"] == Decimal("10.10")
    assert response.metric_four["label_2"] == Decimal("24.24")


def test_metric_response_with_list():
    response = ResponseWithList(
        {
            "this_list": [
                {"login": "user1", "name": "User One", "disk_usage": 100, "plan": {"space": 200}},
                {"login": "user2", "name": "User Two", "disk_usage": 150, "plan": {"space": 300}},
            ],
        }
    )

    assert len(response.this_list) == 2
    assert isinstance(response.this_list[0], User)
    assert response.this_list[0].login == "user1"


def test_metric_response_nested_objects():
    response = ResponseWithNestedObjects(
        {
            "that_list": [
                {
                    "user": {"login": "user1", "name": "User One", "disk_usage": 100, "plan": {"space": 200}},
                    "repository": {"name": "repo1", "full_name": "repo1/full_name"},
                },
                {
                    "user": {"login": "user2", "name": "User Two", "disk_usage": 150, "plan": {"space": 300}},
                    "repository": {"name": "repo2", "full_name": "repo2/full_name"},
                },
            ]
        }
    )
    assert len(response.that_list) == 2

    for item in response.that_list:
        assert isinstance(item, UserWithObject)
        assert isinstance(item.user, User)
        assert isinstance(item.repository, Repository)
