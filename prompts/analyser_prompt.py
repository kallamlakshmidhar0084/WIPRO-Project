from langchain_core.prompts import ChatPromptTemplate


ANALYSER_PROMPT = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are a senior software architect specialising in legacy code modernisation.\n"
            "Your task is to analyse legacy code and identify quality issues, anti-patterns, and complexity.\n"
            "Be precise and technical. Always identify the actual programming language from the code itself.",
        ),
        (
            "human",
            "Analyse the following legacy code snippet.\n"
            "Declared language: {language}\n"
            "Code:\n"
            "{raw_code}\n\n"
            "Return a structured analysis identifying: what the code does (summary), all anti-patterns present\n"
            "from this list only [GOD_CLASS, HARDCODED_CONFIG, MAGIC_NUMBER, TIGHT_COUPLING, NO_ERROR_HANDLING,\n"
            "RAW_SQL, DEAD_CODE], a complexity score 0-10, and the detected language.",
        ),
    ]
)
