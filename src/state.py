from typing import Annotated, Literal
from typing_extensions import NotRequired, TypedDict

from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages


class CopyWriter(TypedDict):
    user_input: str
    route: NotRequired[Literal["seo_blog_writer", "x_blog_writer", "general"]]
    output: NotRequired[str]
    messages: Annotated[list[BaseMessage], add_messages]

    # Security metadata
    security_status: NotRequired[Literal["allow", "block", "review"]]
    security_reason: NotRequired[str]
    validation_status: NotRequired[Literal["pass", "fail", "warning"]]
    validation_reason: NotRequired[str]