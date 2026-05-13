from langchain_core.prompts import ChatPromptTemplate


GENERATOR_PROMPT = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are a senior engineer rewriting legacy code into modern, production-quality code.\n"
            "Every significant change MUST have an inline comment explaining why it was made.\n"
            "Generate complete, runnable code only — no TODOs, no placeholders.",
        ),
        (
            "human",
            "Rewrite this legacy code into modern code.\n"
            "Language: {language}\n"
            "Target framework: {target_framework}\n"
            "Identified patterns: {identified_patterns}\n"
            "Risk report: {risk_report}\n"
            "Legacy code:\n"
            "{raw_code}",
        ),
    ]
)
