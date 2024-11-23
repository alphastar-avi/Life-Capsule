from langchain_ollama import OllamaLLM  # New import
from langchain.prompts import PromptTemplate

# Function to get user input and process with Ollama model
def process_prompt_with_model(user_prompt):
    # Initialize the Ollama model (adjust parameters as per your setup)
    model = OllamaLLM(model="3B")  # Updated model call
    
    # Create a prompt template using LangChain
    prompt_template = PromptTemplate(
        input_variables=["user_input"],
        template="User input: {user_input}. Please provide a response."
    )
    
    # Format the prompt with the user input
    formatted_prompt = prompt_template.format(user_input=user_prompt)

    # Process the prompt with the Ollama model (using 'invoke' instead of '__call__')
    result = model.invoke(formatted_prompt)

    # Output the result to the terminal
    print("Model response:\n", result)

# Main loop to continuously get user input and process it
def main():
    print("Ollama Model is ready. Type your prompts below (type 'exit' to quit):")
    
    while True:
        user_input = input("Your prompt: ")
        
        if user_input.lower() == 'exit':
            print("Exiting...")
            break
        
        # Process the input with the Ollama model
        process_prompt_with_model(user_input)

if __name__ == "__main__":
    main()
