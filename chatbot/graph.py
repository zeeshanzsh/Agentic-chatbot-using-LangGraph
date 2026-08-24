from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import ToolNode, tools_condition

from chatbot.state import ChatState
from chatbot.tools import math_tools

llm = ChatOpenAI(model="gpt-4o-mini")

# give the LLM the math tools' schemas so it can decide to call them
llm_with_tools = llm.bind_tools(math_tools)

checkpoint = MemorySaver()


def chat_node(state: ChatState) -> ChatState:
    # take user query form state
    message = state['messages']
    # send full history to the LLM; it replies with either a normal message
    # or a tool_calls request if it decides a math tool is needed
    response = llm_with_tools.invoke(state["messages"])
    return {"messages": [response]}


def build_graph():
    graph_builder = StateGraph(ChatState)

    # node that runs the LLM and node that actually executes any tool calls it makes
    graph_builder.add_node("chat", chat_node)
    graph_builder.add_node("tools", ToolNode(math_tools))

    graph_builder.add_edge(START, "chat")

    # tools_condition inspects the chat node's output: if it contains tool_calls,
    # route to "tools"; otherwise the conversation is done, so route to END
    graph_builder.add_conditional_edges(
        "chat",
        tools_condition,
        {"tools": "tools", END: END},
    )

    # after running the tool(s), send the results back to the LLM so it can
    # turn the raw numbers into a natural-language reply
    graph_builder.add_edge("tools", "chat")

    return graph_builder.compile(checkpointer=checkpoint)


graph = build_graph()
