from langchain_core.messages import AIMessage, HumanMessage, SystemMessage

from src.agents import (
    make_general_node,
    make_seo_blog_writer_node,
    make_x_blog_writer_node,
)


class FakeLLM:
    def __init__(self, response: str):
        self.response = response
        self.last_messages = None

    def bind_tools(self, tools):
        self.bound_tools = tools
        return self

    def invoke(self, messages):
        self.last_messages = messages
        return AIMessage(content=self.response)


def make_state(user_input="Write something."):
    return {
        "user_input": user_input,
        "route": "",
        "output": "",
        "messages": [HumanMessage(content=user_input)],
    }


def test_seo_agent_prepends_system_prompt():
    llm = FakeLLM("SEO blog output")
    node = make_seo_blog_writer_node(llm)

    result = node(make_state("Write a blog post about AI security."))

    assert result["output"] == "SEO blog output"
    assert isinstance(llm.last_messages[0], SystemMessage)
    assert "seo" in llm.last_messages[0].content.lower()
    assert any(
        isinstance(message, HumanMessage) and "AI security" in message.content
        for message in llm.last_messages
    )


def test_x_agent_prepends_system_prompt():
    llm = FakeLLM("X post output")
    node = make_x_blog_writer_node(llm)

    result = node(make_state("Write an X post about password managers."))

    assert result["output"] == "X post output"
    assert isinstance(llm.last_messages[0], SystemMessage)
    assert (
        "twitter" in llm.last_messages[0].content.lower()
        or "x/" in llm.last_messages[0].content.lower()
    )
    assert any(
        isinstance(message, HumanMessage) and "password managers" in message.content
        for message in llm.last_messages
    )


def test_general_agent_uses_history_and_returns_output():
    llm = FakeLLM("You recently asked for an X post about password managers.")
    node = make_general_node(llm)

    state = {
        "user_input": "What was my recent ask?",
        "route": "general",
        "output": "",
        "messages": [
            HumanMessage(content="Write an X post about password managers."),
            AIMessage(content="Use a password manager to stay secure. #Cybersecurity"),
            HumanMessage(content="What was my recent ask?"),
        ],
    }

    result = node(state)

    assert "recently asked" in result["output"].lower()
    assert isinstance(llm.last_messages[0], SystemMessage)
    assert len(llm.last_messages) == 4
