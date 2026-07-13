from src.tools import research_tool, internet_search_tool, SEO_TOOLS, X_TOOLS


def test_research_tool_returns_topic_specific_notes():
    result = research_tool.invoke("AI in healthcare")

    assert "AI in healthcare" in result
    assert "Research notes" in result
    assert "Suggested structure" in result


def test_internet_search_tool_returns_query_specific_insights():
    result = internet_search_tool.invoke("password managers")

    assert "password managers" in result
    assert "SEO keywords" in result
    assert "Social ideas" in result


def test_seo_tools_include_research_and_search():
    tool_names = {tool.name for tool in SEO_TOOLS}

    assert "research_tool" in tool_names
    assert "internet_search_tool" in tool_names


def test_x_tools_only_include_search_tool():
    tool_names = {tool.name for tool in X_TOOLS}

    assert tool_names == {"internet_search_tool"}