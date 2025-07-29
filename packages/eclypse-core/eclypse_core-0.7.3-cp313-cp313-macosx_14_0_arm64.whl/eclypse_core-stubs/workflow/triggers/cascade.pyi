from eclypse_core.workflow.events.event import EclypseEvent
from eclypse_core.workflow.triggers.trigger import Trigger

class CascadeTrigger(Trigger):
    """A trigger that fires based on the state of another event."""

    def __init__(self, trigger_event: str) -> None:
        """Initialize the cascade trigger.

        Args:
            trigger_event (str): The name of the event that can trigger this cascade.
        """

    def trigger(self, trigger_event: EclypseEvent | None = None) -> bool:
        """Check if the trigger should fire based on its condition."""

class PeriodicCascadeTrigger(CascadeTrigger):
    """A trigger that fires based on the state of another event at regular intervals."""

    def __init__(self, trigger_event: str, every_n_triggers: int = 1) -> None:
        """Initialize the cascade trigger.

        Args:
            trigger_event (str): The name of the event that can trigger this cascade.
            every_n_triggers (int): The number of calls to the triggering event
                required to trigger this cascade. Defaults to 1.
        """

    def trigger(self, trigger_event: EclypseEvent | None = None) -> bool:
        """Check if the trigger should fire based on its condition."""

class ScheduledCascadeTrigger(CascadeTrigger):
    """A trigger that fires based on the state of another event at scheduled times."""

    def __init__(self, trigger_event: str, scheduled_times: list[int]) -> None:
        """Initialize the cascade trigger.

        Args:
            trigger_event (str): The name of the event that can trigger this cascade.
            scheduled_times (List[int]): A list of scheduled times (in number of triggers)
                when the trigger should fire.

        Raises:
            ValueError: If scheduled_times is empty.
        """

    def trigger(self, trigger_event: EclypseEvent | None = None) -> bool:
        """Check if the trigger should fire based on its condition."""

class RandomCascadeTrigger(CascadeTrigger):
    """A trigger that fires based on the state of another event at random intervals."""

    def __init__(
        self, trigger_event: str, probability: float = 0.5, seed: int | None = None
    ) -> None:
        """Initialize the random cascade trigger.

        Args:
            trigger_event (str): The name of the event that can trigger this cascade.
            probability (float): The probability of the trigger firing when the
                triggering event occurs. Defaults to 0.5.
        """

    def init(self) -> None:
        """Initialize the random number generator."""

    def trigger(self, trigger_event: EclypseEvent | None = None) -> bool:
        """Check if the trigger should fire based on its condition."""
