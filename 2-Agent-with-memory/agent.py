from langchain_community.vectorstores import Chroma
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from dotenv import load_dotenv
import os
from langchain_core.prompts import ChatPromptTemplate
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains import create_retrieval_chain
import streamlit as st
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationSummaryBufferMemory
import tempfile


load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")

# UI
st.set_page_config(page_title="RAG PDF Chatbot", layout="wide")
st.title("📄 Uplaod Your PDF")
query = st.text_input("Enter your question:")

# ----------------------
# Session State Init
# ----------------------
if "chat_history_ui" not in st.session_state:
    st.session_state.chat_history_ui = []

# File uploader
uploaded_file = st.file_uploader("📤 Upload a PDF file", type="pdf")
tmp_path = ""  # default file

if uploaded_file:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
        tmp_file.write(uploaded_file.read())
        tmp_file.flush()
        tmp_path = tmp_file.name
if not os.path.exists(tmp_path) or tmp_path=="":
    st.warning("Please upload a PDF file to proceed.")
    st.stop()
else:
    loader = PyPDFLoader(tmp_path)
    documents = loader.load()

# 2. Split the documents into chunks
text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=100)
chunks = text_splitter.split_documents(documents)


# 3. Embed and store into ChromaDB
embedding = OpenAIEmbeddings(openai_api_key=openai_api_key)
vectorstore = Chroma.from_documents(chunks, embedding=embedding, persist_directory="../chroma_store")
retriever = vectorstore.as_retriever(search_kwargs={"k": 3})


# 5. Set up the LLM
llm = ChatOpenAI(openai_api_key=openai_api_key, temperature=0)

 # 🧠 Memory with summarization
memory = ConversationSummaryBufferMemory(
        llm=llm,
        memory_key="chat_history",
        return_messages=True
    )



 # Create RAG chain with memory
rag_chain = ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=retriever,
        memory=memory,
        verbose=True
    )


if query:
    with st.spinner("Generating answer..."):
        result = rag_chain.invoke(query)
        answer = result["answer"]

        # Store for UI rendering
        st.session_state.chat_history_ui.append(("user", query))
        st.session_state.chat_history_ui.append(("assistant", answer))

        st.markdown("### 🤖 Answer")
        st.write(answer)

# ----------------------
# Render UI Chat History
# ----------------------
if st.session_state.chat_history_ui:
    st.markdown("### Chat History")
    for role, msg in st.session_state.chat_history_ui:
        if role == "user":
            st.markdown(f"**🧑 You:** {msg}")
        else:
            st.markdown(f"**🤖 Assistant:** {msg}")
