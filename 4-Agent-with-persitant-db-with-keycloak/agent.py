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
from pymongo import MongoClient
from datetime import datetime

from mongo_client import save_chat_to_mongo,get_chat_history,get_all_chats,render_chat_history
import uuid
from keycloak import KeycloakOpenID


load_dotenv()

openai_api_key = os.getenv("OPENAI_API_KEY")

KEYCLOAK_SERVER = "http://192.168.1.190:8501//auth/"
KEYCLOAK_REALM = "LanChainChatbot1"
KEYCLOAK_CLIENT_ID = "StreamlitBlog-Client"
KEYCLOAK_CLIENT_SECRET = "Gc82Ppmbp3xQMTbK3u1DS3Tc3Pjf3lhP"

KEYCLOAK_LOGOUT_URL = "http://192.168.1.190:8080/realms/LangGraphChatbot/protocol/openid-connect/logout"
REDIRECT_URI_AFTER_LOGOUT = "http://192.168.1.190:8501/"
KEYCLOAK_CLIENT_ID = "StreamlitBlog-Client"

keycloak_openid = KeycloakOpenID(
    server_url=KEYCLOAK_SERVER,
    client_id=KEYCLOAK_CLIENT_ID,
    realm_name=KEYCLOAK_REALM,
    client_secret_key=KEYCLOAK_CLIENT_SECRET
)
# Check if the user is logged in
# Check if the user is logged in

if not st.user.is_logged_in:
    st.write("No user is logged in.")
    if st.button("Log in with Keycloak"):
        st.login("keycloak")  # matches [auth.keycloak] in secrets.toml
        st.stop()
user_id=""

if st.user.is_logged_in:
    st.success("✅ User is logged in.")
    #st.write("Username:", st.user.username)
    st.write("Email:", st.user.email)
    st.write("Name:", st.user.given_name)
    user_id=st.user.preferred_username
    st.write("User name:", user_id)  
    full_chat = get_chat_history(user_id) 
    if full_chat:
         render_chat_history(full_chat,st)
   
       


##3 for Logout
if st.sidebar.button("Logoff"):
    st.session_state.clear()
    st.logout()

    params = {
                "post_logout_redirect_uri": REDIRECT_URI_AFTER_LOGOUT,
                "client_id": KEYCLOAK_CLIENT_ID,
            }
    logout_url = f"{KEYCLOAK_LOGOUT_URL}?{urlparse.urlencode(params)}"
    st.markdown(f'<meta http-equiv="refresh" content="0; url={logout_url}">', unsafe_allow_html=True)
    st.stop()

st.title("🔐 Secure PDF RAG App")


# UI
st.set_page_config(page_title="RAG PDF Chatbot", layout="wide")
st.title("📄 Uplaod Your PDF")


query = st.text_input("Enter your question:")


# Generate a session ID once per user session
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

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


prompt = ChatPromptTemplate.from_template("""
Answer the question using the provided context. If you don't know the answer, say "I don't know".

<context>
{context}
</context>

Question: {input}
""")

# 3. Embed and store into ChromaDB
embedding = OpenAIEmbeddings(openai_api_key=openai_api_key)
vectorstore = Chroma.from_documents(chunks, embedding=embedding, persist_directory="../chroma_store")
retriever = vectorstore.as_retriever(search_kwargs={"k": 3})


# 5. Set up the LLM
llm = ChatOpenAI(openai_api_key=openai_api_key, temperature=0)

memory = ConversationSummaryBufferMemory(
            llm=llm, memory_key="chat_history", return_messages=True
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
          # ✅ Save to MongoDB
        save_chat_to_mongo(
            user_id= user_id,
            session_id=st.session_state.session_id,
            user_msg=query,
            ai_msg=answer,
            pdf_file=uploaded_file.name if uploaded_file else ""
        )
        st.markdown("### 🤖 Answer")
        st.write(answer)




