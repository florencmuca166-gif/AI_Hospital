import urllib.request, json

data = json.dumps({"question": "visiting hours", "history": []}).encode()
req = urllib.request.Request(
    "http://127.0.0.1:8000/ask",
    data=data,
    headers={"Content-Type": "application/json"},
    method="POST"
)
with urllib.request.urlopen(req) as r:
    print(r.read().decode())
