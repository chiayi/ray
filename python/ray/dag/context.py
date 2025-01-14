from dataclasses import dataclass
import os
import threading
from typing import Optional
from ray.util.annotations import DeveloperAPI

# The context singleton on this process.
_default_context: "Optional[DAGContext]" = None
_context_lock = threading.Lock()

DEFAULT_SUBMIT_TIMEOUT_S = int(os.environ.get("RAY_CGRAPH_submit_timeout", 10))
DEFAULT_GET_TIMEOUT_S = int(os.environ.get("RAY_CGRAPH_get_timeout", 10))
DEFAULT_TEARDOWN_TIMEOUT_S = int(os.environ.get("RAY_CGRAPH_teardown_timeout", 30))
# Default buffer size is 1MB.
DEFAULT_BUFFER_SIZE_BYTES = int(os.environ.get("RAY_CGRAPH_buffer_size_bytes", 1e6))
# Default asyncio_max_queue_size is 0, which means no limit.
DEFAULT_ASYNCIO_MAX_QUEUE_SIZE = int(
    os.environ.get("RAY_CGRAPH_asyncio_max_queue_size", 0)
)
# The default max_buffered_results is 1000, and the default buffer size is 1 MB.
# The maximum memory usage for buffered results is 1 GB.
DEFAULT_MAX_BUFFERED_RESULTS = int(
    os.environ.get("RAY_CGRAPH_max_buffered_results", 1000)
)
# The default number of in-flight executions that can be submitted before consuming the
# output.
DEFAULT_MAX_INFLIGHT_EXECUTIONS = int(
    os.environ.get("RAY_CGRAPH_max_inflight_executions", 10)
)

DEFAULT_OVERLAP_GPU_COMMUNICATION = bool(
    os.environ.get("RAY_CGRAPH_overlap_gpu_communication", 0)
)


@DeveloperAPI
@dataclass
class DAGContext:
    """Global settings for Ray DAG.

    You can configure parameters in the DAGContext by setting the environment
    variables, `RAY_CGRAPH_<param>` (e.g., `RAY_CGRAPH_buffer_size_bytes`) or Python.

    Examples:
        >>> from ray.dag import DAGContext
        >>> DAGContext.get_current().buffer_size_bytes
        1000000
        >>> DAGContext.get_current().buffer_size_bytes = 500
        >>> DAGContext.get_current().buffer_size_bytes
        500

    Args:
        submit_timeout: The maximum time in seconds to wait for execute()
            calls.
        get_timeout: The maximum time in seconds to wait when retrieving
            a result from the DAG during `ray.get`. This should be set to a
            value higher than the expected time to execute the entire DAG.
        teardown_timeout: The maximum time in seconds to wait for the DAG to
            cleanly shut down.
        buffer_size_bytes: The initial buffer size in bytes for messages
            that can be passed between tasks in the DAG. The buffers will
            be automatically resized if larger messages are written to the
            channel.
        asyncio_max_queue_size: The max queue size for the async execution.
            It is only used when enable_asyncio=True.
        max_buffered_results: The maximum number of execution results that
            are allowed to be buffered. Setting a higher value allows more
            DAGs to be executed before `ray.get()` must be called but also
            increases the memory usage. Note that if the number of ongoing
            executions is beyond the DAG capacity, the new execution would
            be blocked in the first place; therefore, this limit is only
            enforced when it is smaller than the DAG capacity.
        max_inflight_executions: The maximum number of in-flight executions that
            can be submitted via `execute` or `execute_async` before consuming
            the output using `ray.get()`. If the caller submits more executions,
            `RayCgraphCapacityExceeded` is raised.
        overlap_gpu_communication: (experimental) Whether to overlap GPU
            communication with computation during DAG execution. If True, the
            communication and computation can be overlapped, which can improve
            the performance of the DAG execution.
    """

    submit_timeout: int = DEFAULT_SUBMIT_TIMEOUT_S
    get_timeout: int = DEFAULT_GET_TIMEOUT_S
    teardown_timeout: int = DEFAULT_TEARDOWN_TIMEOUT_S
    buffer_size_bytes: int = DEFAULT_BUFFER_SIZE_BYTES
    asyncio_max_queue_size: int = DEFAULT_ASYNCIO_MAX_QUEUE_SIZE
    max_buffered_results: int = DEFAULT_MAX_BUFFERED_RESULTS
    max_inflight_executions: int = DEFAULT_MAX_INFLIGHT_EXECUTIONS
    overlap_gpu_communication: bool = DEFAULT_OVERLAP_GPU_COMMUNICATION

    @staticmethod
    def get_current() -> "DAGContext":
        """Get or create a singleton context.

        If the context has not yet been created in this process, it will be
        initialized with default settings.
        """
        global _default_context

        with _context_lock:
            if _default_context is None:
                _default_context = DAGContext()

            return _default_context
