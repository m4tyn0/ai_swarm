import requests

# Setup headers if token is being used
api_token = "crawlujuju"  # Same token set in CRAWL4AI_API_TOKEN
headers = {"Authorization": f"Bearer {api_token}"} if api_token else {}

# Making authenticated requests
response = requests.post(
    "http://localhost:11235/crawl",
    headers=headers,
    json={
        "urls": "https://example.com",
        "priority": 10
    }
)

# Checking task status
task_id = response.json()["task_id"]
status = requests.get(
    f"http://localhost:11235/task/{task_id}",
    headers=headers
)
print (status)