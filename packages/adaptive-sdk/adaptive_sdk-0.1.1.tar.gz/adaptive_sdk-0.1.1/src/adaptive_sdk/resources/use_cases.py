from __future__ import annotations
from typing import Sequence, TYPE_CHECKING

from adaptive_sdk.graphql_client import UseCaseCreate, UseCaseSettingsInput, UseCaseData

from .base_resource import SyncAPIResource, AsyncAPIResource, UseCaseResource

if TYPE_CHECKING:
    from adaptive_sdk.client import Adaptive, AsyncAdaptive


class UseCase(SyncAPIResource, UseCaseResource):  # type: ignore[misc]
    """
    Resource to interact with use cases.
    """

    def __init__(self, client: Adaptive) -> None:
        SyncAPIResource.__init__(self, client)
        UseCaseResource.__init__(self, client)

    def create(
        self,
        key: str,
        name: str | None = None,
        description: str | None = None,
        team: str | None = None,
    ) -> UseCaseData:
        """
        Create new use case.

        Args:
            key: Use case key.
            name: Human-readable use case name which will be rendered in the UI.
                If not set, will be the same as `key`.
            description: Description of model which will be rendered in the UI.
        """

        input = UseCaseCreate(
            name=name if name else key,
            key=key,
            description=description,
            team=team,
            settings=UseCaseSettingsInput(defaultMetric=None),
        )
        return self._gql_client.create_use_case(input).create_use_case

    def list(self) -> Sequence[UseCaseData]:
        """
        List all use cases.
        """
        return self._gql_client.list_use_cases().use_cases

    def get(
        self,
        use_case: str | None = None,
    ) -> UseCaseData | None:
        """
        Get details for the client's use case.
        """

        return self._gql_client.describe_use_case(self.use_case_key(use_case)).use_case


class AsyncUseCase(AsyncAPIResource, UseCaseResource):  # type: ignore[misc]
    """
    Resource to interact with use cases.
    """

    def __init__(self, client: AsyncAdaptive) -> None:
        AsyncAPIResource.__init__(self, client)
        UseCaseResource.__init__(self, client)

    async def create(
        self,
        key: str,
        name: str | None = None,
        description: str | None = None,
        team: str | None = None,
        default_feedback_key: str | None = None,
    ) -> UseCaseData:
        """
        Create new use case.

        Args:
            key: Use case key.
            name: Human-readable use case name which will be rendered in the UI.
                If not set, will be the same as `key`.
            description: Description of model which will be rendered in the UI.
        """
        input = UseCaseCreate(
            name=name if name else key,
            key=key,
            description=description,
            team=team,
            settings=UseCaseSettingsInput(defaultMetric=default_feedback_key),
        )
        result = await self._gql_client.create_use_case(input)
        return result.create_use_case

    async def list(self) -> Sequence[UseCaseData]:
        """
        List all use cases.
        """
        result = await self._gql_client.list_use_cases()
        return result.use_cases

    async def get(
        self,
        use_case: str | None = None,
    ) -> UseCaseData | None:
        """
        Get details for the client's use case.
        """
        result = await self._gql_client.describe_use_case(self.use_case_key(use_case))
        return result.use_case
