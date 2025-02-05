from flask import Flask, request, jsonify
from flask_cors import CORS  # Import CORS
from langchain_anthropic import ChatAnthropic
from langchain.memory import ConversationBufferMemory

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Set up your API key for Anthropic

api_key = ""
# Initialize the ChatAnthropic model
llm = ChatAnthropic(model="claude-3-5-sonnet-20240620", temperature=0, anthropic_api_key=api_key)

# Initialize memory for storing chat history
memory = ConversationBufferMemory()

@app.route('/chat', methods=['POST'])
def chat():
    try:
        # Get the prompt from the request body
        prompt = request.json.get('prompt')
        if not prompt:
            return jsonify({"error": "Prompt is required"}), 400

        # Retrieve past conversation history from memory
        chat_history = memory.load_memory_variables({})["history"]

        # Combine history with the new user message
        full_prompt = f"{chat_history}\nUser: {prompt}\nAI:"

        # Get the response from the LLM
        response = llm.invoke(full_prompt)

        # Log the response to check its structure
        print("Response:", response)

        # Extract the bot's response correctly
        if hasattr(response, 'content'):
            bot_message = response.content
        else:
            bot_message = "Sorry, something went wrong."

        # Store the conversation in memory
        memory.save_context({"input": prompt}, {"output": bot_message})

        return jsonify({"response": bot_message})

    except Exception as e:
        return jsonify({"error": "Something went wrong", "details": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
