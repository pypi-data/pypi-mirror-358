from typing import Any

from ray import ObjectRef
from ray.actor import ActorHandle

class RayInterface:
    """A simple interface to customise and configure the Ray backend used by Eclypse."""

    def __init__(self) -> None:
        """Initialize the RayInterface."""

    def init(self, runtime_env: dict[str, Any]):
        """Initialize the Ray backend with the given runtime environment.

        Args:
            runtime_env (Dict[str, Any]): The runtime environment to use for Ray.
        """

    def get(self, obj: ObjectRef) -> Any:
        """Get the result of a Ray task or a list of Ray tasks, ignoring any output to
        stderr.

        Args:
            Any: The Ray task or list of Ray tasks.

        Returns:
            Union[Any, List[Any]]: The result of the Ray task or list of Ray tasks.
        """

    def put(self, obj: Any) -> ObjectRef:
        """Put an object into the Ray object store.

        Args:
            obj (Any): The object to put into the Ray object store.

        Returns:
            ObjectRef: A reference to the object in the Ray object store.
        """

    def get_actor(self, name: str) -> ActorHandle:
        """Get a Ray actor by its name.

        Args:
            name (str): The name of the Ray actor.

        Returns:
            ActorHandle: The Ray actor handle.
        """

    def remote(self, fn_or_class):
        """Handle the remote execution of a function or class.
        Args:
            fn_or_class: The function or class to execute remotely.

        Returns:
            ObjectRef: A reference to the remote execution result.
        """

    @property
    def backend(self):
        """Get the Ray backend. If the backend is not initialised, it will attempt to
        import Ray and set ithe backend.

        Returns:
            Any: The Ray backend.

        Raises:
            ImportError: If Ray cannot be imported, indicating that
                the required dependencies are missing.
        """
