import requests

url = "http://localhost:11434/api/generate"

response = requests.post(
    url,
    json={
        "model": "mistral:latest",
        "prompt": "xin chao",
        "stream": False
    }
)

print(response.status_code)
print(response.text[:500])