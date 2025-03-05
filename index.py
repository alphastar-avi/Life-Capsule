from langchain_ollama import OllamaLLM  
from langchain.prompts import PromptTemplate


def process_prompt_with_model(user_prompt):
    model = OllamaLLM(model="3B") 
    
    prompt_template = PromptTemplate(
        input_variables=["user_input"],
        template="User input: {user_input}. Please provide a response."
    )
    
    formatted_prompt = prompt_template.format(user_input=user_prompt)

    result = model.invoke(formatted_prompt)


    print("Model response:\n", result)


def main():
    print("Ollama Model is ready! Type your prompts below (type 'exit' to quit):")
    
    while True:
        user_input = input("Your prompt: ")
        
        if user_input.lower() == 'exit':
            print("Exiting...")
            break
        
        process_prompt_with_model(user_input)

if __name__ == "__main__":
    main()
