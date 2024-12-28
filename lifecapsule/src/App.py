from flask import Flask, request, jsonify
from flask_cors import CORS
from langchain.prompts import PromptTemplate
from langchain_ollama import OllamaLLM, OllamaEmbeddings
from langchain.vectorstores import Chroma
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains import RetrievalQA
from textblob import TextBlob
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
    try:
        if os.path.exists(file_path):
            with open(file_path, 'r') as file:
                return file.read()
        return ""
    except Exception as e:
        print(f"Error loading diary entries: {e}")
        return ""

# Function to save diary entry
def save_diary_entry(file_path, entry):
    try:
        timestamp = datetime.now().strftime("%B %d, %Y")
        formatted_entry = f"{timestamp}:\n{entry.strip()}\n"
        with open(file_path, 'a') as file:
            file.write(formatted_entry)
    except Exception as e:
        print(f"Error saving diary entry: {e}")

# Perform sentiment analysis
def analyze_sentiment(text):
    try:
        blob = TextBlob(text)
        return blob.sentiment.polarity  # Returns a value between -1 (negative) and 1 (positive)
    except Exception as e:
        print(f"Error analyzing sentiment: {e}")
        return 0

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
        template="{user_input}"
    )

    # Format the input
    formatted_prompt = prompt_template.format(user_input=prompt)

    # Use the Ollama model to generate a response
    try:
        result = ollama_llm.invoke(formatted_prompt)
        return result
    except Exception as e:
        print(f"Error invoking Ollama model: {e}")
        return "I encountered an error while processing your request. Please try again."

# Analyze the diary
def analyze_diary(query):
    if not query.strip():
        return "Please provide a valid question."

    if not qa_chain:
        return "The knowledge base is empty. Please add diary entries first."

    try:
        diary_content = load_diary_entries(DIARY_FILE_PATH)
        entries = diary_content.split("\n\n")  # Split entries by double newlines for proper segmentation

        # Analyze for specific emotions based on query
        if "happy" in query.lower() or "joy" in query.lower():
            positive_entries = [
                entry for entry in entries if analyze_sentiment(entry) > 0.5
            ]
            if positive_entries:
                return f"You seemed happy or joyful on the following days:\n{'\n'.join(positive_entries)}"
            else:
                return "I couldn't find any clear indications of happiness in your diary."

        elif "sad" in query.lower() or "down" in query.lower():
            negative_entries = [
                entry for entry in entries if analyze_sentiment(entry) < -0.5
            ]
            if negative_entries:
                return f"You seemed sad or down on the following days:\n{'\n'.join(negative_entries)}"
            else:
                return "I couldn't find any clear indications of sadness in your diary."

        elif "angry" in query.lower() or "frustrated" in query.lower():
            angry_entries = [
                entry for entry in entries if -0.5 <= analyze_sentiment(entry) < 0
            ]
            if angry_entries:
                return f"You seemed angry or frustrated on the following days:\n{'\n'.join(angry_entries)}"
            else:
                return "I couldn't find any clear indications of anger in your diary."

        elif "calm" in query.lower() or "peaceful" in query.lower():
            calm_entries = [
                entry for entry in entries if 0 <= analyze_sentiment(entry) <= 0.5
            ]
            if calm_entries:
                return f"You seemed calm or peaceful on the following days:\n{'\n'.join(calm_entries)}"
            else:
                return "I couldn't find any clear indications of calmness in your diary."

        # Default case to query the knowledge base
        result = qa_chain({"query": query})
        return result.get("result", "I couldn't find a relevant answer in your diary. Perhaps rephrasing your question could help.")
    except Exception as e:
        print(f"Error analyzing diary: {e}")
        return "Something went wrong while analyzing your diary. Please try again later."

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
        return jsonify({"status": "success", "message": "Your diary entry has been saved."}), 200
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
