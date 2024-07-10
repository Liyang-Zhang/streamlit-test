import streamlit as st

home = st.Page("page/home.py", title="Home", icon=":material/home:", default=True)
upload = st.Page("page/upload.py", title="Upload", icon=":material/upload:")
plot = st.Page("page/plot.py", title="Plot", icon=":material/show_chart:")

pg = st.navigation([home, upload, plot])

pg.run()
