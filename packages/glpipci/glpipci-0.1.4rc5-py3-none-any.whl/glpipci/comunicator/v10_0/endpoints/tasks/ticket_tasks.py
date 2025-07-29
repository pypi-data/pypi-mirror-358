from glpipci.comunicator.v10_0.api import GLPIApiClient
from glpipci.commons.decorators import debug_print_params
from dataclasses import dataclass
from typing import Optional


CONTEXT_URI_PATTERN = "/TicketTask"


@dataclass
class GlpiTicketTasksBodyItem:
    tickets_id: str | int
    content: str
    taskcategories_id: Optional[str | int] = None
    date: Optional[str | int] = None
    users_id: Optional[str | int] = None
    users_id_editor: Optional[str | int] = None
    is_private: Optional[str | int] = None
    actiontime: Optional[str | int] = None
    begin: Optional[str | int] = None
    end: Optional[str | int] = None
    state: Optional[str | int] = None
    users_id_tech: Optional[str | int] = None
    groups_id_tech: Optional[str | int] = None
    date_mod: Optional[str | int] = None
    date_creation: Optional[str | int] = None
    tasktemplates_id: Optional[str | int] = None
    timeline_position: Optional[str | int] = None
    sourceitems_id: Optional[str | int] = None
    sourceof_items_id: Optional[str | int] = None


class GlpiTicketTasks:
    """
    Class to manage TicketTask resource directly.
    """
    def __init__(self, api_client: GLPIApiClient) -> None:
        self.api_client = api_client
        self.api_object_endpoint = CONTEXT_URI_PATTERN

    @debug_print_params
    def get_ticket_tasks(self) -> list[dict]:
        """
        Get the list of all TicketTask objects.
        """
        endpoint = self.api_client.api_server_endpoint + self.api_object_endpoint
        response = self.api_client.make_get(endpoint)
        if 200 <= response.status_code <= 299:
            return response.json()
        else:
            raise Exception(f"Error: {response.status_code} - {response.text}")

    @debug_print_params
    def add_ticket_task(self, ticket_task: dict) -> dict:
        """
        Create a new TicketTask.

        :param ticket_task: dict with required keys 'tickets_id' and 'content', plus optional fields.
        """
        endpoint = self.api_client.api_server_endpoint + self.api_object_endpoint
        response = self.api_client.make_post(endpoint, json=ticket_task)
        if 200 <= response.status_code <= 299:
            return response.json()
        else:
            self.api_client.request_error_handler(response.status_code, response.text)
