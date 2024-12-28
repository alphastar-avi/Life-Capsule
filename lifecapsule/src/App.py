from flask import Flask, request, jsonify
from flask_cors import CORS
from langchain.prompts import PromptTemplate
from langchain_ollama import OllamaLLM, OllamaEmbeddings
from langchain.vectorstores import Chroma
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains import RetrievalQA
import os
from datetime import datetime

# Flask app setup
app = Flask(__name__)
CORS(app)

# Constants
DIARY_FILE_PATH = "./diary.txt"

# Global Variables
vectorstore = None
qa_chain = None

# Initialize the Ollama model
ollama_llm = OllamaLLM(model="llama3.2", streaming=False)

# Initialize Embeddings
embeddings = OllamaEmbeddings(model="llama3.2")

# Initialize Text Splitter
text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)

# Function to load diary entries
def load_diary_entries(file_path):
    if os.path.exists(file_path):
        with open(file_path, 'r') as file:
            return file.read()
    return ""

# Function to save diary entry
def save_diary_entry(file_path, entry):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(file_path, 'a') as file:
        file.write(f"\n[{timestamp}] {entry}")

# Update the knowledge base
def update_knowledge_base():
    global vectorstore, qa_chain
    diary_content = load_diary_entries(DIARY_FILE_PATH)
    
    if diary_content.strip():
        # Split diary content
        split_texts = text_splitter.split_text(diary_content)
        
        # Create a vector store with the embeddings
        vectorstore = Chroma.from_texts(split_texts, embeddings)
        
        # Create a retrieval chain
        qa_chain = RetrievalQA.from_chain_type(
            llm=ollama_llm,
            retriever=vectorstore.as_retriever(),
            return_source_documents=True
        )
        print("Knowledge base updated.")
    else:
        vectorstore = None
        qa_chain = None
        print("No entries found in the diary. Knowledge base is empty.")

# Process a user query using the Ollama model
def process_prompt_with_model(prompt):
    # Define a prompt template
    prompt_template = PromptTemplate(
        input_variables=["user_input"],
        template="User input: {user_input}. Please provide a response."
    )
    
    # Format the input
    formatted_prompt = prompt_template.format(user_input=prompt)
    
    # Use the Ollama model to generate a response
    try:
        result = ollama_llm.invoke(formatted_prompt)
        return result
    except Exception as e:
        print(f"Error invoking Ollama model: {e}")
        return "Error generating a response from the model."

# Analyze the diary
def analyze_diary(query):
    if not query.strip():
        return "Please provide a valid question."
    
    if not qa_chain:
        return "The knowledge base is empty. Please add diary entries first."
    
    try:
        # Query the knowledge base
        result = qa_chain({"query": query})
        return result.get("result", "I couldn't find a relevant answer in your diary.")
    except Exception as e:
        print(f"Error analyzing diary: {e}")
        return "Something went wrong. Please try again later."

# Initialize the knowledge base on server start
update_knowledge_base()

# API Endpoint to save diary entries
@app.route('/save_diary', methods=['POST'])
def save_diary():
    data = request.json
    entry = data.get('entry', '').strip()
    
    if entry:
        save_diary_entry(DIARY_FILE_PATH, entry)
        update_knowledge_base()  # Update the knowledge base with the new entry
        return jsonify({"status": "success"}), 200
    return jsonify({"status": "error", "message": "No entry provided."}), 400

# API Endpoint to analyze diary
@app.route('/analyze_diary', methods=['POST'])
def analyze_diary_endpoint():
    query = request.json.get('query', '').strip()
    
    if query:
        response = analyze_diary(query)
        return jsonify({"answer": response}), 200
    return jsonify({"status": "error", "message": "No query provided."}), 400

# API Endpoint for prompt-based queries using Ollama model
@app.route('/prompt_query', methods=['POST'])
def prompt_query():
    data = request.json
    prompt = data.get('prompt', '').strip()
    
    if prompt:
        response = process_prompt_with_model(prompt)
        return jsonify({"response": response}), 200
    return jsonify({"status": "error", "message": "No prompt provided."}), 400

# Run the Flask app
if __name__ == '__main__':
    app.run(debug=True)
