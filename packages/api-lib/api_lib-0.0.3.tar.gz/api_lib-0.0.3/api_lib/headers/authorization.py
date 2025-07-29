from .header import Header


class Authorization(Header):
    key: str = "Authorization"


class Bearer(Authorization):
    prefix: str = "Bearer"


class Basic(Authorization):
    prefix: str = "Basic"


class ApiKey(Authorization):
    prefix: str = "Apikey"
