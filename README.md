# 🎓 CollegeBot — AI-Powered College Information Assistant

CollegeBot is an AI-powered conversational assistant designed to answer college-related queries using **Azure OpenAI**, **Azure Cognitive Search**, and **Azure Cosmos DB**. It provides precise, dataset-backed responses without generating or assuming information, ensuring reliability for academic and administrative inquiries.

---

## 📌 Features

- 🤖 Natural conversational interface powered by **GPT-4o**
- 🔍 Contextual search using **Azure Cognitive Search vector queries**
- 📊 Embedding generation with **text-embedding-ada-002**
- 💾 Conversation history stored in **Azure Cosmos DB**
- 🎨 Streamlit web UI with styled chat interface
- 💬 Recognizes greetings and casual interactions
- ❌ Strict response policy: No assumptions, only dataset-based answers

---

## 🛠️ Tech Stack

- **Python 3.10+**
- **Streamlit**
- **Azure OpenAI (GPT-4o, ada-002 embeddings)**
- **Azure Cognitive Search**
- **Azure Cosmos DB**
- **dotenv** for secure environment variable management

---

## 📦 Installation

1️⃣ **Clone the repository**
git clone https://github.com/yourusername/collegebot.git
cd collegebot

2️⃣ Create a virtual environment
python -m venv venv
source venv/bin/activate

3️⃣ Install dependencies
pip install -r requirements.txt

4️⃣ Create a .env file in the project root and add your Azure service credentials:
AZURE_OPENAI_ENDPOINT=your_openai_endpoint
AZURE_OPENAI_KEY=your_openai_key
AZURE_OPENAI_EMBEDDING_DEPLOYMENT=text-embedding-ada-002
AZURE_OPENAI_CHAT_DEPLOYMENT=gpt-4o

AZURE_SEARCH_ENDPOINT=your_search_endpoint
AZURE_SEARCH_KEY=your_search_key
AZURE_SEARCH_INDEX=your_index_name
AZURE_SEARCH_VECTOR_FIELD=text_vector
AZURE_SEARCH_CONTENT_FIELD=content

COSMOS_ENDPOINT=your_cosmos_endpoint
COSMOS_KEY=your_cosmos_key
COSMOS_DB_NAME=your_database_name
COSMOS_CONTAINER_NAME=your_container_name
COSMOS_PARTITION_KEY=your_partition_key

5️⃣ Run the Streamlit app
streamlit run app.py
