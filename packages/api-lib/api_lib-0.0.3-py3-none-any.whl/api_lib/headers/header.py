import os
from typing import Optional


class Header:
    key: str = ""
    prefix: str = ""
    value: str = ""

    def __init__(self, value: Optional[str] = None, env_var: Optional[str] = None):
        if env_var:
            if env_value := os.getenv(env_var):
                value = env_value.strip()
            else:
                raise KeyError(f"Environment variable '{env_var}' is not set or empty.")

        self.value = value

    @property
    def header(self) -> dict:
        if self.prefix:
            return {self.key: f"{self.prefix} {self.value}"}
        else:
            return {self.key: self.value}

    def __repr__(self) -> str:
        return str(self.header)
