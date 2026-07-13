from langchain_core.messages import AIMessage, HumanMessage

from src.router import make_router_node, route_decision


class FakeRouterLLM:
    def __init__(self, response: str):
        self.response = response
        self.last_messages = None

    def invoke(self, messages):
        self.last_messages = messages
        return AIMessage(content=self.response)


def test_router_accepts_valid_route():
    llm = FakeRouterLLM("seo_blog_writer")
    router_node = make_router_node(llm)

    state = {
        "user_input": "Write a detailed blog post about AI security.",
        "route": "",
        "output": "",
        "messages": [],
    }

    result = router_node(state)

    assert result["route"] == "seo_blog_writer"
    assert len(result["messages"]) == 1
    assert isinstance(result["messages"][0], HumanMessage)
    assert result["messages"][0].content == state["user_input"]


def test_router_normalizes_whitespace_and_case():
    llm = FakeRouterLLM("  X_BLOG_WRITER\n")
    router_node = make_router_node(llm)

    state = {
        "user_input": "Write a short X post about password managers.",
        "route": "",
        "output": "",
        "messages": [],
    }

    result = router_node(state)

    assert result["route"] == "x_blog_writer"


def test_router_falls_back_to_general_on_invalid_route():
    llm = FakeRouterLLM("I think this should go to the blog writer.")
    router_node = make_router_node(llm)

    state = {
        "user_input": "Write something.",
        "route": "",
        "output": "",
        "messages": [],
    }

    result = router_node(state)

    assert result["route"] == "general"


def test_route_decision_returns_existing_route():
    state = {
        "user_input": "Write a tweet.",
        "route": "x_blog_writer",
        "output": "",
        "messages": [],
    }

    assert route_decision(state) == "x_blog_writer"


def test_route_decision_defaults_to_general_if_missing():
    state = {
        "user_input": "Hello",
        "output": "",
        "messages": [],
    }

    assert route_decision(state) == "general"
