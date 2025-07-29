from typing import List, Iterable, Dict, Any
from datetime import datetime
from langchain_core.documents import Document

import backoff
import requests
from requests.exceptions import RequestException

from langchain_community.document_loaders.base import BaseLoader


class StackOverflowTeamsApiV3Loader(BaseLoader):
    """Load documents from StackOverflow API v3."""

    def __init__(
        self,
        access_token: str,
        content_type: str,
        team: str = "",
        date_from: str = "",
        sort: str = "",
        order: str = "",
        endpoint: str = "api.stackoverflowteams.com",
        is_answered: str = "",
        has_accepted_answer: str = "",
        max_retries: int = 3,
        timeout: int = 30,
    ) -> None:
        """
        Initializes the StackOverflowTeamsApiV3Loader with necessary parameters.

        Args:
            access_token (str): Access token for authentication.
            team (str): The team identifier to fetch documents for.
            content_type (str): The type of content to fetch (must be one of "questions", "answers", or "articles").
            date_from (str, optional): Filter results from this date (ISO 8601 format).
            sort (str, optional): Sort order for results (e.g., "creation", "activity").
            order (str, optional): Order direction ("asc" or "desc").
            endpoint (str, optional): API endpoint to use, default is "api.stackoverflowteams.com".
            is_answered (str, options): Whether or not to filter questions to only those that are answered."
            has_accepted_answer (str, options): Whether or not to filter questions to only those that have an accepted answer.
            max_retries (int, optional): Maximum number of retries for failed requests.
            timeout (int, optional): Timeout for requests in seconds.

        Raises:
            ValueError: If any required parameter is missing or invalid.
        """
        if not access_token:
            raise ValueError("access_token must be provided.")

        allowed_content_types = {"questions", "articles"}
        if content_type not in allowed_content_types:
            raise ValueError(f"content_type must be one of {allowed_content_types}.")
        self.content_type = content_type

        self.headers = {"Authorization": f"Bearer {access_token}"}

        if date_from:
            try:
                datetime.strptime(date_from, "%Y-%m-%dT%H:%M:%SZ")
            except ValueError as exc:
                raise ValueError("date_from must be in ISO 8601 format (YYYY-MM-DDThh:mm:ssZ)") from exc
        self.dateFrom = date_from

        self.endpoint = endpoint

        allowed_sorts = {"activity", "creation", "score"}
        if sort != "" and sort not in allowed_sorts:
            raise ValueError(f"sort must be one of {allowed_sorts}.")
        self.sort = sort

        allowed_orders = {"asc", "desc"}
        if order != "" and order not in allowed_orders:
            raise ValueError(f"order must be one of {allowed_orders}.")
        self.order = order

        self.is_answered = is_answered
        self.has_accepted_answer = has_accepted_answer

        if team:
            self.fullEndpoint = f"https://{endpoint}/v3/teams/{team}/{self.content_type}"
        else:
            self.fullEndpoint = f"https://{self.endpoint}/v3/{self.content_type}"

        self.timeout = timeout
        self.max_retries = max_retries

    def lazy_load(self) -> list[Document]:
        """Load documents from StackOverflow API v3."""

        results: List[Document] = []

        if self.content_type == "questions":
            docs = self._question_and_answer_loader()
        else:
            docs = self._articles_loader()
        results.extend(docs)

        return results

    def _question_and_answer_loader(self) -> Iterable[Document]:
        params = {k: v for k, v in {
            "from": self.dateFrom,
            "sort": self.sort,
            "order": self.order,
            "isAnswered": self.is_answered,
            "hasAcceptedAnswer": self.has_accepted_answer,
        }.items() if v}

        for item in self._get_paginated_results(self.fullEndpoint, params):
            page_content = ""

            answersBody = ""
            for answer in self._get_paginated_results(f"{self.fullEndpoint}/{item['id']}/answers", params={}):
                answersBody += answer["body"] + "\n\n"

            page_content = item["body"] + "\n\n" + answersBody

            metadata = {
                "id": item["id"],
                "type": item.get("type", self.content_type),
                "title": item["title"],
                "creationDate": item["creationDate"],
                "lastActivityDate": item["lastActivityDate"],
                "viewCount": item["viewCount"],
                "webUrl": item["webUrl"],
                "isDeleted": item["isDeleted"],
                "isObsolete": item["isObsolete"],
                "isClosed": item["isClosed"],
                "isAnswered": item["isAnswered"],
                "answerCount": item["answerCount"]
            }

            yield Document(
                page_content=page_content,
                metadata=metadata
            )

    def _articles_loader(self) -> Iterable[Document]:
        params = {k: v for k, v in {
            "from": self.dateFrom,
            "sort": self.sort,
            "order": self.order,
        }.items() if v}

        for item in self._get_paginated_results(self.fullEndpoint, params):
            metadata = {
                "id": item["id"],
                "type": item.get("type", self.content_type),
                "title": item["title"],
                "creationDate": item["creationDate"],
                "lastActivityDate": item["lastActivityDate"],
                "viewCount": item["viewCount"],
                "webUrl": item["webUrl"],
                "isDeleted": item["isDeleted"],
                "isObsolete": item["isObsolete"],
                "isClosed": item["isClosed"],
            }

            yield Document(
                page_content=item["body"],
                metadata=metadata
            )

    @backoff.on_exception(
        backoff.expo,
        RequestException,
        max_tries=3
    )
    def _make_request(self, url: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Make HTTP request with retry logic and error handling."""
        response = requests.get(
            url,
            headers=self.headers,
            params=params,
            timeout=self.timeout,
            verify=True
        )

        if response.status_code == 429:
            raise RequestException("Rate limit exceeded")

        response.raise_for_status()
        return response.json()

    def _get_paginated_results(self, url: str, params: Dict[str, Any]) -> Iterable[Dict[str, Any]]:
        """Handle pagination for any endpoint."""
        page = 1
        items = True
        while items:
            params["page"] = str(page)
            data = self._make_request(url, params)
            items = data.get("items", [])

            for item in items:
                yield item

            page += 1
