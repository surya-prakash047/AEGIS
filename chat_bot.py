# streamlit_app.py
import streamlit as st
from langchain.chains import RetrievalQA
from langchain_community.chat_models import ChatOllama
from RAG.rag_loader import load_vectorstore

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []

# Set up the Streamlit app
st.title("Disaster Management Chatbot")
st.markdown("Ask questions here.")

# Load vectorstore and set up retriever
vectorstore = load_vectorstore()
retriever = vectorstore.as_retriever(search_kwargs={"k": 3})

# Set up the QA chain with Ollama chat model
qa_chain = RetrievalQA.from_chain_type(
    llm=ChatOllama(model="gemma3:1b"),
    retriever=retriever
)

# Chat input
user_input = st.chat_input("Your question:")
if user_input:
    # Display user message
    #st.chat_message("user").markdown(user_input)
    st.session_state.messages.append({"role": "user", "content": user_input})

    # Generate response
    response = qa_chain.invoke(user_input)
    #st.chat_message("assistant").markdown(response['result'])
    st.session_state.messages.append({"role": "assistant", "content": response['result']})

# Display chat history
for msg in st.session_state.messages:
    st.chat_message(msg["role"]).markdown(msg["content"])
