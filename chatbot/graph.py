from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver

from chatbot.state import ChatState

llm = ChatOpenAI(model="gpt-4o-mini")

checkpoint = MemorySaver()


def chat_node(state: ChatState) -> ChatState:
    #take user query form state
    message = state['messages']
    #send to LLM
    response = llm.invoke(state["messages"])
    return {"messages": [response]}


def build_graph():
    graph_builder = StateGraph(ChatState)
    graph_builder.add_node("chat", chat_node)
    graph_builder.add_edge(START, "chat")
    graph_builder.add_edge("chat", END)
    return graph_builder.compile(checkpointer= checkpoint)


graph = build_graph()
