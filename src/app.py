from src.graph import build_graph


def run_graph_test(graph, user_input: str, thread_id: str):
    config = {"configurable": {"thread_id": thread_id}}

    initial_state = {
        "user_input": user_input,
        "route": "",
        "output": "",
        "messages": [],
    }

    result = graph.invoke(initial_state, config=config)

    print("=" * 80)
    print(f"THREAD ID: {thread_id}")
    print(f"INPUT: {user_input}")
    print(f"ROUTE: {result.get('route')}")
    print("\nOUTPUT:")
    print(result.get("output"))
    print("=" * 80)
    print()

    return result


def main():
    graph = build_graph()

    run_graph_test(
        graph,
        user_input="Write a detailed SEO blog post about AI in healthcare.",
        thread_id="seo-test",
    )

    run_graph_test(
        graph,
        user_input="Write a short X post announcing a new AI productivity app.",
        thread_id="x-test",
    )

    run_graph_test(
        graph,
        user_input="Hi, what can you help me with?",
        thread_id="general-test",
    )

    run_graph_test(
        graph,
        user_input="Write a short X post about password managers.",
        thread_id="memory-test",
    )

    run_graph_test(
        graph,
        user_input="What was my recent ask?",
        thread_id="memory-test",
    )


if __name__ == "__main__":
    main()