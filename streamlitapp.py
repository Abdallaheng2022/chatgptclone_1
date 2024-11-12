import openai
import os
from dotenv import load_dotenv
import streamlit as st
import json

# Load environment variables
env_path = os.path.join('.env')
load_dotenv(env_path)

# Initialize OpenAI client
client = openai.OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
MAX_HISTORY_LENGTH = 10

def save_chat_history(chat_history):
    """Save chat history to a file"""
    try:
        with open('chat_history.json', 'w') as f:
            json.dump(chat_history, f)
    except Exception as e:
        st.error(f"Error saving chat history: {str(e)}")

def load_chat_history():
    """Load chat history from file"""
    try:
        if os.path.exists('chat_history.json'):
            with open('chat_history.json', 'r') as f:
                return json.load(f)
    except Exception as e:
        st.error(f"Error loading chat history: {str(e)}")
    return []

def stream_chat_response(message, chat_history):
    """Stream the chat response from OpenAI API"""
    stream = client.chat.completions.create(
        messages=chat_history,
        model="gpt-3.5-turbo",
        temperature=0.7,
        stream=True
    )
    
    for chunk in stream:
        if chunk.choices[0].delta.content:
            yield chunk.choices[0].delta.content

def initialize_session_state():
    """Initialize or restore session state"""
    if 'chat_history' not in st.session_state:
        # Try to load previous chat history
        st.session_state.chat_history = load_chat_history()
    
    if 'is_initialized' not in st.session_state:
        st.session_state.is_initialized = True

def clear_chat():
    """Clear chat history and rerun the app"""
    st.session_state.chat_history = []
    save_chat_history([])
    st.rerun()

def main():
    # Initialize session state
    initialize_session_state()
    
    # Title and welcome message
    st.markdown("""
    # Ask ChatGPT Clone!
    """, unsafe_allow_html=True)
    
    st.markdown("""
    ### Welcome to the ChatGPT Clone!
    This is a simple chatbot powered by OpenAI's GPT-3.5 model. 
    Feel free to ask any questions or start a conversation.
    """)
    
    # Add a clear chat button
    if st.button("Clear Chat History"):
        clear_chat()
    
    # Display chat history
    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            st.write(message["content"])
    
    # User input
    user_input = st.chat_input("Type your message here...")
    
    if user_input:
        # Add user message to history
        st.session_state.chat_history.append({
            "role": "user", 
            "content": user_input
        })
        
        # Display user message
        with st.chat_message("user"):
            st.write(user_input)
        
        # Generate and display assistant response
        with st.chat_message("assistant"):
            response_placeholder = st.empty()
            full_response = ""
            
            # Stream the response
            for chunk in stream_chat_response(user_input, st.session_state.chat_history):
                full_response += chunk
                response_placeholder.write(full_response)
            
            # Add assistant response to history
            st.session_state.chat_history.append({
                "role": "assistant", 
                "content": full_response
            })
            
            # Save updated chat history
            save_chat_history(st.session_state.chat_history)
            
            # Trim history if it gets too long
            if len(st.session_state.chat_history) > MAX_HISTORY_LENGTH * 2:
                st.session_state.chat_history = st.session_state.chat_history[-MAX_HISTORY_LENGTH*2:]
                save_chat_history(st.session_state.chat_history)

if __name__ == "__main__":
    main()