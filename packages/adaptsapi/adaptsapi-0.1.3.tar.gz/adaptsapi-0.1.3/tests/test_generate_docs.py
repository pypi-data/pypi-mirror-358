import requests
import os
from adaptsapi.generate_docs import post, PayloadValidationError

payload = {
    "user_id": "d36a113a-25d3-402b-8f5d-9e443f5570cd",
    "email_address": "sheel@adapts.ai",
    "user_name": "sheel",
    "repo_object": {
        "repository_name": "kotlin-tree-sitter",
        "source": "github",
        "repository_url": "https://github.com/tree-sitter/kotlin-tree-sitter",
        "branch": "master",
        "size": "100",
        "language": "Kotlin",
        "is_private": False,
        "git_provider_type": "github",
        "refresh_token": "1234567890"
    },
}

try:
    AUTH_TOKEN = os.getenv("ADAPTS_API_KEY")
    resp = post("https://ycdwnfjohl.execute-api.us-east-1.amazonaws.com/prod/generate_wiki_docs", AUTH_TOKEN, payload)
    resp.raise_for_status()
    print(resp.json())
except PayloadValidationError as e:
    print("Invalid payload:", e)
except requests.RequestException as e:
    print("Request failed:", e)
