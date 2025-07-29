from glpipci.comunicator.v10_0.endpoints.tasks.ticket_tasks import GlpiTicketTasksBodyItem
from glpipci.comunicator.v10_0.endpoints.tickets.core import GlpiTicket
from glpipci.commons.decorators import debug_print_params


CONTEXT_URI_PATTERN = "/TicketTask"


class GlpiTicketTicketTask:
    """
    Class to manage TicketTask objects as a child of a specific Ticket.
    """
    def __init__(self, ticket_instance: GlpiTicket) -> None:
        self.ticket_instance = ticket_instance

    @debug_print_params
    def get_ticket_tasks(self) -> list[dict]:
        """
        Get the list of TicketTask objects for this ticket.
        """
        endpoint = self.ticket_instance.api_object_endpoint + CONTEXT_URI_PATTERN
        return self._handler_get_tasks(endpoint)

    def _handler_get_tasks(self, endpoint: str) -> list[dict] | None:
        response = self.ticket_instance.api_client.make_get(
            endpoint,
            headers = self.ticket_instance.api_client.auth_headers
        )
        if 200 <= response.status_code <= 299:
            return response.json()
        else:
            self.ticket_instance.api_client.request_error_handler(response.status_code, response.text)

    @debug_print_params
    def add_ticket_task(self, ticket_tasks: list[GlpiTicketTasksBodyItem] | GlpiTicketTasksBodyItem) -> dict:
        """
        Add a new TicketTask to this ticket.

        :param ticket_tasks: list of GlpiTicketTasksBodyItem or GlpiTicketTasksBodyItem with required keys 'tickets_id'
            and 'content', plus optional fields.
        """
        endpoint = self.ticket_instance.api_object_endpoint + CONTEXT_URI_PATTERN
        response = self.ticket_instance.api_client.make_post(
            endpoint,
            json={
                "input": ticket_tasks
            }
        )
        if 200 <= response.status_code <= 299:
            return response.json()
        else:
            self.ticket_instance.api_client.request_error_handler(
                status_code=response.status_code,
                message=response.text
            )
