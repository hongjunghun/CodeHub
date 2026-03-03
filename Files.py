import streamlit as st
import os

SAVE_DIR="saved_files"
os.makedirs(SAVE_DIR,exist_ok=True)

def show_files():
    st.header("Saved Files Manager")

    def display_folder(folder_path):
        items = sorted(os.listdir(folder_path))
        for item in items:
            full_path = os.path.join(folder_path,item)
            if os.path.isdir(full_path):
                with st.expander(f"{item}",expanded=False):
                    display_folder(full_path)
            else:
                cols = st.columns([4,1,1,1])
                rel_path = os.path.relpath(full_path,SAVE_DIR)
                key_prefix = rel_path.replace(os.sep,"_")
                with cols[0]:
                    st.write(item)
                with cols[1]:
                    if st.button("▶ Load",key=key_prefix+"_load"):
                        try:
                            with open(full_path,"r",encoding="utf-8") as f:
                                content = f.read()
                            st.session_state.editor_content = content
                            st.session_state.file_name = os.path.splitext(item)[0]
                            st.success(f"[INFO] {rel_path} loaded into IDE")
                        except Exception as e:
                            st.error(f"[INFO] Failed to load: {str(e)}")
                with cols[2]:
                    with open(full_path,"r",encoding="utf-8") as f:
                        content = f.read()
                    st.download_button("Download",data=content,file_name=item,mime="text/plain",key=key_prefix+"_download")
                with cols[3]:
                    if st.button("🗑 Delete",key=key_prefix+"_delete"):
                        os.remove(full_path)
                        st.success(f"[INFO] {rel_path} deleted")
                        st.experimental_rerun()

    if not os.listdir(SAVE_DIR):
        st.info("[INFO] No saved files found")
    else:
        display_folder(SAVE_DIR)