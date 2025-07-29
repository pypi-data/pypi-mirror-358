from api_lib.headers.accept import Accept


def test_custom_accept_header():
    header = Accept("random/type")

    assert header.header["Accept"] == "random/type"
