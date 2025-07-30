from __future__ import annotations
from typing import TYPE_CHECKING, Sequence

from adaptive_sdk.graphql_client import (
    RemoteEnvData,
    RemoteEnvCreate,
    TestRemoteEnvTestRemoteEnvRemoteEnvTestOnline,
    TestRemoteEnvTestRemoteEnvRemoteEnvTestOffline,
)

from .base_resource import SyncAPIResource, AsyncAPIResource, UseCaseResource

if TYPE_CHECKING:
    from adaptive_sdk.client import Adaptive, AsyncAdaptive


class RewardServers(SyncAPIResource, UseCaseResource):  # type: ignore[misc]
    """
    Resource to interact with external reward servers.
    """

    def __init__(self, client: Adaptive) -> None:
        SyncAPIResource.__init__(self, client)
        UseCaseResource.__init__(self, client)

    def list(self) -> Sequence[RemoteEnvData]:
        return self._gql_client.list_remote_envs().remote_envs

    def add(
        self,
        url: str,
        key: str,
        name: str | None = None,
        description: str | None = None,
    ) -> RemoteEnvData:
        input = RemoteEnvCreate(
            url=url, key=key, name=name or key, description=description
        )
        return self._gql_client.add_remote_env(input).add_remote_env

    def remove(self, key: str) -> str:
        return self._gql_client.remove_remote_env(key).remove_remote_env

    def test(
        self, url: str
    ) -> (
        TestRemoteEnvTestRemoteEnvRemoteEnvTestOnline
        | TestRemoteEnvTestRemoteEnvRemoteEnvTestOffline
    ):
        return self._gql_client.test_remote_env(
            RemoteEnvCreate(url=url)
        ).test_remote_env


class AsyncRewardServers(AsyncAPIResource, UseCaseResource):  # type: ignore[misc]
    """
    Async resource to interact with external rewards servers.
    """

    def __init__(self, client: AsyncAdaptive) -> None:
        AsyncAPIResource.__init__(self, client)
        UseCaseResource.__init__(self, client)

    async def list(self) -> Sequence[RemoteEnvData]:
        return (await self._gql_client.list_remote_envs()).remote_envs

    async def add(
        self,
        url: str,
        key: str,
        name: str | None = None,
        description: str | None = None,
    ) -> RemoteEnvData:
        input = RemoteEnvCreate(
            url=url, key=key, name=name or key, description=description
        )
        return (await self._gql_client.add_remote_env(input)).add_remote_env

    async def remove(self, key: str) -> str:
        return (await self._gql_client.remove_remote_env(key)).remove_remote_env

    async def test(
        self, url: str
    ) -> (
        TestRemoteEnvTestRemoteEnvRemoteEnvTestOnline
        | TestRemoteEnvTestRemoteEnvRemoteEnvTestOffline
    ):
        return (
            await self._gql_client.test_remote_env(RemoteEnvCreate(url=url))
        ).test_remote_env
