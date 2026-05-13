from langchain_core.prompts import ChatPromptTemplate


REPORT_PROMPT = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are a technical writer. Generate a professional markdown migration report.",
        ),
        (
            "human",
            "Generate the final migration report.\n"
            "Language: {language}\n"
            "Summary: {summary}\n"
            "Identified patterns: {identified_patterns}\n"
            "Complexity score: {complexity_score}\n"
            "Risk report: {risk_report}\n"
            "Modern code:\n"
            "{modern_code}\n"
            "Checklist: {checklist}\n"
            "Changes made: {changes_made}",
        ),
    ]
)
