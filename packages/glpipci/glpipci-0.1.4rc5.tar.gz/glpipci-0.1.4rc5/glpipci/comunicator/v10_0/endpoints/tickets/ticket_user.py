from dataclasses import dataclass
from typing import Optional
from glpipci.comunicator.v10_0.endpoints.tickets.core import GlpiTicket
from glpipci.commons.decorators import debug_print_params

CONTEXT_URI_PATTERN = "/Ticket_User"


@dataclass
class GlpiTicketTicketUserBodyItem:
    tickets_id: str | int
    users_id: Optional[str | int] = None
    user_type: Optional[str | int] = 1
    use_notification: Optional[str | int] = 1
    alternative_email: Optional[str] = None


class GlpiTicketTicketUser:

    def __init__(self, ticket_instance: GlpiTicket) -> None:
        self.ticket_instance = ticket_instance
        self.ticket_user_elements = []

    @debug_print_params
    def get_ticket_users(self) -> list[dict] | None:
        """
        Get the list of ITIL followups for a ticket.
        """
        endpoint = self.ticket_instance.api_object_endpoint + CONTEXT_URI_PATTERN
        response = self.ticket_instance.api_client.make_get(
            endpoint,
            headers=self.ticket_instance.api_client.auth_headers
        )
        if 200 <= response.status_code <= 299 :
            return response.json()
        else:
            self.ticket_instance.api_client.request_error_handler(
                status_code=response.status_code,
                message=response.text
            )

    @debug_print_params
    def add_ticket_users(self, ticket_users_list: list[GlpiTicketTicketUserBodyItem] | GlpiTicketTicketUserBodyItem) -> dict:
        """
        Add a new ITIL followup for a ticket.

        TODO: Implement to change from dict to specific class
        """
        endpoint = self.ticket_instance.api_object_endpoint + CONTEXT_URI_PATTERN
        response = self.ticket_instance.api_client.make_post(
            endpoint,
            headers=self.ticket_instance.api_client.auth_headers,
            json={
                "input": ticket_users_list
            }
        )
        if 200 <= response.status_code <= 299 :
            return response.json()
        else:
            self.ticket_instance.api_client.request_error_handler(
                status_code=response.status_code,
                message=response.text
            )
