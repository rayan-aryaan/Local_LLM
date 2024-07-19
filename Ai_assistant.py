# Chat with an intelligent assistant in your terminal
import streamlit as st


def get_bot_response(client, messages):
    # Generate response from the AI model
    response_placeholder = st.empty()
    completion = client.chat.completions.create(
        model="lmstudio-community/Meta-Llama-3-8B-Instruct-GGUF",
        messages=messages,
        temperature=0.7,
        stream=True,
    )
    new_message = {"role": "assistant", "content": ""}
    for chunk in completion:
        if chunk.choices[0].delta.content:
            new_message["content"] += chunk.choices[0].delta.content
            response_placeholder.markdown(new_message["content"])
    return new_message["content"]
