import streamlit as st
from streamlit_ace import st_ace
import io, sys, tempfile, subprocess, traceback, os

from Chat import show_chat_interface

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import keras

SAVE_DIR = "saved_files"
os.makedirs(SAVE_DIR, exist_ok=True)

if "globals" not in st.session_state:
    st.session_state.globals = {
        "np": np,
        "pd": pd,
        "plt": plt,
        "keras": keras,
    }

def show_ide():
    if "editor_content" not in st.session_state:
        st.session_state.editor_content = ""
    if "file_name" not in st.session_state:
        st.session_state.file_name = "main"
    if "username" not in st.session_state:
        st.session_state.username = "user"

    st.header("Web IDE")

    language = st.selectbox(
        "Select Language",
        ["Python","C","C++","Java","JavaScript","Go","Rust"],
        index=0,
        key="language_select"
    )

    extensions = {"Python":"py","C":"c","C++":"cpp","Java":"java","JavaScript":"js","Go":"go","Rust":"rs"}
    editor_lang = {"Python":"python","C":"c_cpp","C++":"c_cpp","Java":"java", "JavaScript":"javascript","Go":"golang","Rust":"rust"}

    default_code = {
        "Python":'print("Hello Python!")',
        "C":'#include <stdio.h>\nint main(){ printf("Hello C!\\n"); return 0; }',
        "C++":'#include <iostream>\nusing namespace std;\nint main(){ cout<<"Hello C++!"<<endl; return 0; }',
        "Java":'public class Main { public static void main(String[] args){ System.out.println("Hello Java!"); } }',
        "JavaScript":'console.log("Hello JavaScript!");',
        "Go":'package main\nimport "fmt"\nfunc main(){ fmt.Println("Hello Go!") }',
        "Rust":'fn main(){ println!("Hello Rust!"); }'
    }
    if st.session_state.editor_content == "":
        st.session_state.editor_content = default_code[language]

    col1, col2 = st.columns([3,2])

    with col1:
        uploaded_file = st.file_uploader("Upload file", type=list(extensions.values()))
        if uploaded_file:
            content = uploaded_file.read().decode("utf-8")
            st.session_state.editor_content = content
            st.session_state.file_name = os.path.splitext(uploaded_file.name)[0]
            st.success(f"[INFO] {uploaded_file.name} loaded into IDE")

        st.session_state.file_name = st.text_input("File Name", st.session_state.file_name)
        code = st_ace(
            value=st.session_state.editor_content,
            language=editor_lang[language],
            theme="monokai",
            height=500,
            font_size=14
        )
        st.session_state.editor_content = code

        col_save1, col_save2 = st.columns(2)
        with col_save1:
            if st.button("Save"):
                full_path = os.path.join(SAVE_DIR, f"{st.session_state.file_name}.{extensions[language]}")
                with open(full_path,"w",encoding="utf-8") as f:
                    f.write(code)
                st.success("[INFO] File Saved to Web")
        with col_save2:
            st.download_button(
                "Download",
                data=code,
                file_name=f"{st.session_state.file_name}.{extensions[language]}",
                mime="text/plain"
            )

    with col2:
        st.subheader("Output")
        if st.button("▶ Run Code"):
            if language=="Python":
                old_stdout=sys.stdout
                redirected_output=sys.stdout=io.StringIO()
                try:
                    exec(code, st.session_state.globals)
                    output = redirected_output.getvalue()
                    st.success("[INFO] Execution Completed")
                    st.code(output if output else "[INFO] No Output")
                except Exception:
                    st.error("[INFO] Runtime Error")
                    st.code(traceback.format_exc())
                finally:
                    sys.stdout = old_stdout
            else:
                with tempfile.TemporaryDirectory() as tmpdir:
                    try:
                        if language=="C":
                            src=os.path.join(tmpdir,"main.c")
                            exe=os.path.join(tmpdir,"main")
                            open(src,"w").write(code)
                            compile_cmd=["gcc",src,"-o",exe]
                            run_cmd=[exe]
                        elif language=="C++":
                            src=os.path.join(tmpdir,"main.cpp")
                            exe=os.path.join(tmpdir,"main")
                            open(src,"w").write(code)
                            compile_cmd=["g++",src,"-o",exe]
                            run_cmd=[exe]
                        elif language=="Java":
                            src=os.path.join(tmpdir,"Main.java")
                            open(src,"w").write(code)
                            compile_cmd=["javac",src]
                            run_cmd=["java","-cp",tmpdir,"Main"]
                        elif language=="JavaScript":
                            src=os.path.join(tmpdir,"main.js")
                            open(src,"w").write(code)
                            compile_cmd=None
                            run_cmd=["node",src]
                        elif language=="Go":
                            src=os.path.join(tmpdir,"main.go")
                            exe=os.path.join(tmpdir,"main")
                            open(src,"w").write(code)
                            compile_cmd=["go","build","-o",exe,src]
                            run_cmd=[exe]
                        elif language=="Rust":
                            src=os.path.join(tmpdir,"main.rs")
                            exe=os.path.join(tmpdir,"main")
                            open(src,"w").write(code)
                            compile_cmd=["rustc",src,"-o",exe]
                            run_cmd=[exe]

                        if compile_cmd:
                            compile_proc = subprocess.run(compile_cmd, capture_output=True, text=True)
                            if compile_proc.returncode != 0:
                                st.error("[INFO] Compilation Error")
                                st.code(compile_proc.stderr)
                                st.stop()

                        run_proc = subprocess.run(run_cmd, capture_output=True, text=True)
                        if run_proc.returncode != 0:
                            st.error("[INFO] Runtime Error")
                            st.code(run_proc.stderr)
                        else:
                            st.success("[INFO] Execution Completed")
                            st.code(run_proc.stdout if run_proc.stdout else "[INFO] No Output")
                    except Exception as e:
                        st.error("[INFO] System Error")
                        st.code(str(e))