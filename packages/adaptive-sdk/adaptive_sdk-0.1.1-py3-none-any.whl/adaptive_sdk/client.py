from typing import Dict
from .base_client import BaseSyncClient, BaseAsyncClient, UseCaseClient
from . import resources


class Adaptive(BaseSyncClient, UseCaseClient):
    def __init__(
        self,
        base_url: str,
        api_key: str | None = None,
        default_headers: Dict[str, str] | None = None,
    ) -> None:
        """
        Instantiates a new synchronous Adaptive client bounded to a use case.

        Args:
            use_case (str): A unique use case key; the client is bounded to this use case.
            base_url (str): The base URL for the Adaptive API.
            api_key (str, optional): API key for authentication.
                Defaults to None, in which case environment variable `ADAPTIVE_API_KEY` needs to be set.

        """
        super().__init__(base_url, api_key, default_headers)
        self.__use_case_key = None

        self.ab_tests: resources.ABTests = resources.ABTests(self)
        self.chat: resources.Chat = resources.Chat(self)
        self.completions: resources.Completions = resources.Completions(self)
        self.compute_pools: resources.ComputePools = resources.ComputePools(self)
        self.custom_recipes: resources.CustomRecipes = resources.CustomRecipes(self)
        self.datasets: resources.Datasets = resources.Datasets(self)
        self.embeddings: resources.Embeddings = resources.Embeddings(self)
        self.evaluation: resources.Evaluation = resources.Evaluation(self)
        self.judges: resources.Judges = resources.Judges(self)
        self.feedback: resources.Feedback = resources.Feedback(self)
        self.interactions: resources.Interactions = resources.Interactions(self)
        self.models: resources.Models = resources.Models(self)
        self.permissions: resources.Permissions = resources.Permissions(self)
        self.reward_servers: resources.RewardServers = resources.RewardServers(self)
        self.roles: resources.Roles = resources.Roles(self)
        self.teams: resources.Teams = resources.Teams(self)
        self.training: resources.Training = resources.Training(self)
        self.use_cases: resources.UseCase = resources.UseCase(self)
        self.users: resources.Users = resources.Users(self)

    @property
    def default_use_case(self) -> str | None:
        """
        Get the current default use case key.
        """
        return self.__use_case_key

    def set_default_use_case(self, use_case: str) -> None:
        """
        Set a default use case key to be used for use case-specific operations.
        """
        if not (isinstance(use_case, str) and bool(use_case.strip())):
            raise ValueError("use_case must be a non-empty string")
        self.__use_case_key = use_case  # type: ignore[assignment]


class AsyncAdaptive(BaseAsyncClient, UseCaseClient):
    def __init__(
        self,
        base_url: str,
        api_key: str | None = None,
        default_headers: Dict[str, str] | None = None,
    ) -> None:
        """
        Instantiates a new asynchronous Adaptive client bounded to a use case.

        Args:
            use_case (str): A unique use case key; the client is bounded to this use case.
            base_url (str): The base URL for the Adaptive API.
            api_key (str, optional): API key for authentication.
                Defaults to None, in which case environment variable `ADAPTIVE_API_KEY` needs to be set.

        """
        super().__init__(base_url, api_key, default_headers)
        self.__use_case_key = None

        self.ab_tests: resources.AsyncABTests = resources.AsyncABTests(self)
        self.chat: resources.AsyncChat = resources.AsyncChat(self)
        self.completions: resources.AsyncCompletions = resources.AsyncCompletions(self)
        self.compute_pools: resources.AsyncComputePools = resources.AsyncComputePools(self)
        self.custom_recipes: resources.AsyncCustomRecipes = resources.AsyncCustomRecipes(self)
        self.datasets: resources.AsyncDatasets = resources.AsyncDatasets(self)
        self.embeddings: resources.AsyncEmbeddings = resources.AsyncEmbeddings(self)
        self.evaluation: resources.AsyncEvaluation = resources.AsyncEvaluation(self)
        self.judges: resources.AsyncJudges = resources.AsyncJudges(self)
        self.feedback: resources.AsyncFeedback = resources.AsyncFeedback(self)
        self.interactions: resources.AsyncInteractions = resources.AsyncInteractions(self)
        self.models: resources.AsyncModels = resources.AsyncModels(self)
        self.permissions: resources.AsyncPermissions = resources.AsyncPermissions(self)
        self.reward_servers: resources.AsyncRewardServers = resources.AsyncRewardServers(self)
        self.roles: resources.AsyncRoles = resources.AsyncRoles(self)
        self.teams: resources.AsyncTeams = resources.AsyncTeams(self)
        self.training: resources.AsyncTraining = resources.AsyncTraining(self)
        self.use_cases: resources.AsyncUseCase = resources.AsyncUseCase(self)
        self.users: resources.AsyncUsers = resources.AsyncUsers(self)

    @property
    def default_use_case(self) -> str | None:
        """
        Get the current default use case key.
        """
        return self.__use_case_key

    def set_default_use_case(self, use_case: str) -> None:
        """
        Set a default use case key to be used for use case-specific operations.
        """
        if not isinstance(use_case, str):
            raise TypeError("use_case must be a string")
        if not use_case.strip():
            raise ValueError("use_case cannot be empty or whitespace")
        self.__use_case_key = use_case  # type: ignore[assignment]
