from test.config.request import RequestClass


def test_request_data_as_dict(request_object: RequestClass):
    assert request_object.field == "test_value"
    assert request_object.path_field == "path_value"
    assert request_object.default_field == "default_value"

    dict_obj = request_object.as_dict
    assert dict_obj["field"] == "test_value"
    assert dict_obj["other_key"] == "path_value"
    assert dict_obj["default_field"] == "default_value"


def test_request_data_as_header_string(request_object: RequestClass):
    assert request_object.as_header_string == "field=test_value&other_key=path_value&default_field=default_value"


def test_request_data_as_query_parameters(request_object: RequestClass):
    assert request_object.as_query_parameters == "?field=test_value&other_key=path_value&default_field=default_value"


def test_request_data_as_array(request_object: RequestClass):
    assert request_object.as_array == ["field", "other_key", "default_field"]
