import streamlit as st

from vanna.remote import VannaDefault


# Set page config at the very beginning
st.set_page_config(layout="wide")

@st.cache_resource(ttl=3600)
def setup_vanna():
    vn = VannaDefault(api_key="3c81178c26c94fe6bcae7d085ecccdcf", model='chinook')
    vn.connect_to_sqlite("https://vanna.ai/Chinook.sqlite")
    return vn

@st.cache_data(show_spinner="Generating sample questions ...")
def generate_questions_cached():
    vn = setup_vanna()
    return vn.generate_questions()


@st.cache_data(show_spinner="Generating SQL query ...")
def generate_sql_cached(question: str):
    vn = setup_vanna()
    return vn.generate_sql(question=question, allow_llm_to_see_data=True)

@st.cache_data(show_spinner="Checking for valid SQL ...")
def is_sql_valid_cached(sql: str):
    vn = setup_vanna()
    return vn.is_sql_valid(sql=sql)

@st.cache_data(show_spinner="Running SQL query ...")
def run_sql_cached(sql: str):
    vn = setup_vanna()
    return vn.run_sql(sql=sql)

@st.cache_data(show_spinner="Checking if we should generate a chart ...")
def should_generate_chart_cached(question, sql, df):
    vn = setup_vanna()
    return vn.should_generate_chart(df=df)

@st.cache_data(show_spinner="Generating Plotly code ...")
def generate_plotly_code_cached(question, sql, df):
    vn = setup_vanna()
    code = vn.generate_plotly_code(question=question, sql=sql, df=df)
    return code


@st.cache_data(show_spinner="Running Plotly code ...")
def generate_plot_cached(code, df):
    vn = setup_vanna()
    return vn.get_plotly_figure(plotly_code=code, df=df)


@st.cache_data(show_spinner="Generating followup questions ...")
def generate_followup_cached(question, sql, df):
    vn = setup_vanna()
    return vn.generate_followup_questions(question=question, sql=sql, df=df)

@st.cache_data(show_spinner="Generating summary ...")
def generate_summary_cached(question, df):
    vn = setup_vanna()
    return vn.generate_summary(question=question, df=df)



## 增加多轮对话功能：
# Initialize session state for conversation history
if 'conversation' not in st.session_state:
    st.session_state.conversation = []

# Streamlit app
st.title("Vanna AI Multi-turn Conversation")

question = st.text_input("Enter your question:")

if question:
    # Append new question to conversation history
    st.session_state.conversation.append({'question': question})
    
    # Generate SQL query
    sql_query = generate_sql_cached(question)
    st.session_state.conversation[-1]['sql'] = sql_query
    st.code(sql_query, language="sql")
    
    # Run SQL query
    df = run_sql_cached(sql_query)
    st.session_state.conversation[-1]['data'] = df
    st.dataframe(df)
    
    # Generate Plotly code
    plotly_code = generate_plotly_code_cached(question, sql_query, df)
    st.session_state.conversation[-1]['plotly_code'] = plotly_code
    st.code(plotly_code, language="python")
    
    # Generate Plotly figure
    plot = generate_plot_cached(plotly_code, df)
    st.session_state.conversation[-1]['plot'] = plot
    st.plotly_chart(plot)
    
    # Generate followup questions
    followup_questions = generate_followup_cached(question, sql_query, df)
    st.session_state.conversation[-1]['followup'] = followup_questions
    st.write("Follow-up questions:")
    for q in followup_questions:
        st.write("- " + q)

# Display conversation history
st.write("Conversation History:")
for turn in st.session_state.conversation:
    st.write(f"**Q:** {turn['question']}")
    st.code(turn.get('sql', 'No SQL generated'), language="sql")
    if 'data' in turn:
        st.dataframe(turn['data'])
    if 'plotly_code' in turn:
        st.code(turn['plotly_code'], language="python")
    if 'plot' in turn:
        st.plotly_chart(turn['plot'])
    if 'followup' in turn:
        st.write("Follow-up questions:")
        for q in turn['followup']:
            st.write("- " + q)