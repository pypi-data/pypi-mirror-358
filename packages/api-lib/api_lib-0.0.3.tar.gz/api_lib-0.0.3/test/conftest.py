import time
from multiprocessing import Process
from test.config.rest_api import run_server

import pytest
from dotenv import load_dotenv

from api_lib.api_lib import ApiLib
from api_lib.headers.authorization import Bearer

from .config.request import RequestClass

load_dotenv()


@pytest.fixture
def api():
    return ApiLib("http://127.0.0.1:5001", Bearer("test_token"))


@pytest.fixture
def api_not_reachable():
    return ApiLib("http://127.0.0.1:5002", Bearer("test_token"))


@pytest.fixture
def request_object():
    return RequestClass("test_value", "path_value")


@pytest.fixture(scope="session", autouse=True)
def rest_server():
    proc = Process(target=run_server, daemon=True)
    proc.start()
    time.sleep(1)  # wait for server to start
    yield
    proc.terminate()
