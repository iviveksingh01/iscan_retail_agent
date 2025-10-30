# chatbot.py
from llm import generate_sql, generate_answer, is_relevant_question  # ← ADD is_relevant_question
from validator import is_safe_sql
from db import execute_query
import logging

logging.basicConfig(level=logging.WARNING)

def main():
    
    print("Ask questions about store performance. Type 'exit' to quit.\n")

    while True:
        try:
            question = input("Question > ").strip()
            if not question or question.lower() in {"exit", "quit"}:
                print("👋 Goodbye!")
                break

            # ✅ NEW: Check if question is about retail store data
            if not is_relevant_question(question):
                print("💬 Answer: I can only answer questions about retail store performance data (e.g., scores, stores, ASEs, regions). Please ask something related to the database.\n")
                continue

            # Step 1: Generate SQL
            print("🧠 Generating SQL...")
            sql = generate_sql(question)
            print(f"✅ SQL: {sql}\n")

            # Step 2: Validate
            if not is_safe_sql(sql):
                print("❌ Rejected: Unsafe SQL detected.\n")
                continue

            # Step 3: Execute
            print("🔍 Querying database...")
            result = execute_query(sql)
            print(f"📊 Rows returned: {len(result)}\n")

            # Step 4: Generate natural answer
            answer = generate_answer(question, result)
            print(f"💬 Answer: {answer}\n")

        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"💥 Error: {e}\n")

if __name__ == "__main__":
    main()