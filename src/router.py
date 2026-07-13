from langchain_core.messages import HumanMessage, SystemMessage

from src.prompts import ROUTER_INSTRUCTIONS
from src.state import CopyWriter

VALID_ROUTES = {"seo_blog_writer", "x_blog_writer", "general"}


def make_router_node(llm):
    def router_node(state: CopyWriter):
        messages = [
            SystemMessage(content=ROUTER_INSTRUCTIONS),
            HumanMessage(content=state["user_input"]),
        ]

        result = llm.invoke(messages)
        route = result.content.strip().lower()

        if route not in VALID_ROUTES:
            route = "general"

        return {
            "route": route,
            "messages": [HumanMessage(content=state["user_input"])],
        }

    return router_node


def route_decision(state: CopyWriter) -> str:
    return state.get("route", "general")
