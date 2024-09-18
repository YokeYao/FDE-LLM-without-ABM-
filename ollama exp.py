import ollama
import time

start_time = time.time()
response = ollama.chat(model='qwen:0.5b', messages=[
  {
    'role': 'user',
    'content': 'Why is the sky blue?',
  },
])
end_time = time.time()
print(f"response time cost: {end_time-start_time}\n")
print(response['message']['content'])