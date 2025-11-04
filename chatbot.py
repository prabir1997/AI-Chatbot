import google.generativeai as genai
genai.configure(api_key="AIzaSyDJ6TxQW9viXxpqXhvEmLSKUDrD3X76XX0")

for m in genai.list_models():
    if "generateContent" in m.supported_generation_methods:
        print(m.name)
