import streamlit as st
import ollama
import config
import uuid
from collections import namedtuple

st.set_page_config(layout="wide")

#function to load the css styling
def load_css(file_path):
    with open(file_path) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

#call the function to load the styling
load_css("Styling/style.css") 

#creates a unique key for each chat message (made this for styling)
def unique_message(name):
    return st.container(key=f"{name}-{uuid.uuid4()}")

MODEL = 'llava:7b' #this is the model we are using

#declare our current chat tuple
CHAT_TUPLE = namedtuple('CHAT_TUPLE', ['CHAT_NAME', 'CHAT_MESSAGES'])

#create the variable for chat counter
CHAT_COUNT = 1

if 'CHATS' not in st.session_state:
    #create our initial chat tuple
    CHAT1 = CHAT_TUPLE('Chat 1', config.SYSTEM_MESSAGE)
    #create the variables for the current chats held with the chatbot
    st.session_state['CHATS'] = [CHAT1]
    st.session_state['CHAT_NAMES'] = ["Chat 1"]

#create our clear chat history function
def clear_chat_history():
    CHAT1 = CHAT_TUPLE('Chat 1', config.SYSTEM_MESSAGE)
    st.session_state['CHATS'] =  [CHAT1]
    st.session_state['CHAT_NAMES'] = ["Chat 1"]
    st.session_state.chat_history = st.session_state['CHAT_NAMES']

#create our new chat function
def new_chat():
    CHAT_COUNT = len(st.session_state['CHAT_NAMES'])
    CHAT_NAME = "Chat " + str(CHAT_COUNT+1)
    TEMP_CHAT = CHAT_TUPLE(CHAT_NAME, config.SYSTEM_MESSAGE)
    st.session_state['CHATS'].append(TEMP_CHAT)
    st.session_state['CHAT_NAMES'].append(CHAT_NAME)
    st.session_state.chat_history = st.session_state['CHAT_NAMES']

st.sidebar.title("BOB A.I.")
with st.sidebar:
    st.button("+New Chat", key="new_chat_button", on_click=new_chat) #button to start a new chat

    #if it doesn't already exist, make it, fill with CHAT_NAMES list
    if 'chat_history' not in st.session_state:
        st.session_state['chat_history'] = st.session_state['CHAT_NAMES']

    #make a select box to view the previous chats
    chatHistorySelectBox = st.selectbox("View Chat History", st.session_state.chat_history)

    files_uploaded = st.file_uploader("Pick a file") #allows user to upload a file ..... this doesn't work yet, you can submit a file, but nothing happens

    if files_uploaded is not None: #if there are files that have been uploaded
        #for file in files_uploaded: #for each file uploaded
        file_contents = files_uploaded.read().decode("utf-8") #read and decode the file (put that in file data)
        st.session_state.messages.append({'role': 'system', 'content': f"A file has been uploaded named: {files_uploaded.name} The contents of the file is: {file_contents}"}) #tell the assistant what the file is, but do not print this out
        
        #TEST
        print(f"File uploaded successfully. File name: {files_uploaded.name} \n File Contents: {file_contents}") #THIS IS A TEST STATEMENT, DELETE LATER
        #TEST


    st.button("-Clear Chat History", key="clear_chat_button", on_click=clear_chat_history) #button to clear chat history


#initializes the messages with the system prompt
if 'messages' not in st.session_state:
    st.session_state.messages = [{"role": "system","content": config.SYSTEM_MESSAGE}]

    #have the chatbot initiate conversation
    st.session_state.messages.append({'role': 'assistant', 'content': 'Hello! I am Bob. Please let me know how I can best assist you today.'}) 


#for all the messages we have in the session state --> display the message content
for message in st.session_state["messages"]:
    if message["role"] != "system":
            #if role is user display user avatar and put in container
            if(message["role"] == "user"):
                with unique_message("user"):
                    with st.chat_message("user", avatar="Assets/User_Icon.png"):
                        st.markdown(message["content"])
        
            else:
            #if role is assistant display assistant avatar
                with st.chat_message("asssistant", avatar="Assets/smiley.jpg"):
                    st.markdown(message["content"])


def generate_response():
    response = ollama.chat(model=MODEL, stream=True, messages=st.session_state.messages) #will get the response from the model

    for chunk in response:
        token = chunk["message"]["content"] #token is getting the chunk content 
        st.session_state["full_message"] += token #adds to the full message so far
        yield token #display the token


if prompt:= st.chat_input("Type here", key="chat_input_styled"): #this text will show up in the input bar
    st.session_state.messages.append({"role": "user", "content": prompt}) #if the user types a prompt append it
    with unique_message("user"):
        with st.chat_message("user", avatar="Assets/User_Icon.png"):
            st.markdown(prompt) #display prompt
    st.session_state['full_message'] = "" #defines a session state for the full message, empty at first as no request has yet been made
    with st.chat_message("assistant", avatar="Assets/smiley.jpg"):
        stream = generate_response()
        response = st.write_stream(stream) #write the stream response
        st.session_state.messages.append({'role': 'assistant', 'content': response}) #append assitant response into content