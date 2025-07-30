"""Tool for asking human input."""

from typing import Callable, Any

from pydantic import Field

from napari_chatgpt.omega.tools.async_base_tool import AsyncBaseTool


def _print_func(text: str) -> None:
    print("\n")
    print(text)


class HumanInputTool(AsyncBaseTool):
    """Tool that adds the capability to ask user for input."""

    name = "HumanInputTool"
    description = (
        "You can ask a human for guidance when you think you "
        "got stuck or you are not sure what to do next. "
        "The input should be a question for the human."
    )
    prompt_func: Callable[[str], None] = Field(
        default_factory=lambda: _print_func)
    input_func: Callable = Field(default_factory=lambda: input)

    def _run(self,
             *args: Any,
             **kwargs: Any
    ) -> Any:
        # Get query:
        query = self.normalise_to_string(kwargs)

        """Use the Human input tool."""
        self.prompt_func(query)
        return self.input_func()
