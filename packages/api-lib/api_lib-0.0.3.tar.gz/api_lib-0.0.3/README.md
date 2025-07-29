# api-lib  [![Format and tests](https://github.com/jeandemeusy/api-lib/actions/workflows/lint_and_test.yaml/badge.svg?branch=master)](https://github.com/jeandemeusy/api-lib/actions/workflows/lint_and_test.yaml) [![cov](https://github.com/jeandemeusy/api-lib/blob/gh-pages/badges/coverage.svg)](https://github.com/jeandemeusy/api-lib/actions)

A lightweight Python library for building and consuming APIs with ease.

## Features

- Simple API client utilities
- Built-in request/response handling
- Extensible and easy to integrate

## Installation

It's recommended to use `uv` to install the package:

```bash
uv add api-lib
```

## Usage

### Example: Consuming an API

```python
from api_lib import ApiLib
from api_lib.headers.accept import AcceptGithub
from api_lib.headers.authorization import Bearer
from api_lib.method import Method

from .response import Repository, User

class GithubAPI(ApiLib):
    headers = [AcceptGithub()]

    async def user(self) -> User:
        return await self.req(Method.GET, "/user", User)


api = GithubAPI("https://api.github.com", Bearer(env_var="GITHUB_TOKEN"))

user = await gh_api.user()
```

## Documentation

See the [full documentation](docs/) for more details and advanced usage.

## Contributing

Contributions are welcome! Please open issues or submit pull requests.

## License

This project is licensed under the MIT License.
