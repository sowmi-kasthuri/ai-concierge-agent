from agent.config import config

print("Provider:", config.provider)
print("Gemini key exists:", bool(config.gemini_key))
print("OpenRouter key exists:", bool(config.openrouter_key))
print("Gemini model:", config.gemini_model)
print("OpenRouter model:", config.openrouter_model)
