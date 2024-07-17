# 在 Streamlit 应用中

if my_question:
    user_message = st.chat_message("user")
    user_message.write(f"{my_question}")

    sql = generate_sql_cached(question=my_question)
    
    if sql is None:
        st.session_state["chat_history"].append({"role": "assistant", "content": "Failed to generate SQL for the question."})
        assistant_message_error = st.chat_message("assistant", avatar=avatar_url)
        assistant_message_error.error("Failed to generate SQL for the question.")
        st.session_state["my_question"] = None
        st.experimental_rerun()

    st.write(f"Generated SQL: {sql}")

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

    # 清除当前问题
    st.session_state["my_question"] = None
    st.experimental_rerun()

# 确保页面保持滚动位置
st.markdown(maintain_scroll_position_js, unsafe_allow_html=True)
