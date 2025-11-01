# app.py
import streamlit as st
from llm import (
    generate_sql_with_memory,
    generate_answer_with_memory,
    is_relevant_question
)
from validator import is_safe_sql
from db import execute_query
import time

# Page config
st.set_page_config(
    page_title="Retail Store Insights",
    page_icon="🛍️",
    layout="wide"
)

# Title
st.title("🛍️ Retail Store LLM Chatbot")
st.caption("Ask questions about store performance, scores, ASEs, regions, and more.")

# Clear history
if st.sidebar.button("Clear Chat"):
    st.session_state.messages = []
    st.rerun()

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display initial greeting if no messages
if len(st.session_state.messages) == 0:
    with st.chat_message("assistant"):
        greeting = "👋 Hi! I'm your **Retail Store Insights Assistant**.\n\n" \
                   "You can ask me questions like:\n" \
                   "- *Which store in Chennai has the highest phr_score?*\n" \
                   "- *What is the sof_score for V V MART TBM?*\n" \
                   "- *How many stores does ASE Anand manage?*\n\n" \
                   "Go ahead — I'm here to help! 😊"
        st.markdown(greeting)
else:
    # Display full chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            if "sql" in message:
                with st.expander("View Generated SQL"):
                    st.code(message["sql"], language="sql")

# User input
if prompt := st.chat_input("e.g., Which store in Chennai has the highest phr_score?"):
    normalized_prompt = prompt.strip().lower()

    # ✅ Handle greetings FIRST — before anything else
    if normalized_prompt in ["hi", "hello", "hey", "hii", "hi there", "hello there"]:
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        with st.chat_message("assistant"):
            reply = "Hi! I'm your Retail Store Insights Assistant. How can I help you today?"
            st.markdown(reply)
            st.session_state.messages.append({"role": "assistant", "content": reply})
        st.stop()  # Skip the rest of the pipeline

    # For non-greeting messages, proceed normally
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Bot response
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""

        try:
            if not is_relevant_question(prompt):
                full_response = "I can only answer questions about retail store performance data (e.g., scores, stores, ASEs, regions). Please ask something related to the database."
                message_placeholder.markdown(full_response)
                st.session_state.messages.append({"role": "assistant", "content": full_response})
                st.stop()

            message_placeholder.markdown("🧠 Generating SQL...")
            sql = generate_sql_with_memory(prompt, st.session_state.messages)

            if not is_safe_sql(sql):
                full_response = "❌ Rejected: Unsafe SQL detected."
                message_placeholder.markdown(full_response)
                st.session_state.messages.append({"role": "assistant", "content": full_response})
                st.stop()

            message_placeholder.markdown("🔍 Querying database...")
            result = execute_query(sql)

            message_placeholder.markdown("💬 Generating answer...")
            answer = generate_answer_with_memory(prompt, result, st.session_state.messages)

            full_response = answer
            message_placeholder.markdown(full_response)

            st.session_state.messages.append({
                "role": "assistant",
                "content": full_response,
                "sql": sql
            })

        except Exception as e:
            error_msg = f"💥 Error: {str(e)}"
            message_placeholder.error(error_msg)
            st.session_state.messages.append({"role": "assistant", "content": error_msg})