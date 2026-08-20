import streamlit as st
from memory.vector_store import VectorStoreManager


def render_memory_view(state: dict):
    st.subheader("🧠 Memory & Vector Store Collection Browser")
    
    vm = VectorStoreManager()
    collections = vm.list_collections()
    
    selected_col = st.selectbox("Select Chroma DB Collection", collections)
    
    st.markdown(f"Browsing items in collection: `{selected_col}`")
    
    query_input = st.text_input("Test Similarity Query in Vector Store", "experimental methodology dataset")
    if query_input:
        hits = vm.query(selected_col, query_input, n_results=5)
        st.markdown(f"Found **{len(hits)}** matching vectors:")
        for idx, hit in enumerate(hits):
            with st.expander(f"Result #{idx+1} (Score/Distance: {hit.get('score', 0):.4f})"):
                st.write(hit.get("document", ""))
                st.json(hit.get("metadata", {}))
