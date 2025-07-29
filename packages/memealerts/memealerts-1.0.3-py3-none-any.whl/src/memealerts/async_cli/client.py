from http import HTTPStatus

import httpx

from memealerts.base_client import BaseMAClient
from memealerts.types.exceptions import MAError
from memealerts.types.models import Balance, SupportersList, User
from memealerts.types.user_id import UserID


class MemealertsAsyncClient(BaseMAClient):
    def __init__(self, token: str) -> None:
        super().__init__(token)
        self.__client = httpx.AsyncClient()

    async def get_supporters(
        self, limit: int | None = None, query: str | None = None, skip: int | None = None
    ) -> SupportersList:
        query_params = {"limit": limit, "query": query, "skip": skip}
        query_params = {k: v for k, v in query_params.items() if v is not None}
        async with self.__client as cli:
            response = await cli.post(
                self._BASE_URL + "/supporters",
                json=query_params,
                headers=self._headers,
            )
            response.raise_for_status()
            return SupportersList.model_validate(response.json())

    async def give_bonus(
        self,
        user: UserID,
        value: int,
    ) -> None:
        if value < 1:
            raise ValueError("Value must be more than 0")
        query_params = {"userId": user, "streamerId": self.streamer_user_id, "value": value}
        query_params = {k: v for k, v in query_params.items() if v is not None}
        async with self.__client as cli:
            response = await cli.post(
                self._BASE_URL + "/user/give-bonus",
                json=query_params,
                headers=self._headers,
            )
            if response.status_code != HTTPStatus.CREATED:
                raise MAError

    async def find_user(self, username: str) -> User:
        """
        Search for a user by username (which is user link actually, but not a name).
        """

        async with self.__client as cli:
            response = await cli.post(
                self._BASE_URL + "/user/find",
                json={"username": username},
                headers=self._headers,
            )
            if response.status_code == HTTPStatus.CREATED:
                return User.model_validate(response.json())
            raise MAError

    async def get_balance(self, username: str) -> Balance:
        """
        Shows you balance for your account at streamer `username` channel
        """
        async with self.__client as cli:
            response = await cli.post(
                self._BASE_URL + "/user/balance",
                json={"username": username},
                headers=self._headers,
            )
            if response.status_code == HTTPStatus.CREATED:
                return Balance.model_validate(response.json())
            raise MAError
