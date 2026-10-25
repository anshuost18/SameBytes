import os, sys, time
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
key = os.environ.get("NEBIUS_API_KEY", "").strip()
if not key:
    sys.exit("NEBIUS_API_KEY not set in .env")

BASES = [
    "https://api.tokenfactory.nebius.com/v1/",
    "https://api.tokenfactory.us-central1.nebius.com/v1/",
]

client = None
for base in BASES:
    try:
        c = OpenAI(base_url=base, api_key=key)
        models = [m.id for m in c.models.list().data]
        print(f"OK base_url: {base} ({len(models)} models)")
        client = c
        break
    except Exception as e:
        print(f"FAIL base_url: {base} -> {type(e).__name__}: {str(e)[:150]}")
if client is None:
    sys.exit("No base URL worked. Check the key and the Token Factory console.")

print("\nNemotron models on this account:")
for m in sorted(models):
    if "nemotron" in m.lower():
        print("  ", m)

model = next((m for m in models if "nemotron-3-nano" in m.lower()), None)
if model is None:
    sys.exit("No Nemotron 3 Nano found in the list above.")

t = time.time()
r = client.chat.completions.create(
    model=model,
    messages=[{"role": "user", "content": "Reply with the single word: ready"}],
    max_tokens=50,
)
print(f"\nModel: {model}")
print("Reply:", r.choices[0].message.content)
print("Usage:", r.usage)
print(f"Latency: {time.time() - t:.2f}s")
