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

load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")

# UI
st.set_page_config(page_title="RAG PDF Chatbot", layout="wide")
st.title("📄 Ask Questions About Your PDF")
query = st.text_input("Enter your question:")


loader = PyPDFLoader("Manoj-Resume.pdf")
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



prompt = ChatPromptTemplate.from_template("""
Answer the following question using the provided context. 
If the context does not contain the answer, say "I don't know."

<context>
{context}
</context>

Question: {input}
""")

combine_docs_chain = create_stuff_documents_chain(llm=llm, prompt=prompt)
rag_chain = create_retrieval_chain(retriever=retriever, combine_docs_chain=combine_docs_chain)


#res=prompt | llm
#rresult=res.invoke({"input": "who is Manoj Kumar?", "context": "Manoj Kumar is a software engineer with expertise in Python and machine learning."})
# 9. Output
#rag_chain_response = rag_chain.invoke({"input": "who is Manoj Kumar?", "context": "Manoj Kumar is a software engineer "})
#print(rag_chain_response["answer"])
##print(response["result"])
# Step 2: Run RAG chain
if query:
    with st.spinner("Generating answer..."):
        result = rag_chain.invoke({"input": query, "context": "tell me in details"})
        st.markdown("### 🤖 Answer")
        st.write(result["answer"])
