# app.py
import streamlit as st
from llm import generate_sql, generate_answer, is_relevant_question
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

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []
# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if "sql" in message:
            with st.expander("View Generated SQL"):
                st.code(message["sql"], language="sql")

# User input
if prompt := st.chat_input("e.g., Which store in Chennai has the highest phr_score?"):
    # Add user message to history
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Bot response
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""

        try:
            # Step 1: Check relevance
            if not is_relevant_question(prompt):
                full_response = "I can only answer questions about retail store performance data (e.g., scores, stores, ASEs, regions). Please ask something related to the database."
                message_placeholder.markdown(full_response)
                st.session_state.messages.append({"role": "assistant", "content": full_response})
                st.stop()

            # Step 2: Generate SQL
            message_placeholder.markdown("🧠 Generating SQL...")
            sql = generate_sql(prompt)

            # Step 3: Validate
            if not is_safe_sql(sql):
                full_response = "❌ Rejected: Unsafe SQL detected."
                message_placeholder.markdown(full_response)
                st.session_state.messages.append({"role": "assistant", "content": full_response})
                st.stop()

            # Step 4: Execute
            message_placeholder.markdown("🔍 Querying database...")
            result = execute_query(sql)

            # Step 5: Generate answer
            message_placeholder.markdown("💬 Generating answer...")
            answer = generate_answer(prompt, result)

            # Final response
            full_response = answer
            message_placeholder.markdown(full_response)

            # Save to history with SQL
            st.session_state.messages.append({
                "role": "assistant",
                "content": full_response,
                "sql": sql
            })

        except Exception as e:
            error_msg = f"💥 Error: {str(e)}"
            message_placeholder.error(error_msg)
            st.session_state.messages.append({"role": "assistant", "content": error_msg})