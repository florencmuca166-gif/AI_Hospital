from dotenv import load_dotenv
import os
load_dotenv(".env")

key = os.getenv("OPENAI_API_KEY")
print(f"Key ends with: ...{key[-6:]}")

from openai import OpenAI
client = OpenAI(api_key=key)
r = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[{"role": "user", "content": "hi"}],
    max_tokens=5
)
print("OK:", r.choices[0].message.content)
