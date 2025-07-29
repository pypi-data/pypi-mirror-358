from pathlib import Path
from typing import Literal

from eclypse_core.remote.bootstrap import RemoteBootstrap
from eclypse_core.report.reporter import Reporter
from eclypse_core.utils._logging import Logger
from eclypse_core.utils.types import LogLevel
from eclypse_core.workflow.events import EclypseEvent

class SimulationConfig(dict):
    """The SimulationConfig is a dictionary-like class that stores the configuration of
    a simulation."""

    def __init__(
        self,
        tick_every_ms: Literal["manual", "auto"] | float | None = "manual",
        timeout: float | None = None,
        max_ticks: int | None = None,
        reporters: dict[str, type[Reporter]] | None = None,
        report_chunk_size: int = 1,
        events: list[EclypseEvent] | None = None,
        incremental_mapping_phase: bool = True,
        seed: int | None = None,
        path: str | None = None,
        log_to_file: bool = False,
        log_level: LogLevel = "ECLYPSE",
        remote: bool | RemoteBootstrap = False,
    ) -> None:
        """Initializes a new SimulationConfig object.

        Args:
            tick_every_ms (Optional[float], optional): The time in milliseconds between each tick. Defaults to None.
            timeout (Optional[float], optional): The maximum time the simulation can run. Defaults to None.
            max_ticks (Optional[int], optional): The number of iterations the simulation will run. Defaults to None.
            reporters (Optional[Dict[str, Type[Reporter]]], optional): The list of reporters that will be used for the final simulation report. Defaults to None.
            report_chunk_size (int, optional): The size of the chunks in which the report will be generated. Defaults to 1 (each event reported immediately).
            events (Optional[List[Callable]], optional): The list of events that will be triggered in the simulation. Defaults to None.
            incremental_mapping_phase (bool, optional): Whether the mapping phase will be incremental. Defaults to True.
            remote (bool, optional): Whether the simulation is local or remote. Defaults to False.
            seed (Optional[int], optional): The seed used to set the randomicity of the simulation. Defaults to None.
            path (Optional[str], optional): The path where the simulation will be stored. Defaults to None.
            log_to_file (bool, optional): Whether the log should be written to a file. Defaults to False.
            log_level (LogLevel, optional): The log level. Defaults to "ECLYPSE".
            remote (Union[bool, RemoteBootstrap], optional): Whether the simulation is local or remote. A RemoteBootstrap object can be passed to configure the remote nodes. Defaults to False.
        """

    @property
    def max_ticks(self) -> int | None:
        """Returns the number of iterations the simulation will run.

        Returns:
            Optional[int]: The number of iterations, if it is set. None otherwise.
        """

    @property
    def timeout(self) -> float | None:
        """Returns the maximum time the simulation can run.

        Returns:
            Optional[float]: The timeout in seconds, if it is set. None otherwise.
        """

    @property
    def tick_every_ms(self) -> float | None:
        """Returns the time between each tick.

        Returns:
            float: The time in milliseconds between each tick.
        """

    @property
    def seed(self) -> int | None:
        """Returns the seed used to set the randomicity of the simulation.

        Returns:
            Optional[int]: The seed, if it is set. None otherwise.
        """

    @property
    def incremental_mapping_phase(self) -> bool:
        """Returns whether the simulator will perform the mapping phase incrementally or
        in batch.

        Returns:
            bool: True if the mapping phase is incremental. False otherwise (batch).
        """

    @property
    def events(self) -> list[EclypseEvent]:
        """Returns the list of events that will be triggered in the simulation.

        Returns:
            List[EclypseEvent]: The list of events.
        """

    @property
    def path(self) -> Path:
        """Returns the path where the simulation will be stored.

        Returns:
            Path: The path where the simulation will be stored.
        """

    @property
    def log_level(self) -> LogLevel:
        """Returns the log level.

        Returns:
            LogLevel: The log level.
        """

    @property
    def log_to_file(self) -> bool:
        """Returns whether the log should be written to a file.

        Returns:
            bool: True if the log should be written to a file. False otherwise.
        """

    @property
    def report_chunk_size(self) -> int:
        """Returns the size of the chunks in which the report will be generated.

        Returns:
            int: The size of the chunks.
        """

    @property
    def reporters(self) -> dict[str, type[Reporter]]:
        """Returns the list of reporters that will be used for the final simulation
        report.

        Returns:
            Dict[str, Type[Reporter]]: The list of reporters.
        """

    @property
    def remote(self) -> RemoteBootstrap | None:
        """Returns whether the simulation is local or remote.

        Returns:
            Union[bool, RemoteBootstrap]: True if the simulation is remote. False otherwise.
        """

    @property
    def logger(self) -> Logger:
        """Returns the logger configuration for the simulation.

        Returns:
            str: The logger configuration.
        """

    def __dict__(self): ...
