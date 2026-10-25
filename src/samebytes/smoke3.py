import os, json
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI(base_url="https://api.tokenfactory.nebius.com/v1/", api_key=os.environ["NEBIUS_API_KEY"])
MODELS = {"ultra": "nvidia/Nemotron-3-Ultra-550b-a55b", "super": "nvidia/nemotron-3-super-120b-a12b"}
tools = [{"type": "function", "function": {"name": "read_file", "description": "Read a file",
    "parameters": {"type": "object", "properties": {"path": {"type": "string"}}, "required": ["path"]}}}]

for name, model in MODELS.items():
    print(f"=== {name}: {model}")
    try:
        r = client.chat.completions.create(model=model, max_tokens=3000, response_format={"type": "json_object"},
            messages=[{"role": "user", "content": 'Return JSON with keys "cause" and "file" for: gzip run without -n in debian/rules.'}])
        print("json:", (r.choices[0].message.content or "").strip()[:200], "| tokens:", r.usage.completion_tokens)
    except Exception as e:
        print("json FAILED:", type(e).__name__, str(e)[:200])
    try:
        r = client.chat.completions.create(model=model, max_tokens=3000, tools=tools,
            messages=[{"role": "user", "content": "Read debian/rules"}])
        print("tools:", r.choices[0].message.tool_calls)
    except Exception as e:
        print("tools FAILED:", type(e).__name__, str(e)[:200])

# caching probe: same long prefix twice, compare usage details
long = "Catalogue entry. " * 1500
for i in (1, 2):
    r = client.chat.completions.create(model="nvidia/NVIDIA-Nemotron-3-Nano-30B-A3B", max_tokens=300,
        messages=[{"role": "system", "content": long}, {"role": "user", "content": "Say ok"}])
    print(f"cache run {i}:", r.usage)
