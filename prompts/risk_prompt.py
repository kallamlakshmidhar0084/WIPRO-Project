from langchain_core.prompts import ChatPromptTemplate


RISK_PROMPT = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are a migration risk analyst. The runtime has already executed all three required tools — \n"
            "calculate_complexity_score, assess_breaking_changes, and estimate_migration_effort — \n"
            "and will provide their results. Use those tool results when forming your final RiskReport.\n"
            "Risk classification rules (deterministic, do not override with LLM judgement):\n"
            "- CRITICAL: if any hardcoded credentials or connection strings are found in the code\n"
            "- HIGH: if raw SQL without ORM or parameterisation is present\n"
            "- MEDIUM: if error handling is absent (On Error Resume Next, empty catch blocks)\n"
            "- LOW: if none of the above apply",
        ),
        (
            "human",
            "Assess migration risk for this code.\n"
            "Language: {language}\n"
            "Identified patterns: {identified_patterns}\n"
            "Code:\n"
            "{raw_code}\n"
            "Use the provided tool results then return a complete RiskReport.",
        ),
    ]
)
