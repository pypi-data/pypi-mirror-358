from test.config.response import Repository, User

import pytest

from api_lib.api_lib import ApiLib
from api_lib.method import Method


@pytest.mark.asyncio
async def test_simple_api(api: ApiLib):
    user = await api.req(Method.GET, "/user", User)

    assert user.login != ""
    assert user.name != ""
    assert user.disk_usage >= 0
    assert user.disk_space_limit > 0


@pytest.mark.asyncio
async def test_api_returns_list(api: ApiLib):
    repos = await api.req(Method.GET, "/orgs/astral-sh/repos", list[Repository])

    assert isinstance(repos, list)
    assert len(repos) > 0


@pytest.mark.asyncio
async def test_api_returns_text(api: ApiLib):
    readme = await api.req(Method.GET, "/read_me", str)

    assert isinstance(readme, str)
    assert len(readme) > 0


@pytest.mark.asyncio
async def test_expect_oserror(api: ApiLib):
    with pytest.raises(RuntimeError):
        await api.req(Method.GET, "/invalid_query")


@pytest.mark.asyncio
async def test_unreachable_endpoint(api_not_reachable: ApiLib):
    with pytest.raises(RuntimeError):
        await api_not_reachable.req(Method.GET, "/user", User)


@pytest.mark.asyncio
async def test_return_state(api: ApiLib):
    result = await api.req(Method.GET, "/user", User, return_state=True)

    assert isinstance(result, bool)
    assert result is True


@pytest.mark.asyncio
async def test_no_return_type(api: ApiLib):
    result = await api.req(Method.GET, "/user", None)
    assert isinstance(result, dict)


@pytest.mark.asyncio
async def test_timeout_check_success(api: ApiLib):
    result = await api.timeout_check_success("/always_fail", timeout=2)
    assert result is False

    result = await api.timeout_check_success("/always_succeed", timeout=2)
    assert result is True

    result = await api.timeout_check_success("/randomly_succeed", timeout=2)
    assert result is True
