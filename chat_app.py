import streamlit as st
from openai import OpenAI
from streamlit_chat import message
import Ai_assistant as ai
from sqlalchemy.orm import Session
import create_database as cd
import user_creation_and_authentication as uc


# Database session
def get_db():
    db = cd.SessionLocal()
    try:
        yield db
    finally:
        db.close()


# User session management
if "user_id" not in st.session_state:
    st.session_state.user_id = None

if "username" not in st.session_state:
    st.session_state.username = ""

if "show_login" not in st.session_state:
    st.session_state.show_login = False

if "show_register" not in st.session_state:
    st.session_state.show_register = False

def register():
    st.subheader("Register")
    username = st.text_input("Username", key="register_username")
    password = st.text_input("Password", type="password", key="register_password")
    if st.button("Confirm registration"):
        with next(get_db()) as db:
            try:
                user = uc.create_user(db, username, password)
                st.session_state.show_login = False
                st.session_state.show_register = False
                st.success("User registered!")
            except Exception as e:
                st.error(f"Error: {e}")


def login():
    st.subheader("Login")
    username = st.text_input("Username", key="login_username")
    password = st.text_input("Password", type="password", key="login_password")
    if st.button("Login"):
        with next(get_db()) as db:
            user = uc.authenticate_user(db, username, password)
            if user:
                st.session_state.user_id = user.id
                st.session_state.username = user.username
                st.session_state.show_login = False
                st.session_state.show_register = False
                st.success("Login successful!")
            else:
                st.error("Invalid username or password")


def chat_interface(user_id : int, db: Session):
    client = OpenAI(base_url="http://localhost:1234/v1", api_key="lm-studio")

    if "messages" not in st.session_state:
        st.session_state.messages = [
        ]

    if "input_text" not in st.session_state:
        st.session_state.input_text = ""

    input_placeholder = st.empty()
    user_input = input_placeholder.text_input("You: ", key="user_input", value=st.session_state.input_text)

    if user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})
        # Generate and display bot response
        with st.spinner("Generating response..."):
            bot_response = ai.get_bot_response(client, st.session_state.messages)
        st.session_state.input_text = ""
        st.session_state.messages.append({"role": "assistant", "content": bot_response})
        db_message = cd.Message(content=user_input, role="user", owner_id=st.session_state.user_id)
        db.add(db_message)
        db.commit()
        db_bot_message = cd.Message(content=bot_response, role="assistant", owner_id=user_id)
        db.add(db_bot_message)
        db.commit()
    # Display chat messages from history on app rerun
    messages = db.query(cd.Message).filter(cd.Message.owner_id == user_id).order_by(cd.Message.created_at.desc()).all()
    for i, msg in enumerate(reversed(messages)):
        if msg.role == "user":
            message(msg.content, is_user=True, key=f"user_{i}")
        else:
            message(msg.content, is_user=False, key=f"assistant_{i}")


st.title("Llama 3.0 8B")

if st.session_state.user_id:
    st.write(f"Welcome, {st.session_state.username}")
    if st.button("Logout"):
        st.session_state.user_id = None
        st.session_state.username = None
        st.session_state.show_login = False
        st.session_state.show_register = False
    else:
        db = next(get_db())
        chat_interface(st.session_state.user_id, db)
else:
    st.write("Please log in or register")
    if st.button("Log in"):
        st.session_state.show_login = True
        st.session_state.show_register = False
    if st.button("Not a user? Please register"):
        st.session_state.show_register = True
        st.session_state.show_login = False

    if st.session_state.show_login:
        login()
    elif st.session_state.show_register:
        register()
