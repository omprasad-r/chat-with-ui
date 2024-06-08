import streamlit as st
from streamlit_chat import message
from utils import get_initial_message, get_chatgpt_response, update_chat
import os
from dotenv import load_dotenv
load_dotenv()
import openai

openai.api_key = os.getenv('OPENAI_API_KEY')

st.title("Chatbot : ChatGPT and Streamlit Chat")
st.subheader("Conversational AI Demo:")

model = st.selectbox(
    "Select a model",
    ("gpt-3.5-turbo", "gpt-4")
)

##initialize the session states to store the generated messages, past queries, and the initial set of messages.
if 'generated' not in st.session_state:
    st.session_state['generated'] = []
if 'past' not in st.session_state:
    st.session_state['past'] = []

#query = st.text_input("Query: ", key="input")

query = st.chat_input("Enter query....")

if 'messages' not in st.session_state:
    st.session_state['messages'] = get_initial_message()

##process the user's query and generate the AI response
if query:
    with st.spinner("generating..."):
        messages = st.session_state['messages']
        messages = update_chat(messages, "user", query)
        response = get_chatgpt_response(messages, model)
        messages = update_chat(messages, "assistant", response)
        st.session_state.past.append(query)
        st.session_state.generated.append(response)


##display the chat messages and an expander to show the full message history
if st.session_state['generated']:
    for i in range(len(st.session_state['generated'])-1, -1, -1):
        message(st.session_state["generated"][i], key=str(i))
        message(st.session_state['past'][i], is_user=True, key=str(i) + '_user')
    
    with st.expander("Show Messages"):
        st.write(messages)


