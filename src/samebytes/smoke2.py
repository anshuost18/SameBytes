import os, json, sys
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI(base_url="https://api.tokenfactory.nebius.com/v1/", api_key=os.environ["NEBIUS_API_KEY"])
NANO = "nvidia/NVIDIA-Nemotron-3-Nano-30B-A3B"

# 1. Plain call with room to think
r = client.chat.completions.create(model=NANO, max_tokens=1500,
    messages=[{"role": "user", "content": "Reply with the single word: ready"}])
m = r.choices[0].message
print("1. content:", repr(m.content))
print("   extra fields:", [k for k in (m.model_extra or {})])
print("   usage:", r.usage.completion_tokens, "completion tokens")

# 2. JSON mode
try:
    r = client.chat.completions.create(model=NANO, max_tokens=1500,
        response_format={"type": "json_object"},
        messages=[{"role": "user", "content": 'Return JSON with keys "cause" and "file" for: gzip run without -n in debian/rules.'}])
    print("2. json_object:", r.choices[0].message.content)
except Exception as e:
    print("2. json_object FAILED:", type(e).__name__, str(e)[:200])

# 3. Function calling
tools = [{"type": "function", "function": {"name": "read_file",
    "description": "Read a file from the source tree",
    "parameters": {"type": "object", "properties": {"path": {"type": "string"}}, "required": ["path"]}}}]
try:
    r = client.chat.completions.create(model=NANO, max_tokens=1500, tools=tools,
        messages=[{"role": "user", "content": "Read debian/rules"}])
    print("3. tool_calls:", r.choices[0].message.tool_calls)
except Exception as e:
    print("3. tools FAILED:", type(e).__name__, str(e)[:200])
