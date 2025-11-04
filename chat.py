import google.generativeai as ai

# Paste your API key here
API_KEY = 'AIzaSyDJ6TxQW9viXxpqXhvEmLSKUDrD3X76XX0'
ai.configure(api_key=API_KEY)

# Initialize the model
model = ai.GenerativeModel("gemini-2.5-flash")
chat = model.start_chat()

# Start the conversation loop
while True:
    message = input('You: ')
    if message.lower() == 'bye':
        print('Chatbot: Goodbye!')
        break
    response = chat.send_message(message)
    print('Chatbot:', response.text)