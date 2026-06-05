from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, StateGraph

from src.agents import (
    make_general_node,
    make_seo_blog_writer_node,
    make_x_blog_writer_node,
    seo_should_continue,
    seo_tool_node,
    x_should_continue,
    x_tool_node,
)
from src.model import get_llm
from src.router import make_router_node, route_decision
from src.state import CopyWriter


def build_graph():
    llm = get_llm()

    graph_builder = StateGraph(CopyWriter)

    graph_builder.add_node("router", make_router_node(llm))
    graph_builder.add_node("seo_blog_writer", make_seo_blog_writer_node(llm))
    graph_builder.add_node("x_blog_writer", make_x_blog_writer_node(llm))
    graph_builder.add_node("general", make_general_node(llm))

    graph_builder.add_node("seo_tools", seo_tool_node)
    graph_builder.add_node("x_tools", x_tool_node)

    graph_builder.set_entry_point("router")

    graph_builder.add_conditional_edges(
        "router",
        route_decision,
        {
            "seo_blog_writer": "seo_blog_writer",
            "x_blog_writer": "x_blog_writer",
            "general": "general",
        },
    )

    graph_builder.add_conditional_edges(
        "seo_blog_writer",
        seo_should_continue,
        {
            "seo_tools": "seo_tools",
            "end": END,
        },
    )

    graph_builder.add_edge("seo_tools", "seo_blog_writer")

    graph_builder.add_conditional_edges(
        "x_blog_writer",
        x_should_continue,
        {
            "x_tools": "x_tools",
            "end": END,
        },
    )

    graph_builder.add_edge("x_tools", "x_blog_writer")
    graph_builder.add_edge("general", END)

    memory = MemorySaver()

    return graph_builder.compile(checkpointer=memory)