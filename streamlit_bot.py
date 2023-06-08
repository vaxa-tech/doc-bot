
import os
import random
import time
import streamlit as st
from datetime import datetime
from streamlit_chat import message
from llama_index import GPTVectorStoreIndex, SimpleDirectoryReader
from decouple import config
import tempfile


# buf1, col, buf2 = st.columns([3, 1, 3])
st.image('VA_Marque_Color_width500px.png', width=50, output_format='PNG')
st.markdown("<h1 style='text-align: left; color: #fbaa36;'>Doc-Bot</h1>", unsafe_allow_html=True)
st.write("""
Doc-Bot is a demo chatbot that answers questions about uploaded documents. 


It's intended to demonstrate how you could extract insight and knowledge vast quantities of documentation, all 
without needing to know exactly where they're stored, or the exact term to search for. 

While Doc-Bot only looks at 
one document at a time, the exact same technology can be used to explore hundreds or even thousands of documents at once.

**It uses the most modern AI natural language processing techniques to understand the meaning of your questions,
and then uses that understanding to find the most relevant answers from your documents.**
""")

st.write('---')

if os.environ.get("OPENAI_API_KEY", None) is None:
    openai_key = config('OPENAI_API_KEY')
    os.environ["OPENAI_API_KEY"] = openai_key

if os.environ["OPENAI_API_KEY"] is None:
    st.error("No OpenAI API key found. Please set one as an environment variable called OPENAI_API_KEY")
    st.stop()

st.write(os.environ["OPENAI_API_KEY"])

st.session_state.all_messages = []

def save_uploaded_file(uploadedfile):
  with open(os.path.join("data",uploadedfile.name),"wb") as f:
     f.write(uploadedfile.getbuffer())

setup_container = st.container()
# container for chat history
response_container = st.container()
# container for text box
container = st.container()

st.session_state['document_read'] = False


with setup_container: 
    if not st.session_state['document_read']:
        datafile = st.file_uploader("Upload your document (must contain highlightable text)",type=['docx', 'doc', 'pdf'],
                                    help="Upload a document to be read by the bot", accept_multiple_files=False)

        if datafile is not None:
            # load datafile to a temp directory
            with tempfile.TemporaryDirectory() as tmp_dir:
                with open(os.path.join(tmp_dir, datafile.name),"wb") as f:
                    f.write(datafile.getbuffer())

                with st.spinner('Our bot is currently reading your doc...'):
                    documents = SimpleDirectoryReader(tmp_dir).load_data()
                    index = GPTVectorStoreIndex.from_documents(documents)
                    query_engine = index.as_chat_engine()
                    st.session_state['document_read'] = True

                st.write('---')

if st.session_state.get('document_read', False):
    with st.form(key='my_form', clear_on_submit=True):
        user_query = st.text_area("You:", key='input', height=100)
        submit_button = st.form_submit_button(label='Send')

        if submit_button and user_query:
            with response_container:
                st.session_state.all_messages.append(
                    {'is_user': True, 'message': user_query, 'time': time.time_ns()}
                )
                for _msg in st.session_state.all_messages:
                    message(f"{_msg['message']}", is_user=_msg['is_user'], key=_msg['time'])

                # get our query response
                with st.spinner('Thinking...'):
                    query_response = str(query_engine.chat(user_query)).strip()
                    query_response_time = time.time_ns()
                message(f"{query_response}", is_user=False, key=query_response_time)

                # store the response
                st.session_state.all_messages.append(
                    {'is_user': False, 'message': str(query_response), 'time': query_response_time}
                )
