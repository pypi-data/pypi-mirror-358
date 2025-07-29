from typing import (
    Any,
    Callable,
    Literal,
)

from eclypse_core.utils.types import (
    ActivatesOnType,
    EventType,
)
from eclypse_core.workflow.triggers.trigger import Trigger

from .event import EclypseEvent

class EventWrapper(EclypseEvent):
    """Class to wrap an event function into a class that can be managed by the
    Simulator."""

    def __init__(
        self,
        event_fn: Callable,
        name: str,
        triggers: list[Trigger],
        activates_on: ActivatesOnType | None = None,
        event_type: EventType | None = None,
        trigger_every_ms: float | None = None,
        max_triggers: int = ...,
        trigger_condition: Literal["any", "all"] = "any",
        is_callback: bool = False,
        report: str | list[str] | None = None,
        remote: bool = False,
        verbose: bool = False,
    ) -> None:
        """Initializes the EventWrapper.

        Args:
            event_fn (Callable): The function to wrap as an event.
            name (str): The name of the event.
            triggers (List[Trigger]): The list of triggers that will trigger the event.
            activates_on (Optional[ActivatesOnType], optional): The conditions that will
                trigger the metric. Defaults to None.
            event_type (Optional[EventType], optional): The type of the event. Defaults to None.
            trigger_every_ms (Optional[float], optional): The time in milliseconds between
                each trigger of the event. Defaults to None.
            max_triggers (Optional[int], optional): The maximum number of times the event
                can be triggered. Defaults to None.
            trigger_condition (Optional[str], optional): The condition for the triggers to fire the
                event. Defaults to "any".
            is_callback (bool, optional): Whether the event is a callback. Defaults to False.
            report (Optional[Union[str, List[str]]], optional): The type of report to generate
                for the event. Defaults to None.
            remote (bool, optional): Whether the event is remote. Defaults to False.
            verbose (bool, optional): Whether to enable verbose logging. Defaults to False.
        """

    def __call__(self, *args, **kwargs) -> dict[str, Any]: ...
