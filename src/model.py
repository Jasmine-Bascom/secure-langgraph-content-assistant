import os

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI


load_dotenv()


def get_llm():
    """
    Create the shared chat model used by the router and agents.
    """
    if not os.getenv("OPENAI_API_KEY"):
        raise RuntimeError("OPENAI_API_KEY is missing. Add it to your .env file.")

    return ChatOpenAI(
        model="gpt-4o",
        temperature=0.2,
    )