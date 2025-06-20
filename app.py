import streamlit as st
import uuid
from datetime import datetime
from openai import AzureOpenAI
from azure.search.documents import SearchClient
from azure.search.documents.models import VectorizedQuery
from azure.core.credentials import AzureKeyCredential
from azure.cosmos import CosmosClient, PartitionKey
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Access environment variables
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
AZURE_OPENAI_KEY = os.getenv("AZURE_OPENAI_KEY")
AZURE_OPENAI_EMBEDDING_DEPLOYMENT = os.getenv("AZURE_OPENAI_EMBEDDING_DEPLOYMENT")
AZURE_OPENAI_CHAT_DEPLOYMENT = os.getenv("AZURE_OPENAI_CHAT_DEPLOYMENT")

AZURE_SEARCH_ENDPOINT = os.getenv("AZURE_SEARCH_ENDPOINT")
AZURE_SEARCH_KEY = os.getenv("AZURE_SEARCH_KEY")
AZURE_SEARCH_INDEX = os.getenv("AZURE_SEARCH_INDEX")
AZURE_SEARCH_VECTOR_FIELD = os.getenv("AZURE_SEARCH_VECTOR_FIELD")
AZURE_SEARCH_CONTENT_FIELD = os.getenv("AZURE_SEARCH_CONTENT_FIELD")

COSMOS_ENDPOINT = os.getenv("COSMOS_ENDPOINT")
COSMOS_KEY = os.getenv("COSMOS_KEY")
COSMOS_DB_NAME = os.getenv("COSMOS_DB_NAME")
COSMOS_CONTAINER_NAME = os.getenv("COSMOS_CONTAINER_NAME")
COSMOS_PARTITION_KEY = os.getenv("COSMOS_PARTITION_KEY") 

# -------------------- CLIENTS --------------------
openai_client = AzureOpenAI(
    api_key=AZURE_OPENAI_KEY,
    azure_endpoint=AZURE_OPENAI_ENDPOINT,
    api_version="2025-03-01-preview"
)

search_client = SearchClient(
    endpoint=AZURE_SEARCH_ENDPOINT,
    index_name=AZURE_SEARCH_INDEX,
    credential=AzureKeyCredential(AZURE_SEARCH_KEY)
)

cosmos_client = CosmosClient(COSMOS_ENDPOINT, COSMOS_KEY)
cosmos_container = cosmos_client.get_database_client(COSMOS_DB_NAME).get_container_client(COSMOS_CONTAINER_NAME)

# -------------------- SYSTEM INSTRUCTION --------------------
SYSTEM_PROMPT = (
    "You are CollegeBot, a strict assistant that only provides information exactly as it appears in the provided dataset. "
    "Do not generate, summarize, or rephrase any information. Only answer using the exact data provided. "
    "If the answer is not found in the dataset, respond: 'Sorry, I couldn’t find that in the dataset.'"
)

# -------------------- FUNCTIONS --------------------
def get_embedding(text):
    response = openai_client.embeddings.create(
        input=[text],
        model=AZURE_OPENAI_EMBEDDING_DEPLOYMENT
    )
    return response.data[0].embedding

def search_collegebot_index(query):
    embedding = get_embedding(query)
    vector_query = VectorizedQuery(
        vector=embedding,
        k_nearest_neighbors=5,
        fields=AZURE_SEARCH_VECTOR_FIELD
    )
    results = search_client.search(
        search_text="",
        vector_queries=[vector_query]
    )
    return [doc[AZURE_SEARCH_CONTENT_FIELD] for doc in results]

def ask_gpt4o(query, context_chunks):
    if not context_chunks:
        return "Sorry, I couldn’t find that in the dataset."

    combined_context = "\n".join(context_chunks)
    response = openai_client.chat.completions.create(
        model=AZURE_OPENAI_CHAT_DEPLOYMENT,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"Question: {query}\n\nContext:\n{combined_context}"}
        ],
        temperature=0.5
    )
    return response.choices[0].message.content.strip()

# -------------------- GREETING AND CASUAL RESPONSE --------------------
def handle_greeting_or_casual_query(user_input):
    greetings = ["hi", "hello", "hey", "hii", "hola"]
    casual_questions = ["how are you", "how's it going", "what's up", "how do you do"]

    user_input_lower = user_input.lower()

    # Handle greetings
    if any(greeting in user_input_lower for greeting in greetings):
        return "Hello, I am CollegeBot! How can I assist you today?"

    # Handle casual questions
    if any(casual_query in user_input_lower for casual_query in casual_questions):
        return "I'm doing great, thanks for asking! How can I help you with college-related queries?"

    return None  # No match, let the bot handle it as usual

# -------------------- SAVE CONVERSATION TO COSMOS DB --------------------
def save_conversation_to_cosmos(session_id, conversation_history):
    conversation_data = {
        "id": session_id,
        "session_id": session_id,
        "conversation": conversation_history,
        "timestamp": datetime.utcnow().isoformat()
    }
    cosmos_container.upsert_item(conversation_data)

# -------------------- STREAMLIT UI --------------------
st.markdown("""
    <style>
    .chat-message {
        padding: 8px 16px;
        border-radius: 10px;
        margin: 5px;
        max-width: 80%;
    }

    .user {
        background-color: white;
        color: black;
        align-self: flex-end;
        text-align: right;
        margin-left: auto;
    }

    .bot {
        background-color: white;
        color: black;
        align-self: flex-start;
        text-align: left;
        margin-right: auto;
    }

    .chat-container {
        display: flex;
        flex-direction: column;
        align-items: center;

        border: 2px solid lightgray !important;
        border-radius: 10px;

        padding: 15px;
        margin-top: 20px;
        width: 100%;
        max-width: 700px;
        margin-left: auto;
        margin-right: auto;
        background-color: #f0f0f0;

        max-height: 500px;
        overflow-y: auto;
    }
    </style>
""", unsafe_allow_html=True)

st.title("🎓 Welcome to College Assistant!")

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())  # Generate unique session ID

user_input = st.chat_input("Ask me about the college...")

if user_input:
    st.session_state.chat_history.append({"role": "user", "message": user_input})

    if user_input.lower() in ["exit", "bye", "end"]:
        st.session_state.chat_history.append({"role": "bot", "message": "👋 Goodbye from CollegeBot!"})
        save_conversation_to_cosmos(st.session_state.session_id, st.session_state.chat_history)
        st.session_state.chat_history = []  # Clear chat history after goodbye
        st.session_state.session_id = str(uuid.uuid4())  # New session ID for next run
    else:
        # Check for greetings or casual queries
        greeting_or_casual_response = handle_greeting_or_casual_query(user_input)
        
        if greeting_or_casual_response:
            st.session_state.chat_history.append({"role": "bot", "message": greeting_or_casual_response})
        else:
            passages = search_collegebot_index(user_input)
            response = ask_gpt4o(user_input, passages)
            st.session_state.chat_history.append({"role": "bot", "message": response})

# Display chat messages
chat_container = "<div class='chat-container'>"
for entry in st.session_state.chat_history:
    css_class = "user" if entry["role"] == "user" else "bot"
    chat_container += f"<div class='chat-message {css_class}'><b>{entry['role'].capitalize()}:</b> {entry['message']}</div>"
chat_container += "</div>"

st.markdown(chat_container, unsafe_allow_html=True)
