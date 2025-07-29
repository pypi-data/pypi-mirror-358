import random
from collections.abc import Callable
from test.config.response import Repository, User
from typing import Optional, Union

from flask import Flask, jsonify

from api_lib.api_lib import ApiLib
from api_lib.headers import Header
from api_lib.method import Method


class RestAPI(ApiLib):
    headers: list[Header] = []

    async def user(self, return_state: bool = False, return_type: Optional[Callable] = User) -> Union[User, bool]:
        return await self.req(Method.GET, "/user", return_type, return_state=return_state)

    async def read_me(
        self,
    ) -> str:
        return await self.req(Method.GET, "/read_me", str)

    async def repositories(self, organization: str) -> list[Repository]:
        return await self.req(Method.GET, f"/orgs/{organization}/repos", list[Repository])

    async def invalid_query(self):
        # This method is intentionally invalid to test error handling
        return await self.req(Method.GET, "/invalid_query")


def create_test_app():
    app = Flask(__name__)

    @app.route("/user", methods=["GET"])
    def user():
        return (
            jsonify(
                {
                    "login": "jeandemeusy",
                    "name": "Jean Demeusy",
                    "disk_usage": 125750,
                    "plan": {"space": 976562499},
                }
            ),
            200,
        )

    @app.route("/read_me", methods=["GET"])
    def read_me():
        return "This is a dummy README", 200

    @app.route("/orgs/<string:organization>/repos", methods=["GET"])
    def repositories(organization: str):
        return (
            jsonify(
                [
                    {"name": "python-build-standalone", "fullname": "astral-sh/python-build-standalone"},
                    {"name": "ruff", "fullname": "astral-sh/ruff"},
                    {"name": "RustPython", "fullname": "astral-sh/RustPython"},
                    {"name": "ruff-pre-commit", "fullname": "astral-sh/ruff-pre-commit"},
                    {"name": "ruff-vscode", "fullname": "astral-sh/ruff-vscode"},
                    {"name": "ruff-lsp", "fullname": "astral-sh/ruff-lsp"},
                    {"name": "rye", "fullname": "astral-sh/rye"},
                    {"name": "RustPython-Parser", "fullname": "astral-sh/RustPython-Parser"},
                    {"name": "schemastore", "fullname": "astral-sh/schemastore"},
                    {"name": "transformers", "fullname": "astral-sh/transformers"},
                    {"name": "uv", "fullname": "astral-sh/uv"},
                    {"name": "pubgrub", "fullname": "astral-sh/pubgrub"},
                    {"name": "packse", "fullname": "astral-sh/packse"},
                    {"name": "pypi-proxy", "fullname": "astral-sh/pypi-proxy"},
                    {"name": "uv-pre-commit", "fullname": "astral-sh/uv-pre-commit"},
                    {"name": "lsp-types", "fullname": "astral-sh/lsp-types"},
                    {"name": "reqwest-middleware", "fullname": "astral-sh/reqwest-middleware"},
                    {"name": "docs", "fullname": "astral-sh/docs"},
                    {"name": "nginx_pypi_cache", "fullname": "astral-sh/nginx_pypi_cache"},
                    {"name": "tl", "fullname": "astral-sh/tl"},
                    {"name": "uv-fastapi-example", "fullname": "astral-sh/uv-fastapi-example"},
                    {"name": "setup-uv", "fullname": "astral-sh/setup-uv"},
                    {"name": "uv-docker-example", "fullname": "astral-sh/uv-docker-example"},
                    {"name": "uv-flask-example", "fullname": "astral-sh/uv-flask-example"},
                    {"name": "ruff-action", "fullname": "astral-sh/ruff-action"},
                    {"name": "trusted-publishing-examples", "fullname": "astral-sh/trusted-publishing-examples"},
                    {"name": "workspace-in-root-test", "fullname": "astral-sh/workspace-in-root-test"},
                    {"name": "workspace-virtual-root-test", "fullname": "astral-sh/workspace-virtual-root-test"},
                    {"name": "sanitize-wheel-test", "fullname": "astral-sh/sanitize-wheel-test"},
                    {"name": ".github", "fullname": "astral-sh/.github"},
                ]
            ),
            200,
        )

    @app.route("/always_fail", methods=["GET"])
    def always_fail():
        return jsonify({"success": False}), 400

    @app.route("/always_succeed", methods=["GET"])
    def always_succeed():
        return jsonify({"success": True}), 200

    @app.route("/randomly_succeed", methods=["GET"])
    def randomly_succeed():
        if random.random() < 0.75:
            return jsonify({"success": False}), 402
        else:
            return jsonify({"success": True}), 200

    return app


def run_server():
    app = create_test_app()
    app.run(debug=False, port=5001)
