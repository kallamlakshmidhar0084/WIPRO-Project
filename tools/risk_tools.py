from langchain_core.tools import tool


@tool
def calculate_complexity_score(code: str, patterns: list[str]) -> float:
    """Calculate a 0-10 migration complexity score from code size, patterns, and nesting."""
    base_score = min(len(code.splitlines()) / 50, 5.0)
    pattern_weights = {
        "GOD_CLASS": 2.0,
        "TIGHT_COUPLING": 1.5,
        "HARDCODED_CONFIG": 1.0,
        "MAGIC_NUMBER": 0.5,
        "NO_ERROR_HANDLING": 1.0,
        "RAW_SQL": 1.5,
        "DEAD_CODE": 0.5,
    }
    pattern_score = sum(pattern_weights.get(pattern, 0.5) for pattern in patterns)
    nesting_score = code.count("    ") / max(len(code.splitlines()), 1) * 2
    return min(round(base_score + pattern_score + nesting_score, 2), 10.0)


@tool
def assess_breaking_changes(code: str, language: str) -> dict:
    """Assess deprecated API markers and signature migration risks in legacy code."""
    deprecated_markers = {
        "VB6/ClassicASP": ["On Error Resume Next", "CreateObject", "ADODB", "Response.Write"],
        "JavaEE": ["EJB", "javax.", "HttpServlet", "doGet", "doPost"],
        "COBOL": ["PERFORM", "GOTO", "PIC X", "WORKING-STORAGE"],
    }
    lowered_code = code.lower()
    deprecated_apis = [
        marker
        for markers in deprecated_markers.values()
        for marker in markers
        if marker.lower() in lowered_code
    ]
    signature_risks = [f"{language} migration requires interface and entrypoint review"] if deprecated_apis else []
    return {
        "deprecated_apis": deprecated_apis,
        "signature_risks": signature_risks,
        "risk_count": len(deprecated_apis) + len(signature_risks),
    }


@tool
def estimate_migration_effort(risk_level: str, complexity_score: float, lines_of_code: int) -> int:
    """Estimate migration effort in days from risk level, complexity, and code size."""
    base = {"LOW": 2, "MEDIUM": 5, "HIGH": 10, "CRITICAL": 20}.get(risk_level, 5)
    return int(base + (complexity_score * 1.5) + (lines_of_code / 100))
