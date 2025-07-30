from __future__ import annotations
from uuid import UUID
from typing import TYPE_CHECKING
from typing_extensions import override
from adaptive_sdk.error_handling import rest_error_handler
from adaptive_sdk.rest import rest_types
from adaptive_sdk.utils import convert_optional_UUID, get_full_model_path

from .base_resource import SyncAPIResource, AsyncAPIResource, UseCaseResource

if TYPE_CHECKING:
    from adaptive_sdk.client import Adaptive, AsyncAdaptive

ROUTE = "/completions"


class Completions(SyncAPIResource, UseCaseResource):  # type: ignore[misc]
    def __init__(self, client: Adaptive) -> None:
        SyncAPIResource.__init__(self, client)
        UseCaseResource.__init__(self, client)

    def create(
        self,
        prompt: str,
        model: str | None = None,
        stream: bool | None = None,
        session_id: str | UUID | None = None,
        use_case: str | None = None,
        user: str | UUID | None = None,
        ab_campaign: str | None = None,
        n: int | None = None,
        labels: dict[str, str] | None = None,
    ) -> rest_types.GenerateResponse:

        input = rest_types.GenerateInput(
            prompt=prompt,
            model=get_full_model_path(self.use_case_key(use_case), model),
            stream=stream,
            session_id=convert_optional_UUID(session_id),
            user=convert_optional_UUID(user),
            ab_campaign=ab_campaign,
            n=n,
            labels=labels,
        )
        r = self._rest_client.post(ROUTE, json=input.model_dump(exclude_none=True))
        rest_error_handler(r)
        return rest_types.GenerateResponse.model_validate(r.json())


class AsyncCompletions(AsyncAPIResource, UseCaseResource):  # type: ignore[misc]
    @override
    def __init__(self, client: AsyncAdaptive) -> None:
        AsyncAPIResource.__init__(self, client)
        UseCaseResource.__init__(self, client)

    async def create(
        self,
        prompt: str,
        model: str | None = None,
        stream: bool | None = None,
        session_id: str | UUID | None = None,
        use_case: str | None = None,
        user: str | UUID | None = None,
        ab_campaign: str | None = None,
        n: int | None = None,
        labels: dict[str, str] | None = None,
    ) -> rest_types.GenerateResponse:

        input = rest_types.GenerateInput(
            prompt=prompt,
            model=get_full_model_path(self.use_case_key(use_case), model),
            stream=stream,
            session_id=convert_optional_UUID(session_id),
            user=convert_optional_UUID(user),
            ab_campaign=ab_campaign,
            n=n,
            labels=labels,
        )
        r = await self._rest_client.post(
            ROUTE, json=input.model_dump(exclude_none=True)
        )
        rest_error_handler(r)
        return rest_types.GenerateResponse.model_validate(r.json())
