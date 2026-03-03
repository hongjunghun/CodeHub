import streamlit as st
from db import get_conn, init_db
import sqlite3

from Home import show_home
from IDE import show_ide
from Files import show_files
from Chat import show_chat_interface

init_db()

for key in ["logged_in","username","editor_content","file_name","globals","page"]:
    if key not in st.session_state:
        st.session_state[key] = False if key=="logged_in" else "" if key in ["username","editor_content","file_name"] else {} if key=="globals" else "Home"

def login(user, password):
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT password FROM users WHERE username=?", (user,))
    result = c.fetchone()
    conn.close()
    if result and result[0]==password:
        st.session_state.logged_in = True
        st.session_state.username = user
        st.session_state.page = "Home"
    else:
        st.error("[INFO] Invalid username or password")

def signup(user, password):
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT username FROM users WHERE username=?", (user,))
    if c.fetchone():
        st.error("[INFO] Username already exists")
    else:
        c.execute("INSERT INTO users(username,password) VALUES (?,?)", (user,password))
        conn.commit()
        st.success("[INFO] Signup successful!")
    conn.close()

def logout():
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.session_state.page = "Home"

st.set_page_config(page_title="CodeHub", layout="wide")

if not st.session_state.logged_in:
    st.title("CodeHub - Login / Signup")
    tab = st.radio("Select Action", ["Login","Signup"])
    username = st.text_input("Username", key="user_input")
    password = st.text_input("Password", type="password", key="pass_input")

    if tab=="Login":
        if st.button("Login"):
            login(username, password)
    elif tab=="Signup":
        if st.button("Signup"):
            signup(username, password)

if st.session_state.logged_in:
    st.sidebar.title("CodeHub")
    st.sidebar.markdown(f"**Logged in as {st.session_state.username}**")

    st.sidebar.markdown(
        """
        <style>
        div.stButton > button {
            border: none !important;
            background-color: transparent !important;
            width: 100%;
            text-align: left;
            padding: 0.5rem 0.5rem;
            font-size: 16px;
        }
        div.stButton > button:hover {
            background-color: #f0f2f6 !important;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    if st.sidebar.button("Home"): st.session_state.page="Home"
    if st.sidebar.button("IDE"): st.session_state.page="IDE"
    if st.sidebar.button("Files"): st.session_state.page="Files"
    if st.sidebar.button("Chat"): st.session_state.page="Chat"
    if st.sidebar.button("Logout"):
        logout()

    if st.session_state.page=="Home": show_home()
    elif st.session_state.page=="IDE": show_ide()
    elif st.session_state.page=="Files": show_files()
    elif st.session_state.page=="Chat":
        show_chat_interface(
            st.session_state.username,
            ide_code=st.session_state.editor_content
        )