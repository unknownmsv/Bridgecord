import requests
from openai import OpenAI


client = OpenAI(api_key="OPENAI KEY")


user_chatcode = input("Enter your chat code: ")
user_request = input("Enter your request to AI: ")


completion = client.chat.completions.create(
    model="gpt-3.5-turbo",  
    messages=[{"role": "user", "content": user_request}]
)

ai_response = completion.choices[0].message.content


response = requests.post(
    "http://localhost:8000/send_message",  
    json={
        "code": user_chatcode,
        "message": ai_response,
        "sender": "DonutAI"
    }
)

if response.status_code == 200:
    print("Message sent successfully!")
else:
    print("Error sending message:", response.json())