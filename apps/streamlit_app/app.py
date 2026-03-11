import streamlit as st
from rag_bot.pipeline import RAGPipeline

st.set_page_config(page_title="Policy-RAG-BOT", page_icon="📚")
st.title("Have Questions about Environment Policy implementation of 2024? 📚")

#rag_pipeline = RAGPipeline()
# This reuses the resources instead of running all the heavy objects repeatedly during the running of pipeline.
@st.cache_resource
def get_pipeline():
    return RAGPipeline()

rag_pipeline = get_pipeline()

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

user_input = st.chat_input("Ask a question about Environment Policy Achievements of 2024")

if user_input:
    with st.chat_message("user"):
        st.markdown(user_input)

    st.session_state.messages.append(
        {"role": "user", "content": user_input}
    )

    with st.chat_message("assistant"):
        with st.spinner("Searching knowledge base..."):
            try:
                answer = rag_pipeline.query(user_input)
                st.markdown(answer)

                st.session_state.messages.append(
                    {"role": "assistant", "content": answer}
                )

            except Exception as e:
                st.error(f"Error: {e}")