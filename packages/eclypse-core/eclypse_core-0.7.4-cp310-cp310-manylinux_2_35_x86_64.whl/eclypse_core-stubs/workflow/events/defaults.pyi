from eclypse_core.workflow.events import EclypseEvent

class StartEvent(EclypseEvent):
    """The start is the beginning of the simulation."""

    def __init__(self) -> None: ...
    def __call__(self) -> None:
        """Empty by default."""

class EnactEvent(EclypseEvent):
    """The enact is the actuation of the placement decisions made by the placement
    algorithms."""

    def __init__(self) -> None: ...
    def __call__(self, _: EclypseEvent | None = None): ...

class TickEvent(EclypseEvent):
    """The tick is the step of the simulation where the applications and infrastructure
    are updated, according to the given update policies."""

    def __init__(self) -> None: ...
    def __call__(self, _: EclypseEvent): ...

class StopEvent(EclypseEvent):
    """The stop is the end of the simulation.

    Its triggers are set after the SimulationConfig is created, so it can be triggered
    by the 'tick' event, according to the parameters defined in the configuration.
    """

    def __init__(self) -> None: ...
    def __call__(self, _: EclypseEvent | None = None):
        """Empty by default."""

def get_default_events(user_events: list[EclypseEvent]) -> list[EclypseEvent]:
    """Returns the default events to be managed by the ECLYPSE simulator, which are:     'start', 'stop', 'tick', and 'enact'. If the user has defined an event with the same
    name as one of the default events, the default event is overridden.

    Args:
        user_events (List[EclypseEvent]): The user-defined events.

    Returns:

        List[EclypseEvent]: The default events.
    """
