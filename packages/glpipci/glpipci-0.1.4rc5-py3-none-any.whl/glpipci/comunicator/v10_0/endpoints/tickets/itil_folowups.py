from glpipci.comunicator.v10_0.endpoints.tickets.core import GlpiTicket
from glpipci.commons.decorators import debug_print_params

CONTEXT_URI_PATTERN = "/ITILFollowup"


class GlpiTicketItilFollowups:

    def __init__(self, ticket_instance: GlpiTicket) -> None:
        self.ticket_instance = ticket_instance

    @debug_print_params
    def get_itil_followups(self) -> list[dict]:
        """
        Get the list of ITIL followups for a ticket.
        """
        return self.__handler_get_itil_followups(
            self.ticket_instance.api_object_endpoint + CONTEXT_URI_PATTERN
        )

    @debug_print_params
    def get_last_itil_followup(self) -> list[dict]:
        return self.__handler_get_itil_followups(
            self.ticket_instance.api_object_endpoint + CONTEXT_URI_PATTERN + "/?range=0-0&order=DESC"
        )

    @debug_print_params
    def get_itil_followups_query(self, query: str) -> list[dict]:
        return self.__handler_get_itil_followups(
            self.ticket_instance.api_object_endpoint + CONTEXT_URI_PATTERN + f"/?{query}"
        )


    def __handler_get_itil_followups(self, endpoint: str):
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
    def add_itil_followup(self, itil_followup: dict) -> dict:
        """
        Add a new ITIL followup for a ticket.

        TODO: Implement to change from dict to specific class
        """
        endpoint = self.ticket_instance.api_object_endpoint + CONTEXT_URI_PATTERN
        response = self.ticket_instance.api_client.make_post(
            endpoint,
            headers=self.ticket_instance.api_client.auth_headers,
            json=itil_followup
        )
        if 200 <= response.status_code <= 299 :
            return response.json()
        else:
            self.ticket_instance.api_client.request_error_handler(
                status_code=response.status_code,
                message=response.text
            )
