from pathlib import Path

from eclypse_core.graph import (
    Application,
    Infrastructure,
)
from eclypse_core.placement.strategy import PlacementStrategy
from eclypse_core.remote.bootstrap import RemoteBootstrap
from eclypse_core.simulation._simulator.local import (
    SimulationState,
    Simulator,
)
from eclypse_core.simulation._simulator.remote import RemoteSimulator
from eclypse_core.simulation.config import SimulationConfig
from eclypse_core.utils._logging import Logger

class Simulation:
    """A Simulation abstracts the deployment of applications on an infrastructure."""

    remote: RemoteBootstrap | None
    simulator: Simulator | RemoteSimulator
    def __init__(
        self,
        infrastructure: Infrastructure,
        simulation_config: SimulationConfig | None = None,
    ) -> None:
        """Create a new Simulation. It instantiates a Simulator or RemoteSimulator based
        on the simulation configuration, than can be either local or remote.

        It also registers an exit handler to ensure the simulation is properly closed
        and the reporting (if enabled) is done properly.

        Args:
            infrastructure (Infrastructure): The infrastructure to simulate.
            simulation_config (SimulationConfig, optional): The configuration of the simulation. Defaults to SimulationConfig().

        Raises:
            ValueError: If all services do not have a logic when including them in a remote
                simulation.
        """

    def start(self) -> None:
        """Start the simulation."""

    def trigger(self, event_name: str):
        """Fire an event in the simulation.

        Args:
            event (str): The event to fire.
        """

    def step(self):
        """Run a single step of the simulation, by triggering the DRIVING_EVENT, thus
        the 'enact' event."""

    def stop(self, blocking: bool = True):
        """Stop the simulation."""

    def wait(self, timeout: float | None = None):
        """Wait for the simulation to finish.

        This method is blocking and will wait until the simulation is finished. It can
        be interrupted by pressing `Ctrl+C`.
        """

    def register(
        self,
        application: Application,
        placement_strategy: PlacementStrategy | None = None,
    ):
        """Include an application in the simulation.

        Args:
            application (Application): The application to include.
            placement_strategy (PlacementStrategy): The placement strategy to use to place the application on the infrastructure.

        Raises:
            ValueError: If all services do not have a logic when including them in a remote simulation.
        """

    @property
    def applications(self) -> dict[str, Application]:
        """Get the applications in the simulation.

        Returns:
            Dict[str, Application]: The applications in the simulation.
        """

    @property
    def logger(self) -> Logger:
        """Get the logger of the simulation.

        Returns:
            Logger: The logger of the simulation.
        """

    @property
    def status(self) -> SimulationState:
        """Check if the simulation is stopped.

        Returns:
            bool: True if the simulation is stopped. False otherwise.
        """

    @property
    def path(self) -> Path:
        """Get the path to the simulation configuration.

        Returns:
            Path: The path to the simulation configuration.
        """
