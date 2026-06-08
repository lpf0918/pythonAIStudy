import requests

url = 'http://127.0.0.1:5000/submit'
payload = {"user_name": "李四", "pwd": "abc123"}

response = requests.post(url, json=payload)
print(response.json())