
chat() {
    if [ -z "$1" ]; then
        echo "Please enter a message for ChatGPT."
        return 1
    fi

    # Call the python script and pass the message
    command python3 ~/.oh-my-zsh/custom/plugins/zsh-chatgpt/chatgpt_plugin.py "$*"
}

