from test.lib import EnvVarContext

import pytest

from api_lib.headers.header import Header


def test_header_from_value():
    header = Header("custom-value")
    assert header.value == "custom-value"


def test_header_from_env_var():
    with EnvVarContext("CUSTOM_HEADER", "custom-value"):
        header = Header(env_var="CUSTOM_HEADER")
        assert header.value == "custom-value"


def test_header_from_inexistant_env_var():
    with pytest.raises(KeyError):
        Header(env_var="CUSTOM_HEADER")
