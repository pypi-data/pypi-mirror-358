from typing import Literal

from eclypse_core.utils._logging import Logger
from eclypse_core.workflow.events.event import EclypseEvent
from eclypse_core.workflow.triggers import Trigger

class TriggerBucket:
    """A class to represent a bucket of triggers for an event."""

    event: EclypseEvent | None
    def __init__(
        self,
        triggers: Trigger | list[Trigger] | None = None,
        condition: Literal["any", "all"] = "any",
        max_triggers: int = ...,
    ) -> None:
        """Initialize the trigger.

        Args:
            triggers (Optional[Union[Trigger, List[Trigger]]]): A single trigger or
                a list of triggers that can activate the event. Defaults to None.
            condition (str): The condition for the triggers to fire the event. If "any",
                the event fires if any trigger is active. If "all", the event fires only
                if all triggers are active. Defaults to "any".
            max_triggers (Optional[int]): The maximum number of times the trigger
                can be called. Defaults to `no limit`.
        """

    def init(self) -> None:
        """Prepare the trigger for use.

        This method can be overridden in subclasses to perform any necessary
        initialization before the trigger is used.
        """

    def trigger(self, trigger_event: EclypseEvent | None = None) -> bool:
        """Check if the trigger should fire.

        Returns:
            bool: True if the trigger should fire, False otherwise.
        """

    def reset(self) -> None:
        """Reset the trigger state."""

    @property
    def logger(self) -> Logger:
        """Get the logger for the event.

        Returns:
            Logger: The logger for the event if it exists, otherwise None.
        """
