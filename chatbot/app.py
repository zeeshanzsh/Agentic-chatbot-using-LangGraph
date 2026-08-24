import sys
import uuid
from pathlib import Path

# streamlit runs this file directly, so add the project root to sys.path
# to make the `chatbot` package importable
if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import streamlit as st
from dotenv import load_dotenv

load_dotenv()

from chatbot.graph import graph

st.set_page_config(page_title="LangGraph Chatbot", page_icon="🤖")
st.title("LangGraph Chatbot")


def new_thread():
    thread_id = str(uuid.uuid4())
    st.session_state.threads[thread_id] = {"title": "New chat", "messages": []}
    st.session_state.thread_order.insert(0, thread_id)
    st.session_state.thread_id = thread_id


# threads: dict[thread_id] -> {"title": str, "messages": [...]}
if "threads" not in st.session_state:
    st.session_state.threads = {}
    st.session_state.thread_order = []
    new_thread()

with st.sidebar:
    if st.button("➕ New chat", use_container_width=True):
        new_thread()
        st.rerun()

    st.divider()
    st.subheader("Chats")
    for thread_id in st.session_state.thread_order:
        thread = st.session_state.threads[thread_id]
        is_active = thread_id == st.session_state.thread_id
        if st.button(
            thread["title"],
            key=f"thread_{thread_id}",
            use_container_width=True,
            type="primary" if is_active else "secondary",
        ):
            st.session_state.thread_id = thread_id
            st.rerun()

    st.divider()
    st.subheader("Checkpoint history")
    st.caption(f"thread_id: {st.session_state.thread_id}")
    if st.button("Load checkpoint history"):
        config = {"configurable": {"thread_id": st.session_state.thread_id}}
        snapshots = list(graph.get_state_history(config))
        if not snapshots:
            st.write("No checkpoints saved yet for this session.")
        for snapshot in snapshots:
            checkpoint_id = snapshot.config["configurable"]["checkpoint_id"]
            with st.expander(checkpoint_id):
                for msg in snapshot.values.get("messages", []):
                    st.write(f"**{msg.type}**: {msg.content}")

current_thread = st.session_state.threads[st.session_state.thread_id]

# re-render past messages on every rerun (streamlit reruns the whole script each time)
for message in current_thread["messages"]:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

user_input = st.chat_input("Type here...")

if user_input:
    # show the user's message immediately
    current_thread["messages"].append({"role": "user", "content": user_input})
    if current_thread["title"] == "New chat":
        current_thread["title"] = user_input[:40] + ("..." if len(user_input) > 40 else "")
    with st.chat_message("user"):
        st.markdown(user_input)

    # thread_id scopes the graph's own message history to this thread
    config = {"configurable": {"thread_id": st.session_state.thread_id}}

    def stream_tokens():
        # stream_mode="messages" yields (chunk, metadata) per LLM token
        for chunk, _metadata in graph.stream(
            {"messages": [{"role": "user", "content": user_input}]},
            config,
            stream_mode="messages",
        ):
            if chunk.content:
                yield chunk.content

    with st.chat_message("assistant"):
        # only the new message is sent; the checkpointer supplies prior history
        response = st.write_stream(stream_tokens())

    current_thread["messages"].append({"role": "assistant", "content": response})
    # rerun so the sidebar re-renders with the (possibly just-updated) thread title
    st.rerun()
