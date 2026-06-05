from langchain_core.messages import AIMessage, SystemMessage
from langgraph.prebuilt import ToolNode

from src.prompts import (
    GENERAL_INSTRUCTIONS,
    SEO_BLOG_INSTRUCTIONS,
    X_BLOG_INSTRUCTIONS,
)
from src.state import CopyWriter
from src.tools import SEO_TOOLS, X_TOOLS


def make_seo_blog_writer_node(llm):
    blog_writer_with_tools = llm.bind_tools(SEO_TOOLS)

    def seo_blog_writer_node(state: CopyWriter):
        history = state.get("messages", [])

        messages = [
            SystemMessage(content=SEO_BLOG_INSTRUCTIONS),
            *history,
        ]

        result = blog_writer_with_tools.invoke(messages)

        if result.tool_calls:
            return {"messages": [result]}

        return {
            "output": result.content,
            "messages": [AIMessage(content=result.content)],
        }

    return seo_blog_writer_node


def make_x_blog_writer_node(llm):
    x_writer_with_tools = llm.bind_tools(X_TOOLS)

    def x_blog_writer_node(state: CopyWriter):
        history = state.get("messages", [])

        messages = [
            SystemMessage(content=X_BLOG_INSTRUCTIONS),
            *history,
        ]

        result = x_writer_with_tools.invoke(messages)

        if result.tool_calls:
            return {"messages": [result]}

        return {
            "output": result.content,
            "messages": [AIMessage(content=result.content)],
        }

    return x_blog_writer_node


def make_general_node(llm):
    def general_node(state: CopyWriter):
        history = state.get("messages", [])

        messages = [
            SystemMessage(content=GENERAL_INSTRUCTIONS),
            *history,
        ]

        result = llm.invoke(messages)

        return {
            "output": result.content,
            "messages": [AIMessage(content=result.content)],
        }

    return general_node


seo_tool_node = ToolNode(SEO_TOOLS)
x_tool_node = ToolNode(X_TOOLS)


def seo_should_continue(state: CopyWriter) -> str:
    last_message = state["messages"][-1]

    if getattr(last_message, "tool_calls", None):
        return "seo_tools"

    return "end"


def x_should_continue(state: CopyWriter) -> str:
    last_message = state["messages"][-1]

    if getattr(last_message, "tool_calls", None):
        return "x_tools"

    return "end"