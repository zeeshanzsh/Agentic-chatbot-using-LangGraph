import sys
from pathlib import Path

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from dotenv import load_dotenv

load_dotenv()

from chatbot.graph import graph


def run():
    print("Simple LangGraph chatbot. Type 'quit' to exit.")
    state = {"messages": []}
    config = {"configurable": {"thread_id": "cli-session"}}

    while True:
        user_input = input("Type here: ")
        if user_input.strip().lower() in {"quit", "exit", "bye"}:
            break

        state["messages"].append({"role": "user", "content": user_input})
        state = graph.invoke(state, config)
        print("Bot:", state["messages"][-1].content)


if __name__ == "__main__":
    run()
