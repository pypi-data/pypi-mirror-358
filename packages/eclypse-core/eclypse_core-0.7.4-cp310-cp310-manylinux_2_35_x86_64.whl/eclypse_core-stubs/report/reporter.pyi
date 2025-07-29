import abc
from abc import (
    ABC,
    abstractmethod,
)
from pathlib import Path
from typing import Any

from eclypse_core.workflow.events.event import EclypseEvent

class Reporter(ABC, metaclass=abc.ABCMeta):
    """Abstract class to report the simulation metrics.

    It provides the interface for the simulation reporters.
    """

    def __init__(self, report_path: str | Path) -> None:
        """Create a new Reporter.

        Args:
            report_path (Union[str, Path]): The path to save the reports.
        """

    async def init(self) -> None:
        """Perform any preparation logic (file creation, folder setup, headers, etc)."""

    @abstractmethod
    async def write(self, callback_type: str, data: Any):
        """Write a batch of buffered data to the destination (file, db, etc)."""

    @abstractmethod
    def report(
        self, event_name: str, event_idx: int, callback: EclypseEvent
    ) -> list[Any]:
        """Report the simulation reportable callbacks.

        Args:
            event_name (str): The name of the event.
            event_idx (int): The index of the event trigger (tick).
            executed (EclypseEvent): The executed event.

        Returns:
            List[Any]: The list of entries to be written.
        """

    def dfs_data(self, data: Any) -> list:
        """Perform DFS on the nested dictionary and build paths (concatenated keys) as
        strings.

        Args:
            data (Any): The data to traverse.

        Returns:
            List: The list of paths.
        """
