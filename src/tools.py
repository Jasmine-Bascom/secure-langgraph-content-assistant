from langchain_core.tools import tool


@tool
def research_tool(topic: str) -> str:
    """
    Finds research notes, article ideas, and references for a given content topic.
    Use this when writing long-form blog posts or detailed articles.
    """
    return f"""
Research notes for: {topic}

- Key background: {topic} has practical business, technical, and social implications.
- Suggested angle: Explain the topic clearly, then discuss benefits, risks, and examples.
- Suggested structure:
  1. Introduction
  2. Why the topic matters
  3. Main benefits
  4. Risks or challenges
  5. Practical examples
  6. Conclusion
"""


@tool
def internet_search_tool(query: str) -> str:
    """
    Finds SEO keywords, search phrases, hashtags, or trending topic ideas.
    Use this for SEO blog writing and X/Twitter post generation.
    """
    return f"""
Search insights for: {query}

SEO keywords:
- {query}
- {query} trends
- {query} benefits
- {query} examples
- how {query} works

Social ideas:
- #AI
- #TechTrends
- #ContentStrategy
- #DigitalMarketing
"""


SEO_TOOLS = [research_tool, internet_search_tool]
X_TOOLS = [internet_search_tool]
