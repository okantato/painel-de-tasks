"""Cliente mínimo para a API de gerenciamento de tasks."""

from __future__ import annotations

import os
from typing import Any

import requests
from dotenv import load_dotenv

load_dotenv()


class TaskAPIError(Exception):
    def __init__(self, message: str, status_code: int | None = None, details: Any = None):
        super().__init__(message)
        self.status_code = status_code
        self.details = details


class TaskAPI:
    def __init__(self) -> None:
        self.base_url = os.getenv("TASK_API_BASE_URL", "").rstrip("/")
        self.token = os.getenv("API_TASK_MANAGEMENT_TOKEN", "")
        if not self.base_url or not self.token:
            raise TaskAPIError(
                "Configure TASK_API_BASE_URL e API_TASK_MANAGEMENT_TOKEN no arquivo .env."
            )
        self.session = requests.Session()
        self.session.headers.update(
            {
                "Authorization": f"Bearer {self.token}",
                "Content-Type": "application/json",
                "Accept": "application/json",
            }
        )

    def get_task(self, glpi_ticket_id: str) -> dict[str, Any]:
        return self._request("GET", glpi_ticket_id)

    def update_task(self, glpi_ticket_id: str, payload: dict[str, Any]) -> dict[str, Any]:
        return self._request("POST", glpi_ticket_id, json=payload)

    def _request(self, method: str, ticket_id: str, **kwargs: Any) -> dict[str, Any]:
        url = f"{self.base_url}/api/tasks/{ticket_id}"
        try:
            response = self.session.request(method, url, timeout=25, **kwargs)
        except requests.RequestException as exc:
            raise TaskAPIError(f"Não foi possível conectar à API: {exc}") from exc

        try:
            body = response.json() if response.content else {}
        except ValueError:
            body = {"message": response.text[:1000]}

        if not response.ok:
            messages = {
                401: "A API recusou a autenticação. Confira o token e a configuração no servidor.",
                404: f"Não existe task associada ao chamado {ticket_id}.",
                409: f"O chamado {ticket_id} está associado a mais de uma task.",
                422: "A API rejeitou alguns campos. Confira os detalhes abaixo.",
            }
            raise TaskAPIError(
                messages.get(response.status_code, f"A API respondeu com HTTP {response.status_code}."),
                response.status_code,
                body,
            )
        if not isinstance(body, dict):
            raise TaskAPIError("A API retornou uma resposta em formato inesperado.", response.status_code)
        return body
