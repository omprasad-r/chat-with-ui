import openai

##sets up the initial conversation between the user and the AI
def get_initial_message():
    messages=[
            {"role": "system", "content": "You are a helpful AI ChatBot. Who anwers brief questions about AI."},
            #{"role": "user", "content": "Hell, I am Rohit"},
            #{"role": "assistant", "content": "Thats awesome, Welcome Rohit...!!!"}
        ]
    return messages

##takes the messages and the model as input, makes an API call to ChatGPT, and returns the generated response
def get_chatgpt_response(messages, model="gpt-3.5-turbo"):
    
    response = openai.ChatCompletion.create(
    model=model,
    messages=messages
    )
    return  response['choices'][0]['message']['content']

##appends new messages to the conversation
def update_chat(messages, role, content):
    messages.append({"role": role, "content": content})
    return messages