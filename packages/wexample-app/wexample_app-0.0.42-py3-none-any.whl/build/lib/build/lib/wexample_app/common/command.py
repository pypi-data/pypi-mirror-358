from typing import Callable, Any, TYPE_CHECKING

from pydantic import BaseModel

from wexample_app.common.abstract_kernel_child import AbstractKernelChild
from wexample_app.response.null_response import NullResponse

if TYPE_CHECKING:
    from wexample_app.common.command_request import CommandRequest

if TYPE_CHECKING:
    from wexample_app.common.abstract_kernel import AbstractKernel
    from wexample_app.response.abstract_response import AbstractResponse


class Command(AbstractKernelChild, BaseModel):
    function: Callable[..., Any] = None

    def __init__(self, kernel: "AbstractKernel", **kwargs):
        BaseModel.__init__(self, **kwargs)
        AbstractKernelChild.__init__(self, kernel=kernel)

    def execute_request(self, request: "CommandRequest") -> Any:
        # Basic way to execute command.
        return self.function(
            kernel=self.kernel,
            arguments=request.arguments
        )

    def execute_request_and_normalize(self, request: "CommandRequest") -> Any:
        return self.normalize_response(
            self.execute_request(
                request=request
            )
        )

    def normalize_response(self, function_output: Any) -> "AbstractResponse":
        from wexample_app.response.abstract_response import AbstractResponse

        if isinstance(function_output, AbstractResponse):
            return function_output
        elif function_output is None:
            return NullResponse(kernel=self.kernel)

        from wexample_app.response.default_response import DefaultResponse
        return DefaultResponse(kernel=self.kernel, content=function_output)
