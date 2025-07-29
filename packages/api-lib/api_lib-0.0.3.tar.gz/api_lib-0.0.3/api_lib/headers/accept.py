from typing import Optional

from .header import Header


class Accept(Header):
    key: str = "Accept"
    value: str = ""

    def __init__(self, accept_type: Optional[str] = None):
        if accept_type:
            self.value = accept_type


class AcceptGithub(Accept):
    value: str = "application/vnd.github+json"


class AcceptTextHtml(Accept):
    value: str = "text/html"


class AcceptJson(Accept):
    value: str = "application/json"


class AcceptTextPlain(Accept):
    value: str = "text/plain"


class AcceptImages(Accept):
    value: str = "image/*"


class AcceptOctetStream(Accept):
    value: str = "application/octet-stream"


class AcceptFormUrlEncoded(Accept):
    value: str = "application/x-www-form-urlencoded"


class AcceptMultipartFormData(Accept):
    value: str = "multipart/form-data"
