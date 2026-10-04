from langchain_core.messages import (
    AIMessage,
    SystemMessage,
    ToolMessage,
)
from langgraph.prebuilt import ToolNode

from src.prompts import (
    GENERAL_INSTRUCTIONS,
    SEO_BLOG_INSTRUCTIONS,
    X_BLOG_INSTRUCTIONS,
)
from src.state import CopyWriter
from src.tools import SEO_TOOLS, X_TOOLS


# ---------------------------------------------------------
# Helpers
# ---------------------------------------------------------


def _json_safe_tool_result(
    value,
):
    """
    Convert a tool result into a value that can safely be
    stored in tester metadata and serialized to JSON.
    """

    if isinstance(
        value,
        (
            str,
            int,
            float,
            bool,
            type(None),
            dict,
            list,
        ),
    ):
        return value

    return str(value)


def _run_instrumented_tool_node(
    *,
    tool_node,
    state: CopyWriter,
) -> dict:
    """
    Execute a ToolNode and capture evidence that the tool
    actually ran.

    Requested tool calls are captured by the agent node.
    This function records the corresponding ToolMessage
    produced after execution.
    """

    raw_result = tool_node.invoke(
        state
    )

    if isinstance(
        raw_result,
        dict,
    ):
        messages = raw_result.get(
            "messages",
            [],
        )

    elif isinstance(
        raw_result,
        list,
    ):
        messages = raw_result

    else:
        messages = []

    executed = []

    for message in messages:
        if not isinstance(
            message,
            ToolMessage,
        ):
            continue

        executed.append(
            {
                "name": (
                    message.name
                    or "unknown_tool"
                ),
                "tool_call_id": (
                    message.tool_call_id
                ),
                "result": (
                    _json_safe_tool_result(
                        message.content
                    )
                ),
                "status": getattr(
                    message,
                    "status",
                    None,
                ),
            }
        )

    previous_executions = (
        state.get(
            "executed_tool_calls",
            [],
        )
        or []
    )

    return {
        "messages": messages,
        "executed_tool_calls": [
            *previous_executions,
            *executed,
        ],
    }


# ---------------------------------------------------------
# SEO blog writer
# ---------------------------------------------------------


def make_seo_blog_writer_node(
    llm,
):
    blog_writer_with_tools = (
        llm.bind_tools(
            SEO_TOOLS
        )
    )

    def seo_blog_writer_node(
        state: CopyWriter,
    ):
        history = state.get(
            "messages",
            [],
        )

        messages = [
            SystemMessage(
                content=(
                    SEO_BLOG_INSTRUCTIONS
                )
            ),
            *history,
        ]

        result = (
            blog_writer_with_tools.invoke(
                messages
            )
        )

        if result.tool_calls:
            previous_calls = (
                state.get(
                    "tool_calls",
                    [],
                )
                or []
            )

            return {
                "messages": [
                    result
                ],
                "tool_calls": [
                    *previous_calls,
                    *result.tool_calls,
                ],
            }

        return {
            "output": (
                result.content
            ),
            "messages": [
                AIMessage(
                    content=(
                        result.content
                    )
                )
            ],
        }

    return seo_blog_writer_node


# ---------------------------------------------------------
# X / Twitter writer
# ---------------------------------------------------------


def make_x_blog_writer_node(
    llm,
):
    x_writer_with_tools = (
        llm.bind_tools(
            X_TOOLS
        )
    )

    def x_blog_writer_node(
        state: CopyWriter,
    ):
        history = state.get(
            "messages",
            [],
        )

        messages = [
            SystemMessage(
                content=(
                    X_BLOG_INSTRUCTIONS
                )
            ),
            *history,
        ]

        result = (
            x_writer_with_tools.invoke(
                messages
            )
        )

        if result.tool_calls:
            previous_calls = (
                state.get(
                    "tool_calls",
                    [],
                )
                or []
            )

            return {
                "messages": [
                    result
                ],
                "tool_calls": [
                    *previous_calls,
                    *result.tool_calls,
                ],
            }

        return {
            "output": (
                result.content
            ),
            "messages": [
                AIMessage(
                    content=(
                        result.content
                    )
                )
            ],
        }

    return x_blog_writer_node


# ---------------------------------------------------------
# General assistant
# ---------------------------------------------------------


def make_general_node(
    llm,
):
    def general_node(
        state: CopyWriter,
    ):
        history = state.get(
            "messages",
            [],
        )

        messages = [
            SystemMessage(
                content=(
                    GENERAL_INSTRUCTIONS
                )
            ),
            *history,
        ]

        result = llm.invoke(
            messages
        )

        return {
            "output": (
                result.content
            ),
            "messages": [
                AIMessage(
                    content=(
                        result.content
                    )
                )
            ],
        }

    return general_node


# ---------------------------------------------------------
# Tool executors
# ---------------------------------------------------------

_seo_tool_executor = ToolNode(
    SEO_TOOLS
)

_x_tool_executor = ToolNode(
    X_TOOLS
)


def seo_tool_node(
    state: CopyWriter,
) -> dict:
    """
    Execute SEO tools and record actual execution results.
    """

    return (
        _run_instrumented_tool_node(
            tool_node=(
                _seo_tool_executor
            ),
            state=state,
        )
    )


def x_tool_node(
    state: CopyWriter,
) -> dict:
    """
    Execute X/Twitter tools and record actual execution results.
    """

    return (
        _run_instrumented_tool_node(
            tool_node=(
                _x_tool_executor
            ),
            state=state,
        )
    )


# ---------------------------------------------------------
# Conditional routing after agent calls
# ---------------------------------------------------------


def seo_should_continue(
    state: CopyWriter,
) -> str:
    last_message = (
        state["messages"][-1]
    )

    if getattr(
        last_message,
        "tool_calls",
        None,
    ):
        return "seo_tools"

    return "end"


def x_should_continue(
    state: CopyWriter,
) -> str:
    last_message = (
        state["messages"][-1]
    )

    if getattr(
        last_message,
        "tool_calls",
        None,
    ):
        return "x_tools"

    return "end"