import streamlit as st
import os
from datetime import datetime
import matplotlib.pyplot as plt

SAVE_DIR = "saved_files"

def list_files_recursive(directory):
    file_list=[]
    for root, dirs, files in os.walk(directory):
        for file in files:
            file_list.append(os.path.join(root,file))
    return file_list

def get_language_by_extension(filename):
    ext_map = {".py":"Python",".c":"C",".cpp":"C++",".java":"Java",".js":"JavaScript",".go":"Go",".rs":"Rust"}
    ext = os.path.splitext(filename)[1]
    return ext_map.get(ext,"Other")

def show_home():
    st.header("Home Dashboard")
    all_files = list_files_recursive(SAVE_DIR)
    all_files.sort(key=lambda x: os.path.getmtime(x), reverse=True)

    total_files = len(all_files)
    total_folders = sum([len(dirs) for _, dirs, _ in os.walk(SAVE_DIR)])
    language_count = {}
    for f in all_files:
        lang = get_language_by_extension(f)
        language_count[lang] = language_count.get(lang,0)+1
    most_used_lang = max(language_count, key=language_count.get) if language_count else "-"
    col1,col2,col3 = st.columns(3)
    col1.metric("Total Files",total_files)
    col2.metric("Total Folders",total_folders)
    col3.metric("Most Used Language",most_used_lang,f"{language_count.get(most_used_lang,0)} files")

    if all_files:
        recent_file = all_files[0]
        st.subheader("Most Recent File")
        st.write(f"**File:** {os.path.relpath(recent_file,SAVE_DIR)}")
        st.write(f"**Last Modified:** {datetime.fromtimestamp(os.path.getmtime(recent_file))}")
        with open(recent_file,"r",encoding="utf-8") as f:
            content = f.read()
        st.code(content,language=get_language_by_extension(recent_file))

    st.subheader("Recent 5 Files")
    for f in all_files[:5]:
        cols = st.columns([4,1,1])
        rel_path = os.path.relpath(f,SAVE_DIR)
        with cols[0]:
            st.write(rel_path)
        with cols[1]:
            if st.button("▶ Load",key=f+"_load"):
                try:
                    with open(f,"r",encoding="utf-8") as file:
                        content = file.read()
                    st.session_state.editor_content = content
                    st.session_state.file_name = os.path.splitext(os.path.basename(f))[0]
                    st.success(f"[INFO] {rel_path} loaded into IDE")
                except Exception as e:
                    st.error(f"[INFO] Failed to load: {str(e)}")
        with cols[2]:
            size_kb = os.path.getsize(f)/1024
            st.write(f"{size_kb:.1f} KB")