import os
import openai


def call_llm(prompt: str, model: str = "gpt-4") -> str:
    # Default: OpenAI, can later extend for other LLMs
    client = openai.OpenAI(
        api_key=os.getenv("OPENAI_API_KEY"), base_url="https://api.openai.com/v1"
    )
    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
        max_tokens=150,
    )
    content = response.choices[0].message.content
    if content is None:
        raise ValueError("LLM returned empty response")
    return content
