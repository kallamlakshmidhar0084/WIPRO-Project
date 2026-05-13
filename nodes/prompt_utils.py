def to_litellm_messages(prompt, values: dict) -> list[dict]:
    """Convert a LangChain prompt template into LiteLLM chat messages."""
    role_map = {"human": "user", "ai": "assistant"}
    return [
        {
            "role": role_map.get(message.type, message.type),
            "content": message.content,
        }
        for message in prompt.format_messages(**values)
    ]
