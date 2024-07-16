import streamlit as st

st.set_page_config(layout="wide")

home = st.Page("page/home.py", title="Home", icon=":material/home:", default=True)
sample = st.Page("page/sample.py", title="Sample", icon=":material/patient_list:")
etiology = st.Page("page/etiology.py", title="Etiology", icon=":material/microbiology:")
drugresis = st.Page("page/drugresis.py", title="Drugresis", icon=":material/pill:")
test = st.Page("page/test.py", title="Test", icon=":material/bug_report:")

pg = st.navigation([home, sample, etiology, drugresis, test])

pg.run()
