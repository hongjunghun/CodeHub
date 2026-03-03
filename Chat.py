import streamlit as st
import sqlite3
from db import get_conn

def send_message(sender, receiver, message, code=""):
    conn = get_conn()
    c = conn.cursor()
    c.execute(
        "INSERT INTO chat(sender, receiver, message, code) VALUES (?, ?, ?, ?)",
        (sender, receiver, message, code)
    )
    conn.commit()
    conn.close()

def get_messages(user):
    """로그인한 사용자가 받은 메시지와 보낸 메시지 가져오기"""
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT sender, receiver, message, code, timestamp FROM chat WHERE sender=? OR receiver=? ORDER BY timestamp ASC", (user,user))
    messages = c.fetchall()
    conn.close()
    return messages

def show_chat_interface(current_user, ide_code=""):
    st.header("Chat")
    
    receiver = st.text_input("Receiver ID", key="chat_receiver")
    message = st.text_area("Message", key="chat_content")
    
    include_code = st.checkbox("Include current IDE code", key="include_code")
    
    if st.button("Send Message", key="send_msg"):
        if receiver and message:
            code_to_send = ide_code if include_code else ""
            send_message(current_user, receiver, message, code_to_send)
            st.success("[INFO] Message sent!")
        else:
            st.error("[INFO] Please enter receiver and message")
    
    st.subheader("Messages")
    messages = get_messages(current_user)
    for m in messages:
        sender, receiver, msg, code, timestamp = m
        if sender==current_user or receiver==current_user:
            st.markdown(f"**{timestamp}** | **From:** {sender} → **To:** {receiver}")
            st.markdown(f"Message: {msg}")
            if code:
                st.code(code)
            st.markdown("---")