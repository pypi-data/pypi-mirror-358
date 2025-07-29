import abc
from abc import (
    ABC,
    abstractmethod,
)
from datetime import (
    datetime,
    timedelta,
)

from eclypse_core.workflow.events.event import EclypseEvent

class Trigger(ABC, metaclass=abc.ABCMeta):
    """Base class for triggers."""

    @abstractmethod
    def trigger(self, _: EclypseEvent | None = None) -> bool:
        """Check if the trigger should fire.

        Args:
            trigger_event (Optional[EclypseEvent]): The event that triggered the check.

        Returns:
            bool: True if the trigger should fire, False otherwise.
        """

    def init(self) -> None:
        """Prepare the trigger for use.

        This method can be overridden in subclasses to perform any necessary
        initialization before the trigger is used.
        """

    def reset(self) -> None:
        """Reset the trigger state.

        This method can be overridden in subclasses to reset any internal state of the
        trigger.
        """

class PeriodicTrigger(Trigger):
    """A trigger that fires periodically."""

    last_exec_time: datetime | None
    first_trigger: bool
    def __init__(self, trigger_every_ms: float = 0.0) -> None:
        """Initialize the periodic trigger.

        Args:
            trigger_every_ms (float): The interval in milliseconds at which the trigger
                should fire. Defaults to 0.0, which means it will not trigger.
        """

    def trigger(self, _: EclypseEvent | None = None) -> bool:
        """Check if the trigger should fire based on its interval."""

    def reset(self) -> None:
        """Reset the trigger state."""

class ScheduledTrigger(Trigger):
    """A trigger that fires at scheduled times."""

    def __init__(
        self, scheduled_timedelta: timedelta | list[timedelta] | None = None
    ) -> None:
        """Initialize the scheduled trigger.

        Args:
            scheduled_times (Optional[Union[timedelta, List[timedelta]]]):
                Time(s) when the trigger should fire.
                Defaults to None, which means no scheduled times.
        """

    def init(self) -> None:
        """Prepare the trigger by setting the initial time."""

    def trigger(self, _: EclypseEvent | None = None) -> bool:
        """Return True if the current call count matches a scheduled time."""

class RandomTrigger(Trigger):
    """A trigger that fires randomly."""

    def __init__(self, probability: float = 0.5, seed: int | None = None) -> None:
        """Initialize the random trigger.

        Args:
            probability (float): The probability of the trigger firing. Defaults to 0.5.
            seed (Optional[int]): An optional seed for the random number generator.
                Defaults to None, which means that the random number generator gets
                the RND_SEED from the simulator.
        """

    def init(self) -> None:
        """Initialize the random number generator."""

    def trigger(self, _: EclypseEvent | None = None) -> bool:
        """Check if the trigger should fire based on its probability."""
