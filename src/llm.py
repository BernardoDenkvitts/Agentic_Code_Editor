import os
import json
import hashlib
from groq import Groq


client = Groq(api_key=os.environ["GROQ_API_KEY"])
MODEL = "qwen/qwen3-32b"


def call_llm(system_prompt: str, user_message: str) -> str:
    """Call the LLM with a system prompt and user message."""
    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user",   "content": user_message}
        ],
        temperature=0,
        response_format={"type": "json_object"}
    )
    return response.choices[0].message.content.strip()

def call_llm_json(system_prompt: str, user_message: str) -> dict:
    """
    Call the LLM and return the response as a JSON object.
    Used when we need structured output (e.g. from orchestrator)
    """
    raw = call_llm(system_prompt, user_message)
    return json.loads(raw)

def call_llm_cached(system_prompt: str, user_message: str) -> str:
    # Unique key based on input
    key = hashlib.md5(f"{system_prompt}{user_message}".encode()).hexdigest()
    cache_path = f".cache/{key}.json"
    
    if os.path.exists(cache_path):
        with open(cache_path) as f:
            return json.load(f)["response"]
    
    result = call_llm(system_prompt, user_message)
    
    os.makedirs(".cache", exist_ok=True)
    with open(cache_path, "w") as f:
        json.dump({"response": result}, f)
    return result

def call_llm_json_cached(system_prompt: str, user_message: str) -> dict:
    raw = call_llm_cached(system_prompt, user_message)
    return json.loads(raw)