from logging import Logger as NativeLogger
from typing import Callable, Optional

from core_infinity_stones.errors.base_error import HttpError
from core_infinity_stones.logging.schemas import (
    ErrorEvent,
    Event,
    EventType,
    EventWithTracesDetails,
    TracingDetails,
)
import random


class Logger:
    def __init__(
        self,
        service_name: str,
        tracing_details_resolver: Callable[[], TracingDetails],
        logger: NativeLogger,
        url: Optional[str] = None,
        user_agent: Optional[str] = None,
        event_codes_to_sampling_percentages_map: Optional[dict[str, int]] = None,
    ):
        """
        Initialize the Logger instance.

        Args:
            service_name (str): The name of the service.

            tracing_details_resolver (Callable[[], TracingDetails]): A callable that returns tracing details
                for the current request or context.

            logger (NativeLogger): The logger instance to use for logging events.

            url (Optional[str]): The URL of the service, if applicable.

            user_agent (Optional[str]): The user agent string, if applicable.

            event_codes_to_sampling_percentages_map (Optional[dict[str, int]]): A mapping of event
                codes to their sampling percentages.
                This is a dictionary where keys are event codes and values are integers between 0 and 100,
                representing the probability of logging the specified event.
                If None, all events will be logged with 100% sampling.
                If an event code is not present in the map, it will default to 100% sampling.
        """
        self.service_name = service_name
        self.tracing_details_resolver = tracing_details_resolver
        self.logger = logger
        self.url = url
        self.user_agent = user_agent
        self.event_codes_to_sampling_percentages_map = (
            event_codes_to_sampling_percentages_map
        )

    def info(self, event: Event) -> None:
        if not self._should_log_based_on_sampling_percentage(event.code):
            return

        tracing_details = self.tracing_details_resolver()

        event_with_tracing_details = EventWithTracesDetails.from_event(
            event,
            tracing_details,
            type=EventType.INFO,
            service=self.service_name,
            url=self.url,
            user_agent=self.user_agent,
        )

        self.logger.info(event_with_tracing_details.model_dump(mode="json"))

    def warning(self, event: Event) -> None:
        if not self._should_log_based_on_sampling_percentage(event.code):
            return

        tracing_details = self.tracing_details_resolver()

        event_with_tracing_details = EventWithTracesDetails.from_event(
            event,
            tracing_details,
            type=EventType.WARNING,
            service=self.service_name,
            url=self.url,
            user_agent=self.user_agent,
        )

        self.logger.info(event_with_tracing_details.model_dump(mode="json"))

    def error(self, error: HttpError) -> None:
        event_code = error.debug_details.debug_code

        if not self._should_log_based_on_sampling_percentage(event_code):
            return

        tracing_details = self.tracing_details_resolver()

        self.logger.error(
            ErrorEvent(
                trace_id=tracing_details.trace_id,
                span_id=tracing_details.span_id,
                code=event_code,
                type=EventType.ERROR,
                service=self.service_name,
                message=error.debug_details.debug_message,
                details=error.debug_details.debug_details,
                severity=error.debug_details.severity,
                occurred_while=error.debug_details.occurred_while,
                caused_by=error.debug_details.caused_by,
                status_code=error.public_details.status_code,
                public_code=error.public_details.code,
                public_message=error.public_details.message,
                public_details=error.public_details.details,
            ).model_dump(mode="json")
        )
    
    def _should_log_based_on_sampling_percentage(self, event_code: str) -> bool:
        """
        Determines whether an event should be logged based on its code and the configured sampling percentages.
        """

        if not self.event_codes_to_sampling_percentages_map:
            return True

        sampling_percentage = self.event_codes_to_sampling_percentages_map.get(event_code, 100)

        if sampling_percentage <= 0:
            return False

        if sampling_percentage >= 100:
            return True

        return random.randint(0, 100) < sampling_percentage