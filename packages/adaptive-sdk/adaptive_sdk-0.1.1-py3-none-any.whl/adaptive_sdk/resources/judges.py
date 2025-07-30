from __future__ import annotations

from typing import List, Sequence, TYPE_CHECKING, Union, Literal

from adaptive_sdk.graphql_client import (
    JudgeData,
    JudgeCreate,
    JudgeExampleInput,
    JudgeExampleInputTurnEntry,
    PrebuiltJudgeCreate,
    PrebuiltCriteriaKey,
    JudgeUpdate,
)
from adaptive_sdk import input_types

from .base_resource import SyncAPIResource, AsyncAPIResource, UseCaseResource

if TYPE_CHECKING:
    from adaptive_sdk.client import Adaptive, AsyncAdaptive


def _parse_judge_examples(examples: List[input_types.JudgeExampleInput]) -> List[JudgeExampleInput]:
    """Convert a list of python dicts JudgeExampleInput pydantic models"""
    parsed: List[JudgeExampleInput] = []
    for ex in examples:
        if not all(k in ex for k in ("input", "output", "passes", "reasoning")):
            raise ValueError("Each judge example must contain 'input', 'output', 'reasoning' and 'passes' keys")
        input_turns = [JudgeExampleInputTurnEntry(role=t["role"], content=t["content"]) for t in ex["input"]]
        pass_value = bool(ex["passes"])
        parsed.append(
            JudgeExampleInput(
                input=input_turns,
                output=ex["output"],
                reasoning=ex["reasoning"],
                **{"pass": pass_value},
            )
        )
    return parsed


class Judges(SyncAPIResource, UseCaseResource):  # type: ignore[misc]
    """Resource to interact with Judge definitions used to evaluate model completions."""

    def __init__(self, client: Adaptive) -> None:
        SyncAPIResource.__init__(self, client)
        UseCaseResource.__init__(self, client)

    def create(
        self,
        *,
        criteria: str,
        judge_model: str,
        key: str,
        examples: List[input_types.JudgeExampleInput] | None = None,
        name: str | None = None,
        feedback_key: str | None = None,
        use_case: str | None = None,
    ) -> JudgeData:
        """Create a new custom Judge.

        Args:
            criteria: Natural-language explanation of what should be verified in the completion to be considered a *pass* for this judge.
            judge_model: Model key of the judge model.
            key: Unique key for the judge.
            examples: List of annotated examples used in few-shot prompting for the judge.
                Each example is a ``dict`` with:
                • ``input``: list of ``{"role": str, "content": str}`` messages
                • ``output``: the assistant response
                • ``passes``: bool indicating if the output meets the criteria
                • ``reasoning`` (optional): explanation of the decision
            name: Human-readable judge name; if omitted, the key will be used.
            feedback_key: Optional feedback key this judge will write feedback to. If omitted, the judge key will be used.
            use_case: Explicit use-case key. Falls back to ``client.default_use_case`` when omitted.
        """
        input_obj = JudgeCreate(
            key=key,
            name=name or key,
            criteria=criteria,
            examples=_parse_judge_examples(examples or []),
            model=judge_model,
            metric=feedback_key,
        )
        return self._gql_client.create_judge(use_case=self.use_case_key(use_case), input=input_obj).create_judge

    # def create_prebuilt(
    #     self,
    #     *,
    #     prebuilt_criteria: Literal["ANSWER_RELEVANCY", "CONTEXT_RELEVANCY", "FAITHFULNESS"],
    #     judge_model: str,
    #     key: str,
    #     name: str | None = None,
    #     use_case: str | None = None,
    # ) -> JudgeData:
    #     """
    #     Create a Judge based on a pre-built criteria.

    #     Args:
    #         prebuilt_criteria: Pre-built criteria identifier.
    #         judge_model: Model key of the judge model.
    #         key: Unique key for the judge.
    #         name: Optional human-readable judge name; if omitted, the key will be used.
    #         use_case: Explicit use-case key. Falls back to ``client.default_use_case`` when omitted.
    #     """
    #     prebuilt_criteria_enum = PrebuiltCriteriaKey(prebuilt_criteria)
    #     input_obj = PrebuiltJudgeCreate(
    #         key=key,
    #         name=name or key,
    #         model=judge_model,
    #         prebuiltCriteriaKey=prebuilt_criteria_enum,
    #     )
    #     return self._gql_client.create_prebuilt_judge(
    #         use_case=self.use_case_key(use_case), input=input_obj
    #     ).create_prebuilt_judge

    def update(
        self,
        *,
        key: str,
        name: str | None = None,
        criteria: str | None = None,
        examples: List[input_types.JudgeExampleInput] | None = None,
        judge_model: str | None = None,
        use_case: str | None = None,
    ) -> JudgeData:
        """
        Update an existing Judge version.
        Any field set to ``None`` will be left unchanged.
        """
        input_obj = JudgeUpdate(
            name=name,
            criteria=criteria,
            examples=_parse_judge_examples(examples) if examples is not None else None,
            model=judge_model,
        )
        return self._gql_client.update_judge(
            use_case=self.use_case_key(use_case), key=key, input=input_obj
        ).update_judge

    def delete(self, *, key: str, use_case: str | None = None) -> bool:
        """Delete a Judge. Returns ``True`` on success."""
        result = self._gql_client.delete_judge(use_case=self.use_case_key(use_case), key=key).delete_judge
        return result.success

    def list(self, *, use_case: str | None = None) -> Sequence[JudgeData]:
        """List all Judges for the given use case."""
        return self._gql_client.list_judges(use_case=self.use_case_key(use_case)).judges

    def list_versions(self, *, key: str, use_case: str | None = None) -> Sequence[JudgeData]:
        """List all historical versions of a Judge key."""
        return self._gql_client.list_judge_versions(use_case=self.use_case_key(use_case), key=key).judge_versions

    def get(
        self,
        *,
        key: str,
        version: int | None = None,
        use_case: str | None = None,
    ) -> JudgeData | None:
        """Retrieve a specific Judge by key (optionally specifying version)."""
        return self._gql_client.get_judge(
            id=key,
            use_case=self.use_case_key(use_case),
            version=version if version is not None else None,
        ).judge


class AsyncJudges(AsyncAPIResource, UseCaseResource):  # type: ignore[misc]
    """Asynchronous resource to interact with Judge definitions used to evaluate model completions."""

    def __init__(self, client: AsyncAdaptive) -> None:
        AsyncAPIResource.__init__(self, client)
        UseCaseResource.__init__(self, client)

    async def create(
        self,
        *,
        criteria: str,
        judge_model: str,
        key: str,
        examples: List[input_types.JudgeExampleInput] | None = None,
        name: str | None = None,
        feedback_key: str | None = None,
        use_case: str | None = None,
    ) -> JudgeData:
        input_obj = JudgeCreate(
            key=key,
            name=name or key,
            criteria=criteria,
            examples=_parse_judge_examples(examples or []),
            model=judge_model,
            metric=feedback_key,
        )
        result = await self._gql_client.create_judge(use_case=self.use_case_key(use_case), input=input_obj)
        return result.create_judge

    # async def create_prebuilt(
    #     self,
    #     *,
    #     prebuilt_criteria: Literal["ANSWER_RELEVANCY", "CONTEXT_RELEVANCY", "FAITHFULNESS"],
    #     judge_model: str,
    #     key: str,
    #     name: str | None = None,
    #     use_case: str | None = None,
    # ) -> JudgeData:
    #     prebuilt_criteria_enum = PrebuiltCriteriaKey(prebuilt_criteria)
    #     input_obj = PrebuiltJudgeCreate(
    #         key=key,
    #         name=name or key,
    #         model=judge_model,
    #         prebuiltCriteriaKey=prebuilt_criteria_enum,
    #     )
    #     result = await self._gql_client.create_prebuilt_judge(use_case=self.use_case_key(use_case), input=input_obj)
    #     return result.create_prebuilt_judge

    async def update(
        self,
        *,
        key: str,
        name: str | None = None,
        criteria: str | None = None,
        examples: List[input_types.JudgeExampleInput] | None = None,
        judge_model: str | None = None,
        use_case: str | None = None,
    ) -> JudgeData:
        input_obj = JudgeUpdate(
            name=name,
            criteria=criteria,
            examples=_parse_judge_examples(examples) if examples is not None else None,
            model=judge_model,
        )
        result = await self._gql_client.update_judge(use_case=self.use_case_key(use_case), key=key, input=input_obj)
        return result.update_judge

    async def delete(self, *, key: str, use_case: str | None = None) -> bool:
        result = await self._gql_client.delete_judge(use_case=self.use_case_key(use_case), key=key)
        return result.delete_judge.success

    async def list(self, *, use_case: str | None = None) -> Sequence[JudgeData]:
        results = await self._gql_client.list_judges(use_case=self.use_case_key(use_case))
        return results.judges

    async def list_versions(self, *, key: str, use_case: str | None = None) -> Sequence[JudgeData]:
        results = await self._gql_client.list_judge_versions(use_case=self.use_case_key(use_case), key=key)
        return results.judge_versions

    async def get(
        self,
        *,
        key: str,
        version: int | None = None,
        use_case: str | None = None,
    ) -> JudgeData | None:
        result = await self._gql_client.get_judge(
            id=key,
            use_case=self.use_case_key(use_case),
            version=version if version is not None else None,
        )
        return result.judge
