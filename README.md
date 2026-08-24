# LangGraph Chatbot

A simple chatbot built with LangGraph, LangChain, and OpenAI, with a Streamlit UI.

## Features

1. **Workflow** — the chat logic is a LangGraph `StateGraph` (see [chatbot/graph.py](chatbot/graph.py)): a `chat` node sends the conversation state to the LLM (`ChatOpenAI`), and a `tools` node executes any math tool calls the LLM requests, looping back to `chat` until it has a final answer.
2. **Math tools** — [chatbot/tools.py](chatbot/tools.py) defines `add`, `subtract`, `multiply`, `divide`, and `power` as LangChain tools. The LLM is bound to them (`llm.bind_tools`), so it can call them for arithmetic instead of computing by hand; `tools_condition` routes the graph to the `tools` node whenever a call is requested.
3. **Streaming** — responses are streamed token-by-token in the UI. The Streamlit app ([chatbot/app.py](chatbot/app.py)) calls `graph.stream(..., stream_mode="messages")` and renders it live with `st.write_stream`, instead of waiting for the full reply. Whenever a math tool runs mid-stream, a line like `🔧 used multiply → 376.0` is streamed in above the final answer, so tool use is visible live and stays part of the saved message history.
4. **Resume / chat persistence** — the graph is compiled with a `MemorySaver` checkpointer keyed by `thread_id`. Each conversation gets its own `thread_id`, so history is automatically resumed across messages and reruns within that thread — you only need to send the newest message; the checkpointer supplies the prior history.
   - **Scope**: this persistence is in-process RAM only. It survives page interactions within a live session, but is lost if the Streamlit server restarts or the browser session ends. There's no on-disk store yet — swapping `MemorySaver` for a persistent backend (e.g. `SqliteSaver`) would be needed for history to survive a restart.
5. **Multiple chat threads** — the sidebar has a **➕ New chat** button that starts a fresh thread with its own `thread_id` and empty history. Past threads are listed below it (titled from their first message); clicking one switches back to it and restores its full conversation, so you can hop between chats without losing context.

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Add your OpenAI key to `.env`:

```
OPENAI_API_KEY=sk-...
```

## Running

**Streamlit UI (recommended):**

```bash
streamlit run chatbot/app.py
```

**CLI:**

```bash
python -m chatbot.main
```
