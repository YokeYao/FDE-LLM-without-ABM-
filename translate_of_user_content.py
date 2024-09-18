import json
from tqdm import tqdm
from gpt_request import ChatGLMAPI

# Initialize the API
chatglm_api = ChatGLMAPI()

# Load the content from the JSON file
with open('user_content1.json', 'r') as file:
    data = json.load(file)

# Iterate over the contents, translate it, and update the content
for item in tqdm(data, desc="Translating content", unit="item"):
    original_content = item['content']

    prompt = [{
        "role": "user",
        "content": f"English translation of {original_content}"
    }]
    response = chatglm_api.ChatGLM_single_request(prompt)

    item['content'] = response

# Write the updated content back to the JSON file
with open('user_content2.json', 'w') as file:
    json.dump(data, file)

print("Translation completed and written back to 'user_content2.json'.")
