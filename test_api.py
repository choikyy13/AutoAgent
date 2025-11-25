import os
import requests
from dotenv import load_dotenv
load_dotenv()

import os
import requests
from dotenv import load_dotenv
load_dotenv()

def _call_constructor(prompt: str) -> str:


    api_key = os.getenv("CONSTRUCTOR_API_KEY")
    km_id  = os.getenv("CONSTRUCTOR_KM_ID")
    base   = os.getenv("CONSTRUCTOR_API_URL")

    if not api_key:
        raise Exception("CONSTRUCTOR_API_KEY is missing.")
    if not km_id:
        raise Exception("CONSTRUCTOR_KM_ID is missing.")
    if not base:
        raise Exception("CONSTRUCTOR_API_URL is missing.")

    headers = {
        "X-KM-AccessKey": f"Bearer {api_key}",
        "X-KM-Extension": "direct_llm"
    }

    data = {
        "model": "gpt-4o-2024-08-06",   
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "stream": "false"
    }

    url = f"{base}/knowledge-models/{km_id}/chat/completions"
    response = requests.post(url, headers=headers, json=data)

    if response.status_code != 200:
        raise Exception(f"Constructor API error {response.status_code}: {response.text}")

    # Return JUST the assistant content
    return response.json()["choices"][0]["message"]["content"]

print(_call_constructor("give me a hello world in assembly"))


'''def send_message_with_context(model, messages, stream="false"):
    api_key = os.getenv("CONSTRUCTOR_API_KEY")
    km_id = os.getenv("CONSTRUCTOR_KM_ID")
    API_BASE = os.getenv("CONSTRUCTOR_API_URL")

    headers = {'X-KM-AccessKey': f'Bearer {api_key}'}     
    data = {"model": model, "messages": messages, "stream": stream}     
    response = requests.post(f'{API_BASE}/knowledge-models/{km_id}/chat/completions', headers=headers, json=data)     
    return response.json()


messages = [
    {"role": "system", "content": "You are a helpful math tutor. Guide the user through the solution step by step.", "name": "Math tutor"},
    {"role": "user", "content": "how can I solve 8x + 7 = -23", "name": "Student"}
]
response = send_message_with_context("gpt-4o-2024-08-06", messages) 
print(response)'''