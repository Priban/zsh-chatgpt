import openai
import sys
import os
import json
import configparser
import textwrap

# Configurations
CONFIG_FILE = "/Users/lpriban/.oh-my-zsh/custom/plugins/zsh-chatgpt/openai.config"
CONVERSATION_FILE = "/Users/lpriban/.oh-my-zsh/custom/plugins/zsh-chatgpt/conversation.json"
RESPONSE_TEXT_WIDTH = 80

def get_token_from_config():
    config = configparser.ConfigParser()
    try:
        config.read(CONFIG_FILE)
        return config['openai']['token_id']
    except KeyError:
        print(f"Error reading token from {CONFIG_FILE}")
        exit(1)

def send_to_gpt3(text):
    openai.api_key = get_token_from_config()
    messages = [{"role": "system", "content": "You are a helpful assistant operating in a zsh terminal with oh-my-zsh on an M1 Mac. Provide concise, accurate, and relevant answers to user queries in this command-line context."}]

    # Load previous conversation
    if os.path.exists(CONVERSATION_FILE):
        with open(CONVERSATION_FILE, 'r') as f:
            conversation = json.load(f)
            for q, a in zip(conversation["questions"], conversation["answers"]):
                messages.append({"role": "user", "content": q})
                messages.append({"role": "assistant", "content": a})

    # Append current message
    messages.append({"role": "user", "content": text})

    # Create the completion with streaming enabled
    completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages,
        stream=True
    )

    full_response = ''
    for chunk in completion:
        delta = chunk.choices[0].delta
        delta_content = delta.get("content", "")  # Use get() to provide a default value if 'content' is absent
        full_response += delta_content
        if delta_content:  # Only print if there's content
            sys.stdout.write(delta_content)
            sys.stdout.flush()            
 
    return full_response

def save_conversation(question, answer):
    conversation = {"questions": [], "answers": []}
    if os.path.exists(CONVERSATION_FILE):
        with open(CONVERSATION_FILE, 'r') as f:
            conversation = json.load(f)

    conversation["questions"].append(question)
    conversation["answers"].append(answer)

    with open(CONVERSATION_FILE, 'w') as f:
        json.dump(conversation, f)

def clear_conversation():
    if os.path.exists(CONVERSATION_FILE):
        os.remove(CONVERSATION_FILE)

def wrap_text_preserving_newlines(text, width):
    # Split the text into lines and wrap each line individually
    wrapped_lines = [textwrap.fill(line, width=width) for line in text.splitlines()]
    # Join the wrapped lines with newline characters
    return '\n'.join(wrapped_lines)

if __name__ == "__main__":
    if "--clear" in sys.argv:
        clear_conversation()
        print("Conversation cleared.")
    else:
        if len(sys.argv) < 2:
            print("Please provide a text to send to GPT-3.5 Turbo.")
            sys.exit(1)

        text = sys.argv[1]
        response = send_to_gpt3(text)
        sys.stdout.write("\n")
        sys.stdout.flush()

        # wrapped_response = wrap_text_preserving_newlines(response, RESPONSE_TEXT_WIDTH)

        save_conversation(text, response)

