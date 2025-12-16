# mongo_client.py
from pymongo import MongoClient
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()
MONGO_URI = os.getenv("MONGO_URI")  # set this in .env

client = MongoClient(MONGO_URI)
db = client["pdfusion_rag"]
chat_collection = db["chat_history"]

def save_chat_to_mongo(user_id,session_id, user_msg, ai_msg, source="PDFusion", pdf_file=""):
    chat_collection.insert_one({
        "user_id": user_id,
        "session_id": session_id,
        "timestamp": datetime.utcnow(),
        "user_message": user_msg,
        "assistant_message": ai_msg,
        "source": source,
        "pdf_file": pdf_file
    })

def save_chat_to_mongo_without_user(session_id, user_msg, ai_msg, source="PDFusion", pdf_file=""):
    chat_collection.insert_one({
         "session_id": session_id,
        "timestamp": datetime.utcnow(),
        "user_message": user_msg,
        "assistant_message": ai_msg,
        "source": source,
        "pdf_file": pdf_file
    })

def get_chat_history(user_id):
    return list(chat_collection.find({"user_id": user_id}))

def get_all_chats():
    """
    Returns all chat history documents in the 'chat_history' collection,
    sorted by timestamp (oldest to newest).
    """
    return list(chat_collection.find({}).sort("timestamp", 1))

# ----------------------
# Render UI Chat History
# ---------------------
def render_chat_history(full_chat,st):
    if full_chat:
        st.markdown("## 💬 Chat History")
        for chat in full_chat:
            st.markdown(f"**User:** {chat['user_message']}")
            st.markdown(f"**Assistant:** {chat['assistant_message']}")
            st.markdown("---") 
