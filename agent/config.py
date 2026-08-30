import os


OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "").strip()

AI_MODEL = os.environ.get(
    "NEXORA_AI_MODEL",
    "gpt-5.6"
)
