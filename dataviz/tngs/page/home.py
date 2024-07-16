import streamlit as st

st.write("# Welcome to Streamlit Demo TNGS App! 👋")

uploaded_file = st.file_uploader(
    label="Please choose an Excel file to upload", type=["xlsx"]
)

if uploaded_file is not None:
    st.session_state._uploaded_file = uploaded_file


st.markdown(
    """
    ### Want to learn more?
    - Check out [streamlit.io](https://streamlit.io)
    - Jump into our [documentation](https://docs.streamlit.io)
    - Ask a question in our [community
        forums](https://discuss.streamlit.io)
    ### See more complex demos
    - Use a neural net to [analyze the Udacity Self-driving Car Image
        Dataset](https://github.com/streamlit/demo-self-driving)
    - Explore a [New York City rideshare dataset](https://github.com/streamlit/demo-uber-nyc-pickups)
"""
)
