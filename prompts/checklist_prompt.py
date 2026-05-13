from langchain_core.prompts import ChatPromptTemplate


CHECKLIST_PROMPT = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are a migration project manager. Generate a concrete, ordered migration checklist.",
        ),
        (
            "human",
            "Build a migration checklist.\n"
            "Language: {language}\n"
            "Modern code:\n"
            "{modern_code}\n"
            "Risk report: {risk_report}\n"
            "Identified patterns: {identified_patterns}",
        ),
    ]
)
