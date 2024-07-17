import time
import streamlit as st
from vanna_calls import (
    generate_questions_cached,
    generate_sql_cached,
    run_sql_cached,
    generate_plotly_code_cached,
    generate_plot_cached,
    generate_followup_cached,
    should_generate_chart_cached,
    is_sql_valid_cached,
    generate_summary_cached
)

avatar_url = "https://vanna.ai/img/vanna.svg"

st.set_page_config(layout="wide")

# JavaScript code to maintain scroll position
maintain_scroll_position_js = """
<script>
    window.addEventListener("load", () => {
        window.scrollTo(0, localStorage.getItem("scrollPosition") || 0);
    });
    window.addEventListener("scroll", () => {
        localStorage.setItem("scrollPosition", window.scrollY);
    });
</script>
"""

st.sidebar.title("Output Settings")
st.sidebar.checkbox("Show SQL", value=True, key="show_sql")
st.sidebar.checkbox("Show Table", value=True, key="show_table")
st.sidebar.checkbox("Show Plotly Code", value=True, key="show_plotly_code")
st.sidebar.checkbox("Show Chart", value=True, key="show_chart")
st.sidebar.checkbox("Show Summary", value=True, key="show_summary")
st.sidebar.checkbox("Show Follow-up Questions", value=True, key="show_followup")
st.sidebar.button("Reset", on_click=lambda: reset_chat(), use_container_width=True)

st.title("Vanna AI")

# 重置聊天的函数
def reset_chat():
    # 初始化
    st.session_state["chat_history"] = []
    st.session_state["my_question"] = None
    st.session_state["show_suggestions"] = False

# Initialize chat history
if "chat_history" not in st.session_state:
    st.session_state["chat_history"] = []

if "my_question" not in st.session_state:
    st.session_state["my_question"] = None

if "show_suggestions" not in st.session_state:
    st.session_state["show_suggestions"] = False

# Function to set question
def set_question(question):
    st.session_state["my_question"] = question
    st.session_state["show_suggestions"] = False

# Display chat history 显示聊天历史
for chat in st.session_state["chat_history"]:
    if chat["role"] == "user":
        user_message = st.chat_message("user")
        user_message.write(chat["content"])
    else:
        assistant_message = st.chat_message("assistant", avatar=avatar_url)
        if chat.get("type") == "sql":
            assistant_message.code(chat["content"], language="sql", line_numbers=True)
        elif chat.get("type") == "dataframe":
            assistant_message.dataframe(chat["content"])
        elif chat.get("type") == "plot":
            assistant_message.plotly_chart(chat["content"])
        else:
            assistant_message.write(chat["content"])

assistant_message_suggested = st.chat_message("assistant", avatar=avatar_url)
if assistant_message_suggested.button("Click to show suggested questions"):
    st.session_state["show_suggestions"] = True

# 显示推荐问题
if st.session_state["show_suggestions"]:
    questions = generate_questions_cached()
    for i, question in enumerate(questions):
        time.sleep(0.05)
        st.button(question, on_click=lambda q=question: set_question(q))

# 确保只有一个输入框
if st.session_state["my_question"] is None:
    user_input = st.chat_input("Ask me a question about your data", key="user_input")
    if user_input:
        st.session_state["my_question"] = user_input
        st.session_state["chat_history"].append({"role": "user", "content": user_input})

my_question = st.session_state.get("my_question", None)

if my_question:
    user_message = st.chat_message("user")
    user_message.write(f"{my_question}")

    try:
        sql = generate_sql_cached(question=my_question)

        if "Artist" not in sql and "items" in sql:
            st.session_state["chat_history"].append({"role": "assistant", "content": "It seems the SQL query is not valid for the current database."})
            assistant_message_error = st.chat_message("assistant", avatar=avatar_url)
            assistant_message_error.error("It seems the SQL query is not valid for the current database.")
            st.session_state["my_question"] = None
            st.experimental_rerun()

        if sql:
            if is_sql_valid_cached(sql=sql):
                if st.session_state.get("show_sql", True):
                    st.session_state["chat_history"].append({"role": "assistant", "content": sql, "type": "sql"})
                    assistant_message_sql = st.chat_message("assistant", avatar=avatar_url)
                    assistant_message_sql.code(sql, language="sql", line_numbers=True)
            else:
                st.session_state["chat_history"].append({"role": "assistant", "content": sql})
                assistant_message = st.chat_message("assistant", avatar=avatar_url)
                assistant_message.write(sql)
                st.session_state["my_question"] = None
                st.experimental_rerun()

            df = run_sql_cached(sql=sql)

            if df is not None:
                st.session_state["df"] = df

            if st.session_state.get("df") is not None:
                if st.session_state.get("show_table", True):
                    df = st.session_state.get("df")
                    if len(df) > 10:
                        st.session_state["chat_history"].append({"role": "assistant", "content": "First 10 rows of data"})
                        st.session_state["chat_history"].append({"role": "assistant", "content": df.head(10), "type": "dataframe"})
                        assistant_message_table = st.chat_message("assistant", avatar=avatar_url)
                        assistant_message_table.text("First 10 rows of data")
                        assistant_message_table.dataframe(df.head(10))
                    else:
                        st.session_state["chat_history"].append({"role": "assistant", "content": df, "type": "dataframe"})
                        assistant_message_table = st.chat_message("assistant", avatar=avatar_url)
                        assistant_message_table.dataframe(df)

                if should_generate_chart_cached(question=my_question, sql=sql, df=df):
                    code = generate_plotly_code_cached(question=my_question, sql=sql, df=df)

                    if st.session_state.get("show_plotly_code", False):
                        st.session_state["chat_history"].append({"role": "assistant", "content": code, "type": "sql"})
                        assistant_message_plotly_code = st.chat_message("assistant", avatar=avatar_url)
                        assistant_message_plotly_code.code(code, language="python", line_numbers=True)

                    if code is not None and code != "":
                        if st.session_state.get("show_chart", True):
                            fig = generate_plot_cached(code=code, df=df)
                            if fig is not None:
                                st.session_state["chat_history"].append({"role": "assistant", "content": fig, "type": "plot"})
                                assistant_message_chart = st.chat_message("assistant", avatar=avatar_url)
                                assistant_message_chart.plotly_chart(fig)
                            else:
                                st.session_state["chat_history"].append({"role": "assistant", "content": "I couldn't generate a chart"})
                                assistant_message_chart = st.chat_message("assistant", avatar=avatar_url)
                                assistant_message_chart.error("I couldn't generate a chart")

                if st.session_state.get("show_summary", True):
                    summary = generate_summary_cached(question=my_question, df=df)
                    if summary is not None:
                        st.session_state["chat_history"].append({"role": "assistant", "content": summary})
                        assistant_message_summary = st.chat_message("assistant", avatar=avatar_url)
                        assistant_message_summary.text(summary)

                if st.session_state.get("show_followup", True):
                    followup_questions = generate_followup_cached(question=my_question, sql=sql, df=df)
                    st.session_state["df"] = None

                    if len(followup_questions) > 0:
                        st.session_state["chat_history"].append({"role": "assistant", "content": "Here are some possible follow-up questions"})
                        assistant_message_followup = st.chat_message("assistant", avatar=avatar_url)
                        assistant_message_followup.text("Here are some possible follow-up questions")
                        for question in followup_questions[:5]:
                            assistant_message_followup.button(question, on_click=lambda q=question: set_question(q))

        else:
            st.session_state["chat_history"].append({"role": "assistant", "content": "I wasn't able to generate SQL for that question"})
            assistant_message_error = st.chat_message("assistant", avatar=avatar_url)
            assistant_message_error.error("I wasn't able to generate SQL for that question")

    except Exception as e:
        st.session_state["chat_history"].append({"role": "assistant", "content": f"An error occurred: {str(e)}"})
        assistant_message_error = st.chat_message("assistant", avatar=avatar_url)
        assistant_message_error.error(f"An error occurred: {str(e)}")
        st.session_state["my_question"] = None

    # 清除当前问题
    st.session_state["my_question"] = None
    st.experimental_rerun()

# 确保页面保持滚动位置
st.markdown(maintain_scroll_position_js, unsafe_allow_html=True)
